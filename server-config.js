/**
 * AuthGuard Auto Server Connection â€” Smart Multi-Port Auto-Discovery
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
    const DEFAULT_URL = 'https://minimum-think-ordering-ends.trycloudflare.com';

    // â”€â”€â”€ Inject status badge CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
                bottom: 25px; 
                top: auto; 
                left: 20px; 
                transform: none; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            }
        }
        }
    `;
    document.head.appendChild(style);

    // â”€â”€â”€ Inject status badge HTML â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    const badge = document.createElement('div');
    badge.id = 'ag-status-badge';
    badge.innerHTML = `<span id="ag-dot"></span><span id="ag-label">Connecting...</span>`;
    document.body.appendChild(badge);

    const dot   = document.getElementById('ag-dot');
    const label = document.getElementById('ag-label');

    // â”€â”€â”€ State setters â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

    // â”€â”€â”€ Try a single URL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    async function tryUrl(url) {
        try {
            const res = await fetch(`${url}/api/health`, {
                signal: AbortSignal.timeout(25000)
            });
            return res.ok;
        } catch {
            return false;
        }
    }

    // â”€â”€â”€ Smart auto-connect: LOCAL FIRST, then live tunnel URL, then fallback â”€â”€â”€â”€â”€
    async function autoConnect() {
        const savedUrl = localStorage.getItem(STORAGE_KEY_URL);

        // 1. Try localhost first (works when user's PC is the server)
        const localPorts = ['http://localhost:8000', 'http://localhost:5000'];
        for (const url of localPorts) {
            if (await tryUrl(url)) {
                // While on localhost, fetch and update the tunnel URL in background
                fetch(`${url}/api/tunnel-url`)
                    .then(r => r.json())
                    .then(d => { if (d.url) localStorage.setItem('zrok_url', d.url); })
                    .catch(() => {});
                setOnline(url);
                return;
            }
        }

        // 2. If we have a saved URL, ask the server for the LIVE tunnel URL first
        if (savedUrl && !localPorts.includes(savedUrl)) {
            const clean = savedUrl.replace(/\/$/, '');
            if (await tryUrl(clean)) {
                // Refresh the live URL in the background
                fetch(`${clean}/api/tunnel-url`)
                    .then(r => r.json())
                    .then(d => { if (d.url && d.url !== clean) { localStorage.setItem('zrok_url', d.url); } })
                    .catch(() => {});
                setOnline(clean);
                return;
            }
        }

        // 3. Try the baked-in DEFAULT_URL
        if (await tryUrl(DEFAULT_URL)) { setOnline(DEFAULT_URL); return; }

        // 4. Nothing worked
        setOffline();
    }

    autoConnect();
    setInterval(autoConnect, 30000);   // Re-check every 30 seconds
})();
















