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
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const element = document.getElementById('result-card');
            const opt = {
                margin:       10,
                filename:     `URL_Report_${Date.now()}.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true, backgroundColor: document.documentElement.getAttribute('data-theme') === 'light' ? '#ffffff' : '#1e1e2e' },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        });
    }

    resetBtn.addEventListener('click', () => {
        urlInput.value = '';
        resultsSection.classList.add('hidden');
        btnAnalyze.style.display = 'inline-flex';
        btnAnalyze.classList.add('disabled');
        hideError();
    });

    urlInput.addEventListener('input', () => {
        if (urlInput.value.trim().length > 5) {
            btnAnalyze.classList.remove('disabled');
        } else {
            btnAnalyze.classList.add('disabled');
        }
    });

    // Handle Analyze
    btnAnalyze.addEventListener('click', async () => {
        if (btnAnalyze.classList.contains('disabled')) return;
        const url = urlInput.value.trim();
        if (!url) return;
        
        const apiKey = localStorage.getItem('api_key');
        if (!apiKey) {
            alert('Please log in to use the URL Scanner.');
            window.location.href = '../login.html';
            return;
        }

        scannerLine.classList.remove('hidden');
        hideError();
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/predict_url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server error');
            }

            const data = await response.json();
            loadingState.classList.add('hidden');
            showResults(data, url);
        } catch (error) {
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';
            showError('Analysis failed: ' + error.message);
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
        
        const isAi = data.prediction === "AI";
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
