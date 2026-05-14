document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const tabUpload = document.getElementById('tab-upload');
    const tabRecord = document.getElementById('tab-record');
    const uploadArea = document.getElementById('upload-area');
    const recordArea = document.getElementById('record-area');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const recordBtn = document.getElementById('record-btn');
    const recordStatus = document.getElementById('record-status');
    const recordingTimer = document.getElementById('recording-timer');
    
    const audioPreviewContainer = document.getElementById('audio-preview-container');
    const fileNameDisplay = document.getElementById('file-name');
    const audioPlayer = document.getElementById('audio-player');
    const removeAudioBtn = document.getElementById('remove-audio');
    
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingState = document.getElementById('loading-state');
    const resultState = document.getElementById('result-state');
    const resultCard = document.getElementById('result-card');
    const resultIconFa = document.getElementById('result-icon-fa');
    const resultText = document.getElementById('result-text');
    const confidencePercentage = document.getElementById('confidence-percentage');
    const confidenceBar = document.getElementById('confidence-bar');
    const resetBtn = document.getElementById('reset-btn');
    
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const inputSection = document.getElementById('input-section');

    // --- State Variables ---
    let currentAudioFile = null;
    let currentAudioUrl = null;
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let recordInterval = null;
    let recordTime = 0;

    // --- Tab Switching Logic ---
    tabUpload.addEventListener('click', () => {
        tabUpload.classList.add('active');
        tabRecord.classList.remove('active');
        uploadArea.classList.add('active');
        recordArea.classList.remove('active');
        
        // Stop recording if active when switching tabs
        if (isRecording) stopRecording();
    });

    tabRecord.addEventListener('click', () => {
        tabRecord.classList.add('active');
        tabUpload.classList.remove('active');
        recordArea.classList.add('active');
        uploadArea.classList.remove('active');
    });

    // --- File Upload Logic ---
    // Trigger file input on click
    dropZone.addEventListener('click', () => fileInput.click());

    // Handle drag events for visual feedback
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    // Handle file drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Handle normal file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        hideError();
        
        // Validate file format
        const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/flac', 'audio/x-flac'];
        // Also check extension as fallback for some OS
        const validExtensions = ['.wav', '.mp3', '.flac'];
        const fileName = file.name.toLowerCase();
        const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

        if (!validTypes.includes(file.type) && !hasValidExtension) {
            showError('Unsupported file format. Please upload a WAV, MP3, or FLAC file.');
            return;
        }

        currentAudioFile = file;
        
        // Free memory if there was a previous URL
        if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
        currentAudioUrl = URL.createObjectURL(file);
        
        showAudioPreview(file.name, currentAudioUrl);
    }

    // --- Microphone Recording Logic ---
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
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            // Determine correct extension based on browser
            recordingExt = 'webm';
            if (mediaRecorder.mimeType && mediaRecorder.mimeType.includes('mp4')) {
                recordingExt = 'mp4';
            } else if (mediaRecorder.mimeType && mediaRecorder.mimeType.includes('ogg')) {
                recordingExt = 'ogg';
            }

            mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            });

            mediaRecorder.addEventListener('stop', () => {
                // Combine chunks into a blob
                const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' }); 
                
                if (currentAudioUrl) URL.revokeObjectURL(currentAudioUrl);
                currentAudioUrl = URL.createObjectURL(audioBlob);
                currentAudioFile = audioBlob; 
                currentAudioFile.recordedName = `recorded_audio.${recordingExt}`;
                
                showAudioPreview(`recorded_audio.${recordingExt}`, currentAudioUrl);
                
                // Release the microphone stream
                stream.getTracks().forEach(track => track.stop());
            });

            mediaRecorder.start();
            isRecording = true;
            
            // UI Updates for recording state
            recordBtn.classList.add('recording');
            recordBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
            recordStatus.textContent = 'Recording...';
            startTimer();
            hideError();

        } catch (err) {
            console.error('Error accessing microphone:', err);
            // Specific error handling based on user action
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                showError('Microphone access denied. Please allow microphone permissions in your browser.');
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                showError('No microphone found on this device.');
            } else {
                showError('Error accessing microphone: ' + err.message);
            }
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        
        isRecording = false;
        
        // Reset UI
        recordBtn.classList.remove('recording');
        recordBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
        recordStatus.textContent = 'Click to start recording';
        stopTimer();
    }

    function startTimer() {
        recordTime = 0;
        updateTimerDisplay();
        recordInterval = setInterval(() => {
            recordTime++;
            updateTimerDisplay();
        }, 1000);
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

    // --- Audio Preview Logic ---
    function showAudioPreview(filename, url) {
        fileNameDisplay.textContent = filename;
        audioPlayer.src = url;
        audioPreviewContainer.classList.remove('hidden');
        analyzeBtn.disabled = false;
    }

    removeAudioBtn.addEventListener('click', () => {
        resetInputState();
    });

    function resetInputState() {
        currentAudioFile = null;
        if (currentAudioUrl) {
            URL.revokeObjectURL(currentAudioUrl);
            currentAudioUrl = null;
        }
        audioPlayer.src = '';
        audioPreviewContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        fileInput.value = ''; 
        hideError();
    }

    // --- Analysis Logic ---
    analyzeBtn.addEventListener('click', () => {
        if (!currentAudioFile && !currentAudioUrl) {
            showError('Please upload or record an audio file first.');
            return;
        }

        startAnalysis();
    });

    async function startAnalysis() {
        // Hide inputs and analyze button
        inputSection.style.display = 'none';
        analyzeBtn.style.display = 'none';
        hideError();
        
        // Show loading state
        loadingState.classList.remove('hidden');
        resultState.classList.add('hidden');
        
        // Pause audio if it's currently playing
        audioPlayer.pause();

        try {
            const formData = new FormData();
            const filename = currentAudioFile.recordedName || currentAudioFile.name || 'recorded_audio.webm';
            formData.append('audio', currentAudioFile, filename);

            const response = await fetch('http://127.0.0.1:5000/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            const isHuman = data.prediction === "Human Voice";
            showResult(isHuman);
        } catch (err) {
            console.error('Error during analysis:', err);
            showError('An error occurred while analyzing the audio: ' + err.message);
            // Reset UI on error
            inputSection.style.display = 'block';
            analyzeBtn.style.display = 'flex';
            loadingState.classList.add('hidden');
        }
    }

    function showResult(isHuman) {
        loadingState.classList.add('hidden');
        resultState.classList.remove('hidden');

        // Reset any previous result classes
        resultCard.className = 'result-card';
        confidenceBar.style.width = '0%';
        
        // Use a tiny timeout to allow the browser to render the initial state before applying animations
        setTimeout(() => {
            if (isHuman) {
                resultCard.classList.add('human');
                resultIconFa.className = 'fa-solid fa-user';
                resultText.textContent = 'Human Voice';
            } else {
                resultCard.classList.add('ai');
                resultIconFa.className = 'fa-solid fa-robot';
                resultText.textContent = 'AI Generated Voice';
            }
            
            // Animate progress bar and set text
            confidencePercentage.textContent = 'Analysis Complete';
            confidenceBar.style.width = '100%';
        }, 50);
    }

    // --- Reset Application Logic ---
    resetBtn.addEventListener('click', () => {
        // Restore initial UI state
        inputSection.style.display = 'block';
        analyzeBtn.style.display = 'flex';
        
        resultState.classList.add('hidden');
        confidenceBar.style.width = '0%';
        
        resetInputState();
    });

    // --- Helper Functions ---
    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }

    function hideError() {
        errorAlert.classList.add('hidden');
    }

    // --- Theme Toggle Logic ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    // Check local storage for saved theme, default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    // Apply saved theme on load
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
