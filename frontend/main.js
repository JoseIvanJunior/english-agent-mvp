const API = "https://english-agent-mvp-production.up.railway.app";
const USER = "junior";

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");

function addMessage(sender, text) {
  const p = document.createElement("div");
  p.classList.add("chat-msg");
  p.classList.add(sender === "You" ? "chat-user" : "chat-agent");
  p.innerHTML = `<b>${sender}:</b> ${text}`;
  chat.appendChild(p);
  chat.scrollTop = chat.scrollHeight;
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });

async function sendMessage(){
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMessage("You", text);

  try {
    const res = await fetch(`${API}/send_message`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({user: USER, text})
    });
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    addMessage("Agent", data.response);
  } catch (err) {
    console.error("Error sending message:", err);
    addMessage("Agent", "(error) Failed to fetch. Please check your connection.");
  }
}

// Lessons
document.getElementById("addLesson").addEventListener("click", async () => {
  const phrase = document.getElementById("lessonPhrase").value.trim();
  const translation = document.getElementById("lessonTranslation").value.trim();
  if (!phrase) return alert("Add a phrase");
  
  try {
    const res = await fetch(`${API}/lessons/`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({phrase, translation})
    });
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    document.getElementById("lessonPhrase").value = "";
    document.getElementById("lessonTranslation").value = "";
    loadLessons();
  } catch (err) {
    console.error("Error adding lesson:", err);
    alert("Error adding lesson. Please try again.");
  }
});

async function loadLessons(){
  const list = document.getElementById("lessonsList");
  list.innerHTML = "<li>Loading lessons...</li>";
  
  try {
    const res = await fetch(`${API}/lessons/`);
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const lessons = await res.json();
    list.innerHTML = "";
    
    if (lessons.length === 0) {
      list.innerHTML = "<li>No lessons yet. Add some phrases!</li>";
      return;
    }
    
    lessons.forEach(l => {
      const li = document.createElement("li");
      li.innerHTML = `${l.id}: ${l.phrase} [${l.translation || ""}] <button data-id="${l.id}">Play</button>`;
      list.appendChild(li);
    });
    
    // bind play buttons
    document.querySelectorAll("#lessonsList button").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        try {
          const r = await fetch(`${API}/speak/${id}`);
          
          if (!r.ok) {
            throw new Error(`HTTP error! status: ${r.status}`);
          }
          
          const info = await r.json();
          const audio = new Audio(API + info.audio_url);
          audio.play().catch(err => {
            console.error("Error playing audio:", err);
            alert("Error playing audio. Please try again.");
          });
        } catch (err) {
          console.error("Error fetching audio:", err);
          alert("Error playing audio. Please try again.");
        }
      });
    });
  } catch (err) {
    console.error("Error loading lessons:", err);
    list.innerHTML = "<li>Error loading lessons. Please refresh the page.</li>";
  }
}

// Função para verificar se a API está online
async function checkAPIStatus() {
  try {
    const res = await fetch(`${API}/lessons/`);
    return res.ok;
  } catch (err) {
    return false;
  }
}

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
  // Verificar se a API está online
  const isOnline = await checkAPIStatus();
  if (!isOnline) {
    const statusDiv = document.createElement('div');
    statusDiv.style.cssText = 'background: #ff4444; color: white; padding: 10px; text-align: center;';
    statusDiv.textContent = '⚠️ Connection error. Please check your internet connection.';
    document.body.insertBefore(statusDiv, document.body.firstChild);
  }
  
  loadLessons();
});