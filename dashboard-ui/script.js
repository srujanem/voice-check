document.addEventListener('DOMContentLoaded', () => {
    // Load history from localStorage (key matches history.js STORAGE_KEY)
    const historyData = JSON.parse(localStorage.getItem('ai_detection_history') || '[]');
    
    // Update Stat Cards
    const totalScans = historyData.length;
    document.getElementById('totalScans').textContent = totalScans;

    let aiCount = 0;
    const typeCount = { 'Voice': 0, 'Image': 0, 'Text': 0, 'Video': 0 };
    const dateCount = {};

    historyData.forEach(item => {
        if (item.isAi) aiCount++;  // history.js stores 'isAi', not 'isFake'
        typeCount[item.type] = (typeCount[item.type] || 0) + 1;
        
        // history.js stores 'id' as a timestamp number and 'date' as a locale string
        const d = new Date(item.id).toLocaleDateString();
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
        // Sort newest first (id = Date.now()), take top 10
        const sortedHistory = [...historyData].sort((a, b) => b.id - a.id).slice(0, 10);
        sortedHistory.forEach(item => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';

            // history.js stores 'date' as a pre-formatted locale string, 'isAi' (not isFake)
            const dateStr = item.date || new Date(item.id).toLocaleString();
            const color = item.isAi ? 'var(--color-error)' : 'var(--color-success)';
            const resultText = item.isAi ? 'Fake (AI)' : 'Authentic';
            const confidenceText = (item.confidence !== undefined && item.confidence !== null) ? item.confidence + '%' : '--';

            // Use textContent for all user-data fields to prevent XSS
            const tdDate = document.createElement('td');
            tdDate.style.padding = '12px 8px';
            tdDate.textContent = dateStr;

            const tdType = document.createElement('td');
            tdType.style.padding = '12px 8px';
            tdType.textContent = item.type || 'Unknown';

            const tdConf = document.createElement('td');
            tdConf.style.cssText = `padding: 12px 8px; color: ${color};`;
            tdConf.textContent = confidenceText;

            const badge = document.createElement('span');
            badge.style.cssText = `background: ${color}22; color: ${color}; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px;`;
            badge.textContent = resultText;
            const tdResult = document.createElement('td');
            tdResult.style.padding = '12px 8px';
            tdResult.appendChild(badge);

            tr.appendChild(tdDate);
            tr.appendChild(tdType);
            tr.appendChild(tdConf);
            tr.appendChild(tdResult);
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

    // Retrieve the real API key set by login.html
    let savedKey = localStorage.getItem('api_key') || localStorage.getItem('authGuard_apiKey');
    if (!savedKey) {
        savedKey = 'Not logged in — please sign in first.';
    }
    // Show a masked version for security (first 12 chars + ***)
    apiKeyInput.value = savedKey.length > 12 ? savedKey.substring(0, 12) + '••••••••••••••••••••' : savedKey;
    apiKeyInput.dataset.realKey = savedKey;  // store for copy

    toggleKeyBtn.addEventListener('click', () => {
        const realKey = apiKeyInput.dataset.realKey || '';
        if (apiKeyInput.type === 'password') {
            apiKeyInput.type = 'text';
            apiKeyInput.value = realKey;  // show real key
            toggleKeyBtn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
        } else {
            apiKeyInput.type = 'password';
            // re-mask
            apiKeyInput.value = realKey.length > 12 ? realKey.substring(0, 12) + '••••••••••••••••••••' : realKey;
            toggleKeyBtn.innerHTML = '<i class="fa-solid fa-eye"></i>';
        }
    });

    copyKeyBtn.addEventListener('click', () => {
        // Copy the real key, not the masked display value
        const realKey = apiKeyInput.dataset.realKey || apiKeyInput.value;
        navigator.clipboard.writeText(realKey);
        copyKeyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--color-success);"></i>';
        setTimeout(() => {
            copyKeyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
        }, 2000);
    });

    generateKeyBtn.addEventListener('click', () => {
        alert('To change your API key, please log out and log back in with your new VK Cloud key.');
    });
});
