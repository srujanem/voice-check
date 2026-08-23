function initVoiceUI() {
    // --- DOM Elements ---
    const uploadArea    = document.getElementById('upload-area');
    const dropZone      = document.getElementById('drop-zone');
    const fileInput     = document.getElementById('file-input');

    const audioPreviewContainer = document.getElementById('audio-preview-container');
    const fileNameDisplay       = document.getElementById('file-name');
    const audioPlayer           = document.getElementById('audio-player');
    const removeAudioBtn        = document.getElementById('remove-audio');

    const analyzeBtn            = document.getElementById('analyze-btn');
    const loadingState          = document.getElementById('loading-state');
    const resultState           = document.getElementById('result-state');
    const resultCard            = document.getElementById('result-card');
    const resultIconFa          = document.getElementById('result-icon-fa');
    const resultText            = document.getElementById('result-text');
    const confidencePercentage  = document.getElementById('confidence-percentage');
    const confidenceBar         = document.getElementById('confidence-bar');
    const resetBtn              = document.getElementById('reset-btn');

    const errorAlert    = document.getElementById('error-alert');
    const errorMessage  = document.getElementById('error-message');
    const inputSection  = document.getElementById('input-section');

    // Probability detail elements (added in index.html below)
    const probHumanEl = document.getElementById('prob-human');
    const probAiEl    = document.getElementById('prob-ai');

    // Handle Reset (duplicate listener removed — the one at line ~303 is the canonical one)
    // This block was referencing non-existent variables; it is intentionally left empty
    // The actual reset logic is handled by the resetBtn listener defined at the bottom.

    

    // --- File Upload ---
    dropZone.addEventListener('click', () => fileInput.click());
    // Keyboard support for role="button" divs
    dropZone.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); } });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        hideError();
        const validTypes      = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/flac', 'audio/x-flac'];
        const validExtensions = ['.wav', '.mp3', '.flac'];
        const fileName        = file.name.toLowerCase();
        const hasValidExt     = validExtensions.some(ext => fileName.endsWith(ext));

        if (!validTypes.includes(file.type) && !hasValidExt) {
            showError('Unsupported file format. Please upload a WAV, MP3, or FLAC file.');
            return;
        }

        currentAudioFile = file;
        if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
        currentAudioUrl = URL.createObjectURL(file);
        showAudioPreview(file.name, currentAudioUrl);
    }



    // --- Audio Preview & Real-Time Neon Equalizer ---
    let audioCtx = null;
    let analyser = null;
    let sourceNode = null;
    let animFrameId = null;

    function initAudioVisualizer() {
        const canvas = document.getElementById('voice-equalizer-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = canvas.parentElement.offsetWidth || 400;
            canvas.height = canvas.parentElement.offsetHeight || 110;
        }
        resize();

        function drawIdleWave() {
            if (audioPlayer && !audioPlayer.paused) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            const time = Date.now() * 0.003;
            for (let x = 0; x < canvas.width; x += 4) {
                const y = canvas.height / 2 + Math.sin(x * 0.05 + time) * 6 + Math.cos(x * 0.02 - time) * 4;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            animFrameId = requestAnimationFrame(drawIdleWave);
        }
        drawIdleWave();

        audioPlayer.addEventListener('play', () => {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 64;
                try {
                    sourceNode = audioCtx.createMediaElementSource(audioPlayer);
                    sourceNode.connect(analyser);
                    analyser.connect(audioCtx.destination);
                } catch(e) {}
            }
            if (audioCtx.state === 'suspended') audioCtx.resume();
            renderLiveEqualizer();
        });

        function renderLiveEqualizer() {
            if (audioPlayer.paused) {
                drawIdleWave();
                return;
            }
            const bufferLength = analyser ? analyser.frequencyBinCount : 32;
            const dataArray = new Uint8Array(bufferLength);
            if (analyser) analyser.getByteFrequencyData(dataArray);

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const barWidth = (canvas.width / bufferLength) * 1.5;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * (canvas.height * 0.85);
                const grad = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
                grad.addColorStop(0, '#06b6d4');
                grad.addColorStop(0.5, '#8b5cf6');
                grad.addColorStop(1, '#ec4899');

                ctx.fillStyle = grad;
                ctx.shadowBlur = 8;
                ctx.shadowColor = '#06b6d4';
                ctx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);
                ctx.shadowBlur = 0;
                x += barWidth + 1;
            }
            animFrameId = requestAnimationFrame(renderLiveEqualizer);
        }
    }

    function showAudioPreview(filename, url) {
        fileNameDisplay.textContent = filename;
        audioPlayer.src = url;
        audioPlayer.load();
        audioPreviewContainer.classList.remove('hidden');
        analyzeBtn.disabled = false;
        uploadArea.style.display = 'none';
        setTimeout(initAudioVisualizer, 100);
    }

    removeAudioBtn.addEventListener('click', resetInputState);

    function resetInputState() {
        currentAudioFile = null;
        if (currentAudioUrl) { URL.revokeObjectURL(currentAudioUrl); currentAudioUrl = null; }
        if (animFrameId) cancelAnimationFrame(animFrameId);
        audioPlayer.src = '';
        audioPreviewContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        fileInput.value = '';
        hideError();
        uploadArea.style.display = '';
    }

    // --- Analysis ---
    analyzeBtn.addEventListener('click', () => {
        if (window.checkScanGate && !window.checkScanGate()) return;
        if (!currentAudioFile) {
            showError('Please upload or record an audio file first.');
            return;
        }
        startAnalysis();
    });

    async function startAnalysis() {
        inputSection.style.display = 'none';
        analyzeBtn.style.display   = 'none';
        hideError();
        loadingState.classList.remove('hidden');

        // Cycle through loading messages for a lively loader
        const loadingMessages = [
            'Extracting audio features...',
            'Running AI inference...',
            'Analysing voice patterns...',
            'Calculating probabilities...',
            'Almost there...'
        ];
        let msgIdx = 0;
        const msgEl = document.getElementById('loading-msg');
        const msgInterval = setInterval(() => {
            msgIdx = (msgIdx + 1) % loadingMessages.length;
            if (msgEl) { msgEl.style.animation = 'none'; msgEl.offsetHeight; msgEl.style.animation = ''; msgEl.textContent = loadingMessages[msgIdx]; }
        }, 1800);

        // Auto-use the saved backend URL (set by server-config.js auto-connect)
        let backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';

        const formData = new FormData();
        const filename = currentAudioFile.recordedName || currentAudioFile.name || 'recorded_audio.webm';
        formData.append('file', currentAudioFile, filename);
        formData.append('type', 'voice');

        try {
            const response = await fetch(`${backendUrl}/api/infer`, {
                method: 'POST',
                body: formData,
                headers: window.getAuthHeaders ? window.getAuthHeaders() : {}
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Server error (${response.status})`);
            }

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            clearInterval(msgInterval);

            // Handle both flat response (Node server) and wrapped response (Python /api/infer)
            const analysis = data.analysis || data;
            
            // Fallbacks in case backend doesn't send exact fields
            let rawConf = analysis.confidence || 0.5;
            if (rawConf > 1) rawConf = rawConf / 100;
            
            const probAi = analysis.prob_ai !== undefined ? analysis.prob_ai : Math.round(rawConf * 100);
            const probHuman = analysis.prob_human !== undefined ? analysis.prob_human : (100 - probAi);
            
            // Recalculate verdict robustly
            const isHuman = probHuman >= probAi;
            const confidence = Math.max(probHuman, probAi);

            showResult(isHuman, confidence, probHuman, probAi);

        } catch (err) {
            clearInterval(msgInterval);
            console.error('Analysis error:', err);
            let msg = err.message;
            if (msg.includes('fetch') || msg.includes('Failed') || msg.includes('NetworkError')) {
                msg = 'Cannot reach server. Make sure the Node server is running and connected.';
            }
            showError('Error analyzing audio: ' + msg);
            inputSection.style.display = 'block';
            analyzeBtn.style.display   = 'flex';
            loadingState.classList.add('hidden');
        }
    }

    function animateCountUp(element, target, duration, prefix = '', suffix = '%') {
        let start = 0;
        const targetNum = parseFloat(target);
        if (isNaN(targetNum)) { element.textContent = prefix + target + suffix; return; }
        const increment = targetNum / (duration / 16);
        const interval = setInterval(() => {
            start += increment;
            if (start >= targetNum) {
                start = targetNum;
                clearInterval(interval);
            }
            element.textContent = prefix + start.toFixed(1) + suffix;
        }, 16);
    }

    // --- Show Result with REAL confidence ---
    function showResult(isHuman, confidence, probHuman, probAi) {
        loadingState.classList.add('hidden');
        resultState.classList.remove('hidden');

        // ── Voice Animation Banner ─────────────────────────────────────────
        const humanAnim = document.getElementById('human-anim');
        const aiAnim    = document.getElementById('ai-anim');
        if (humanAnim && aiAnim) {
            if (isHuman) {
                humanAnim.classList.remove('hidden');
                aiAnim.classList.add('hidden');
            } else {
                aiAnim.classList.remove('hidden');
                humanAnim.classList.add('hidden');
            }
        }

        // Apply status class on the card
        resultCard.className = 'result-card';
        resultCard.classList.add(isHuman ? 'status-authentic' : 'status-fake');

        const ring = document.getElementById('confidence-bar-circle');
        const icon = document.getElementById('result-icon');
        ring.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            // ── Verdict Hero ──
            const verdictSub = document.getElementById('verdict-sub');
            if (isHuman) {
                resultText.textContent  = 'Human Voice';
                icon.className = 'fa-solid fa-user-check';
                if (verdictSub) verdictSub.textContent = 'This audio is genuine human speech';
            } else {
                resultText.textContent  = 'AI Generated Voice';
                icon.className = 'fa-solid fa-robot';
                if (verdictSub) verdictSub.textContent = 'This audio was synthesised by AI';
            }

            // ── Confidence ring ──
            animateCountUp(confidencePercentage, confidence, 1500);
            const circumference = 339.292;
            ring.style.strokeDashoffset = circumference - (confidence / 100) * circumference;

            // ── Probability Duel ── show winner BIGGER
            const humanValEl  = document.getElementById('prob-human-val');
            const aiValEl     = document.getElementById('prob-ai-val');
            const humanBlock  = document.getElementById('prob-human-block');
            const aiBlock     = document.getElementById('prob-ai-block');

            if (humanValEl) animateCountUp(humanValEl, probHuman, 1500, '', '%');
            if (aiValEl)    animateCountUp(aiValEl,    probAi,    1500, '', '%');

            // Mark winner block
            if (humanBlock && aiBlock) {
                if (probHuman >= probAi) {
                    humanBlock.classList.add('winner');
                    aiBlock.classList.remove('winner');
                } else {
                    aiBlock.classList.add('winner');
                    humanBlock.classList.remove('winner');
                }
            }

            // ── Hidden compat spans ──
            if (probHumanEl) animateCountUp(probHumanEl, probHuman, 1500, 'Human: ');
            if (probAiEl)    animateCountUp(probAiEl, probAi, 1500, 'AI: ');

            // ── Confidence chart bars ──
            const chartHumanBar   = document.getElementById('chart-human-bar');
            const chartAiBar      = document.getElementById('chart-ai-bar');
            const chartHumanLabel = document.getElementById('chart-human-label');
            const chartAiLabel    = document.getElementById('chart-ai-label');
            if (chartHumanBar) {
                chartHumanBar.style.width = '0%';
                chartAiBar.style.width    = '0%';
                setTimeout(() => {
                    chartHumanBar.style.width = probHuman + '%';
                    chartAiBar.style.width    = probAi    + '%';
                    animateCountUp(chartHumanLabel, probHuman, 1500, '', '%');
                    animateCountUp(chartAiLabel,    probAi,    1500, '', '%');
                }, 120);
            }

            if (typeof scanHistory !== 'undefined') {
                const fName = currentAudioFile ? currentAudioFile.name : 'Audio File';
                scanHistory.addScan('Voice', fName, !isHuman, confidence);
            }

            // Show share button
            const shareBtn = document.getElementById('share-btn');
            if (shareBtn) {
                shareBtn.classList.remove('hidden');
                shareBtn._lastResult = { is_ai: !isHuman, confidence: confidence / 100, prob_ai: probAi, prob_human: probHuman, generator: isHuman ? 'Authentic Human Voice' : 'AI Voice Synthesis' };
                shareBtn._lastName   = currentAudioFile ? currentAudioFile.name : 'Audio File';
            }

        }, 50);
    }

    // --- Share Result ---
    const shareBtn = document.getElementById('share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', async () => {
            let backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';
            const result     = shareBtn._lastResult;
            const filename   = shareBtn._lastName || 'voice.wav';

            shareBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
            try {
                const res  = await fetch(`${backendUrl}/api/results/save`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                    body: JSON.stringify({ result, filename, type: 'voice' })
                });
                const data = await res.json();
                if (data.id) {
                    const shareUrl = `${window.location.origin}/result.html?id=${data.id}`;
                    await navigator.clipboard.writeText(shareUrl);
                    shareBtn.innerHTML = '<i class="fa-solid fa-check"></i> Link Copied!';
                    setTimeout(() => { shareBtn.innerHTML = '<i class="fa-solid fa-share-nodes"></i> Share Result'; }, 3000);
                }
            } catch (e) {
                shareBtn.innerHTML = '<i class="fa-solid fa-share-nodes"></i> Share Result';
                alert('Could not save result. Make sure the server is connected.');
            }
        });
    }

    // --- Reset ---
    resetBtn.addEventListener('click', () => {
        inputSection.style.display = 'block';
        analyzeBtn.style.display   = 'flex';
        resultState.classList.add('hidden');
        const ring = document.getElementById('confidence-bar-circle');
        if (ring) ring.style.strokeDashoffset = '339.292';
        const shareBtn = document.getElementById('share-btn');
        if (shareBtn) shareBtn.classList.add('hidden');
        // ── Hide voice animations on reset ─────────────────────────────────
        const humanAnim = document.getElementById('human-anim');
        const aiAnim    = document.getElementById('ai-anim');
        if (humanAnim) humanAnim.classList.add('hidden');
        if (aiAnim)    aiAnim.classList.add('hidden');
        // ── Reset confidence chart bars ─────────────────────────────────────
        const cHBar = document.getElementById('chart-human-bar');
        const cABar = document.getElementById('chart-ai-bar');
        const cHLbl = document.getElementById('chart-human-label');
        const cALbl = document.getElementById('chart-ai-label');
        if (cHBar) { cHBar.style.width = '0%'; cHLbl.textContent = '0%'; }
        if (cABar) { cABar.style.width = '0%'; cALbl.textContent = '0%'; }
        resetInputState();
    });

    // --- Live Microphone Mode ---
    const liveModeBtn  = document.getElementById('live-mode-btn');
    const liveModePanel = document.getElementById('live-mode-panel');
    const stopLiveBtn  = document.getElementById('stop-live-btn');
    const liveHumanEl  = document.getElementById('live-human-pct');
    const liveAiEl     = document.getElementById('live-ai-pct');
    const liveVerdict  = document.getElementById('live-verdict');

    let liveStream     = null;
    let liveInterval   = null;
    let liveRecorder   = null;

    async function runLiveChunk() {
        if (!liveStream) return;
        const mimeType = ['audio/webm;codecs=opus','audio/webm','audio/mp4',''].find(t => t === '' || MediaRecorder.isTypeSupported(t));
        const rec = mimeType ? new MediaRecorder(liveStream, { mimeType }) : new MediaRecorder(liveStream);
        const chunks = [];
        rec.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
        rec.start();
        setTimeout(() => rec.stop(), 4000);
        rec.onstop = async () => {
            const usedMime = rec.mimeType || 'audio/webm';
            const ext = usedMime.includes('mp4') ? 'm4a' : 'webm';
            const blob = new Blob(chunks, { type: usedMime });
            const file = new File([blob], `live_chunk.${ext}`, { type: usedMime });

            let backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';
            const fd = new FormData();
            fd.append('file', file);
            fd.append('type', 'voice');

            liveVerdict.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
            try {
                const res  = await fetch(`${backendUrl}/api/infer`, {
                    method: 'POST',
                    body: fd,
                    headers: window.getAuthHeaders ? window.getAuthHeaders() : {}
                });
                const data = await res.json();
                if (data.error) throw new Error(data.error);

                const probHuman = data.is_ai ? Math.round((1 - data.confidence) * 100) : Math.round(data.confidence * 100);
                const probAi    = 100 - probHuman;
                liveHumanEl.textContent = probHuman + '%';
                liveAiEl.textContent    = probAi + '%';

                if (data.is_ai) {
                    liveVerdict.innerHTML = '<i class="fa-solid fa-robot" style="color:#ef4444"></i> <span style="color:#ef4444">AI Generated Voice Detected</span>';
                } else {
                    liveVerdict.innerHTML = '<i class="fa-solid fa-user-check" style="color:#10b981"></i> <span style="color:#10b981">Human Voice Confirmed</span>';
                }
            } catch (e) {
                liveVerdict.innerHTML = '<i class="fa-solid fa-exclamation-triangle" style="color:#f59e0b"></i> <span style="color:#f59e0b">Analysis failed — retrying...</span>';
            }
        };
    }

    if (liveModeBtn) {
        liveModeBtn.addEventListener('click', async () => {
            if (!navigator.mediaDevices) {
                alert('Microphone not supported on this browser/connection (needs HTTPS).');
                return;
            }
            try {
                liveStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                liveModePanel.style.display = 'block';
                liveModeBtn.style.display   = 'none';
                liveHumanEl.textContent = '--';
                liveAiEl.textContent    = '--';
                liveVerdict.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Collecting audio...';

                await runLiveChunk();
                liveInterval = setInterval(runLiveChunk, 5000);
            } catch {
                alert('Microphone access denied.');
            }
        });
    }

    if (stopLiveBtn) {
        stopLiveBtn.addEventListener('click', () => {
            clearInterval(liveInterval);
            if (liveStream) { liveStream.getTracks().forEach(t => t.stop()); liveStream = null; }
            liveModePanel.style.display = 'none';
            liveModeBtn.style.display   = 'inline-flex';
        });
    }

    // --- Helpers ---
    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }

    function hideError() {
        errorAlert.classList.add('hidden');
    }

} // end initVoiceUI

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceUI);
} else {
    initVoiceUI();
}

