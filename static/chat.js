const messages = document.getElementById("messages");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendButton");

let socket;

// WebSocket
function connect() {
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${protocol}://${location.host}/ws`);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addMessage("agent", data.content, true);
    };

    socket.onclose = () => {
        addMessage("agent", "_Соединение закрыто. Обновите страницу._", true);
    };
}

// Сообщения
function addMessage(role, text, markdown = false) {
    const msg = document.createElement("div");
    msg.className = `message ${role}`;

    const content = document.createElement("div");
    content.className = "message-content";

    content.innerHTML = markdown ? marked.parse(text) : text;

    msg.appendChild(content);
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
}

// Отправка
function sendMessage() {
    const text = input.value.trim();
    if (!text || !socket) return;

    addMessage("user", text);
    socket.send(text);

    input.value = "";
}

sendBtn.onclick = sendMessage;

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.addEventListener("DOMContentLoaded", connect);
