document.addEventListener('DOMContentLoaded', () => {
    // â”€â”€ Element references â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    const uploadArea           = document.getElementById('upload-area');
    const dropZone             = document.getElementById('drop-zone');
    const fileInput            = document.getElementById('fileInput');
    const imagePreviewContainer= document.getElementById('imagePreviewContainer');
    const imagePreview         = document.getElementById('imagePreview');
    const btnRemove            = document.getElementById('btnRemove');
    const btnAnalyze           = document.getElementById('btnAnalyze');
    const scannerLine          = document.getElementById('scannerLine');
    const loadingState         = document.getElementById('loading-state');
    const resultsSection       = document.getElementById('resultsSection');
    const scoreProgress        = document.getElementById('scoreProgress');
    const scorePercentage      = document.getElementById('scorePercentage');
    const resultCard           = document.getElementById('result-card');
    const classificationResult = document.getElementById('classificationResult');
    const probReal             = document.getElementById('prob-real');
    const probFake             = document.getElementById('prob-fake');

    let currentFile = null;

    // â”€â”€ Drag-and-drop support â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt =>
        dropZone.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); }, false)
    );
    dropZone.addEventListener('dragover',  () => dropZone.classList.add('dragover'));
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files && files.length > 0) setFile(files[0]);
    });

    // â”€â”€ File input change â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    fileInput.addEventListener('change', function () {
        if (this.files && this.files.length > 0) setFile(this.files[0]);
    });

    // â”€â”€ Set current file and show preview â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    function setFile(file) {
        currentFile = file;
        const reader = new FileReader();
        reader.onloadend = function () {
            imagePreview.src = reader.result;
            uploadArea.classList.add('hidden');
            imagePreviewContainer.classList.remove('hidden');
            btnAnalyze.classList.remove('disabled');
            btnAnalyze.disabled = false;
            resultsSection.classList.add('hidden');
            if (scoreProgress) scoreProgress.style.strokeDashoffset = '339.292';
        };
        reader.readAsDataURL(file);
    }

    // â”€â”€ Remove / Reset â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if (btnRemove) {
        btnRemove.addEventListener('click', e => {
            e.stopPropagation();
            currentFile = null;
            fileInput.value = '';
            uploadArea.classList.remove('hidden');
            imagePreviewContainer.classList.add('hidden');
            btnAnalyze.classList.add('disabled');
            btnAnalyze.disabled = true;
            resultsSection.classList.add('hidden');
            if (scannerLine) scannerLine.classList.add('hidden');
            if (scoreProgress) scoreProgress.style.strokeDashoffset = '339.292';
        });
    }

    // â”€â”€ Analyze â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    btnAnalyze.addEventListener('click', async () => {
        if (window.checkScanGate && !window.checkScanGate()) return;
        if (btnAnalyze.disabled || !currentFile) return;

        if (scannerLine)  scannerLine.classList.remove('hidden');
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('type', 'image');

        try {
            // Use the server-config URL discovery (window.AUTHGUARD_BACKEND_URL),
            // then fall back to localhost:5000
            let backendUrl = (window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';

            const response = await fetch(`${backendUrl}/api/infer`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let errMsg = 'Server error ' + response.status;
                try { const e = await response.json(); errMsg = e.error || errMsg; } catch (_) {}
                throw new Error(errMsg);
            }

            const data = await response.json();

            if (scannerLine)  scannerLine.classList.add('hidden');
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';

            if(window.activeHudInterval) clearInterval(window.activeHudInterval);
            const cyberOverlay = document.getElementById('cyber-scanner-overlay');
            if(cyberOverlay) {
                const hudPct = document.getElementById('hud-pct');
                const hudStatus = document.getElementById('hud-status');
                if(hudPct) hudPct.innerText = "100";
                if(hudStatus) hudStatus.innerText = "ANALYSIS COMPLETE";
                setTimeout(() => { cyberOverlay.classList.add('hidden'); }, 600);
            }
            
            // Handle Interactive Forensic Split-Screen Slider
            if (data.heatmap) {
                const previewWrapper = document.querySelector('.preview-image-wrapper');
                if (previewWrapper) {
                    const existingSplit = document.getElementById('forensic-split-container');
                    if (existingSplit) existingSplit.remove();

                    const splitContainer = document.createElement('div');
                    splitContainer.id = 'forensic-split-container';
                    splitContainer.style.cssText = 'position:relative;width:100%;height:100%;overflow:hidden;border-radius:14px;user-select:none;touch-action:none;';

                    const baseImg = document.getElementById('imagePreview');
                    baseImg.style.display = 'block';
                    baseImg.style.opacity = '1';

                    const overlayLayer = document.createElement('div');
                    overlayLayer.id = 'split-overlay-layer';
                    overlayLayer.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;overflow:hidden;clip-path:polygon(0 0, 50% 0, 50% 100%, 0 100%);pointer-events:none;';

                    const heatmapImg = document.createElement('img');
                    heatmapImg.src = data.heatmap;
                    heatmapImg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;mix-blend-mode:screen;';
                    overlayLayer.appendChild(heatmapImg);

                    // Draggable Divider Line & Handle
                    const divider = document.createElement('div');
                    divider.id = 'split-divider';
                    divider.style.cssText = 'position:absolute;top:0;bottom:0;left:50%;width:3px;background:linear-gradient(180deg,#06b6d4,#8b5cf6);box-shadow:0 0 12px #06b6d4;cursor:ew-resize;z-index:20;display:flex;align-items:center;justify-content:center;';

                    const handle = document.createElement('div');
                    handle.style.cssText = 'width:32px;height:32px;border-radius:50%;background:rgba(10,11,20,0.9);border:2px solid #06b6d4;box-shadow:0 0 15px rgba(6,182,212,0.8);display:flex;align-items:center;justify-content:center;color:#06b6d4;font-size:12px;';
                    handle.innerHTML = '<i class="fa-solid fa-arrows-left-right"></i>';
                    divider.appendChild(handle);

                    // Badge labels
                    const badgeLeft = document.createElement('div');
                    badgeLeft.style.cssText = 'position:absolute;top:12px;left:14px;background:rgba(6,182,212,0.25);border:1px solid #06b6d4;color:#a5f3fc;font-family:var(--font-mono);font-size:10px;padding:4px 8px;border-radius:6px;backdrop-filter:blur(8px);z-index:25;pointer-events:none;';
                    badgeLeft.innerText = 'â—€ FORENSIC SCAN';

                    const badgeRight = document.createElement('div');
                    badgeRight.style.cssText = 'position:absolute;top:12px;right:14px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);color:#f1f5f9;font-family:var(--font-mono);font-size:10px;padding:4px 8px;border-radius:6px;backdrop-filter:blur(8px);z-index:25;pointer-events:none;';
                    badgeRight.innerText = 'ORIGINAL â–¶';

                    previewWrapper.appendChild(overlayLayer);
                    previewWrapper.appendChild(divider);
                    previewWrapper.appendChild(badgeLeft);
                    previewWrapper.appendChild(badgeRight);

                    let isDragging = false;
                    const updateSplit = (clientX) => {
                        const rect = previewWrapper.getBoundingClientRect();
                        let pos = ((clientX - rect.left) / rect.width) * 100;
                        pos = Math.max(0, Math.min(100, pos));
                        overlayLayer.style.clipPath = `polygon(0 0, ${pos}% 0, ${pos}% 100%, 0 100%)`;
                        divider.style.left = `${pos}%`;
                    };

                    const onMove = (e) => {
                        if (!isDragging) return;
                        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                        updateSplit(clientX);
                    };

                    const onUp = () => { isDragging = false; window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); window.removeEventListener('touchmove', onMove); window.removeEventListener('touchend', onUp); };

                    divider.addEventListener('mousedown', () => { isDragging = true; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp); });
                    divider.addEventListener('touchstart', () => { isDragging = true; window.addEventListener('touchmove', onMove); window.addEventListener('touchend', onUp); });
                    previewWrapper.addEventListener('click', (e) => updateSplit(e.clientX));
                }
            }

            showResults(data);

        } catch (error) {
            if(window.activeHudInterval) clearInterval(window.activeHudInterval);
            const cyberOverlay = document.getElementById('cyber-scanner-overlay');
            if(cyberOverlay) cyberOverlay.classList.add('hidden');
            if (scannerLine)  scannerLine.classList.add('hidden');
            loadingState.classList.add('hidden');
            btnAnalyze.style.display = 'inline-flex';
            alert('Analysis failed: ' + error.message);
        }
    });

    // â”€â”€ Count-up animation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    function animateCountUp(element, target, duration, prefix = '', suffix = '%') {
        if (!element) return;
        let start = 0;
        const targetNum = parseFloat(target);
        if (isNaN(targetNum)) { element.textContent = prefix + target + suffix; return; }
        const increment = targetNum / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= targetNum) { start = targetNum; clearInterval(timer); }
            element.textContent = prefix + start.toFixed(1) + suffix;
        }, 16);
    }

    // â”€â”€ Show results â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    function showResults(data) {
        resultsSection.classList.remove('hidden');

        const inner     = data.analysis || data;
        const isFake    = data.is_ai !== undefined
            ? data.is_ai
            : (String(inner.prediction).toLowerCase().includes('ai') || String(inner.prediction).toLowerCase().includes('fake'));

        let rawConf = data.confidence !== undefined ? data.confidence : inner.confidence;
        if (rawConf !== undefined && rawConf <= 1 && rawConf > 0) rawConf = rawConf * 100;
        const confidence = Math.round(rawConf || 50);

        const realPct = inner.prob_human !== undefined
            ? Math.round(inner.prob_human)
            : (isFake ? Math.round(100 - confidence) : Math.round(confidence));
        const fakePct = inner.prob_ai !== undefined
            ? Math.round(inner.prob_ai)
            : (isFake ? Math.round(confidence) : Math.round(100 - confidence));

        if (resultCard) resultCard.className = 'result-card';
        if (scoreProgress) scoreProgress.style.strokeDashoffset = '339.292';

        setTimeout(() => {
            const icon = document.getElementById('result-icon');
            if (!isFake) {
                if (resultCard)           resultCard.classList.add('status-authentic');
                if (classificationResult) classificationResult.textContent = 'Human Image';
                if (icon)                 icon.className = 'fa-solid fa-user-check';
            } else {
                if (resultCard)           resultCard.classList.add('status-fake');
                if (classificationResult) classificationResult.textContent = 'AI-Generated Image';
                if (icon)                 icon.className = 'fa-solid fa-robot';
            }

            animateCountUp(scorePercentage, confidence, 1500);

            if (scoreProgress) {
                const circumference = 339.292;
                scoreProgress.style.strokeDashoffset = circumference - (confidence / 100) * circumference;
            }

            animateCountUp(probReal, realPct, 1500, 'Real: ');
            animateCountUp(probFake, fakePct, 1500, 'Fake: ');

            const chartRealBar   = document.getElementById('chart-real-bar');
            const chartFakeBar   = document.getElementById('chart-fake-bar');
            const chartRealLabel = document.getElementById('chart-real-label');
            const chartFakeLabel = document.getElementById('chart-fake-label');
            if (chartRealBar) {
                chartRealBar.style.width = '0%';
                chartFakeBar.style.width = '0%';
                setTimeout(() => {
                    chartRealBar.style.width  = realPct + '%';
                    chartFakeBar.style.width  = fakePct + '%';
                    animateCountUp(chartRealLabel, realPct, 1500, '', '%');
                    animateCountUp(chartFakeLabel, fakePct, 1500, '', '%');
                }, 120);
            }

            if (typeof scanHistory !== 'undefined' && scanHistory) {
                const fName = currentFile ? currentFile.name : 'Image File';
                scanHistory.addScan('Image', fName, isFake, confidence);
            }
        }, 50);
    }
});



