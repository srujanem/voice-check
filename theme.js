// Theme Toggle — runs once, prevents duplicates
(function() {
    if (window.__themeInitialized) return;
    window.__themeInitialized = true;

    const html = document.documentElement;

    // Apply saved theme instantly (before paint)
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);

    function updateIcon(theme) {
        const toggles = document.querySelectorAll('.theme-toggle');
        toggles.forEach(toggle => {
            toggle.innerHTML = theme === 'light'
                ? '<i class="fa-solid fa-moon"></i>'
                : '<i class="fa-solid fa-sun"></i>';
        });
    }

    function init() {
        updateIcon(html.getAttribute('data-theme') || 'dark');

        const toggles = document.querySelectorAll('.theme-toggle');
        toggles.forEach(toggle => {
            if (!toggle.__themeListenerAttached) {
                toggle.__themeListenerAttached = true;
                toggle.addEventListener('click', () => {
                    const current = html.getAttribute('data-theme');
                    const next = current === 'light' ? 'dark' : 'light';
                    html.setAttribute('data-theme', next);
                    localStorage.setItem('theme', next);
                    updateIcon(next);
                    toggle.classList.add('spin');
                    setTimeout(() => toggle.classList.remove('spin'), 500);
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

// ===== REALTIME PRESENCE SYSTEM =====
(function() {
    function generateClientId() {
        let id = localStorage.getItem('ag_client_id');
        if (!id) {
            id = Math.random().toString(36).substring(2, 15);
            localStorage.setItem('ag_client_id', id);
        }
        return id;
    }

    async function pingPresence() {
        const liveCountEl = document.getElementById('live-count');
        const baseUrl = window.AUTHGUARD_BACKEND_URL || localStorage.getItem('zrok_url') || 'http://localhost:8000';
        const cleanUrl = baseUrl.replace(/\/$/, '');
        
        try {
            // Ping that we are alive
            await fetch(\/api/presence, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ clientId: generateClientId() })
            });

            // Get the current online count
            const res = await fetch(\/api/presence);
            const data = await res.json();
            
            if (data && data.online !== undefined && liveCountEl) {
                // Add an artificial baseline offset of 14 for visual mass, plus the real count
                // Or just show the real count! Since it's local/small, showing "1 online" might look too empty?
                // The user said "if the person is online show correctly" -> I will show the exact real count!
                liveCountEl.textContent = data.online;
            }
        } catch (e) {
            console.log("Presence check failed", e);
        }
    }

    // Ping immediately and then every 30 seconds
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            pingPresence();
            setInterval(pingPresence, 30000);
        });
    } else {
        pingPresence();
        setInterval(pingPresence, 30000);
    }
})();
