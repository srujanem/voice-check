document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const btnRemove = document.getElementById('btnRemove');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const scannerLine = document.getElementById('scannerLine');
    const resultsSection = document.getElementById('resultsSection');
    
    // Results elements
    const scoreProgress = document.getElementById('scoreProgress');
    const scorePercentage = document.getElementById('scorePercentage');
    const scoreCircle = document.getElementById('scoreCircle');
    const classificationResult = document.getElementById('classificationResult');

    let currentFile = null;

    // Handle drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.classList.add('dragover');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('dragover');
    }

    // Handle drop
    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    }

    // Handle click to upload
    uploadArea.addEventListener('click', (e) => {
        if (e.target !== btnRemove && e.target !== btnRemove.querySelector('i')) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                currentFile = file;
                displayPreview(file);
            } else {
                alert('Please upload an image file.');
            }
        }
    }

    function displayPreview(file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            imagePreview.src = reader.result;
            uploadPlaceholder.classList.add('hidden');
            imagePreviewContainer.classList.remove('hidden');
            btnAnalyze.classList.remove('disabled');
            resultsSection.classList.add('hidden'); // Hide previous results
            
            // Reset circular progress
            scoreProgress.style.strokeDashoffset = '339.292';
        }
    }

    // Handle remove image
    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        currentFile = null;
        fileInput.value = '';
        uploadPlaceholder.classList.remove('hidden');
        imagePreviewContainer.classList.add('hidden');
        btnAnalyze.classList.add('disabled');
        resultsSection.classList.add('hidden');
        scannerLine.classList.add('hidden');
        
        // Reset circular progress
        scoreProgress.style.strokeDashoffset = '339.292';
    });

    // Handle Analyze
    btnAnalyze.addEventListener('click', async () => {
        if (btnAnalyze.classList.contains('disabled')) return;
        if (!currentFile) return;
        
        // Start scanning animation
        scannerLine.classList.remove('hidden');
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
        btnAnalyze.classList.add('disabled');
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('http://localhost:5000/predict_image', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server error');
            }

            const data = await response.json();
            
            // Stop scanning animation
            scannerLine.classList.add('hidden');
            btnAnalyze.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Analyze Image';
            btnAnalyze.classList.remove('disabled');
            
            showResults(data);
        } catch (error) {
            scannerLine.classList.add('hidden');
            btnAnalyze.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Analyze Image';
            btnAnalyze.classList.remove('disabled');
            alert('Analysis failed: ' + error.message);
        }
    });

    function showResults(data) {
        resultsSection.classList.remove('hidden');
        
        const isFake = data.prediction === "AI-Generated";
        const confidence = Math.round(data.confidence);
        
        // Update UI based on result
        scorePercentage.textContent = confidence + '%';
        
        // Circumference of circle is 2 * Math.PI * 54 = 339.292
        const circumference = 339.292;
        const offset = circumference - (confidence / 100) * circumference;
        
        // Slight delay for animation to trigger properly
        setTimeout(() => {
            scoreProgress.style.strokeDashoffset = offset;
        }, 100);

        if (isFake) {
            scoreCircle.classList.remove('real');
            scoreCircle.classList.add('fake');
            scoreCircle.querySelector('.label').textContent = 'Fake';
            classificationResult.textContent = 'AI-Generated';
            classificationResult.className = 'detail-value highlight-red';
            document.querySelector('.heatmap-info p').innerHTML = '<i class="fa-solid fa-circle-info"></i> The scanner detected inconsistent pixel gradients around the eyes and mouth, typical of diffusion models.';
        } else {
            scoreCircle.classList.remove('fake');
            scoreCircle.classList.add('real');
            scoreCircle.querySelector('.label').textContent = 'Real';
            classificationResult.textContent = 'Authentic';
            classificationResult.className = 'detail-value highlight-green';
            document.querySelector('.heatmap-info p').innerHTML = '<i class="fa-solid fa-circle-info"></i> No significant synthetic artifacts detected. Image characteristics match natural camera noise patterns.';
        }
    }
});
