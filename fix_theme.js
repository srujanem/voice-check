const fs = require('fs');
let content = fs.readFileSync('D:/voice-check/voice-check/theme.js', 'utf8');

// Fix the presence ping syntax error that was corrupted
content = content.replace(/await fetch\(\\\/api\/presence/g, "await fetch(cleanUrl + '/api/presence'");
content = content.replace(/const res = await fetch\(\\\/api\/presence\);/g, "const res = await fetch(cleanUrl + '/api/presence');");

// Slice off the corrupted Chatbot code
const chatbotIndex = content.indexOf('// ===== AUTHGUARD ASSISTANT CHATBOT =====');
if (chatbotIndex !== -1) {
    content = content.substring(0, chatbotIndex);
}

// Add the fresh, uncorrupted chatbot code
const chatbotCode = `
// ===== AUTHGUARD ASSISTANT CHATBOT =====
(function() {
    if (document.getElementById('ag-chat-btn')) return;

    const style = document.createElement('style');
    style.textContent = \`
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
    \`;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.innerHTML = \`
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
    \`;
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

    function getBotResponse(q) {
        q = q.toLowerCase();
        if (q.includes('price') || q.includes('pricing') || q.includes('cost') || q.includes('money')) {
            return "We have 3 tiers: <br><b>Free</b> (Basic scans up to 5MB)<br><b>Pro</b> ($19/mo - 50MB uploads & Batch Processing)<br><b>Enterprise</b> ($99/mo - Full API access).";
        }
        if (q.includes('api') || q.includes('developer')) {
            return "Our Enterprise plan ($99/mo) gives you full access to the AuthGuard API. You can programmatically scan text, images, video, and audio directly from your own apps.";
        }
        if (q.includes('accuracy') || q.includes('accurate') || q.includes('trust')) {
            return "AuthGuard is industry-leading! Our average accuracy is <b>96.8%</b>. Voice Detection hits 96.5%, Image Detection hits 96.8%, and Text Detection is at 98.1%.";
        }
        if (q.includes('watermark') || q.includes('protect')) {
            return "We offer an Authentic Watermark Creator! It embeds an invisible cryptographic signature into your images to permanently prove they are human-made.";
        }
        if (q.includes('voice') || q.includes('audio') || q.includes('speech')) {
            return "Our Voice Detector analyzes spectrograms and audio frequencies to instantly flag AI voice clones from tools like ElevenLabs or PlayHT with 96.5% accuracy.";
        }
        if (q.includes('image') || q.includes('photo') || q.includes('picture')) {
            return "Our Image Detector uses an advanced Convolutional Neural Network (EfficientNetB0) to spot hidden artifacts left by MidJourney, DALL-E, and Stable Diffusion. We just retrained it and hit 96.8% accuracy on unseen data!";
        }
        if (q.includes('text') || q.includes('chatgpt') || q.includes('written') || q.includes('writing')) {
            return "Our Text Detector uses a RoBERTa ensemble model combined with perplexity heuristics to detect ChatGPT, Claude, and Gemini text with 98.1% accuracy.";
        }
        if (q.includes('video') || q.includes('deepfake')) {
            return "The Video Content Scanner extracts frames and analyzes both the visual artifacts and the audio track to detect deepfakes with 94.8% accuracy.";
        }
        if (q.includes('who are you') || q.includes('what is authguard') || q.includes('what is voicecheck') || q.includes('about')) {
            return "I am the AuthGuard AI! AuthGuard (also known as VoiceCheck) is the ultimate multi-modal AI detection suite. We detect AI-generated text, images, voices, and videos.";
        }
        if (q.includes('contact') || q.includes('support') || q.includes('feedback')) {
            return "You can use the 'Rate Your Experience' form at the bottom of the homepage to send an email directly to our support team!";
        }
        if (q.includes('hi ') || q === 'hi' || q.includes('hello') || q.includes('hey')) {
            return "Hello! What would you like to know about AuthGuard's AI detection capabilities?";
        }
        return "I'm specifically trained to answer questions about AuthGuard's detection tools, pricing, API, and accuracy metrics. Could you rephrase your question regarding our platform?";
    }

    function handleSend() {
        const text = input.value.trim();
        if (!text) return;
        
        addMessage(text, 'user');
        input.value = '';
        
        setTimeout(() => {
            addMessage(getBotResponse(text), 'bot');
        }, 500 + Math.random() * 500);
    }

    sendBtn.addEventListener('click', handleSend);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleSend(); });
})();
`;

fs.writeFileSync('D:/voice-check/voice-check/theme.js', content + '\n' + chatbotCode, 'utf8');
