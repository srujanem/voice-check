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


// ===== PDF EVIDENCE GENERATOR =====
document.addEventListener('DOMContentLoaded', () => {
    const pdfBtn = document.getElementById('download-pdf-btn');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', async () => {
            const resultCard = document.getElementById('result-card');
            if (!resultCard || resultCard.classList.contains('hidden')) {
                alert("Please analyze a file first before downloading the report.");
                return;
            }
            
            // Show loading state on button
            const originalText = pdfBtn.innerHTML;
            pdfBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Generating...';
            pdfBtn.style.pointerEvents = 'none';

            try {
                // Dynamically load libraries
                if (!window.html2canvas) {
                    await new Promise(r => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'; s.onload = r; document.head.appendChild(s); });
                    await new Promise(r => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'; s.onload = r; document.head.appendChild(s); });
                }

                const canvas = await html2canvas(resultCard, {
                    scale: 2,
                    backgroundColor: '#0f172a',
                    logging: false
                });

                const imgData = canvas.toDataURL('image/png');
                const { jsPDF } = window.jspdf;
                
                // Create PDF (A4 size)
                const pdf = new jsPDF('p', 'mm', 'a4');
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
                
                // Add header
                pdf.setFillColor(6, 182, 212);
                pdf.rect(0, 0, pdfWidth, 20, 'F');
                pdf.setTextColor(255, 255, 255);
                pdf.setFontSize(16);
                pdf.setFont("helvetica", "bold");
                pdf.text("AuthGuard AI - Official Evidence Report", 15, 13);
                
                pdf.setTextColor(150, 150, 150);
                pdf.setFontSize(10);
                pdf.setFont("helvetica", "normal");
                pdf.text("Generated: " + new Date().toLocaleString(), 15, 30);
                pdf.text("Authorized by: Srujan EM (Founder)", 15, 36);
                
                // Add the result card image
                pdf.addImage(imgData, 'PNG', 15, 45, pdfWidth - 30, pdfHeight - ((30/pdfWidth) * pdfHeight));
                
                // Save
                pdf.save(`AuthGuard_Report_${Date.now()}.pdf`);
            } catch (err) {
                console.error("PDF Error:", err);
                alert("Failed to generate PDF. Please try again.");
            } finally {
                pdfBtn.innerHTML = originalText;
                pdfBtn.style.pointerEvents = 'auto';
            }
        });
    }
});
