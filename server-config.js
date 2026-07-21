/**
 * AuthGuard Auto Server Connection — Smart Multi-Port Auto-Discovery
 *
 * Permanently fixes "Cannot reach server" by trying:
 *   1. localhost:5000  (Flask default)
 *   2. localhost:8000  (Node / alternate)
 *   3. Any previously saved Cloudflare tunnel URL
 *   4. The default Cloudflare URL (for remote phone access)
 *
 * Saves the working URL to localStorage so all tool pages reuse it.
 * Re-checks every 30 seconds to keep the status dot accurate.
 */
(function () {
    const STORAGE_KEY_URL    = 'zrok_url';
    const STORAGE_KEY_STATUS = 'server_online';
    const DEFAULT_URL = 'https://registered-respondent-strategic-links.trycloudflare.com';

    // ─── Inject status badge CSS ──────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
        #ag-status-badge {
            position: fixed; bottom: 20px; left: 20px; z-index: 9999;
            display: flex; align-items: center; gap: 7px;
            background: rgba(15,23,42,0.88); border: 1px solid #334155;
            backdrop-filter: blur(12px); padding: 7px 14px;
            border-radius: 50px; font-family: 'Inter', system-ui, sans-serif;
            font-size: 12px; font-weight: 600; color: #94a3b8;
            pointer-events: none; transition: opacity 0.3s ease;
        }
        #ag-dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: #f59e0b; transition: background 0.4s ease;
        }
        #ag-dot.online  { background: #10b981; animation: ag-pulse 2s infinite; }
        #ag-dot.offline { background: #ef4444; }
        @keyframes ag-pulse {
            0%   { box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }
            70%  { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
            100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
        }
        @media (max-width: 768px) {
            #ag-status-badge { 
                bottom: auto; 
                top: 85px; 
                left: 50%; 
                transform: translateX(-50%); 
                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            }
        }
    `;
    document.head.appendChild(style);

    // ─── Inject status badge HTML ─────────────────────────────────────────────
    const badge = document.createElement('div');
    badge.id = 'ag-status-badge';
    badge.innerHTML = `<span id="ag-dot"></span><span id="ag-label">Connecting...</span>`;
    document.body.appendChild(badge);

    const dot   = document.getElementById('ag-dot');
    const label = document.getElementById('ag-label');

    // ─── State setters ────────────────────────────────────────────────────────
    function setOnline(url) {
        localStorage.setItem(STORAGE_KEY_URL, url);
        localStorage.setItem(STORAGE_KEY_STATUS, 'true');
        window.AUTHGUARD_BACKEND_URL = url;
        dot.className     = 'online';
        label.textContent = 'Server Online';
    }

    function setOffline() {
        localStorage.removeItem(STORAGE_KEY_URL);
        localStorage.setItem(STORAGE_KEY_STATUS, 'false');
        window.AUTHGUARD_BACKEND_URL = null;
        dot.className     = 'offline';
        label.textContent = 'Server Offline';
    }

    // ─── Try a single URL ─────────────────────────────────────────────────────
    async function tryUrl(url) {
        try {
            const res = await fetch(`${url}/api/health`, {
                signal: AbortSignal.timeout(2500)
            });
            return res.ok;
        } catch {
            return false;
        }
    }

    // ─── Smart auto-connect: LOCAL FIRST, then tunnel ─────────────────────────
    async function autoConnect() {
        const savedUrl = localStorage.getItem(STORAGE_KEY_URL);

        // Port 8000 = Node.js Backend, Port 5000 = Flask ML backend
        const localPorts = ['http://localhost:8000', 'http://localhost:5000'];

        for (const url of localPorts) {
            if (await tryUrl(url)) { setOnline(url); return; }
        }

        // Try previously saved (possibly tunnel) URL next
        if (savedUrl && !localPorts.includes(savedUrl)) {
            const clean = savedUrl.replace(/\/$/, '');
            if (await tryUrl(clean)) { setOnline(clean); return; }
        }

        // Finally try the Cloudflare tunnel (for phone/remote access)
        if (await tryUrl(DEFAULT_URL)) { setOnline(DEFAULT_URL); return; }

        // Nothing worked
        setOffline();
    }

    autoConnect();
    setInterval(autoConnect, 30000);   // Re-check every 30 seconds
})();
