document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const tabUpload     = document.getElementById('tab-upload');
    const tabRecord     = document.getElementById('tab-record');
    const uploadArea    = document.getElementById('upload-area');
    const recordArea    = document.getElementById('record-area');
    const dropZone      = document.getElementById('drop-zone');
    const fileInput     = document.getElementById('file-input');
    const recordBtn     = document.getElementById('record-btn');
    const recordStatus  = document.getElementById('record-status');
    const recordingTimer = document.getElementById('recording-timer');

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

    // --- State Variables ---
    let currentAudioFile = null;
    let currentAudioUrl  = null;
    let isRecording      = false;
    let mediaRecorder    = null;
    let audioChunks      = [];
    let recordInterval   = null;
    let recordTime       = 0;

    // --- Tab Switching ---
    tabUpload.addEventListener('click', () => {
        tabUpload.classList.add('active');
        tabRecord.classList.remove('active');
        uploadArea.classList.add('active');
        recordArea.classList.remove('active');
        if (isRecording) stopRecording();
    });

    tabRecord.addEventListener('click', () => {
        tabRecord.classList.add('active');
        tabUpload.classList.remove('active');
        recordArea.classList.add('active');
        uploadArea.classList.remove('active');
    });

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

    // --- Microphone Recording ---
    let isRequesting = false;
    let recordingExt = 'webm';

    recordBtn.addEventListener('click', async () => {
        if (isRequesting) return;
        if (!isRecording) {
            isRequesting = true;
            await startRecording();
            isRequesting = false;
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream   = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder  = new MediaRecorder(stream);
            audioChunks    = [];

            recordingExt = 'webm';
            if (mediaRecorder.mimeType && mediaRecorder.mimeType.includes('mp4'))  recordingExt = 'mp4';
            else if (mediaRecorder.mimeType && mediaRecorder.mimeType.includes('ogg')) recordingExt = 'ogg';

            mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data.size > 0) audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', () => {
                const audioBlob       = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
                if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
                currentAudioUrl       = URL.createObjectURL(audioBlob);
                currentAudioFile      = audioBlob;
                currentAudioFile.recordedName = `recorded_audio.${recordingExt}`;
                showAudioPreview(`recorded_audio.${recordingExt}`, currentAudioUrl);
                stream.getTracks().forEach(track => track.stop());
            });

            mediaRecorder.start();
            isRecording = true;
            recordBtn.classList.add('recording');
            recordBtn.innerHTML     = '<i class="fa-solid fa-stop"></i>';
            recordStatus.textContent = 'Recording...';
            startTimer();
            hideError();

        } catch (err) {
            console.error('Microphone error:', err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                showError('Microphone access denied. Please allow microphone permissions.');
            } else if (err.name === 'NotFoundError') {
                showError('No microphone found on this device.');
            } else {
                showError('Microphone error: ' + err.message);
            }
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        recordBtn.innerHTML      = '<i class="fa-solid fa-microphone"></i>';
        recordStatus.textContent = 'Click to start recording';
        stopTimer();
    }

    function startTimer() {
        recordTime = 0;
        updateTimerDisplay();
        recordInterval = setInterval(() => { recordTime++; updateTimerDisplay(); }, 1000);
    }

    function stopTimer() {
        clearInterval(recordInterval);
        recordTime = 0;
        updateTimerDisplay();
    }

    function updateTimerDisplay() {
        const mins = Math.floor(recordTime / 60).toString().padStart(2, '0');
        const secs = (recordTime % 60).toString().padStart(2, '0');
        recordingTimer.textContent = `${mins}:${secs}`;
    }

    // --- Audio Preview ---
    function showAudioPreview(filename, url) {
        fileNameDisplay.textContent = filename;
        audioPlayer.src = url;
        audioPlayer.load();
        audioPreviewContainer.classList.remove('hidden');
        analyzeBtn.disabled = false;
        document.querySelector('.tabs').style.display = 'none';
        uploadArea.style.display = 'none';
        recordArea.style.display = 'none';
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
        document.querySelector('.tabs').style.display = '';
        uploadArea.style.display = '';
        recordArea.style.display = '';
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
        resultState.classList.add('hidden');
        audioPlayer.pause();

        try {
            const formData = new FormData();
            const filename = currentAudioFile.recordedName || currentAudioFile.name || 'recorded_audio.webm';
            formData.append('audio', currentAudioFile, filename);

            const response = await fetch('http://127.0.0.1:5000/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            const isHuman = data.prediction === "Human Voice";
            showResult(isHuman, data.confidence, data.prob_human, data.prob_ai);

        } catch (err) {
            console.error('Analysis error:', err);
            showError('Error analyzing audio: ' + err.message);
            inputSection.style.display = 'block';
            analyzeBtn.style.display   = 'flex';
            loadingState.classList.add('hidden');
        }
    }

    // --- Show Result with REAL confidence ---
    function showResult(isHuman, confidence, probHuman, probAi) {
        loadingState.classList.add('hidden');
        resultState.classList.remove('hidden');

        resultCard.className   = 'result-card';
        confidenceBar.style.width = '0%';

        setTimeout(() => {
            if (isHuman) {
                resultCard.classList.add('human');
                resultIconFa.className  = 'fa-solid fa-user';
                resultText.textContent  = 'Human Voice';
            } else {
                resultCard.classList.add('ai');
                resultIconFa.className  = 'fa-solid fa-robot';
                resultText.textContent  = 'AI Generated Voice';
            }

            // ✅ Real confidence score from model
            confidencePercentage.textContent  = `${confidence}%`;
            confidenceBar.style.width         = `${confidence}%`;

            // ✅ Show both probabilities if elements exist
            if (probHumanEl) probHumanEl.textContent = `Human: ${probHuman}%`;
            if (probAiEl)    probAiEl.textContent    = `AI: ${probAi}%`;

        }, 50);
    }

    // --- Reset ---
    resetBtn.addEventListener('click', () => {
        inputSection.style.display = 'block';
        analyzeBtn.style.display   = 'flex';
        resultState.classList.add('hidden');
        confidenceBar.style.width  = '0%';
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

    // --- Theme Toggle ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon      = document.getElementById('theme-icon');
    const savedTheme     = localStorage.getItem('theme') || 'dark';

    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        themeIcon.classList.replace('fa-sun', 'fa-moon');
    }

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeIcon.classList.replace('fa-sun', 'fa-moon');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
            themeIcon.classList.replace('fa-moon', 'fa-sun');
        }
    });
});
