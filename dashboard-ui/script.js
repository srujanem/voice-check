document.addEventListener('DOMContentLoaded', () => {
    // Load history from localStorage
    const historyData = JSON.parse(localStorage.getItem('voiceCheckHistory') || '[]');
    
    // Update Stat Cards
    const totalScans = historyData.length;
    document.getElementById('totalScans').textContent = totalScans;

    let aiCount = 0;
    const typeCount = { 'Voice': 0, 'Image': 0, 'Text': 0, 'Video': 0 };
    const dateCount = {};

    historyData.forEach(item => {
        if (item.isFake) aiCount++;
        typeCount[item.type] = (typeCount[item.type] || 0) + 1;
        
        const d = new Date(item.timestamp).toLocaleDateString();
        dateCount[d] = (dateCount[d] || 0) + 1;
    });

    if (totalScans > 0) {
        document.getElementById('aiDetected').textContent = Math.round((aiCount / totalScans) * 100) + '%';
        
        let maxType = '-';
        let maxVal = 0;
        for (const [type, count] of Object.entries(typeCount)) {
            if (count > maxVal) { maxVal = count; maxType = type; }
        }
        document.getElementById('mostUsedTool').textContent = maxType;
    }

    // Colors
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const textColor = isLight ? '#334155' : '#cbd5e1';
    Chart.defaults.color = textColor;
    Chart.defaults.font.family = 'Inter';

    // Chart 1: Types (Doughnut)
    const ctxType = document.getElementById('typeChart').getContext('2d');
    new Chart(ctxType, {
        type: 'doughnut',
        data: {
            labels: ['Voice', 'Image', 'Text', 'Video'],
            datasets: [{
                data: [typeCount.Voice, typeCount.Image, typeCount.Text, typeCount.Video],
                backgroundColor: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Usage by Tool Type' }
            }
        }
    });

    // Chart 2: AI vs Human (Pie)
    const ctxResult = document.getElementById('resultChart').getContext('2d');
    new Chart(ctxResult, {
        type: 'pie',
        data: {
            labels: ['Authentic (Human)', 'AI-Generated (Fake)'],
            datasets: [{
                data: [totalScans - aiCount, aiCount],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Overall Detection Results' }
            }
        }
    });

    // Chart 3: Timeline (Bar)
    const dates = Object.keys(dateCount).sort((a, b) => new Date(a) - new Date(b));
    const counts = dates.map(d => dateCount[d]);
    
    const ctxTime = document.getElementById('timelineChart').getContext('2d');
    new Chart(ctxTime, {
        type: 'bar',
        data: {
            labels: dates.length ? dates : ['No Data'],
            datasets: [{
                label: 'Scans per day',
                data: dates.length ? counts : [0],
                backgroundColor: '#06b6d4',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Activity Timeline' }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        }
    });

    // Theme toggle redraw
    document.getElementById('themeToggle').addEventListener('click', () => {
        setTimeout(() => location.reload(), 300); // Reload to redraw charts with new colors
    });

    // Populate History Table
    const tableBody = document.getElementById('historyTableBody');
    if (historyData.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 20px; color: var(--text-secondary);">No scans recorded yet.</td></tr>';
    } else {
        // Sort newest first, take top 10
        const sortedHistory = [...historyData].sort((a, b) => b.timestamp - a.timestamp).slice(0, 10);
        sortedHistory.forEach(item => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
            
            const dateStr = new Date(item.timestamp).toLocaleString();
            const color = item.isFake ? 'var(--color-error)' : 'var(--color-success)';
            const resultText = item.isFake ? 'Fake (AI)' : 'Authentic';
            
            tr.innerHTML = `
                <td style="padding: 12px 8px;">${dateStr}</td>
                <td style="padding: 12px 8px;">${item.type}</td>
                <td style="padding: 12px 8px; color: ${color};">${item.confidence || '99.9%'}</td>
                <td style="padding: 12px 8px;"><span style="background: ${color}22; color: ${color}; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px;">${resultText}</span></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Export PDF (Mock print for now)
    document.getElementById('exportPdfBtn').addEventListener('click', () => {
        window.print();
    });

    // API Key Management
    const apiKeyInput = document.getElementById('apiKeyInput');
    const toggleKeyBtn = document.getElementById('toggleKeyBtn');
    const copyKeyBtn = document.getElementById('copyKeyBtn');
    const generateKeyBtn = document.getElementById('generateKeyBtn');

    // Retrieve or generate key
    let savedKey = localStorage.getItem('authGuard_apiKey');
    if (!savedKey) {
        savedKey = 'sk_live_' + Math.random().toString(36).substr(2, 24);
        localStorage.setItem('authGuard_apiKey', savedKey);
    }
    apiKeyInput.value = savedKey;

    toggleKeyBtn.addEventListener('click', () => {
        if (apiKeyInput.type === 'password') {
            apiKeyInput.type = 'text';
            toggleKeyBtn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
        } else {
            apiKeyInput.type = 'password';
            toggleKeyBtn.innerHTML = '<i class="fa-solid fa-eye"></i>';
        }
    });

    copyKeyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(apiKeyInput.value);
        copyKeyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--color-success);"></i>';
        setTimeout(() => {
            copyKeyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
        }, 2000);
    });

    generateKeyBtn.addEventListener('click', () => {
        if(confirm("Are you sure? This will invalidate your old API key immediately.")) {
            savedKey = 'sk_live_' + Math.random().toString(36).substr(2, 24);
            localStorage.setItem('authGuard_apiKey', savedKey);
            apiKeyInput.value = savedKey;
            
            // Show toast if available, else alert
            if (window.showToast) {
                window.showToast('success', 'New API key generated successfully.');
            } else {
                alert('New API key generated successfully.');
            }
        }
    });
});
