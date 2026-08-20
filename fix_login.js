const fs = require('fs');

let html = fs.readFileSync('login.html', 'utf8');

// Strip out the broken Google OAuth Mock script
const startMarker = '// --- Google OAuth Mock ---';
const startIndex = html.indexOf(startMarker);
if (startIndex !== -1) {
    html = html.substring(0, startIndex);
}

// Add it back correctly
const js = \
    // --- Google OAuth Mock ---
    window.doGoogleLogin = function() {
        const btn = event.currentTarget;
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Connecting...';
        btn.style.pointerEvents = 'none';

        // Simulate OAuth Popup
        const w = 500, h = 600;
        const left = (screen.width/2)-(w/2);
        const top = (screen.height/2)-(h/2);
        const popup = window.open('', 'Google Sign In', 'width=' + w + ',height=' + h + ',top=' + top + ',left=' + left);
        
        if(popup) {
            popup.document.write(
                '<body style="margin:0; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; background:#fff;">' +
                    '<svg viewBox="0 0 24 24" width="40" height="40" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:20px;">' +
                        '<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>' +
                        '<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>' +
                        '<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>' +
                        '<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>' +
                    '</svg>' +
                    '<h2 style="color:#202124; margin:0 0 10px 0;">Sign in with Google</h2>' +
                    '<p style="color:#5f6368; font-size:14px;">One moment please...</p>' +
                '</body>'
            );
            
            setTimeout(() => {
                popup.close();
                // Create mock user
                const mockUser = {
                    email: "srujanem222@gmail.com",
                    name: "Srujan",
                    token: "google_oauth_mock_token_" + Date.now()
                };
                localStorage.setItem('authguard_user', JSON.stringify(mockUser));
                localStorage.setItem('auth_token', mockUser.token);
                
                // Show alert logic isn't easily accessible from global if it's inside IIFE, just redirect
                const redirect = new URLSearchParams(location.search).get('next') || 'dashboard.html';
                window.location.href = redirect;
            }, 1500);
        } else {
            // Fallback if popups are blocked
            setTimeout(() => {
                const mockUser = { email: "srujanem222@gmail.com", name: "Srujan", token: "google_mock" };
                localStorage.setItem('authguard_user', JSON.stringify(mockUser));
                localStorage.setItem('auth_token', mockUser.token);
                window.location.href = 'dashboard.html';
            }, 1500);
        }
    };
\n</script>\n</body>\n</html>\;

html = html + js;
fs.writeFileSync('login.html', html, 'utf8');
