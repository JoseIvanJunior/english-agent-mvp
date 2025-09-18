const API = "http://localhost:8000"; // ajuste se backend rodar em outro host/porta
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
    const data = await res.json();
    addMessage("Agent", data.response);
  } catch (err) {
    addMessage("Agent", "(error) " + err.message);
  }
}

// Lessons
document.getElementById("addLesson").addEventListener("click", async () => {
  const phrase = document.getElementById("lessonPhrase").value.trim();
  const translation = document.getElementById("lessonTranslation").value.trim();
  if (!phrase) return alert("Add a phrase");
  const res = await fetch(`${API}/lessons/`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({phrase, translation})
  });
  document.getElementById("lessonPhrase").value = "";
  document.getElementById("lessonTranslation").value = "";
  loadLessons();
});

async function loadLessons(){
  const list = document.getElementById("lessonsList");
  list.innerHTML = "";
  const res = await fetch(`${API}/lessons/`);
  const lessons = await res.json();
  lessons.forEach(l => {
    const li = document.createElement("li");
    li.innerHTML = `${l.id}: ${l.phrase} [${l.translation || ""}] <button data-id="${l.id}">Play</button>`;
    list.appendChild(li);
  });
  // bind play buttons
  document.querySelectorAll("#lessonsList button").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      const r = await fetch(`${API}/speak/${id}`);
      const info = await r.json();
      const audio = new Audio(API + info.audio_url);
      audio.play();
    });
  });
}

// initial load
loadLessons();
