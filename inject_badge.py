import os
auth_js_path = r'D:\voice-check\voice-check\auth.js'

with open(auth_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Modify injectNavAuthState to show the remaining free scans if not logged in
replacement = '''
    window.injectNavAuthState = function(containerEl) {
        if (!containerEl) return;
        const user = window.getCurrentUser();
        if (user) {
            const initials = user.name.slice(0, 2).toUpperCase();
            containerEl.innerHTML = 
                <div style="display:flex;align-items:center;gap:15px;font-family:inherit;">
                    <span style="font-size:12px;font-weight:600;color:var(--success);background:rgba(16,185,129,0.1);padding:4px 10px;border-radius:12px;border:1px solid rgba(16,185,129,0.2);"><i class="fa-solid fa-crown"></i> Pro</span>
                    <a href="/dashboard.html" style="text-decoration:none;"><div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#06b6d4,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0;box-shadow:0 0 10px rgba(6,182,212,0.3);transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform=''"></div></a>
                    <a href="/dashboard.html" class="hide-on-mobile" style="font-size:13px;font-weight:600;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary);text-decoration:none;transition:color 0.2s;" onmouseover="this.style.color='var(--accent-cyan)'" onmouseout="this.style.color='var(--text-primary)'"></a>
                    <button onclick="authLogout()" style="background:none;border:1px solid rgba(239,68,68,0.3);color:#ef4444;padding:4px 10px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:600;font-family:inherit;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.1)'" onmouseout="this.style.background='none'">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i> <span class="hide-on-mobile">Logout</span>
                    </button>
                </div>;
        } else {
            let scans = parseInt(localStorage.getItem('free_scans_used') || '0', 10);
            let remaining = Math.max(0, 2 - scans);
            let badgeColor = remaining > 0 ? 'var(--accent-cyan)' : 'var(--error)';
            let badgeText = remaining + '/2 Free Scans';
            
            containerEl.innerHTML = 
                <div style="display:flex;align-items:center;gap:12px;font-family:inherit;">
                    <span class="hide-on-mobile" style="font-size:11px;font-weight:600;color:;background:rgba(255,255,255,0.05);padding:5px 10px;border-radius:12px;border:1px solid ; opacity:0.8;">
                        <i class="fa-solid fa-bolt"></i> 
                    </span>
                    <a href="/login.html" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:8px;background:linear-gradient(135deg,#06b6d4,#8b5cf6);color:#fff;text-decoration:none;font-size:13px;font-weight:600;font-family:inherit;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform=''">
                        <i class="fa-solid fa-right-to-bracket"></i> Sign In
                    </a>
                </div>;
        }
    };
    
    // Also re-inject nav state after gate increments
    const oldCheck = window.checkScanGate;
    window.checkScanGate = function() {
        const res = oldCheck();
        if (res && !window.getCurrentUser() && document.getElementById('nav-auth')) {
            window.injectNavAuthState(document.getElementById('nav-auth'));
        }
        return res;
    };
'''

# We need to replace the old injectNavAuthState block
import re
content = re.sub(r'window\.injectNavAuthState = function\(containerEl\).*?};', replacement, content, flags=re.DOTALL)

with open(auth_js_path, 'w', encoding='utf-8') as f:
    f.write(content)

