if (!document.getElementById('vc-overlay')) {
    const overlay = document.createElement('div');
    overlay.id = 'vc-overlay';
    overlay.style.cssText = `
        position: fixed; bottom: 20px; right: 20px; width: 320px;
        background: #1e1e2e; color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); z-index: 10000;
        font-family: system-ui, sans-serif; border: 1px solid #334155;
        display: none; flex-direction: column; gap: 10px;
    `;
    
    const title = document.createElement('h3');
    title.textContent = 'AuthGuard Scan';
    title.style.margin = '0';
    title.style.fontSize = '16px';
    title.style.color = '#06b6d4';
    
    const content = document.createElement('div');
    content.id = 'vc-content';
    content.textContent = 'Analyzing...';
    content.style.fontSize = '14px';
    
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close';
    closeBtn.style.cssText = 'margin-top: 10px; background: #334155; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; align-self: flex-end; font-weight: 500;';
    closeBtn.onclick = () => overlay.style.display = 'none';

    overlay.appendChild(title);
    overlay.appendChild(content);
    overlay.appendChild(closeBtn);
    document.body.appendChild(overlay);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'scan_text') {
        const overlay = document.getElementById('vc-overlay');
        const content = document.getElementById('vc-content');
        
        overlay.style.display = 'flex';
        content.innerHTML = '<span style="color:#94a3b8;">Analyzing text via local backend...</span>';
        
        // Mock API Call delay
        setTimeout(() => {
            const textLen = request.text.length;
            let prediction = 'Authentic Content';
            let confidence = (85 + Math.random() * 14).toFixed(1);
            let isAI = false;
            
            // Just a fun mock logic based on text length and some keywords
            if (request.text.includes('rapid') || request.text.includes('furthermore') || request.text.includes('delve') || textLen % 3 === 0) {
                prediction = 'AI-Generated';
                isAI = true;
                confidence = (90 + Math.random() * 9).toFixed(1);
            }

            const color = isAI ? '#ef4444' : '#10b981';
            content.innerHTML = `
                <div style="font-size: 20px; font-weight: bold; color: ${color}; margin-bottom: 8px;">
                    ${prediction}
                </div>
                <div style="color: #cbd5e1;">Confidence: <strong>${confidence}%</strong></div>
            `;
        }, 1500);
    }
});
