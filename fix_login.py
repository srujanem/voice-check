import re

with open(r'D:\voice-check\voice-check\login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the doGoogleLogin function
new_google = r'''
    window.doGoogleLogin = function(event) {
        if(event) event.preventDefault();
        const btn = event.currentTarget || document.querySelector('.google-btn');
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Connecting to Google...';
        btn.style.pointerEvents = 'none';

        setTimeout(() => {
            try {
                localStorage.setItem('auth_email', "srujanem222@gmail.com");
                localStorage.setItem('user_name', "Srujan");
                localStorage.setItem('auth_token', "google_oauth_mock_token_" + Date.now());
            } catch(e) {
                alert("Please disable Private/Incognito mode. Your browser is blocking the login data storage.");
                return;
            }
            window.location.href = 'dashboard.html';
        }, 800);
    };
'''

content = re.sub(r'window\.doGoogleLogin\s*=\s*function\(event\).*?\}\s*;\s*</script>', new_google + "\n</script>", content, flags=re.DOTALL)

with open(r'D:\voice-check\voice-check\login.html', 'w', encoding='utf-8') as f:
    f.write(content)
