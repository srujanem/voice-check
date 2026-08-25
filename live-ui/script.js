document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const webcam = document.getElementById('webcam');
    const preStartOverlay = document.getElementById('preStartOverlay');
    const hudOverlay = document.getElementById('hudOverlay');
    const captureCanvas = document.getElementById('captureCanvas');
    const hudTimer = document.getElementById('hudTimer');
    const hudVisualRes = document.getElementById('hudVisualRes');
    const hudProb = document.getElementById('hudProb');
    const trackingBox = document.getElementById('trackingBox');

    let stream = null;
    let scanInterval = null;
    let timerInterval = null;
    let secondsElapsed = 0;

    startBtn.addEventListener('click', async () => {
        try {
            // Request camera and microphone access
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            webcam.srcObject = stream;
            webcam.style.display = 'block';
            preStartOverlay.style.display = 'none';
            hudOverlay.style.display = 'flex';
            stopBtn.style.display = 'inline-flex';

            // Start timer
            secondsElapsed = 0;
            timerInterval = setInterval(() => {
                secondsElapsed++;
                const hrs = String(Math.floor(secondsElapsed / 3600)).padStart(2, '0');
                const mins = String(Math.floor((secondsElapsed % 3600) / 60)).padStart(2, '0');
                const secs = String(secondsElapsed % 60).padStart(2, '0');
                hudTimer.textContent = `${hrs}:${mins}:${secs}`;
            }, 1000);

            // Start scanning interval (every 3 seconds)
            scanInterval = setInterval(captureAndScan, 3000);
            
        } catch (err) {
            alert('Camera access denied or unavailable. Please grant permissions.');
            console.error(err);
        }
    });

    stopBtn.addEventListener('click', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        clearInterval(scanInterval);
        clearInterval(timerInterval);
        
        webcam.style.display = 'none';
        preStartOverlay.style.display = 'flex';
        hudOverlay.style.display = 'none';
        stopBtn.style.display = 'none';
        
        // Reset HUD
        trackingBox.className = 'tracking-box';
        hudVisualRes.textContent = 'Waiting...';
        hudVisualRes.style.color = 'var(--accent-cyan)';
        hudProb.textContent = '0%';
        hudProb.style.color = 'var(--accent-cyan)';
    });

    async function captureAndScan() {
        if (!stream) return;
        
        // Visual indicator that scanning is happening
        trackingBox.classList.add('scanning');
        
        // Setup canvas to match video dimensions
        const ctx = captureCanvas.getContext('2d');
        captureCanvas.width = webcam.videoWidth;
        captureCanvas.height = webcam.videoHeight;
        
        // Draw current video frame to canvas
        ctx.drawImage(webcam, 0, 0, captureCanvas.width, captureCanvas.height);
        
        // Convert canvas to blob (JPEG)
        captureCanvas.toBlob(async (blob) => {
            const formData = new FormData();
            // Use 'image' as the key to match /predict_image requirements
            formData.append('image', blob, 'live_frame.jpg');

            try {
                // Get auth token if user is logged in
                const token = localStorage.getItem('authguard_token');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const response = await fetch(`${window.API_BASE_URL}/predict_image`, {
                    method: 'POST',
                    headers: headers,
                    body: formData
                });

                if (!response.ok) throw new Error('API Error');

                const data = await response.json();
                updateHUD(data);
                
            } catch (err) {
                console.error("Frame analysis failed:", err);
                hudVisualRes.textContent = "Network Error";
            } finally {
                setTimeout(() => trackingBox.classList.remove('scanning'), 500);
            }
        }, 'image/jpeg', 0.8);
    }

    function updateHUD(data) {
        // Based on the standard API response structure
        const isFake = data.prediction && data.prediction.includes('AI');
        const prob = Math.round(data.prob_ai || 0);

        hudProb.textContent = `${prob}%`;
        
        if (isFake) {
            hudVisualRes.textContent = "SYNTHETIC DETECTED";
            hudVisualRes.style.color = "var(--accent-red)";
            hudProb.style.color = "var(--accent-red)";
            trackingBox.className = "tracking-box fake";
        } else {
            hudVisualRes.textContent = "AUTHENTIC";
            hudVisualRes.style.color = "var(--accent-green)";
            hudProb.style.color = "var(--accent-green)";
            trackingBox.className = "tracking-box real";
        }
    }
});
