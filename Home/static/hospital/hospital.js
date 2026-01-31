// Generate or reuse a session ID
let sessionId = localStorage.getItem("chat_session_id");
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("chat_session_id", sessionId);
}

const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");

// Send message on Enter key
userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

function appendMessage(text, sender) { 
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    userInput.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });

        const data = await response.json();

        appendMessage(data.answer, "bot");

    } catch (error) {
        appendMessage("⚠️ Server error. Please try again.", "bot");
        console.error(error);
    }
}
