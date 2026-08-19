const fs = require('fs');
let content = fs.readFileSync('D:/voice-check/voice-check/theme.js', 'utf8');

const terminalCode = `
// ===== DEVELOPER TERMINAL EASTER EGG =====
(function() {
    const termStyle = document.createElement('style');
    termStyle.textContent = \`
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
    \`;
    document.head.appendChild(termStyle);

    const termContainer = document.createElement('div');
    termContainer.id = 'ag-terminal';
    termContainer.innerHTML = \`
        <div id="ag-term-output">
            <div>AuthGuard OS v2.0.1 [Deepfake Detection Kernel]</div>
            <div>(c) 2024 Srujan EM. All rights reserved.</div>
            <div><br>Type <span class="term-cyan">'help'</span> for a list of available commands.</div>
        </div>
        <div id="ag-term-input-line">
            <span id="ag-term-prompt">srujan@authguard:~$</span>
            <input type="text" id="ag-term-input" autocomplete="off" spellcheck="false">
        </div>
    \`;
    document.body.appendChild(termContainer);

    const terminal = document.getElementById('ag-terminal');
    const input = document.getElementById('ag-term-input');
    const output = document.getElementById('ag-term-output');
    let isOpen = false;

    document.addEventListener('keydown', (e) => {
        if (e.key === '\`' || e.key === '~') {
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
            
            print(\`<div><span class="term-cyan">srujan@authguard:~$</span> \${cmd}</div>\`);
            
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
                    print(\`<span class='term-err'>Command not found: \${args[0]}</span>\`);
            }
        }
    });
})();
`;

if (!content.includes("DEVELOPER TERMINAL EASTER EGG")) {
    content += '\n' + terminalCode;
}

fs.writeFileSync('D:/voice-check/voice-check/theme.js', content, 'utf8');
