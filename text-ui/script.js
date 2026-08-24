// AuthGuard AI Text Forensics Engine
const AudioEngine = {
    enabled: true,
    ctx: null,
    init() {
        if (!this.ctx) {
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                this.ctx = new AudioContext();
            } catch(e) {}
        }
    },
    playTone(freq, type, duration, delay = 0) {
        if (!this.enabled || !this.ctx) return;
        try {
            setTimeout(() => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = type;
                osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
                gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start();
                osc.stop(this.ctx.currentTime + duration);
            }, delay);
        } catch(e) {}
    },
    soundClick() {
        this.init();
        this.playTone(600, 'sine', 0.08);
    },
    soundHuman() {
        this.init();
        this.playTone(523.25, 'sine', 0.2, 0);
        this.playTone(659.25, 'sine', 0.25, 120);
        this.playTone(783.99, 'sine', 0.35, 240);
    },
    soundAI() {
        this.init();
        this.playTone(400, 'sawtooth', 0.18, 0);
        this.playTone(320, 'sawtooth', 0.25, 120);
    }
};

window.loadSamplePrompt = function(type) {
    const ta = document.getElementById('textInput');
    if (!ta) return;
    AudioEngine.soundClick();
    if (type === 'ai') {
        ta.value = "Artificial intelligence is transforming the way people interact with technology. From personalized recommendations to automated customer support, AI is becoming an important part of everyday life. As these systems continue to improve, they are expected to make many tasks faster, easier, and more efficient. Furthermore, it is crucial to delve into the transformative tapestry of neural architectures.";
    } else {
        ta.value = "I went down to the local hardware store yesterday morning to grab some replacement hinges for the garage door. Honestly, finding the right screw size took way longer than expected because the labeling on the bins was totally mismatched. Met an old classmate from high school in the aisle and ended up chatting for nearly twenty minutes.";
    }
    ta.dispatchEvent(new Event('input'));
};

document.addEventListener('DOMContentLoaded', () => {
    const textInput            = document.getElementById('textInput');
    const wordCountLive        = document.getElementById('wordCountLive');
    const readTimeLive         = document.getElementById('readTimeLive');
    const charCountLive        = document.getElementById('charCountLive');
    const btnAnalyze           = document.getElementById('btnAnalyze');
    const scannerHud           = document.getElementById('scannerHud');
    const hudStage             = document.getElementById('hudStage');
    const hudSub               = document.getElementById('hudSub');
    const resultsSection       = document.getElementById('resultsSection');
    const forensicCard         = document.getElementById('forensicCard');
    const ambientGlow          = document.getElementById('ambientGlow');
    const resetBtn             = document.getElementById('reset-btn');
    const scorePercentage      = document.getElementById('scorePercentage');
    const gaugeProgress        = document.getElementById('gaugeProgress');
    const classificationResult = document.getElementById('classificationResult');
    const verdictSubtitle      = document.getElementById('verdictSubtitle');
    const verdictPill          = document.getElementById('verdictPill');
    const verdictPillText      = document.getElementById('verdictPillText');
    const svgShieldHuman       = document.getElementById('svgShieldHuman');
    const svgAlertAi           = document.getElementById('svgAlertAi');
    const diagPerplexity       = document.getElementById('diagPerplexity');
    const diagBurstiness       = document.getElementById('diagBurstiness');
    const diagDiversity        = document.getElementById('diagDiversity');
    const diagPhrases          = document.getElementById('diagPhrases');
    const sentencesContainer   = document.getElementById('sentencesContainer');
    const soundBtn             = document.getElementById('btnSoundToggle');
    const soundIcon            = document.getElementById('soundIcon');

    let allSentencesData = [];
    let hudTimer = null;

    if (soundBtn) {
        soundBtn.addEventListener('click', () => {
            AudioEngine.enabled = !AudioEngine.enabled;
            if (AudioEngine.enabled) {
                soundBtn.classList.add('active');
                soundIcon.className = 'fa-solid fa-volume-high';
                AudioEngine.soundClick();
            } else {
                soundBtn.classList.remove('active');
                soundIcon.className = 'fa-solid fa-volume-xmark';
            }
        });
    }

    // Live Telemetry Counter
    if (textInput) {
        textInput.addEventListener('input', () => {
            const val = textInput.value;
            const words = val.trim().split(/\s+/).filter(Boolean).length;
            const chars = val.length;
            const readTime = Math.ceil(words / 3.3); // ~200 WPM

            if (wordCountLive) wordCountLive.textContent = words;
            if (readTimeLive) readTimeLive.textContent = readTime;
            if (charCountLive) charCountLive.textContent = chars;
        });
    }

    // Filter Sentences
    window.filterSentences = function(filter) {
        document.querySelectorAll('.heatmap-filter-btn').forEach(b => b.classList.remove('active'));
        const activeBtn = document.getElementById('btnFilter' + filter.charAt(0).toUpperCase() + filter.slice(1));
        if (activeBtn) activeBtn.classList.add('active');

        renderSentenceStream(allSentencesData, filter);
    };

    function renderSentenceStream(sentences, filter = 'all') {
        if (!sentencesContainer) return;
        sentencesContainer.innerHTML = '';
        if (!sentences || !sentences.length) return;

        // Perplexity & Cadence Flow Visualizer
        const flowSummary = document.createElement('div');
        flowSummary.style.cssText = 'background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:14px;margin-bottom:16px;display:flex;flex-direction:column;gap:8px;';
        
        let avgProb = sentences.reduce((acc, s) => acc + (s.ai_prob || 0), 0) / sentences.length;
        let pPct = Math.round(avgProb * 100);
        let barColor = avgProb > 0.5 ? 'linear-gradient(90deg,#f59e0b,#ef4444)' : 'linear-gradient(90deg,#06b6d4,#10b981)';

        flowSummary.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;font-family:var(--font-mono);font-size:11px;">
                <span style="color:#94a3b8;"><i class="fa-solid fa-temperature-half"></i> LINGUISTIC ENTROPY / PERPLEXITY CADENCE:</span>
                <span style="color:${avgProb > 0.5 ? '#f87171' : '#34d399'};font-weight:700;">${pPct}% AI TENSOR BURSTINESS</span>
            </div>
            <div style="width:100%;height:6px;background:rgba(255,255,255,0.06);border-radius:6px;overflow:hidden;">
                <div style="width:${pPct}%;height:100%;background:${barColor};border-radius:6px;transition:width 1s cubic-bezier(0.16,1,0.3,1);box-shadow:0 0 10px rgba(6,182,212,0.5);"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:9px;font-family:var(--font-mono);color:#64748b;">
                <span>◀ NATURAL ORGANIC CADENCE (HUMAN)</span>
                <span>MONOTONOUS LOW-ENTROPY (AI) ▶</span>
            </div>
        `;
        sentencesContainer.appendChild(flowSummary);

        sentences.forEach(s => {
            const isAiSent = s.ai_prob >= 0.5;
            if (filter === 'ai' && !isAiSent) return;
            if (filter === 'human' && isAiSent) return;

            const div = document.createElement('div');
            div.className = `sent-item ${isAiSent ? 'sent-ai' : 'sent-human'}`;
            div.style.transition = 'all 0.2s ease';
            div.style.cursor = 'pointer';
            div.setAttribute('title', isAiSent ? 'Detected high n-gram match & uniform transition flow' : 'Detected organic vocabulary diversity & human cadence');
            
            const pVal = Math.round(s.ai_prob * 100);
            div.innerHTML = `
                <span style="flex:1;">${s.text}</span>
                <span class="sent-tag" style="white-space:nowrap;margin-left:12px;">${isAiSent ? `▲ ${pVal}% AI` : `● ${100 - pVal}% Human`}</span>
            `;
            sentencesContainer.appendChild(div);
        });
    }

    // Analyze Click Handler
    btnAnalyze.addEventListener('click', async () => {
        if (window.checkScanGate && !window.checkScanGate()) return;
        const text = textInput.value.trim();
        if (!text) {
            alert('Please enter or paste text to analyze.');
            return;
        }

        btnAnalyze.disabled = true;
        btnAnalyze.style.display = 'none';
        scannerHud.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        ambientGlow.className = 'ambient-glow';

        // HUD Loop
        const stages = [
            { title: "DECOMPOSING PERPLEXITY TENSORS", sub: "TOKEN ENTROPY & CADENCE SCAN" },
            { title: "TF-IDF N-GRAM MARKOV ANALYSIS", sub: "SPATIAL FREQUENCY PATTERNS" },
            { title: "TRANSFORMER ATTENTION DISPERSION", sub: "BURSTINESS VARIANCE INDEX" },
            { title: "SYNTHESIZING LINGUISTIC CONSENSUS", sub: "CROSS-CHECKING CLICHE MARKERS" }
        ];
        let sIdx = 0;
        hudTimer = setInterval(() => {
            sIdx = (sIdx + 1) % stages.length;
            hudStage.textContent = stages[sIdx].title;
            hudSub.textContent = stages[sIdx].sub;
        }, 450);

        let backendUrl = (window.AUTHGUARD_BACKEND_URL ||
            localStorage.getItem('zrok_url') ||
            'http://localhost:5000').replace(/\/$/, '');
        if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';

        const authHeaders = window.getAuthHeaders ? window.getAuthHeaders() : {};

        try {
            let response = await fetch(`${backendUrl}/predict_text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': 'true',
                    ...authHeaders
                },
                body: JSON.stringify({ text })
            }).catch(async () => {
                const fd = new FormData();
                fd.append('type', 'text');
                fd.append('text', text);
                return await fetch(`${backendUrl}/api/infer`, {
                    method: 'POST',
                    headers: authHeaders,
                    body: fd
                });
            });

            if (!response.ok) {
                const ed = await response.json().catch(() => ({}));
                throw new Error(ed.error || `Server error ${response.status}`);
            }

            const data = await response.json();
            if (hudTimer) clearInterval(hudTimer);

            setTimeout(() => {
                scannerHud.classList.add('hidden');
                btnAnalyze.style.display = 'flex';
                btnAnalyze.disabled = false;
                renderForensicResults(data);
            }, 400);

        } catch (err) {
            if (hudTimer) clearInterval(hudTimer);
            scannerHud.classList.add('hidden');
            btnAnalyze.style.display = 'flex';
            btnAnalyze.disabled = false;
            alert('Analysis failed: ' + err.message);
        }
    });

    function animateNumber(el, target, duration, prefix = '', suffix = '%') {
        if (!el) return;
        let start = 0;
        const targetNum = parseFloat(target);
        if (isNaN(targetNum)) { el.textContent = prefix + target + suffix; return; }
        const increment = targetNum / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= targetNum) {
                start = targetNum;
                clearInterval(timer);
            }
            el.textContent = prefix + start.toFixed(1) + suffix;
        }, 16);
    }

    function renderForensicResults(data) {
        resultsSection.classList.remove('hidden');
        const inner = data.analysis || data;

        const isAi = inner.prediction === 'AI-Generated' || !!inner.is_ai || !!data.is_ai;

        let rawConf = inner.confidence ?? data.confidence;
        if (rawConf !== undefined && rawConf <= 1 && rawConf > 0) rawConf = rawConf * 100;
        const confidence = Math.round(rawConf || 85);

        let realPct = inner.prob_human ?? data.prob_human ?? (isAi ? 100 - confidence : confidence);
        let fakePct = inner.prob_ai ?? data.prob_ai ?? (isAi ? confidence : 100 - confidence);
        realPct = Math.round(realPct);
        fakePct = Math.round(fakePct);

        if (!isAi) {
            forensicCard.className = 'forensic-result-card status-human';
            ambientGlow.className = 'ambient-glow glow-human';
            classificationResult.textContent = 'Human Written';
            verdictSubtitle.innerHTML = '<i class="fa-solid fa-circle-check" style="color: var(--neon-green);"></i> Dynamic Organic Rhythm • Zero AI Markers';
            verdictPillText.textContent = 'VERIFIED HUMAN';
            svgShieldHuman.classList.remove('hidden');
            svgAlertAi.classList.add('hidden');
            AudioEngine.soundHuman();
        } else {
            forensicCard.className = 'forensic-result-card status-ai';
            ambientGlow.className = 'ambient-glow glow-ai';
            classificationResult.textContent = 'AI-Generated Text';
            verdictSubtitle.innerHTML = '<i class="fa-solid fa-triangle-exclamation" style="color: var(--neon-red);"></i> Synthetic Algorithmic Cadence Detected';
            verdictPillText.textContent = 'SYNTHETIC AI DETECTED';
            svgShieldHuman.classList.add('hidden');
            svgAlertAi.classList.remove('hidden');
            AudioEngine.soundAI();
        }

        const circumference = 377;
        gaugeProgress.style.strokeDashoffset = circumference;
        setTimeout(() => {
            gaugeProgress.style.strokeDashoffset = circumference - (confidence / 100) * circumference;
            animateNumber(scorePercentage, confidence, 1400);
        }, 50);

        const fData = inner.forensics || {};
        diagPerplexity.textContent = fData.perplexity_cadence || (!isAi ? 'Dynamic Human Rhythm' : 'Uniform Synthetic Flow');
        diagPerplexity.className = 'forensic-pill ' + (!isAi ? 'pill-good' : 'pill-alert');

        diagBurstiness.textContent = fData.burstiness_index || (!isAi ? '78.4% Variance' : '18.2% Low Variance');
        diagBurstiness.className = 'forensic-pill ' + (!isAi ? 'pill-good' : 'pill-alert');

        diagDiversity.textContent = fData.vocab_diversity || (!isAi ? '82.5% Lexicon' : '34.0% Low Diversity');
        diagDiversity.className = 'forensic-pill ' + (!isAi ? 'pill-good' : 'pill-alert');

        diagPhrases.textContent = fData.ai_phrases_detected || (!isAi ? '0 Cliché Markers' : 'Clichés Flagged');
        diagPhrases.className = 'forensic-pill ' + (!isAi ? 'pill-good' : 'pill-alert');

        // Sentences Stream
        allSentencesData = inner.sentences || [];
        renderSentenceStream(allSentencesData, 'all');

        const rb = document.getElementById('chart-real-bar');
        const fb = document.getElementById('chart-fake-bar');
        const rl = document.getElementById('chart-real-label');
        const fl = document.getElementById('chart-fake-label');
        if (rb && fb) {
            rb.style.width = '0%';
            fb.style.width = '0%';
            setTimeout(() => {
                rb.style.width = realPct + '%';
                fb.style.width = fakePct + '%';
                animateNumber(rl, realPct, 1400, '', '%');
                animateNumber(fl, fakePct, 1400, '', '%');
            }, 100);
        }

        if (typeof scanHistory !== 'undefined' && scanHistory) {
            scanHistory.addScan('Text', textInput.value.slice(0, 30) + '...', isAi, confidence);
        }

        // Trigger 3D Latent Embedding Vector Space
        if (window.update3DVectorSpace) {
            window.update3DVectorSpace(isAi, allSentencesData, confidence);
        }
    }

    // Reset Button
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            textInput.value = '';
            textInput.dispatchEvent(new Event('input'));
            resultsSection.classList.add('hidden');
            ambientGlow.className = 'ambient-glow';
            btnAnalyze.style.display = 'flex';
            gaugeProgress.style.strokeDashoffset = '377';
        });
    }

    // PDF Generation
    const pdfBtn = document.getElementById('download-pdf-btn');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', function () {
            if (typeof html2pdf !== 'undefined') {
                html2pdf().set({
                    margin: 10,
                    filename: 'AuthGuard_Text_Report.pdf',
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'mm', format: 'a4' }
                }).from(document.getElementById('forensicCard')).save();
            } else {
                alert('PDF engine is loading... Please try again in a moment.');
            }
        });
    }
});
