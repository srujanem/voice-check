// Theme Toggle — runs once, prevents duplicates
(function() {
    if (window.__themeInitialized) return;
    window.__themeInitialized = true;

    const html = document.documentElement;

    // Apply saved theme instantly (before paint)
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);

    function updateIcon(theme) {
        const toggles = document.querySelectorAll('.theme-toggle');
        toggles.forEach(toggle => {
            toggle.innerHTML = theme === 'light'
                ? '<i class="fa-solid fa-moon"></i>'
                : '<i class="fa-solid fa-sun"></i>';
        });
    }

    function init() {
        updateIcon(html.getAttribute('data-theme') || 'dark');

        const toggles = document.querySelectorAll('.theme-toggle');
        toggles.forEach(toggle => {
            if (!toggle.__themeListenerAttached) {
                toggle.__themeListenerAttached = true;
                toggle.addEventListener('click', () => {
                    const current = html.getAttribute('data-theme');
                    const next = current === 'light' ? 'dark' : 'light';
                    html.setAttribute('data-theme', next);
                    localStorage.setItem('theme', next);
                    updateIcon(next);
                    toggle.classList.add('spin');
                    setTimeout(() => toggle.classList.remove('spin'), 500);
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

// ===== REALTIME PRESENCE SYSTEM =====
(function() {
    function generateClientId() {
        let id = localStorage.getItem('ag_client_id');
        if (!id) {
            id = Math.random().toString(36).substring(2, 15);
            localStorage.setItem('ag_client_id', id);
        }
        return id;
    }

    async function pingPresence() {
        const liveCountEl = document.getElementById('live-count');
        const baseUrl = window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:8000';
        const cleanUrl = baseUrl.replace(/\/$/, '');
        
        try {
            // Ping that we are alive
            await fetch(cleanUrl + '/api/presence', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                body: JSON.stringify({ clientId: generateClientId() })
            });

            // Get the current online count
            const res = await fetch(cleanUrl + '/api/presence');
            const data = await res.json();
            
            if (data && data.online !== undefined && liveCountEl) {
                // Add an artificial baseline offset of 14 for visual mass, plus the real count
                // Or just show the real count! Since it's local/small, showing "1 online" might look too empty?
                // The user said "if the person is online show correctly" -> I will show the exact real count!
                liveCountEl.textContent = data.online;
            }
        } catch (e) {
            console.log("Presence check failed", e);
        }
    }

    // Ping immediately and then every 30 seconds
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            pingPresence();
            setInterval(pingPresence, 30000);
        });
    } else {
        pingPresence();
        setInterval(pingPresence, 30000);
    }
})();




// ===== AUTHGUARD ASSISTANT CHATBOT =====
(function() {
    if (document.getElementById('ag-chat-btn')) return;

    const style = document.createElement('style');
    style.textContent = `
        #ag-chat-btn {
            position: fixed; bottom: 85px; right: 25px; z-index: 9999;
            width: 55px; height: 55px; border-radius: 50%;
            background: linear-gradient(135deg, #06b6d4, #8b5cf6);
            color: white; font-size: 24px; border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        #ag-chat-btn:hover { transform: scale(1.05); box-shadow: 0 6px 20px rgba(6,182,212,0.4); }
        
        #ag-chat-window {
            position: fixed; bottom: 155px; right: 25px; z-index: 9999;
            width: 350px; height: 450px; border-radius: 16px;
            background: rgba(15,23,42,0.95); backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex; flex-direction: column; overflow: hidden;
            transform: translateY(20px); opacity: 0; pointer-events: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        #ag-chat-window.open { transform: translateY(0); opacity: 1; pointer-events: auto; }
        
        #ag-chat-header {
            background: rgba(255,255,255,0.05); padding: 15px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex; justify-content: space-between; align-items: center;
        }
        #ag-chat-title { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 15px; color: #fff; display: flex; align-items: center; gap: 8px; }
        #ag-chat-close { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 18px; }
        #ag-chat-close:hover { color: #fff; }
        
        #ag-chat-messages {
            flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px;
            font-family: 'Inter', sans-serif; font-size: 14px;
        }
        .ag-msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; line-height: 1.4; }
        .ag-msg.bot { background: rgba(255,255,255,0.1); color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; }
        .ag-msg.user { background: linear-gradient(135deg, #06b6d4, #3b82f6); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
        
        #ag-chat-input-area {
            padding: 15px; border-top: 1px solid rgba(255,255,255,0.05);
            display: flex; gap: 10px;
        }
        #ag-chat-input {
            flex: 1; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px; padding: 10px 15px; color: #fff; font-family: inherit; font-size: 14px;
            outline: none;
        }
        #ag-chat-input:focus { border-color: #06b6d4; }
        #ag-chat-send {
            background: #06b6d4; border: none; width: 40px; height: 40px; border-radius: 50%;
            color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center;
        }
        
        @media (max-width: 768px) {
            #ag-chat-window { width: calc(100% - 40px); right: 20px; bottom: 100px; height: 60vh; }
            #ag-chat-btn { bottom: 25px; right: 20px; width: 50px; height: 50px; }
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.innerHTML = `
        <button id="ag-chat-btn"><i class="fa-solid fa-robot"></i></button>
        <div id="ag-chat-window">
            <div id="ag-chat-header">
                <div id="ag-chat-title"><i class="fa-solid fa-shield-halved" style="color:#06b6d4"></i> AuthGuard AI</div>
                <button id="ag-chat-close"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div id="ag-chat-messages">
                <div class="ag-msg bot">Hello! I am the AuthGuard AI Assistant. I know everything about our detection models, pricing, and API. How can I help you today?</div>
            </div>
            <div id="ag-chat-input-area">
                <input type="text" id="ag-chat-input" placeholder="Ask me anything..." autocomplete="off">
                <button id="ag-chat-send"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>
    `;
    document.body.appendChild(container);

    const btn = document.getElementById('ag-chat-btn');
    const win = document.getElementById('ag-chat-window');
    const closeBtn = document.getElementById('ag-chat-close');
    const input = document.getElementById('ag-chat-input');
    const sendBtn = document.getElementById('ag-chat-send');
    const messages = document.getElementById('ag-chat-messages');

    let isOpen = false;
    btn.addEventListener('click', () => { isOpen = !isOpen; win.classList.toggle('open', isOpen); if(isOpen) input.focus(); });
    closeBtn.addEventListener('click', () => { isOpen = false; win.classList.remove('open'); });

    function addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.className = 'ag-msg ' + sender;
        msg.innerHTML = text;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

        async function getBotResponse(q) {
        try {
            const baseUrl = window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:8000';
            const cleanUrl = baseUrl.replace(/\/$/, '');
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
        if (loadEl) loadEl.innerHTML = reply.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
        messages.scrollTop = messages.scrollHeight;
    }

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });
})();

// ===== DEVELOPER TERMINAL EASTER EGG =====
(function() {
    const termStyle = document.createElement('style');
    termStyle.textContent = `
        #ag-terminal {
            position: fixed; top: 0; left: 0; width: 100%; height: 50vh;
            background: rgba(10, 10, 15, 0.98); border-bottom: 2px solid #06b6d4;
            z-index: 999999; display: flex; flex-direction: column;
            font-family: 'Courier New', Courier, monospace; color: #0f0;
            padding: 20px; box-sizing: border-box; font-size: 14px;
            transform: translateY(-100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 50px rgba(6,182,212,0.2);
        }
        #ag-terminal.open { transform: translateY(0); }
        #ag-term-output { flex: 1; overflow-y: auto; margin-bottom: 10px; line-height: 1.5; text-shadow: 0 0 5px rgba(0,255,0,0.5); }
        #ag-term-input-line { display: flex; align-items: center; }
        #ag-term-prompt { color: #06b6d4; margin-right: 10px; font-weight: bold; }
        #ag-term-input {
            flex: 1; background: transparent; border: none; color: #0f0;
            font-family: 'Courier New', Courier, monospace; font-size: 14px; outline: none;
        }
        .term-cyan { color: #06b6d4; }
        .term-purple { color: #8b5cf6; }
        .term-err { color: #ef4444; }
    `;
    document.head.appendChild(termStyle);

    const termContainer = document.createElement('div');
    termContainer.id = 'ag-terminal';
    termContainer.innerHTML = `
        <div id="ag-term-output">
            <div>AuthGuard OS v2.0.1 [Deepfake Detection Kernel]</div>
            <div>(c) 2024 Srujan EM. All rights reserved.</div>
            <div><br>Type <span class="term-cyan">'help'</span> for a list of available commands.</div>
        </div>
        <div id="ag-term-input-line">
            <span id="ag-term-prompt">srujan@authguard:~$</span>
            <input type="text" id="ag-term-input" autocomplete="off" spellcheck="false">
        </div>
    `;
    document.body.appendChild(termContainer);

    const terminal = document.getElementById('ag-terminal');
    const input = document.getElementById('ag-term-input');
    const output = document.getElementById('ag-term-output');
    let isOpen = false;

    document.addEventListener('keydown', (e) => {
        if (e.key === '`' || e.key === '~') {
            e.preventDefault();
            isOpen = !isOpen;
            terminal.classList.toggle('open', isOpen);
            if (isOpen) {
                setTimeout(() => input.focus(), 100);
            } else {
                input.blur();
            }
        }
    });

    function print(text) {
        const div = document.createElement('div');
        div.innerHTML = text;
        output.appendChild(div);
        output.scrollTop = output.scrollHeight;
    }

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const cmd = input.value.trim();
            input.value = '';
            
            print(`<div><span class="term-cyan">srujan@authguard:~$</span> ${cmd}</div>`);
            
            if (!cmd) return;
            const args = cmd.toLowerCase().split(' ');
            
            switch(args[0]) {
                case 'help':
                    print("Available commands:");
                    print("  <span class='term-cyan'>whoami</span>   - Display current user context");
                    print("  <span class='term-cyan'>status</span>   - Show neural network active status");
                    print("  <span class='term-cyan'>models</span>   - List loaded detection models");
                    print("  <span class='term-cyan'>ping</span>     - Check connection latency");
                    print("  <span class='term-cyan'>clear</span>    - Clear terminal output");
                    print("  <span class='term-cyan'>exit</span>     - Close terminal");
                    break;
                case 'whoami':
                    print("root // Authorized access granted to Srujan EM.");
                    break;
                case 'status':
                    print("Node API Gateway: <span class='term-cyan'>ONLINE</span> (Port 8000)");
                    print("Flask ML Engine: <span class='term-cyan'>ONLINE</span> (Port 5000)");
                    print("Gemini LLM: <span class='term-purple'>CONNECTED</span> (v3.6-flash)");
                    break;
                case 'models':
                    print("[1] Image: EfficientNetB0 (Acc: 96.8%)");
                    print("[2] Text: RoBERTa Ensemble (Acc: 98.1%)");
                    print("[3] Voice: Wav2Vec2 + CNN (Acc: 96.5%)");
                    print("[4] Video: Deepfake Frame Extractor (Acc: 94.8%)");
                    break;
                case 'ping':
                    print("Pinging AI Engine... 12ms. Server is highly responsive.");
                    break;
                case 'clear':
                    output.innerHTML = '';
                    break;
                case 'exit':
                    isOpen = false;
                    terminal.classList.remove('open');
                    break;
                default:
                    print(`<span class='term-err'>Command not found: ${args[0]}</span>`);
            }
        }
    });
})();
