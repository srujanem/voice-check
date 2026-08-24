class ScanHistory {
    constructor() {
        this.STORAGE_KEY = 'ai_detection_history';
    }

    getHistory() {
        return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
    }

    addScan(type, fileName, isAi, confidence) {
        const history = this.getHistory();
        history.unshift({
            id: Date.now(),
            date: new Date().toLocaleString(),
            type, // 'Voice', 'Image', 'Text'
            fileName,
            isAi,
            confidence
        });
        
        if (history.length > 50) history.pop();
        
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(history));
        this.renderHistory();
        window.dispatchEvent(new CustomEvent('authguard-scan', { detail: { type, fileName, isAi, confidence } }));

        // Push to Database if logged in
        const email = localStorage.getItem('user_email') || localStorage.getItem('user_id');
        if (email) {
            const backendUrl = (window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            fetch(`${backendUrl}/api/history`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    ...(window.getAuthHeaders ? window.getAuthHeaders() : {})
                },
                body: JSON.stringify({
                    email: email,
                    type: type,
                    fileName: fileName,
                    isAi: isAi,
                    confidence: confidence,
                    date: new Date().toLocaleString()
                })
            }).catch(e => console.error("Failed to sync history to DB", e));
        }
    }

    clearHistory() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.renderHistory();
    }

    renderHistory() {
        const history = this.getHistory();
        
        // Render for sidebar or UI panels if they exist
        const container = document.getElementById('history-list');
        if (container) {
            if (history.length === 0) {
                container.innerHTML = '<p style="text-align:center; color: var(--text-secondary); margin-top: 20px;">No recent scans.</p>';
            } else {
                container.innerHTML = history.map(scan => {
                    const statusColor = scan.isAi ? 'var(--color-error, #ef4444)' : 'var(--color-success, #10b981)';
                    const statusIcon = scan.isAi ? 'fa-triangle-exclamation' : 'fa-circle-check';
                    const statusText = scan.isAi ? 'AI Generated' : 'Authentic';
                    return `
                    <div class="history-item" style="padding: 15px; border-radius: 12px; margin-bottom: 10px; background: var(--bg-card); border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">
                                <i class="fa-solid ${scan.type === 'Voice' ? 'fa-microphone' : scan.type === 'Image' ? 'fa-image' : 'fa-font'}"></i> ${scan.type} • ${scan.date}
                            </div>
                            <div style="font-weight: 500; font-size: 14px; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px;">${scan.fileName}</div>
                            <div style="font-size: 12px; font-weight: bold; color: ${statusColor}">
                                 ${statusText} (${scan.confidence}%)
                            </div>
                        </div>
                        <div style="font-size: 24px; color: ${statusColor}">
                            <i class="fa-solid ${statusIcon}"></i>
                        </div>
                    </div>`;
                }).join('');
            }
        }

        // Render for Dashboard table if it exists
        const dashTable = document.getElementById('dash-recent-scans');
        if (dashTable) {
            if (history.length === 0) {
                dashTable.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:30px;">No scan history yet.</td></tr>';
            } else {
                dashTable.innerHTML = history.map(scan => {
                    const statusClass = scan.isAi ? 'status-fake' : 'status-authentic';
                    const statusIcon = scan.isAi ? 'fa-robot' : 'fa-user-check';
                    const statusText = scan.isAi ? 'AI Generated' : 'Authentic';
                    
                    let typeIcon = 'fa-file';
                    if (scan.type === 'Voice') typeIcon = 'fa-microphone';
                    if (scan.type === 'Image') typeIcon = 'fa-image';
                    if (scan.type === 'Text') typeIcon = 'fa-font';
                    if (scan.type === 'Video') typeIcon = 'fa-video';
                    
                    return `
                        <tr>
                            <td>
                                <div style="display:flex;align-items:center;gap:12px;">
                                    <div style="width:36px;height:36px;border-radius:10px;background:rgba(255,255,255,0.05);display:flex;align-items:center;justify-content:center;color:#fff;">
                                        <i class="fa-solid ${typeIcon}"></i>
                                    </div>
                                    <span style="font-weight:600;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${scan.fileName}</span>
                                </div>
                            </td>
                            <td>${scan.type}</td>
                            <td>
                                <span class="status-badge ${statusClass}">
                                    <i class="fa-solid ${statusIcon}"></i> ${statusText} (${scan.confidence}%)
                                </span>
                            </td>
                            <td style="color:#94a3b8;font-size:13px;">${scan.date}</td>
                            <td>
                                <button onclick="alert('View report feature coming soon!')" style="background:none;border:none;color:var(--accent-cyan, #06b6d4);cursor:pointer;font-weight:600;">View Report</button>
                            </td>
                        </tr>`;
                }).join('');
            }
            
            // Update counts on dashboard
            const totalScansEl = document.getElementById('dash-total-scans');
            const aiScansEl = document.getElementById('dash-ai-threats');
            if (totalScansEl) totalScansEl.innerText = history.length;
            
            if (aiScansEl) aiScansEl.innerText = history.filter(s => s.isAi).length;
            const avgConfEl = document.getElementById('dash-avg-conf');
            if (avgConfEl && history.length > 0) {
                const avg = history.reduce((sum, s) => sum + parseFloat(s.confidence || 0), 0) / history.length;
                avgConfEl.innerText = avg.toFixed(1) + '%';
            }
        }
    }

    async fetchHistoryFromDB() {
        const email = localStorage.getItem('user_email') || localStorage.getItem('user_id');
        if (!email) return;
        try {
            const backendUrl = (window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
            const res = await fetch(`${backendUrl}/api/history?email=${email}`, {
                headers: {
                    ...(window.getAuthHeaders ? window.getAuthHeaders() : {})
                }
            });
            if (res.ok) {
                const data = await res.json();
                const formatted = data.map(scan => ({
                    id: scan.id,
                    date: scan.date,
                    type: scan.type,
                    fileName: scan.fileName,
                    isAi: scan.isAi,
                    confidence: scan.confidence
                }));
                localStorage.setItem(this.STORAGE_KEY, JSON.stringify(formatted));
                this.renderHistory();
            }
        } catch (e) {
            console.error("Failed to fetch history from DB", e);
        }
    }

    initSidebar() {
        if (!document.getElementById('history-sidebar')) {
            const sidebarHTML = `
                <div id="history-sidebar" class="history-sidebar hidden">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="font-size: 20px;"><i class="fa-solid fa-clock-rotate-left"></i> Scan History</h2>
                        <button id="close-history" class="btn-icon" style="background: none; border: none; color: var(--text-primary); font-size: 20px; cursor: pointer;"><i class="fa-solid fa-xmark"></i></button>
                    </div>
                    <div id="history-list" style="overflow-y: auto; max-height: calc(100vh - 150px); padding-right: 10px;"></div>
                    <button id="clear-history" class="btn-secondary" style="width: 100%; margin-top: 20px; color: var(--color-error); border-color: rgba(239, 68, 68, 0.3);">Clear History</button>
                </div>
                <div id="history-overlay" class="history-overlay hidden"></div>
                
                <button id="open-history" class="floating-history-btn" title="View History">
                    <i class="fa-solid fa-clock-rotate-left"></i>
                </button>
            `;
            document.body.insertAdjacentHTML('beforeend', sidebarHTML);
        }

        const sidebar = document.getElementById('history-sidebar');
        const overlay = document.getElementById('history-overlay');
        const openBtn = document.getElementById('open-history');
        const closeBtn = document.getElementById('close-history');
        const clearBtn = document.getElementById('clear-history');

        if (openBtn) {
            openBtn.addEventListener('click', () => {
                sidebar.classList.remove('hidden');
                overlay.classList.remove('hidden');
                this.renderHistory();
            });
        }

        const closeSidebar = () => {
            if (sidebar) sidebar.classList.add('hidden');
            if (overlay) overlay.classList.add('hidden');
        };

        if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
        if (overlay) overlay.addEventListener('click', closeSidebar);
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if(confirm("Are you sure you want to clear all scan history?")) {
                    this.clearHistory();
                }
            });
        }

        this.renderHistory();
    }
}

const scanHistory = new ScanHistory();
window.scanHistory = scanHistory;

function initHistory() {
    scanHistory.initSidebar();
    scanHistory.fetchHistoryFromDB();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHistory);
} else {
    initHistory();
}