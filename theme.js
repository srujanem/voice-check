// Theme Toggle — runs once, prevents duplicates
(function() {
    if (window.__themeInitialized) return;
    window.__themeInitialized = true;

    const html = document.documentElement;

    // Apply saved theme instantly (before paint)
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);

    function updateIcon(theme) {
        const toggle = document.getElementById('themeToggle');
        if (!toggle) return;
        toggle.innerHTML = theme === 'light'
            ? '<i class="fa-solid fa-moon"></i>'
            : '<i class="fa-solid fa-sun"></i>';
    }

    function init() {
        updateIcon(html.getAttribute('data-theme') || 'dark');

        const toggle = document.getElementById('themeToggle');
        if (toggle && !toggle.__themeListenerAttached) {
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
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
