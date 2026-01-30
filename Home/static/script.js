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

        if (data.urgency_level !== undefined) {
            updateUrgency(data.urgency_level, data.urgency_label);
        }


    } catch (error) {
        appendMessage("⚠️ Server error. Please try again.", "bot");
        console.error(error);
    }
}

function updateUrgency(level, label) {
    if (level === 3) {
    alert("⚠️ This may be a medical emergency. Please seek immediate medical care.");
    }

    const fill = document.getElementById("urgency-fill");
    const text = document.getElementById("urgency-label");

    const map = {
        0: { h: "25%", c: "green" },
        1: { h: "50%", c: "orange" },
        2: { h: "75%", c: "red" },
        3: { h: "100%", c: "darkred" }
    };

    fill.style.height = map[level].h;
    fill.style.background = map[level].c;
    text.innerText = label;
}
