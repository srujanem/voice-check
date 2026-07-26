document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('fileInput');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const btnRemove = document.getElementById('btnRemove');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const scannerLine = document.getElementById('scannerLine');
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('resultsSection');
    
    // Results elements
    const scoreProgress = document.getElementById('scoreProgress');
    const scorePercentage = document.getElementById('scorePercentage');
    const resultCard = document.getElementById('result-card');
    const classificationResult = document.getElementById('classificationResult');
    const probReal = document.getElementById('prob-real');
    const probFake = document.getElementById('prob-fake');

    let currentFile = null;

    // PDF Download logic
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    dropZone.addEventListener('dragover', () => dropZone.classList.add('dragover'));
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files && files.length > 0) {
            const file = files[0];
            currentFile = file;
            displayPreview(file);
        }
    }

    function displayPreview(file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            imagePreview.src = reader.result;
            dropZone.parentElement.classList.add('hidden');
            imagePreviewContainer.classList.remove('hidden');
            btnAnalyze.classList.remove('disabled');
            btnAnalyze.disabled = false;
            resultsSection.classList.add('hidden');
            scoreProgress.style.strokeDashoffset = '339.292';
        }
    }

    // Handle remove image
    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        currentFile = null;
        fileInput.value = '';
        dropZone.parentElement.classList.remove('hidden');
        imagePreviewContainer.classList.add('hidden');
        btnAnalyze.classList.add('disabled');
        btnAnalyze.disabled = true;
        resultsSection.classList.add('hidden');
        scannerLine.classList.add('hidden');
        scoreProgress.style.strokeDashoffset = '339.292';
    });

    // Handle Analyze
    btnAnalyze.addEventListener('click', async () => {
        if (btnAnalyze.classList.contains('disabled')) return;
        if (!currentFile) return;
        
        scannerLine.classList.remove('hidden');
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('type', 'image');

        try {
            let zrokUrl = 'http://localhost:5000';
            if (zrokUrl === 'http://localhost:8000') zrokUrl = 'http://localhost:5000';
            const response = await fetch(`${zrokUrl}/api/infer`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server error');
            }

            let data = await response.json();
            
            scannerLine.classList.add('hidden');
            loadingState.classList.add('hidden');
            
            showResults(data);
        } catch (error) {
            scannerLine.classList.add('hidden');
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';
            alert('Analysis failed: ' + error.message);
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

    function showResults(data) {
        resultsSection.classList.remove('hidden');
        
        const innerData = data.analysis || data;
        const isFake = data.is_ai !== undefined ? data.is_ai : (innerData.prediction === "AI-Generated" || innerData.prediction === "AI Voice" || (innerData.prob_ai >= 50));
        
        let rawConf = data.confidence !== undefined ? data.confidence : innerData.confidence;
        if (rawConf !== undefined && rawConf <= 1 && rawConf > 0) rawConf = rawConf * 100;
        const confidence = Math.round(rawConf || 50);

        const realPct = innerData.prob_human !== undefined ? Math.round(innerData.prob_human) : (isFake ? Math.round(100 - confidence) : Math.round(confidence));
        const fakePct = innerData.prob_ai !== undefined ? Math.round(innerData.prob_ai) : (isFake ? Math.round(confidence) : Math.round(100 - confidence));
        
        resultCard.className = 'result-card';
        const icon = document.getElementById('result-icon');
        scoreProgress.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            if (!isFake) {
                resultCard.classList.add('status-authentic');
                resultCard.classList.remove('status-fake');
                classificationResult.textContent = 'Authentic Image';
                icon.className = 'fa-solid fa-user-check';
            } else {
                resultCard.classList.add('status-fake');
                resultCard.classList.remove('status-authentic');
                classificationResult.textContent = 'AI-Generated Image';
                icon.className = 'fa-solid fa-robot';
            }

            animateCountUp(scorePercentage, confidence, 1500);
            
            const circumference = 339.292;
            const offset = circumference - (confidence / 100) * circumference;
            scoreProgress.style.strokeDashoffset = offset;

            if (probReal) animateCountUp(probReal, realPct, 1500, 'Real: ');
            if (probFake) animateCountUp(probFake, fakePct, 1500, 'Fake: ');

            // ── Animate confidence chart bars ─────────────────────────────────
            const chartRealBar   = document.getElementById('chart-real-bar');
            const chartFakeBar   = document.getElementById('chart-fake-bar');
            const chartRealLabel = document.getElementById('chart-real-label');
            const chartFakeLabel = document.getElementById('chart-fake-label');
            if (chartRealBar) {
                chartRealBar.style.width = '0%';
                chartFakeBar.style.width = '0%';
                setTimeout(() => {
                    chartRealBar.style.width = realPct + '%';
                    chartFakeBar.style.width = fakePct + '%';
                    animateCountUp(chartRealLabel, realPct, 1500, '', '%');
                    animateCountUp(chartFakeLabel, fakePct, 1500, '', '%');
                }, 120);
            }

            if (typeof scanHistory !== 'undefined') {
                const fName = (typeof currentFile !== 'undefined' && currentFile) ? currentFile.name : 'Image File';
                scanHistory.addScan('Image', fName, isFake, confidence);
            }
        }, 50);
    }
});
