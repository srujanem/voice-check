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
});
