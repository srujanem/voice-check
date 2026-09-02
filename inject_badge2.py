import os
auth_js_path = r'D:\voice-check\voice-check\auth.js'

with open(auth_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "window.injectNavAuthState = function(containerEl) {"
gate_marker = "    // --- Premium Scan Gate ---"

start_idx = content.find(start_marker)
end_idx = content.find(gate_marker)

if start_idx != -1 and end_idx != -1:
    new_func = """    window.injectNavAuthState = function(containerEl) {
        if (!containerEl) return;
        const user = window.getCurrentUser();
        if (user) {
            const initials = user.name.slice(0, 2).toUpperCase();
            containerEl.innerHTML = `
                <div style="display:flex;align-items:center;gap:15px;font-family:inherit;">
                    <span style="font-size:12px;font-weight:600;color:var(--success);background:rgba(16,185,129,0.1);padding:4px 10px;border-radius:12px;border:1px solid rgba(16,185,129,0.2);"><i class="fa-solid fa-crown"></i> Pro</span>
                    <a href="/dashboard.html" style="text-decoration:none;"><div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#06b6d4,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0;box-shadow:0 0 10px rgba(6,182,212,0.3);transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform=''">${initials}</div></a>
                    <a href="/dashboard.html" class="hide-on-mobile" style="font-size:13px;font-weight:600;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary);text-decoration:none;transition:color 0.2s;" onmouseover="this.style.color='var(--accent-cyan)'" onmouseout="this.style.color='var(--text-primary)'">${user.email}</a>
                    <button onclick="authLogout()" style="background:none;border:1px solid rgba(239,68,68,0.3);color:#ef4444;padding:4px 10px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:600;font-family:inherit;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.1)'" onmouseout="this.style.background='none'">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i> <span class="hide-on-mobile">Logout</span>
                    </button>
                </div>`;
        } else {
            let scans = parseInt(localStorage.getItem('free_scans_used') || '0', 10);
            let remaining = Math.max(0, 2 - scans);
            let badgeColor = remaining > 0 ? 'var(--accent-cyan)' : 'var(--error)';
            let badgeText = remaining + '/2 Free Scans';
            
            containerEl.innerHTML = `
                <div style="display:flex;align-items:center;gap:12px;font-family:inherit;">
                    <span class="hide-on-mobile" style="font-size:11px;font-weight:600;color:${badgeColor};background:rgba(255,255,255,0.05);padding:5px 10px;border-radius:12px;border:1px solid ${badgeColor}; opacity:0.8;">
                        <i class="fa-solid fa-bolt"></i> ${badgeText}
                    </span>
                    <a href="/login.html" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:8px;background:linear-gradient(135deg,#06b6d4,#8b5cf6);color:#fff;text-decoration:none;font-size:13px;font-weight:600;font-family:inherit;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform=''">
                        <i class="fa-solid fa-right-to-bracket"></i> Sign In
                    </a>
                </div>`;
        }
    };

"""
    
    content = content[:start_idx] + new_func + content[end_idx:]
    with open(auth_js_path, 'w', encoding='utf-8') as f:
        f.write(content)

