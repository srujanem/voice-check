document.addEventListener('DOMContentLoaded', () => {
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

    // Handle Reset
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            currentFile = null;
            if (fileInput) fileInput.value = '';
            
            uploadArea.classList.remove('hidden');
            fileNameDisplay.textContent = '';
            
            btnAnalyze.classList.add('disabled');
            btnAnalyze.disabled = true;
            resultsSection.classList.add('hidden');
        });
    }

    // PDF Download logic
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const element = document.getElementById('result-card');
            const opt = {
                margin:       10,
                filename:     `Voice_Report_${Date.now()}.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true, backgroundColor: document.documentElement.getAttribute('data-theme') === 'light' ? '#ffffff' : '#1e1e2e' },
                jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            html2pdf().set(opt).from(element).save();
        });
    }

    // --- State Variables ---
    let currentAudioFile = null;
    let currentAudioUrl  = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;

    // --- Recording Logic ---
    const recordBtn = document.getElementById('record-btn');
    const micIcon = document.getElementById('mic-icon');
    const recordText = document.getElementById('record-text');
    const recordSubtext = document.getElementById('record-subtext');

    if (recordBtn) {
        recordBtn.addEventListener('click', async () => {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = e => {
                        if (e.data.size > 0) audioChunks.push(e.data);
                    };

                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const file = new File([audioBlob], `Recording_${Date.now()}.webm`, { type: 'audio/webm' });
                        currentAudioFile = file;
                        if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
                        currentAudioUrl = URL.createObjectURL(file);
                        showAudioPreview(file.name, currentAudioUrl);
                        
                        // Reset UI
                        isRecording = false;
                        micIcon.className = 'fa-solid fa-microphone upload-icon';
                        micIcon.style.color = 'var(--accent-cyan)';
                        recordText.textContent = 'Record Mic';
                        recordSubtext.textContent = 'Click to start';
                        
                        // Stop all tracks to release mic
                        stream.getTracks().forEach(track => track.stop());
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    
                    // Update UI to show recording state
                    micIcon.className = 'fa-solid fa-circle-dot upload-icon fa-fade';
                    micIcon.style.color = '#ef4444';
                    recordText.textContent = 'Recording...';
                    recordSubtext.textContent = 'Click to stop';
                    
                } catch (err) {
                    alert('Microphone access denied or not available.');
                }
            } else {
                mediaRecorder.stop();
            }
        });
    }

    // --- File Upload ---
    dropZone.addEventListener('click', () => fileInput.click());

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



    // --- Audio Preview ---
    function showAudioPreview(filename, url) {
        fileNameDisplay.textContent = filename;
        audioPlayer.src = url;
        audioPlayer.load();
        audioPreviewContainer.classList.remove('hidden');
        analyzeBtn.disabled = false;
        uploadArea.style.display = 'none';
    }

    removeAudioBtn.addEventListener('click', resetInputState);

    function resetInputState() {
        currentAudioFile = null;
        if (currentAudioUrl) { URL.revokeObjectURL(currentAudioUrl); currentAudioUrl = null; }
        audioPlayer.src = '';
        audioPreviewContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        fileInput.value = '';
        hideError();
        uploadArea.style.display = '';
    }

    // --- Analysis ---
    analyzeBtn.addEventListener('click', () => {
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
        const apiKey = localStorage.getItem('api_key');
        if (!apiKey) {
            alert('Please log in to use the Voice Analysis tool.');
            window.location.href = '../login.html';
            return;
        }

        scannerLine.classList.remove('hidden');
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        const filename = currentAudioFile.recordedName || currentAudioFile.name || 'recorded_audio.webm';
        formData.append('audio', currentAudioFile, filename);

        try {
            const response = await fetch('http://localhost:5000/predict_voice', {
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
            if (data.error) throw new Error(data.error);

            const isHuman = data.prediction === "Human";
            showResult(isHuman, data.confidence, data.prob_human, data.prob_ai);

        } catch (err) {
            console.error('Analysis error:', err);
            showError('Error analyzing audio: ' + err.message);
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

        resultCard.className   = 'result-card';
        const ring = document.getElementById('confidence-bar-circle');
        const icon = document.getElementById('result-icon');
        ring.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            if (isHuman) {
                resultCard.classList.add('status-authentic');
                resultCard.classList.remove('status-fake');
                resultText.textContent  = 'Human Voice';
                icon.className = 'fa-solid fa-user-check';
            } else {
                resultCard.classList.add('status-fake');
                resultCard.classList.remove('status-authentic');
                resultText.textContent  = 'AI Generated Voice';
                icon.className = 'fa-solid fa-robot';
            }

            animateCountUp(confidencePercentage, confidence, 1500);
            
            const circumference = 339.292;
            const offset = circumference - (confidence / 100) * circumference;
            ring.style.strokeDashoffset = offset;

            if (probHumanEl) animateCountUp(probHumanEl, probHuman, 1500, 'Human: ');
            if (probAiEl)    animateCountUp(probAiEl, probAi, 1500, 'AI: ');

            if (typeof scanHistory !== 'undefined') {
                const fName = (typeof currentFile !== 'undefined' && currentFile) ? currentFile.name : 'Audio File';
                scanHistory.addScan('Voice', fName, !isHuman, confidence);
            }

        }, 50);
    }

    // --- Reset ---
    resetBtn.addEventListener('click', () => {
        inputSection.style.display = 'block';
        analyzeBtn.style.display   = 'flex';
        resultState.classList.add('hidden');
        const ring = document.getElementById('confidence-bar-circle');
        if (ring) ring.style.strokeDashoffset = '339.292';
        resetInputState();
    });

    // --- Helpers ---
    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }

    function hideError() {
        errorAlert.classList.add('hidden');
    }

});
