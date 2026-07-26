document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('fileInput');
    const videoPreviewContainer = document.getElementById('videoPreviewContainer');
    const videoPreview = document.getElementById('videoPreview');
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
    const icon = document.getElementById('result-icon');

    let currentFile = null;

    // PDF Download logic

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        if (typeof dropZone !== 'undefined') dropZone.addEventListener(eventName, preventDefaults, false);
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
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('video/')) {
                currentFile = file;
                displayPreview(file);
            } else {
                alert('Please upload a video file.');
            }
        }
    }

    function displayPreview(file) {
        const url = URL.createObjectURL(file);
        videoPreview.src = url;
        dropZone.parentElement.classList.add('hidden');
        videoPreviewContainer.classList.remove('hidden');
        btnAnalyze.classList.remove('disabled');
        btnAnalyze.disabled = false;
        resultsSection.classList.add('hidden');
        scoreProgress.style.strokeDashoffset = '339.292';
    }

    // Handle remove video
    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        currentFile = null;
        fileInput.value = '';
        if (videoPreview.src) {
            URL.revokeObjectURL(videoPreview.src);
            videoPreview.src = '';
        }
        dropZone.parentElement.classList.remove('hidden');
        videoPreviewContainer.classList.add('hidden');
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
        formData.append('type', 'video');

        try {
            const zrokUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            if (zrokUrl === 'http://localhost:8000') zrokUrl = 'http://localhost:5000';
            const response = await fetch(`${zrokUrl}/api/infer`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok && response.status !== 202) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Server error (${response.status})`);
            }

            let data = await response.json();
            
            // Check if task is async (video_routes returns task_id)
            const taskId = data.task_id || (data.analysis && data.analysis.task_id);
            if (taskId) {
                let attempts = 0;
                while (attempts < 30) {
                    await new Promise(r => setTimeout(r, 2000));
                    attempts++;
                    const statusRes = await fetch(`${zrokUrl}/video_status/${taskId}`);
                    if (statusRes.ok) {
                        const statusData = await statusRes.json();
                        if (statusData.prediction) {
                            data = statusData;
                            break;
                        } else if (statusData.status === 'FAILED') {
                            throw new Error(statusData.error || 'Video task failed');
                        }
                    }
                }
            }
            
            const innerData = data.analysis || data;
            const isFake = data.is_ai !== undefined ? data.is_ai : (innerData.prediction === "AI-Generated" || innerData.prediction === "AI Voice" || (innerData.prob_ai >= 50));
            
            let rawConf = data.confidence !== undefined ? data.confidence : innerData.confidence;
            if (rawConf !== undefined && rawConf <= 1 && rawConf > 0) rawConf = rawConf * 100;
            const confidence = Math.round(rawConf || 50);

            const realPct = innerData.prob_human !== undefined ? Math.round(innerData.prob_human) : (isFake ? Math.round(100 - confidence) : Math.round(confidence));
            const fakePct = innerData.prob_ai !== undefined ? Math.round(innerData.prob_ai) : (isFake ? Math.round(confidence) : Math.round(100 - confidence));

            const mapped = {
                prediction: isFake ? "AI-Generated" : "Authentic",
                confidence: confidence,
                prob_ai: fakePct,
                prob_human: realPct,
                is_ai: isFake
            };
            
            scannerLine.classList.add('hidden');
            loadingState.classList.add('hidden');
            showResults(mapped);

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
        
        const isFake = data.prediction === "AI-Generated";
        const confidence = Math.round(data.confidence);
        
        resultCard.className = 'result-card';
        scoreProgress.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            if (!isFake) {
                resultCard.classList.add('status-authentic');
                resultCard.classList.remove('status-fake');
                classificationResult.textContent = 'Authentic Video';
                icon.className = 'fa-solid fa-user-check';
            } else {
                resultCard.classList.add('status-fake');
                resultCard.classList.remove('status-authentic');
                classificationResult.textContent = 'AI-Generated Video';
                icon.className = 'fa-solid fa-robot';
            }

            animateCountUp(scorePercentage, confidence, 1500);
            
            const circumference = 339.292;
            const offset = circumference - (confidence / 100) * circumference;
            scoreProgress.style.strokeDashoffset = offset;

            if (probReal) animateCountUp(probReal, data.prob_human, 1500, 'Real: ');
            if (probFake) animateCountUp(probFake, data.prob_ai, 1500, 'Fake: ');

            if (typeof scanHistory !== 'undefined') {
                const fName = currentFile ? currentFile.name : 'Video File';
                scanHistory.addScan('Video', fName, isFake, confidence);
            }
        }, 50);
    }
});
