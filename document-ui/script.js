document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const textInput = document.getElementById('textInput');
    const dropZone = document.getElementById('drop-zone');
    const btnAnalyze = document.getElementById('btnAnalyze');
    
    const inputSection = document.getElementById('input-section');
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('resultsSection');
    
    const classificationResult = document.getElementById('classificationResult');
    const overallScore = document.getElementById('overallScore');
    const heatmapContent = document.getElementById('heatmapContent');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');

    let selectedFile = null;

    // Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.style.borderColor = 'var(--accent-cyan)', false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.style.borderColor = 'var(--border-color)', false);
    });

    dropZone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        handleFile(file);
    }, false);

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        if (!file) return;
        selectedFile = file;
        textInput.value = `[Document Attached: ${file.name}]\nReady for analysis.`;
    }

    // Analyze
    btnAnalyze.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!selectedFile && !text) {
            showError("Please paste text or upload a document to analyze.");
            return;
        }

        errorAlert.classList.add('hidden');
        heatmapContent.innerHTML = '';
        inputSection.style.display = 'none';
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');

        try {
            let backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';
            const formData = new FormData();
            formData.append('type', 'text');
            
            if (selectedFile) {
                formData.append('file', selectedFile);
            } else {
                formData.append('file', new Blob([text], { type: 'text/plain' }), 'text.txt');
            }

            const response = await fetch(`${backendUrl}/api/infer`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || `Server error (${response.status})`);
            }

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            loadingState.classList.add('hidden');
            showResults(data);

        } catch (error) {
            loadingState.classList.add('hidden');
            inputSection.style.display = 'block';
            btnAnalyze.style.display = 'block';
            showError('Analysis failed: ' + error.message);
        }
    });

    function showResults(data) {
        let innerData = data.analysis || data;
        
        const isAi = innerData.prediction === 'AI-Generated' || innerData.prediction === 'ai' || !!innerData.is_ai || !!data.is_ai;
        let aiProb = innerData.prob_ai ?? data.prob_ai;
        let conf = innerData.confidence ?? data.confidence;
        
        if (aiProb === undefined) aiProb = isAi ? 85 : 15;
        if (conf === undefined) conf = 85;

        const finalPercentage = (aiProb).toFixed(1);
        overallScore.textContent = finalPercentage + '%';
        
        if (aiProb > 70) {
            classificationResult.textContent = "Likely AI-Generated";
            classificationResult.style.color = "var(--color-error)";
        } else if (aiProb < 30) {
            classificationResult.textContent = "Likely Human-Written";
            classificationResult.style.color = "var(--color-success)";
        } else {
            classificationResult.textContent = "Mixed Content Detected";
            classificationResult.style.color = "var(--text-primary)";
        }

        // Sentence-level highlighting if provided by backend
        if (innerData.sentences && innerData.sentences.length) {
            innerData.sentences.forEach(s => {
                const p = Number(s.ai_prob);
                let heatClass = "heat-low";
                if (p > 0.7) heatClass = "heat-high";
                else if (p > 0.4) heatClass = "heat-med";
                
                const span = document.createElement('span');
                span.className = heatClass;
                span.title = `${(p*100).toFixed(1)}% AI`;
                span.textContent = s.text + ' ';
                heatmapContent.appendChild(span);
            });
        } else {
            const p = document.createElement('p');
            p.textContent = "Sentence level highlighting is not available for this document.";
            heatmapContent.appendChild(p);
        }

        if (typeof scanHistory !== 'undefined') {
            const previewText = selectedFile ? selectedFile.name : (textInput.value.substring(0, 50) + '...');
            scanHistory.addScan('Document', previewText, isAi, conf);
        }

        resultsSection.classList.remove('hidden');
    }

    document.getElementById('reset-btn').addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        inputSection.style.display = 'block';
        btnAnalyze.style.display = 'block';
        textInput.value = '';
        fileInput.value = '';
        selectedFile = null;
    });

    

    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }
});
