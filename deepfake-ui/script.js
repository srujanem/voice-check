document.addEventListener('DOMContentLoaded', () => {
    // ── Element references ────────────────────────────────────────────────────
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

    // ── Drag-and-drop support ─────────────────────────────────────────────────
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

    // ── File input change ─────────────────────────────────────────────────────
    fileInput.addEventListener('change', function () {
        if (this.files && this.files.length > 0) setFile(this.files[0]);
    });

    // ── Set current file and show preview ─────────────────────────────────────
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

    // ── Remove / Reset ────────────────────────────────────────────────────────
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

    // ── Analyze ───────────────────────────────────────────────────────────────
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
            
            // Handle Heatmap Display
            if (data.heatmap) {
                const previewContainer = document.getElementById('imagePreview').parentElement;
                document.getElementById('imagePreview').style.opacity = '0.3';
                const existingHeatmap = document.getElementById('heatmap-img');
                if (existingHeatmap) existingHeatmap.remove();
                
                const heatmapImg = document.createElement('img');
                heatmapImg.id = 'heatmap-img';
                heatmapImg.src = data.heatmap;
                heatmapImg.style.position = 'absolute';
                heatmapImg.style.top = '0';
                heatmapImg.style.left = '0';
                heatmapImg.style.width = '100%';
                heatmapImg.style.height = '100%';
                heatmapImg.style.objectFit = 'contain';
                heatmapImg.style.zIndex = '5';
                heatmapImg.style.borderRadius = '8px';
                heatmapImg.style.mixBlendMode = 'screen';
                heatmapImg.style.animation = 'pulse-heat 2s infinite';
                
                if (!document.getElementById('heatmap-style')) {
                    const style = document.createElement('style');
                    style.id = 'heatmap-style';
                    style.innerHTML = '@keyframes pulse-heat { 0% { opacity: 0.8; } 50% { opacity: 1; filter: brightness(1.2); } 100% { opacity: 0.8; } }';
                    document.head.appendChild(style);
                }
                previewContainer.style.position = 'relative';
                previewContainer.appendChild(heatmapImg);
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

    // ── Count-up animation ────────────────────────────────────────────────────
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

    // ── Show results ──────────────────────────────────────────────────────────
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



