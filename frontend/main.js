const API = "https://english-agent-mvp-production.up.railway.app";
const USER = "Junior";
const AGENT_NAME = "Professor Liam";

// Global variables
let mediaRecorder = null;
let audioChunks = [];
let recordingTimer = null;
let recordingStartTime = null;
let audioUsage = 0;
let audioLimit = 10;
let deferredPrompt = null; // For PWA installation

// DOM Elements
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const stopRecordBtn = document.getElementById("stopRecord");
const visualizer = document.getElementById("visualizer");
const visualizerBars = document.querySelector(".visualizer-bars");
const recordingTime = document.querySelector(".recording-time");
const audioUsageElement = document.getElementById("audioUsage");
const statusBar = document.getElementById("statusBar");

// ==================== PWA FUNCTIONALITY ====================

// Register Service Worker
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
        
        // Check for updates every hour
        setInterval(() => {
          registration.update();
        }, 60 * 60 * 1000);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  }
}

// Handle PWA installation prompt
function setupPWAInstallPrompt() {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button (you can add this to your UI)
    showInstallButton();
  });

  window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
    deferredPrompt = null;
    hideInstallButton();
  });
}

function showInstallButton() {
  // Create install button if it doesn't exist
  if (!document.getElementById('installButton')) {
    const installBtn = document.createElement('button');
    installBtn.id = 'installButton';
    installBtn.textContent = '📱 Install App';
    installBtn.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      padding: 10px 15px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 20px;
      cursor: pointer;
      z-index: 1000;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    installBtn.onclick = installPWA;
    document.body.appendChild(installBtn);
  }
}

function hideInstallButton() {
  const installBtn = document.getElementById('installButton');
  if (installBtn) {
    installBtn.remove();
  }
}

async function installPWA() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }
    
    deferredPrompt = null;
    hideInstallButton();
  }
}

// Check if app is running as PWA
function isRunningAsPWA() {
  return window.matchMedia('(display-mode: standalone)').matches || 
         window.navigator.standalone ||
         document.referrer.includes('android-app://');
}

// ==================== AUDIO FUNCTIONALITY ====================

// Initialize visualizer bars
function initVisualizer() {
  visualizerBars.innerHTML = '';
  for (let i = 0; i < 20; i++) {
    const bar = document.createElement('div');
    bar.className = 'visualizer-bar';
    bar.style.height = '2px';
    visualizerBars.appendChild(bar);
  }
}

// Visualizer update
function updateVisualizer(analyser, dataArray) {
  if (!analyser || !dataArray) return;
  
  analyser.getByteFrequencyData(dataArray);
  const bars = visualizerBars.children;
  const step = Math.floor(dataArray.length / bars.length);
  
  for (let i = 0; i < bars.length; i++) {
    const value = dataArray[i * step] / 255;
    const height = Math.max(2, value * 40);
    bars[i].style.height = `${height}px`;
  }
  
  requestAnimationFrame(() => updateVisualizer(analyser, dataArray));
}

// Recording timer
function updateRecordingTimer() {
  if (!recordingStartTime) return;
  const elapsed = Date.now() - recordingStartTime;
  const seconds = Math.floor(elapsed / 1000);
  const minutes = Math.floor(seconds / 60);
  recordingTime.textContent = `${minutes.toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
}

// Start recording
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        sampleSize: 16
      } 
    });

    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus',
      audioBitsPerSecond: 128000
    });
    
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      source.disconnect();
      audioContext.close();
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      await processRecordedAudio(audioBlob);
    };

    mediaRecorder.start(100);
    updateVisualizer(analyser, dataArray);
    recordingStartTime = Date.now();
    recordingTimer = setInterval(updateRecordingTimer, 1000);

    visualizer.classList.remove('hidden');
    micBtn.classList.add('recording');
    input.disabled = true;
  } catch (error) {
    console.error('Recording error:', error);
    showStatus('Permissão do microfone negada.', 'error');
  }
}

// Stop recording
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    clearInterval(recordingTimer);
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    visualizer.classList.add('hidden');
    micBtn.classList.remove('recording');
    input.disabled = false;
    recordingStartTime = null;
    initVisualizer();
  }
}

// Process audio
async function processRecordedAudio(audioBlob) {
  showStatus('Processando áudio...', 'warning');

  if (audioUsage >= audioLimit) {
    showStatus('Limite de áudio diário atingido.', 'error');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('user', USER);

    const response = await fetch(`${API}/audio/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.usage_left !== undefined) {
      audioUsage = audioLimit - result.usage_left;
      updateUsageDisplay();
    }

    addMessage(USER, '🎤 Áudio enviado', null, result.audio_url);
    showTypingIndicator();

    const aiResponse = await fetch(`${API}/send_message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user: USER, text: 'Audio message transcribed' })
    });

    if (!aiResponse.ok) {
      throw new Error(`HTTP error! status: ${aiResponse.status}`);
    }

    const aiData = await aiResponse.json();
    hideTypingIndicator();

    addMessage(AGENT_NAME, aiData.response, null, result.audio_response_url);
    showStatus('Áudio processado com sucesso.', 'success');

  } catch (error) {
    console.error('Audio processing error:', error);
    showStatus('Erro ao processar áudio.', 'error');
    hideTypingIndicator();
  }
}

// ==================== CHAT FUNCTIONALITY ====================

// Add message to chat
function addMessage(senderName, text, correction = null, audioUrl = null) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('chat-msg');
  messageDiv.classList.add(senderName === AGENT_NAME ? 'chat-agent' : 'chat-user');

  let audioHTML = '';
  if (audioUrl) {
    audioHTML = `
      <div class="audio-message">
        <audio class="audio-player" src="${audioUrl}"></audio>
        <button class="play-btn" onclick="playAudio(this)">▶</button>
      </div>`;
  }

  let correctionHTML = '';
  if (correction) {
    correctionHTML = `
      <div class="correction">
        <strong>✏️ Correção:</strong> ${correction}
      </div>`;
  }

  messageDiv.innerHTML = `
    <strong>${senderName}:</strong> ${text}
    ${correctionHTML}
    ${audioHTML}
  `;
  
  chat.appendChild(messageDiv);
  chat.scrollTop = chat.scrollHeight;
  
  // Save to local storage for offline access
  saveMessageToStorage(senderName, text, correction, audioUrl);
}

// Save message to local storage
function saveMessageToStorage(sender, text, correction, audioUrl) {
  const messages = JSON.parse(localStorage.getItem('chatMessages') || '[]');
  messages.push({
    sender,
    text,
    correction,
    audioUrl,
    timestamp: new Date().toISOString()
  });
  
  // Keep only last 100 messages
  if (messages.length > 100) {
    messages.shift();
  }
  
  localStorage.setItem('chatMessages', JSON.stringify(messages));
}

// Load messages from local storage
function loadMessagesFromStorage() {
  const messages = JSON.parse(localStorage.getItem('chatMessages') || '[]');
  messages.forEach(msg => {
    addMessage(msg.sender, msg.text, msg.correction, msg.audioUrl);
  });
}

// Typing indicator
function showTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.classList.add('chat-msg', 'chat-agent');
  typingDiv.id = 'typingIndicator';
  typingDiv.innerHTML = `
    <strong>${AGENT_NAME}:</strong>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  
  chat.appendChild(typingDiv);
  chat.scrollTop = chat.scrollHeight;
}

function hideTypingIndicator() {
  const typing = document.getElementById('typingIndicator');
  if (typing) typing.remove();
}

// Send text message
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  
  input.value = '';
  addMessage(USER, text);
  showTypingIndicator();

  try {
    const response = await fetch(`${API}/send_message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user: USER, text })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    hideTypingIndicator();
    
    addMessage(AGENT_NAME, data.response, null, data.audio_url);
  } catch (err) {
    console.error('Send message error:', err);
    hideTypingIndicator();
    showStatus('Erro ao enviar mensagem.', 'error');
    addMessage(AGENT_NAME, '(Erro de conexão. Verifique sua internet.)');
  }
}

// ==================== UTILITY FUNCTIONS ====================

function playAudio(btn) {
  const audio = btn.parentElement.querySelector('.audio-player');
  if (!audio) return;
  
  const playing = !audio.paused;
  if (playing) {
    audio.pause();
    btn.textContent = '▶';
    btn.classList.remove('playing');
  } else {
    audio.play()
      .then(() => {
        btn.textContent = '⏸';
        btn.classList.add('playing');
        
        audio.onended = () => {
          btn.textContent = '▶';
          btn.classList.remove('playing');
        };
      })
      .catch(error => {
        console.error('Audio play error:', error);
        showStatus('Erro ao reproduzir áudio.', 'error');
      });
  }
}

function showStatus(msg, type = 'info') {
  statusBar.textContent = msg;
  statusBar.className = '';
  
  if (type === 'error') {
    statusBar.classList.add('status-offline');
  } else if (type === 'warning') {
    statusBar.classList.add('status-warning');
  } else {
    statusBar.classList.add('status-online');
  }
  
  setTimeout(() => {
    statusBar.textContent = '';
    statusBar.className = '';
  }, 5000);
}

function updateUsageDisplay() {
  const usage = `Uso de áudio: ${audioUsage}/${audioLimit} hoje`;
  audioUsageElement.textContent = usage;
  audioUsageElement.classList.toggle('usage-warning', audioUsage >= audioLimit);
}

// ==================== LESSONS FUNCTIONALITY ====================

async function loadLessons() {
  const list = document.getElementById('lessonsList');
  list.innerHTML = '<li>Carregando...</li>';

  try {
    const response = await fetch(`${API}/lessons/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const lessons = await response.json();
    list.innerHTML = '';
    
    if (lessons.length === 0) {
      list.innerHTML = '<li>Nenhuma lição disponível.</li>';
      return;
    }

    lessons.forEach((lesson) => {
      const li = document.createElement('li');
      li.innerHTML = `
        ${lesson.phrase} [${lesson.translation || ''}] 
        <button onclick="playLessonAudio(${lesson.id})">▶</button>
      `;
      list.appendChild(li);
    });
  } catch (err) {
    console.error('Load lessons error:', err);
    list.innerHTML = '<li>Erro ao carregar lições.</li>';
  }
}

async function playLessonAudio(id) {
  try {
    const response = await fetch(`${API}/speak/${id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const audio = new Audio(API + data.audio_url);
    
    audio.play().catch(error => {
      console.error('Lesson audio play error:', error);
      showStatus('Erro ao reproduzir áudio da lição.', 'error');
    });
  } catch (err) {
    console.error('Play lesson error:', err);
    showStatus('Erro ao carregar áudio da lição.', 'error');
  }
}

// ==================== OFFLINE FUNCTIONALITY ====================

function checkOnlineStatus() {
  if (!navigator.onLine) {
    showStatus('Você está offline. Algumas funcionalidades podem não estar disponíveis.', 'warning');
    loadMessagesFromStorage();
  } else {
    showStatus('Conectado ao English Agent', 'success');
  }
}

// ==================== INITIALIZATION ====================

function initializeApp() {
  // Initialize PWA functionality
  registerServiceWorker();
  setupPWAInstallPrompt();
  
  // Initialize UI components
  initVisualizer();
  updateUsageDisplay();
  loadLessons();
  loadMessagesFromStorage();
  checkOnlineStatus();
  
  // Setup event listeners
  setupEventListeners();
  
  // Add welcome message if no messages exist
  if (JSON.parse(localStorage.getItem('chatMessages') || '[]').length === 0) {
    addMessage(AGENT_NAME, 'Olá! Sou o Professor Liam. Como posso ajudar você a aprender inglês hoje? 😊');
  }
}

function setupEventListeners() {
  sendBtn.addEventListener('click', sendMessage);
  
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  
  micBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      stopRecording();
    } else {
      startRecording();
    }
  });
  
  stopRecordBtn.addEventListener('click', stopRecording);
  
  // Auto-resize textarea
  input.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  });
  
  // Online/offline detection
  window.addEventListener('online', checkOnlineStatus);
  window.addEventListener('offline', checkOnlineStatus);
}

// Start the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);

// Make functions available globally for HTML onclick attributes
window.playAudio = playAudio;
window.playLessonAudio = playLessonAudio;