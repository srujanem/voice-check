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

        // Push to Database if logged in
        const userId = localStorage.getItem('user_id');
        if (userId) {
            fetch('/history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    scan_type: type,
                    target_name: fileName,
                    is_ai: isAi,
                    confidence: confidence
                })
            }).catch(e => console.error("Failed to sync history to DB", e));
        }
    }

    clearHistory() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.renderHistory();
    }

    renderHistory() {
        const container = document.getElementById('history-list');
        if (!container) return;

        const history = this.getHistory();
        if (history.length === 0) {
            container.innerHTML = '<p style="text-align:center; color: var(--text-secondary); margin-top: 20px;">No recent scans.</p>';
            return;
        }

        container.innerHTML = history.map(scan => `
            <div class="history-item ${scan.isAi ? 'fake' : 'authentic'}" style="padding: 15px; border-radius: 12px; margin-bottom: 10px; background: var(--bg-card); border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">
                        <i class="fa-solid ${scan.type === 'Voice' ? 'fa-microphone' : scan.type === 'Image' ? 'fa-image' : 'fa-file-signature'}"></i> ${scan.date}
                    </div>
                    <div style="font-weight: 500; font-size: 14px; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px;">${scan.fileName}</div>
                    <div style="font-size: 12px; font-weight: bold; color: ${scan.isAi ? 'var(--color-error)' : 'var(--color-success)'}">
                        ${scan.isAi ? 'AI Generated' : 'Human / Authentic'} (${scan.confidence}%)
                    </div>
                </div>
                <div style="font-size: 24px; color: ${scan.isAi ? 'var(--color-error)' : 'var(--color-success)'}">
                    <i class="fa-solid ${scan.isAi ? 'fa-robot' : 'fa-user-check'}"></i>
                </div>
            </div>
        `).join('');
    }

    async fetchHistoryFromDB() {
        const userId = localStorage.getItem('user_id');
        if (!userId) return;
        try {
            const res = await fetch(`/history?user_id=${userId}`);
            if (res.ok) {
                const data = await res.json();
                const formatted = data.map(scan => ({
                    id: scan.id,
                    date: new Date(scan.timestamp).toLocaleString(),
                    type: scan.scan_type,
                    fileName: scan.target_name,
                    isAi: scan.is_ai,
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

        openBtn.addEventListener('click', () => {
            sidebar.classList.remove('hidden');
            overlay.classList.remove('hidden');
            this.renderHistory();
        });

        const closeSidebar = () => {
            sidebar.classList.add('hidden');
            overlay.classList.add('hidden');
        };

        closeBtn.addEventListener('click', closeSidebar);
        overlay.addEventListener('click', closeSidebar);
        
        clearBtn.addEventListener('click', () => {
            if(confirm("Are you sure you want to clear all scan history?")) {
                this.clearHistory();
            }
        });

        this.renderHistory();
    }
}

const scanHistory = new ScanHistory();

document.addEventListener('DOMContentLoaded', () => {
    scanHistory.initSidebar();
    scanHistory.fetchHistoryFromDB();
});
