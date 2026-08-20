
(function() {
    // ── Theme ──────────────────────────────────────────────────────────────
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    const themeBtn = document.getElementById('themeToggle');
    function updateThemeIcon() {
        themeBtn.innerHTML = html.getAttribute('data-theme') === 'dark'
            ? '<i class="fa-solid fa-sun"></i>'
            : '<i class="fa-solid fa-moon"></i>';
    }
    updateThemeIcon();
    themeBtn.addEventListener('click', () => {
        const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon();
    });

    // ── Tab switch ─────────────────────────────────────────────────────────
    window.switchTab = function(tab) {
        clearAlert();
        document.getElementById('login-flow').style.display  = tab === 'login'  ? '' : 'none';
        document.getElementById('signup-flow').style.display = tab === 'signup' ? '' : 'none';
        document.getElementById('tab-login').classList.toggle('active',  tab === 'login');
        document.getElementById('tab-signup').classList.toggle('active', tab === 'signup');
    };

    // ── Alert helpers ───────────────────────────────────────────────────────
    function showAlert(msg, type) {
        const box = document.getElementById('alert-box');
        box.className = 'alert show ' + type;
        box.querySelector('i').className = type === 'success'
            ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-exclamation';
        document.getElementById('alert-msg').textContent = msg;
    }
    function clearAlert() { document.getElementById('alert-box').classList.remove('show'); }

    // ── Password visibility toggle ─────────────────────────────────────────
    window.togglePw = function(inputId, btn) {
        const input = document.getElementById(inputId);
        const isText = input.type === 'text';
        input.type = isText ? 'password' : 'text';
        btn.querySelector('i').className = isText ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
    };

    // ── Password strength ──────────────────────────────────────────────────
    window.checkStrength = function(pw) {
        const fill  = document.getElementById('strength-fill');
        const label = document.getElementById('strength-label');
        let score = 0;
        if (pw.length >= 8) score++;
        if (/[A-Z]/.test(pw)) score++;
        if (/[0-9]/.test(pw)) score++;
        if (/[^A-Za-z0-9]/.test(pw)) score++;
        const levels = [
            { label: '',              color: 'transparent', w: '0%'  },
            { label: 'Weak',          color: '#ef4444',     w: '25%' },
            { label: 'Fair',          color: '#f59e0b',     w: '50%' },
            { label: 'Good',          color: '#06b6d4',     w: '75%' },
            { label: 'Strong ✓',      color: '#10b981',     w: '100%'},
        ];
        const l = levels[score] || levels[0];
        fill.style.width = l.w;
        fill.style.background = l.color;
        label.textContent = l.label;
        label.style.color = l.color;
    };

    // ── Backend URL helper ─────────────────────────────────────────────────
    function getBackendUrl() {
        return (window.AUTHGUARD_BACKEND_URL ||
                localStorage.getItem('zrok_url') ||
                'http://localhost:5000').replace(/\/$/, '');
    }

    // ── Button loading state ───────────────────────────────────────────────
    function setLoading(btn, loading) {
        btn.disabled = loading;
        if (loading) {
            btn.dataset.orig = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-spinner"></i> Please wait…';
            btn.classList.add('loading');
        } else {
            btn.innerHTML = btn.dataset.orig || btn.innerHTML;
            btn.classList.remove('loading');
        }
    }

    // ══════════════════════════════════════════════════════════════════════
    // LOGIN
    // ══════════════════════════════════════════════════════════════════════
    window.doLogin = async function() {
        clearAlert();
        const email    = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        if (!email || !password) { showAlert('Please fill in both fields.', 'error'); return; }

        const btn = document.getElementById('login-btn');
        setLoading(btn, true);

        try {
            const res = await fetch(getBackendUrl() + '/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Login failed');

            // Persist auth
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_email', email);
            localStorage.setItem('user_name', email.split('@')[0]);

            showAlert('Signed in! Redirecting…', 'success');
            setTimeout(() => {
                const redirect = new URLSearchParams(location.search).get('next') || 'dashboard.html';
                location.href = redirect;
            }, 900);
        } catch (err) {
            showAlert(err.message, 'error');
        } finally {
            setLoading(btn, false);
        }
    };

    // Enter key on login form
    ['login-email', 'login-password'].forEach(id => {
        document.getElementById(id)?.addEventListener('keydown', e => {
            if (e.key === 'Enter') window.doLogin();
        });
    });

    // ══════════════════════════════════════════════════════════════════════
    // SIGNUP — Step 1: Request OTP
    // ══════════════════════════════════════════════════════════════════════
    window.requestOtp = async function() {
        clearAlert();
        const email = document.getElementById('signup-email').value.trim();
        if (!email || !email.includes('@')) { showAlert('Please enter a valid email address.', 'error'); return; }

        const btn = document.getElementById('send-otp-btn');
        setLoading(btn, true);

        try {
            const res = await fetch(getBackendUrl() + '/api/auth/request-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to send OTP');

            // Move to step 2
            document.getElementById('signup-step-1').classList.remove('active');
            document.getElementById('signup-step-2').classList.add('active');
            document.querySelector('#otp-subtitle strong').textContent = email;
            startCountdown();
            document.querySelector('.otp-box').focus();
        } catch (err) {
            showAlert(err.message, 'error');
        } finally {
            setLoading(btn, false);
        }
    };

    document.getElementById('signup-email')?.addEventListener('keydown', e => {
        if (e.key === 'Enter') window.requestOtp();
    });

    // ── OTP box auto-advance ──────────────────────────────────────────────
    document.querySelectorAll('.otp-box').forEach((box, i, arr) => {
        box.addEventListener('input', () => {
            box.value = box.value.replace(/\D/g, '');
            if (box.value && i < arr.length - 1) arr[i + 1].focus();
        });
        box.addEventListener('keydown', e => {
            if (e.key === 'Backspace' && !box.value && i > 0) arr[i - 1].focus();
        });
        box.addEventListener('paste', e => {
            const text = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
            arr.forEach((b, j) => { b.value = text[j] || ''; });
            arr[Math.min(text.length, arr.length - 1)].focus();
            e.preventDefault();
        });
    });

    // ══════════════════════════════════════════════════════════════════════
    // SIGNUP — Step 2: Verify OTP + create account
    // ══════════════════════════════════════════════════════════════════════
    window.verifyOtp = async function() {
        clearAlert();
        const email    = document.getElementById('signup-email').value.trim();
        const otp      = [...document.querySelectorAll('.otp-box')].map(b => b.value).join('');
        const password = document.getElementById('signup-password').value;

        if (otp.length < 6) { showAlert('Please enter the full 6-digit code.', 'error'); return; }
        if (password.length < 8) { showAlert('Password must be at least 8 characters.', 'error'); return; }

        const btn = document.getElementById('verify-btn');
        setLoading(btn, true);

        try {
            const res = await fetch(getBackendUrl() + '/api/auth/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp, password })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Verification failed');

            // Persist auth
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_email', email);
            localStorage.setItem('user_name', email.split('@')[0]);

            // Success screen
            document.getElementById('signup-step-2').classList.remove('active');
            document.getElementById('signup-step-3').classList.add('active');
            setTimeout(() => { document.getElementById('redirect-bar').style.width = '100%'; }, 100);
            setTimeout(() => {
                const redirect = new URLSearchParams(location.search).get('next') || 'dashboard.html';
                location.href = redirect;
            }, 3200);
        } catch (err) {
            showAlert(err.message, 'error');
        } finally {
            setLoading(btn, false);
        }
    };

    // ── Countdown + resend ──────────────────────────────────────────────
    let countdownTimer;
    function startCountdown(seconds = 60) {
        const resendBtn = document.getElementById('resend-btn');
        const countEl   = document.getElementById('countdown');
        resendBtn.classList.remove('ready');
        resendBtn.disabled = true;
        let left = seconds;
        clearInterval(countdownTimer);
        countdownTimer = setInterval(() => {
            left--;
            countEl.textContent = left;
            if (left <= 0) {
                clearInterval(countdownTimer);
                resendBtn.disabled = false;
                resendBtn.classList.add('ready');
                resendBtn.innerHTML = 'Resend code';
            }
        }, 1000);
    }

    window.resendOtp = async function() {
        const resendBtn = document.getElementById('resend-btn');
        if (!resendBtn.classList.contains('ready')) return;

        clearAlert();
        const email = document.getElementById('signup-email').value.trim();
        try {
            const res = await fetch(getBackendUrl() + '/api/auth/request-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            if (!res.ok) throw new Error((await res.json()).error || 'Failed');
            showAlert('A new code has been sent!', 'success');
            resendBtn.innerHTML = 'Resend code (<span id="countdown">60</span>s)';
            startCountdown(60);
            document.querySelectorAll('.otp-box').forEach(b => b.value = '');
            document.querySelector('.otp-box').focus();
        } catch (err) {
            showAlert(err.message, 'error');
        }
    };

    // ── If already logged in, skip to index ──────────────────────────────
    if (localStorage.getItem('auth_token')) {
        const redirect = new URLSearchParams(location.search).get('next') || 'dashboard.html';
        location.replace(redirect);
    }
})();

    
    // --- Google OAuth Mock ---
    
    
    window.doGoogleLogin = function(event) {
        if(event) event.preventDefault();
        const btn = event.currentTarget;
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Connecting to Google...';
        btn.style.pointerEvents = 'none';

        // Simulate network delay then redirect, no popups on mobile!
        setTimeout(() => {
            const mockUser = {
                email: "srujanem222@gmail.com",
                name: "Srujan",
                token: "google_oauth_mock_token_" + Date.now()
            };
            localStorage.setItem('auth_email', mockUser.email);
            localStorage.setItem('user_name', mockUser.name);
            localStorage.setItem('auth_token', mockUser.token);
            
            const redirect = new URLSearchParams(location.search).get('next') || 'dashboard.html';
            window.location.href = redirect;
        }, 1500);
    };
