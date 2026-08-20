import re

with open(r'D:\voice-check\voice-check\login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the broken function entirely
content = re.sub(r'window\.doGoogleLogin\s*=\s*function\(event\).*?\}\s*\}\s*;\s*</script>', r'''
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
</script>''', content, flags=re.DOTALL)

with open(r'D:\voice-check\voice-check\login.html', 'w', encoding='utf-8') as f:
    f.write(content)
