const fs = require('fs');
let content = fs.readFileSync('D:/voice-check/voice-check/theme.js', 'utf8');

const regex = /function getBotResponse\(q\) \{[\s\S]*?\n    \}/;

const newLogic = `
    async function getBotResponse(q) {
        try {
            const baseUrl = window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:8000';
            const cleanUrl = baseUrl.replace(/\\/$/, '');
            const res = await fetch(cleanUrl + '/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                body: JSON.stringify({ message: q })
            });
            const data = await res.json();
            return data.reply || "Error: Empty response.";
        } catch (e) {
            console.error('Chat error:', e);
            return "I am having trouble connecting to the backend right now!";
        }
    }
`;

content = content.replace(regex, newLogic.trim());

// Update handleSend to await the response
const handleRegex = /function handleSend\(\) \{[\s\S]*?setTimeout\(\(\) => \{[\s\S]*?addMessage\(getBotResponse\(text\), 'bot'\);[\s\S]*?\}, 500 \+ Math\.random\(\) \* 500\);[\s\S]*?\}/;

const newHandleSend = `
    async function handleSend() {
        const text = input.value.trim();
        if (!text) return;
        
        addMessage(text, 'user');
        input.value = '';
        
        // Add loading indicator
        const loadingId = 'msg-' + Date.now();
        const msg = document.createElement('div');
        msg.className = 'ag-msg bot';
        msg.id = loadingId;
        msg.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Thinking...';
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;

        const reply = await getBotResponse(text);
        
        // Replace loading with real response
        const loadEl = document.getElementById(loadingId);
        if (loadEl) loadEl.innerHTML = reply.replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>').replace(/\\n/g, '<br>');
        messages.scrollTop = messages.scrollHeight;
    }
`;

content = content.replace(handleRegex, newHandleSend.trim());

fs.writeFileSync('D:/voice-check/voice-check/theme.js', content, 'utf8');
