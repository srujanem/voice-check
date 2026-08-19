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

        function getBotResponse(q) {
        q = q.toLowerCase();
        
        if (q === 'hi' || q === 'hello' || q === 'hey' || q.includes('hi ') || q.includes('hello ') || q.includes('hey ')) {
            return "Hello! ?? I'm the AuthGuard AI Assistant. I can help you with questions about our detection models, pricing, API, batch analysis, URL scanning, or how everything works under the hood. What would you like to know?";
        }
        
        if (q.includes('who made') || q.includes('who created') || q.includes('founder') || q.includes('ceo') || q.includes('srujan') || q.includes('developer')) {
            return "AuthGuard (VoiceCheck) was created by **Srujan**. He built this platform to combat the rise of deepfakes and AI-generated misinformation!";
        }
        
        if (q.includes('price') || q.includes('pricing') || q.includes('cost') || q.includes('money') || q.includes('pay') || q.includes('subscription') || q.includes('free') || q.includes('plans')) {
            return "We offer 3 straightforward tiers:<br><br>?? <b>Free Plan:</b> Basic scans up to 5MB file sizes.<br>?? <b>Pro Plan ($19/mo):</b> Increased 50MB limits, Batch Analysis tools, and priority processing.<br>?? <b>Enterprise Plan ($99/mo):</b> Full programmatic API access for your own applications.";
        }
        
        if (q.includes('api') || q.includes('code') || q.includes('programmatic') || q.includes('integrate') || q.includes('endpoint')) {
            return "Developers love AuthGuard! By subscribing to our Enterprise plan ($99/mo), you gain full access to the AuthGuard REST API. You can securely send text, images, video, and audio to our endpoints and receive detailed AI probability scores in JSON format.";
        }
        
        if (q.includes('accuracy') || q.includes('accurate') || q.includes('trust') || q.includes('reliable') || q.includes('performance') || q.includes('good is')) {
            return "AuthGuard is incredibly accurate, averaging <b>96.8%</b> overall across all modalities.<br>??? Voice: 96.5%<br>??? Image: 96.8% (Just retrained!)<br>?? Text: 98.1%<br>?? Video: 94.8%";
        }
        
        if (q.includes('watermark') || q.includes('protect') || q.includes('signature') || q.includes('hide') || q.includes('invisible')) {
            return "Our <b>Authentic Watermark Creator</b> is a unique tool that embeds an invisible, tamper-proof cryptographic signature directly into your image's pixels. It proves permanently that the image was human-made and authenticated by AuthGuard.";
        }
        
        if (q.includes('voice') || q.includes('audio') || q.includes('speech') || q.includes('elevenlabs') || q.includes('clone') || q.includes('mp3') || q.includes('wav')) {
            return "The <b>Voice Detector</b> converts your audio into visual spectrograms and analyzes micro-frequencies. It easily flags AI voice clones from tools like ElevenLabs, PlayHT, and Murf.ai with 96.5% accuracy.";
        }
        
        if (q.includes('image') || q.includes('photo') || q.includes('picture') || q.includes('midjourney') || q.includes('dalle') || q.includes('dall-e') || q.includes('stable diffusion') || q.includes('jpeg') || q.includes('png')) {
            return "Our <b>Image Detector</b> analyzes pixel-level inconsistencies and compression artifacts using a highly trained EfficientNetB0 neural network. It catches MidJourney, DALL-E 3, and Stable Diffusion fakes with 96.8% accuracy. We just fed it 31 brand new edge cases today!";
        }
        
        if (q.includes('text') || q.includes('chatgpt') || q.includes('written') || q.includes('writing') || q.includes('essay') || q.includes('claude') || q.includes('gemini') || q.includes('gpt')) {
            return "Our <b>Text Detector</b> analyzes linguistic patterns, perplexity, and burstiness using a RoBERTa ensemble model. It excels at catching ChatGPT, Claude, and Gemini generated essays and articles with a stunning 98.1% accuracy rate.";
        }
        
        if (q.includes('video') || q.includes('deepfake') || q.includes('sora') || q.includes('runway') || q.includes('mp4') || q.includes('movie')) {
            return "The <b>Video Content Scanner</b> works by extracting frames from your video clip and analyzing both the visual anomalies (like weird blinking or blurring) and the audio track. It detects Deepfakes with 94.8% accuracy.";
        }
        
        if (q.includes('url') || q.includes('website') || q.includes('link') || q.includes('article') || q.includes('scan web')) {
            return "Don't want to copy and paste? Use our <b>URL Scanner</b>! Just paste a link to any news article or blog post, and we will automatically extract the text and analyze it for AI generation.";
        }
        
        if (q.includes('batch') || q.includes('bulk') || q.includes('multiple') || q.includes('many files') || q.includes('folder')) {
            return "Got a lot of files? The <b>Batch Analysis</b> tool (available on the Pro Plan) lets you upload up to 50 files at once. We'll scan them all simultaneously and generate a downloadable PDF report.";
        }
        
        if (q.includes('how does it work') || q.includes('how to use') || q.includes('instructions') || q.includes('steps') || q.includes('guide')) {
            return "It's simple!<br>1?? <b>Select a Tool</b> (Text, Image, Voice, etc.)<br>2?? <b>Upload</b> your file or paste your text.<br>3?? <b>Analyze</b> - our neural networks process it in seconds.<br>4?? <b>Review</b> the detailed probability breakdown!";
        }
        
        if (q.includes('privacy') || q.includes('secure') || q.includes('safe') || q.includes('data') || q.includes('save my file') || q.includes('steal')) {
            return "Your privacy is our top priority. Files you upload are processed securely in memory by our backend and are <b>never</b> permanently stored or used to train our models without your explicit consent.";
        }
        
        if (q.includes('login') || q.includes('sign in') || q.includes('account') || q.includes('register') || q.includes('dashboard') || q.includes('sign up')) {
            return "You can log in or register by clicking the 'Sign In' button in the top right corner of the navigation bar. Creating an account lets you view your past scan history!";
        }
        
        if (q.includes('history') || q.includes('past scans') || q.includes('previous') || q.includes('old scans')) {
            return "If you are logged into your account, all of your previous scans are securely saved to your personal Dashboard. You can access your history anytime to review past results.";
        }
        
        if (q.includes('who are you') || q.includes('what is authguard') || q.includes('what is voicecheck') || q.includes('about') || q.includes('your name')) {
            return "I am the AuthGuard AI Assistant! AuthGuard (also known as VoiceCheck) is the ultimate multi-modal AI detection suite built to secure the internet against deceptive AI content.";
        }
        
        if (q.includes('contact') || q.includes('support') || q.includes('feedback') || q.includes('help') || q.includes('email') || q.includes('issue') || q.includes('bug')) {
            return "Need help? You can use the 'Rate Your Experience' / Feedback form at the bottom of the homepage to send a direct email to our support team (srujanem222@gmail.com). We usually reply within 24 hours!";
        }
        
        if (q.includes('thank') || q === 'thanks' || q.includes('awesome') || q.includes('great') || q.includes('cool') || q.includes('good bot')) {
            return "You're very welcome! Feel free to ask if you need anything else.";
        }
        
        if (q.includes('bye') || q.includes('goodbye') || q.includes('see ya') || q.includes('cya')) {
            return "Goodbye! Stay safe out there on the internet! ???";
        }
        
        return "I'm specifically trained on AuthGuard's ecosystem. I can tell you about our Creator (Srujan), our exact Accuracy metrics, Pricing plans, the API, Privacy policies, or how our specific tools (like URL scanning and Batch analysis) work. Could you rephrase your question?";
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
