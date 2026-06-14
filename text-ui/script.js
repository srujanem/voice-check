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
            const response = await fetch('http://localhost:5000/predict_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server error');
            }

            const data = await response.json();
            
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
        
        const isAi = data.prediction === "AI-Generated";
        const confidence = Math.round(data.confidence);
        
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

            animateCountUp(scorePercentage, confidence, 1500);
            
            const circumference = 339.292;
            const offset = circumference - (confidence / 100) * circumference;
            scoreProgress.style.strokeDashoffset = offset;

            if (probHuman) animateCountUp(probHuman, data.prob_human, 1500, 'Human: ');
            if (probAi) animateCountUp(probAi, data.prob_ai, 1500, 'AI: ');

            if (data.sentences) {
                const xaiSection = document.getElementById('xai-section');
                if (xaiSection) {
                    xaiSection.innerHTML = '<h4 style="margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 5px;"><i class="fa-solid fa-magnifying-glass"></i> Sentence Analysis</h4>';
                    data.sentences.forEach(s => {
                        const span = document.createElement('span');
                        span.textContent = s.text + ' ';
                        if (s.ai_prob >= 0.5) {
                            const alpha = (s.ai_prob - 0.5) * 2; 
                            span.style.backgroundColor = `rgba(239, 68, 68, ${alpha * 0.4})`;
                            span.style.color = document.documentElement.getAttribute('data-theme') === 'light' ? '#7f1d1d' : '#fecaca';
                        } else {
                            const alpha = (0.5 - s.ai_prob) * 2;
                            span.style.backgroundColor = `rgba(16, 185, 129, ${alpha * 0.2})`;
                        }
                        span.title = `AI Probability: ${(s.ai_prob * 100).toFixed(1)}%`;
                        span.style.borderRadius = '3px';
                        span.style.padding = '2px 0';
                        span.style.cursor = 'help';
                        xaiSection.appendChild(span);
                    });
                }
            }

            if (typeof scanHistory !== 'undefined') {
                scanHistory.addScan('Text', 'Text Snippet', isAi, confidence);
            }
        }, 50);
    }
});
