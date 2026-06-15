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
        
        // Mock reading file
        if (file.type === "text/plain") {
            const reader = new FileReader();
            reader.onload = (e) => textInput.value = e.target.result;
            reader.readAsText(file);
        } else {
            // Mock PDF extraction
            textInput.value = `[Extracted text from ${file.name}]\n\nThe rapid advancement of artificial intelligence has brought profound changes to various sectors of society. From healthcare and finance to education and entertainment, AI systems are increasingly integrated into our daily lives. While these technologies offer unprecedented opportunities for efficiency and innovation, they also present significant ethical and societal challenges. \n\nOne of the most pressing concerns is the potential for AI-driven automation to displace human workers. Although historical technological shifts have eventually created new job categories, the speed and scale of AI disruption may outpace the ability of the workforce to adapt. Furthermore, algorithms can inadvertently perpetuate and amplify biases present in their training data, leading to discriminatory outcomes in areas such as hiring and law enforcement.\n\nTo address these issues, it is imperative that policymakers, technologists, and ethicists collaborate to establish robust regulatory frameworks. Ensuring transparency and accountability in AI development will be crucial for maximizing its benefits while mitigating its risks.`;
        }
    }

    // Analyze
    btnAnalyze.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) {
            showError("Please paste text or upload a document to analyze.");
            return;
        }

        errorAlert.classList.add('hidden');
        inputSection.style.display = 'none';
        btnAnalyze.style.display = 'none';
        loadingState.classList.remove('hidden');

        // Mock API Call delay
        await new Promise(r => setTimeout(r, 2000));

        // Process text into sentences
        // Simple regex to split by sentence
        const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
        
        let totalScore = 0;
        let htmlOutput = "";

        sentences.forEach(sentence => {
            // Assign a random fake probability for demo
            let prob = Math.random();
            // If it's the mock text, make some parts specifically fake
            if (sentence.includes("rapid advancement") || sentence.includes("opportunities for efficiency")) {
                prob = 0.85 + Math.random() * 0.1;
            } else if (sentence.includes("address these issues") || sentence.includes("collaborate to establish")) {
                prob = 0.1 + Math.random() * 0.2;
            }

            totalScore += prob;

            let heatClass = "heat-low";
            if (prob > 0.7) heatClass = "heat-high";
            else if (prob > 0.35) heatClass = "heat-med";

            htmlOutput += `<span class="${heatClass}" title="${(prob*100).toFixed(1)}% AI">${sentence}</span> `;
        });

        const avgProb = totalScore / sentences.length;
        const finalPercentage = (avgProb * 100).toFixed(1);

        heatmapContent.innerHTML = htmlOutput;
        overallScore.textContent = finalPercentage + '%';
        
        if (avgProb > 0.7) {
            classificationResult.textContent = "Likely AI-Generated";
            classificationResult.style.color = "var(--color-error)";
        } else if (avgProb < 0.3) {
            classificationResult.textContent = "Likely Human-Written";
            classificationResult.style.color = "var(--color-success)";
        } else {
            classificationResult.textContent = "Mixed Content Detected";
            classificationResult.style.color = "var(--text-primary)";
        }

        // Save to History
        if (window.saveScanToHistory) {
            window.saveScanToHistory('Document', text.substring(0, 50) + '...', avgProb > 0.5, finalPercentage + '%');
        }

        loadingState.classList.add('hidden');
        resultsSection.classList.remove('hidden');
    });

    document.getElementById('reset-btn').addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        inputSection.style.display = 'block';
        btnAnalyze.style.display = 'block';
        textInput.value = '';
        fileInput.value = '';
    });

    document.getElementById('download-btn').addEventListener('click', () => {
        const element = document.getElementById('result-card');
        const opt = {
            margin:       1,
            filename:     'AuthGuard_Document_Report.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        html2pdf().set(opt).from(element).save();
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('hidden');
    }
});
