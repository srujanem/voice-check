document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('resultsSection');
    const resetBtn = document.getElementById('reset-btn');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    
    // Results elements
    const scoreProgress = document.getElementById('scoreProgress');
    const scorePercentage = document.getElementById('scorePercentage');
    const resultCard = document.getElementById('result-card');
    const classificationResult = document.getElementById('classificationResult');
    const probHuman = document.getElementById('prob-human');
    const probAi = document.getElementById('prob-ai');
    const icon = document.getElementById('result-icon');
    const previewSection = document.getElementById('preview-section');

    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }

    function hideError() {
        errorAlert.classList.add('hidden');
    }

    // PDF Download logic
    });

    urlInput.addEventListener('input', () => {
        if (urlInput.value.trim().length > 5) {
            btnAnalyze.classList.remove('disabled');
            btnAnalyze.disabled = false;
        } else {
            btnAnalyze.classList.add('disabled');
            btnAnalyze.disabled = true;
        }
    });

    // Handle Analyze
    btnAnalyze.addEventListener('click', async () => {
        if (btnAnalyze.classList.contains('disabled')) return;
        const url = urlInput.value.trim();
        if (!url) return;

        hideError();
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');

        // Auto-detect type from URL extension
        const urlLower = url.toLowerCase();
        let scanType = 'image';
        if (urlLower.match(/\.(mp3|wav|flac|ogg|m4a)(\?|$)/)) scanType = 'voice';
        else if (urlLower.match(/\.(mp4|webm|mov|avi)(\?|$)/)) scanType = 'video';

        try {
            const response = await fetch(`${backendUrl}/api/scan-url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, type: scanType })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Server error (${response.status})`);
            }

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            // Map new API response to old showResults format
            const mapped = {
                prediction:  data.is_ai ? 'AI-Generated' : 'Authentic',
                confidence:  Math.round(data.confidence * 100),
                prob_ai:     data.prob_ai    || Math.round((data.is_ai ? data.confidence : 1 - data.confidence) * 100),
                prob_human:  data.prob_human || Math.round((data.is_ai ? 1 - data.confidence : data.confidence) * 100),
            };

            loadingState.classList.add('hidden');
            showResults(mapped, url);
        } catch (error) {
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';
            let msg = error.message;
            if (msg.includes('fetch') || msg.includes('NetworkError')) {
                msg = 'Cannot reach server. Make sure the Node server is running.';
            }
            showError('Analysis failed: ' + msg);
        }
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

    function showResults(data, url) {
        resultsSection.classList.remove('hidden');
        
        const isAi = data.prediction === "AI-Generated";
        const confidence = Math.round(data.confidence);
        
        resultCard.className = 'result-card';
        scoreProgress.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            if (!isAi) {
                resultCard.classList.add('status-authentic');
                resultCard.classList.remove('status-fake');
                classificationResult.textContent = 'Human Written Content';
                icon.className = 'fa-solid fa-user-check';
            } else {
                resultCard.classList.add('status-fake');
                resultCard.classList.remove('status-authentic');
                classificationResult.textContent = 'AI-Generated Content';
                icon.className = 'fa-solid fa-robot';
            }

            animateCountUp(scorePercentage, confidence, 1500);
            
            const circumference = 339.292;
            const offset = circumference - (confidence / 100) * circumference;
            scoreProgress.style.strokeDashoffset = offset;

            if (probHuman) animateCountUp(probHuman, data.prob_human, 1500, 'Human: ');
            if (probAi) animateCountUp(probAi, data.prob_ai, 1500, 'AI: ');

            if (data.extracted_text_preview) {
                previewSection.textContent = '"' + data.extracted_text_preview + '"';
            }

            if (typeof scanHistory !== 'undefined') {
                try {
                    const hostname = new URL(url).hostname;
                    scanHistory.addScan('Text', hostname, isAi, confidence);
                } catch(e) {
                    scanHistory.addScan('Text', 'URL Scan', isAi, confidence);
                }
            }
        }, 50);
    }
});
