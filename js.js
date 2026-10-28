const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.innerText = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to bottom
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // 1. Show user message in UI
    appendMessage(query, 'user');
    userInput.value = '';

    // 2. Add a temporary loading message for the AI
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot');
    loadingDiv.innerText = "Thinking...";
    chatMessages.appendChild(loadingDiv);

    try {
        // Use the current host so this works through Codespaces port forwarding.
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: query })
        });        
        
        const data = await response.json();
        
        // Remove loading text and show actual answer
        loadingDiv.innerText = data.answer;
    } catch (error) {
        loadingDiv.innerText = "Error: Could not connect to local AI server.";
        console.error(error);
    }
}