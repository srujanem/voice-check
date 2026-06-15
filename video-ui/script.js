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
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const element = document.getElementById('result-card');
            const opt = {
                margin:       10,
                filename:     `Video_Report_${Date.now()}.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true, backgroundColor: document.documentElement.getAttribute('data-theme') === 'light' ? '#ffffff' : '#1e1e2e' },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        });
    }

    // Handle drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

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
        
        const apiKey = localStorage.getItem('api_key');
        if (!apiKey) {
            alert('Please log in to use the Video Analysis tool.');
            window.location.href = '../login.html';
            return;
        }

        scannerLine.classList.remove('hidden');
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('video', currentFile);

        try {
            const response = await fetch('/predict_video', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${apiKey}`
                },
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server error');
            }

            const data = await response.json();
            const taskId = data.task_id;
            
            // Poll for status
            loadingState.querySelector('p').innerText = "Processing video in background...";
            
            const pollInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(`/video_status/${taskId}`);
                    if (statusRes.ok) {
                        const statusData = await statusRes.json();
                        if (statusData.status) {
                            // Still processing
                            loadingState.querySelector('p').innerText = "Analyzing frames... " + statusData.status;
                        } else {
                            // Completed, has results
                            clearInterval(pollInterval);
                            scannerLine.classList.add('hidden');
                            loadingState.classList.add('hidden');
                            loadingState.querySelector('p').innerText = "Processing..."; // reset
                            showResults(statusData);
                        }
                    } else {
                        const errData = await statusRes.json();
                        throw new Error(errData.error || "Failed polling");
                    }
                } catch (e) {
                    clearInterval(pollInterval);
                    scannerLine.classList.add('hidden');
                    loadingState.classList.add('hidden');
                    btnAnalyze.style.display = 'inline-flex';
                    alert('Background analysis failed: ' + e.message);
                }
            }, 2000);

        } catch (error) {
            scannerLine.classList.add('hidden');
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';
            alert('Upload failed: ' + error.message);
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
