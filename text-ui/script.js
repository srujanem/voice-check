document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('resultsSection');
    const resetBtn = document.getElementById('reset-btn');
    
    // Results elements
    const scoreProgress = document.getElementById('scoreProgress');
    const scorePercentage = document.getElementById('scorePercentage');
    const resultCard = document.getElementById('result-card');
    const classificationResult = document.getElementById('classificationResult');
    const probHuman = document.getElementById('prob-human');
    const probAi = document.getElementById('prob-ai');
    const icon = document.getElementById('result-icon');

    // PDF Download logic
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const element = document.getElementById('result-card');
            const opt = {
                margin:       10,
                filename:     `Text_Report_${Date.now()}.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true, backgroundColor: document.documentElement.getAttribute('data-theme') === 'light' ? '#ffffff' : '#1e1e2e' },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        });
    }

    // Handle Analyze
    btnAnalyze.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) {
            alert("Please paste some text to analyze.");
            return;
        }
        
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:8000').replace(/\/$/, '');
            const formData = new FormData();
            formData.append('type', 'text');
            formData.append('file', new Blob([text], { type: 'text/plain' }), 'text.txt');

            const response = await fetch(`${backendUrl}/api/infer`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Server error (${response.status})`);
            }

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            loadingState.classList.add('hidden');
            showResults(data);
        } catch (error) {
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';
            alert('Analysis failed: ' + error.message);
        }
    });

    resetBtn.addEventListener('click', () => {
        textInput.value = '';
        resultsSection.classList.add('hidden');
        btnAnalyze.style.display = 'inline-flex';
        scoreProgress.style.strokeDashoffset = '339.292';
        // Clear previous sentence highlights so they don't show on next scan
        const xaiSection = document.getElementById('xai-section');
        if (xaiSection) xaiSection.innerHTML = '';
        if (probHuman) probHuman.textContent = 'Human: --';
        if (probAi) probAi.textContent = 'AI: --';
    });

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

    function showResults(data) {
        resultsSection.classList.remove('hidden');

        // Deep unwrap nested analysis objects if present
        let innerData = data;
        if (innerData.analysis && typeof innerData.analysis === 'object') {
            innerData = innerData.analysis;
        }
        if (innerData.analysis && typeof innerData.analysis === 'object') {
            innerData = innerData.analysis;
        }

        // --- Safe numeric extraction ---
        const isAi = innerData.prediction === 'AI-Generated' ||
                     innerData.prediction === 'ai' ||
                     !!innerData.is_ai ||
                     !!data.is_ai;

        // Extract prob_ai and prob_human from any level
        let rawAi = innerData.prob_ai ?? data.prob_ai ?? (data.analysis ? data.analysis.prob_ai : undefined);
        let rawHuman = innerData.prob_human ?? data.prob_human ?? (data.analysis ? data.analysis.prob_human : undefined);
        let rawConf = innerData.confidence ?? data.confidence;

        let aiProb    = rawAi !== undefined ? Number(rawAi) : NaN;
        let humanProb = rawHuman !== undefined ? Number(rawHuman) : NaN;
        let conf      = rawConf !== undefined ? Number(rawConf) : NaN;

        // If confidence is between 0 and 1, convert to 0-100 scale
        if (!isNaN(conf) && conf <= 1) conf = conf * 100;
        if (!isNaN(aiProb) && aiProb <= 1) aiProb = aiProb * 100;
        if (!isNaN(humanProb) && humanProb <= 1) humanProb = humanProb * 100;

        // Fill in missing values
        if (isNaN(aiProb) || isNaN(humanProb)) {
            if (!isNaN(conf)) {
                aiProb    = isAi ? conf : 100 - conf;
                humanProb = isAi ? 100 - conf : conf;
            } else {
                aiProb    = isAi ? 85 : 15;
                humanProb = isAi ? 15 : 85;
                conf      = 85;
            }
        }

        if (isNaN(conf)) conf = isAi ? aiProb : humanProb;

        const confidence = Math.round(conf);

        resultCard.className = 'result-card';
        scoreProgress.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            if (!isAi) {
                resultCard.classList.add('status-authentic');
                resultCard.classList.remove('status-fake');
                classificationResult.textContent = 'Human Written';
                icon.className = 'fa-solid fa-user-pen';
            } else {
                resultCard.classList.add('status-fake');
                resultCard.classList.remove('status-authentic');
                classificationResult.textContent = 'AI-Generated Text';
                icon.className = 'fa-solid fa-robot';
            }

            // Animate confidence ring
            animateCountUp(scorePercentage, confidence, 1500);
            const circumference = 339.292;
            scoreProgress.style.strokeDashoffset = circumference - (confidence / 100) * circumference;

            // Animate prob bars
            if (probHuman) animateCountUp(probHuman, humanProb.toFixed(1), 1500, 'Human: ');
            if (probAi)    animateCountUp(probAi,    aiProb.toFixed(1),    1500, 'AI: ');

            // Word count
            const wordCountEl = document.getElementById('word-count');
            if (wordCountEl) wordCountEl.textContent = innerData.word_count ?? '--';

            // Confidence label badge
            const confLabelEl = document.getElementById('confidence-label');
            if (confLabelEl) {
                const label = innerData.confidence_label || '';
                confLabelEl.textContent = label ? `Confidence: ${label}` : '';
                const colors = { 'Very High': '#10b981', 'High': '#6366f1', 'Moderate': '#f59e0b', 'Low': '#ef4444' };
                confLabelEl.style.color = colors[label] || 'var(--accent-cyan)';
            }

            // Sentence-level highlighting
            if (innerData.sentences && innerData.sentences.length) {
                const xaiSection = document.getElementById('xai-section');
                if (xaiSection) {
                    xaiSection.innerHTML = '<h4 style="margin-bottom:10px;border-bottom:1px solid var(--border-color);padding-bottom:5px;"><i class="fa-solid fa-magnifying-glass"></i> Sentence Analysis</h4>';
                    innerData.sentences.forEach(s => {
                        const span = document.createElement('span');
                        span.textContent = s.text + ' ';
                        const p = Number(s.ai_prob);
                        if (p >= 0.5) {
                            const alpha = (p - 0.5) * 2;
                            span.style.backgroundColor = `rgba(239,68,68,${(alpha * 0.4).toFixed(2)})`;
                            span.style.color = document.documentElement.getAttribute('data-theme') === 'light' ? '#7f1d1d' : '#fecaca';
                        } else {
                            const alpha = (0.5 - p) * 2;
                            span.style.backgroundColor = `rgba(16,185,129,${(alpha * 0.2).toFixed(2)})`;
                        }
                        span.title  = `AI Probability: ${(p * 100).toFixed(1)}%`;
                        span.style.borderRadius = '3px';
                        span.style.padding      = '2px 0';
                        span.style.cursor       = 'help';
                        xaiSection.appendChild(span);
                    });
                }
            }

            if (typeof scanHistory !== 'undefined') {
                scanHistory.addScan('Text', `Text Snippet (${innerData.word_count || '?'} words)`, isAi, confidence);
            }
        }, 50);
    }
});
