document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const imagePreview = document.getElementById('image-preview');
    const btnProtect = document.getElementById('btnProtect');
    const loadingState = document.getElementById('loading-state');
    const successState = document.getElementById('success-state');
    const resetBtn = document.getElementById('reset-btn');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    
    let currentFile = null;

    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }
    function hideError() { errorAlert.classList.add('hidden'); }

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = '#06b6d4'; });
    dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = '');
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '';
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
        hideError();
        if (!file.type.startsWith('image/')) {
            showError('Please upload an image file.');
            return;
        }
        currentFile = file;
        const url = URL.createObjectURL(file);
        imagePreview.src = url;
        imagePreview.classList.remove('hidden');
        dropZone.style.display = 'none';
        btnProtect.style.display = 'inline-flex';
    }

    resetBtn.addEventListener('click', () => {
        currentFile = null;
        imagePreview.src = '';
        imagePreview.classList.add('hidden');
        dropZone.style.display = 'block';
        btnProtect.style.display = 'none';
        successState.classList.add('hidden');
        fileInput.value = '';
    });

    btnProtect.addEventListener('click', async () => {
        if (!currentFile) return;
        
        const apiKey = localStorage.getItem('api_key');
        if (!apiKey) {
            alert('Please log in to use the Watermark tools.');
            window.location.href = '../login.html';
            return;
        }
        
        hideError();
        btnProtect.style.display = 'none';
        loadingState.classList.remove('hidden');

        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('/create_watermark', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${apiKey}`
                },
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server error applying watermark.');
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = `protected_${currentFile.name}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            
            loadingState.classList.add('hidden');
            successState.classList.remove('hidden');
        } catch (error) {
            loadingState.classList.add('hidden');
            btnProtect.style.display = 'inline-flex';
            showError('Watermark failed: ' + error.message);
        }
    });
});
