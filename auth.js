/**
 * auth.js — Shared auth helper used by all detection UIs
 *
 * Provides:
 *   getAuthHeaders()   → { Authorization: 'Bearer <token>' } or {}
 *   getBackendUrl()    → the active backend URL
 *   getCurrentUser()   → { email, name } or null
 *   authLogout()       → clears auth state
 *   injectNavAuthState(containerEl) → renders login/avatar pill in nav
 */

(function(window) {
    'use strict';

    const TOKEN_KEY = 'auth_token';
    const EMAIL_KEY = 'auth_email';
    const NAME_KEY  = 'user_name';

    function getToken() {
        return localStorage.getItem(TOKEN_KEY) || '';
    }

    window.getAuthHeaders = function() {
        const t = getToken();
        return t ? { 'Authorization': 'Bearer ' + t } : {};
    };

    window.getBackendUrl = function() {
        return (window.AUTHGUARD_BACKEND_URL ||
                localStorage.getItem('zrok_url') ||
                'http://localhost:5000').replace(/\/$/, '');
    };

    window.getCurrentUser = function() {
        const email = localStorage.getItem(EMAIL_KEY);
        const name  = localStorage.getItem(NAME_KEY);
        if (!email) return null;
        return { email, name: name || email.split('@')[0] };
    };

    window.authLogout = function() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(EMAIL_KEY);
        localStorage.removeItem(NAME_KEY);
        location.href = '/login.html';
    };

    /**
     * Injects a small auth pill into a given container element.
     * - If logged in: shows avatar circle + email + logout button.
     * - If not logged in: shows a "Sign In" link.
     */
        window.injectNavAuthState = function(containerEl) {
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
            containerEl.innerHTML = `
                <div style="display:flex;align-items:center;gap:12px;width:100%;justify-content:center;">
                    <a href="login.html" class="nav-signin-btn" style="text-decoration:none;font-size:14px;font-weight:600;color:#fff;background:rgba(255,255,255,0.1);padding:8px 18px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);transition:all 0.2s;display:flex;align-items:center;gap:8px;">
                        <i class="fa-solid fa-right-to-bracket"></i> Sign In
                    </a>
                    <a href="login.html" class="nav-signup-btn hide-on-mobile" style="text-decoration:none;font-size:14px;font-weight:600;color:#fff;background:linear-gradient(135deg, #06b6d4, #8b5cf6);padding:8px 18px;border-radius:8px;transition:all 0.2s;">
                        Get Started
                    </a>
                </div>
            `;
        }
    };

    // Also re-inject nav state after gate increments
    const oldCheck = window.checkScanGate;
    window.checkScanGate = function() {
    return true; // Pricing and scan limits have been removed
};


window.getCurrentUser() && document.getElementById('nav-auth')) {
            window.injectNavAuthState(document.getElementById('nav-auth'));
        }
        return res;
    };
    
    // --- Premium Scan Gate ---
    window.checkScanGate = function() {
    return true; // Pricing and scan limits have been removed
};


window.getCurrentUser()) return true; // Logged in, unlimited

        let scans = parseInt(localStorage.getItem('free_scans_used') || '0', 10);
        
        if (scans < 2) {
            scans += 1;
            localStorage.setItem('free_scans_used', scans.toString());
            
            // Show a non-blocking toast
            const toast = document.createElement('div');
            toast.style.cssText = 'position:fixed;bottom:20px;right:20px;background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);backdrop-filter:blur(10px);color:#fff;padding:12px 20px;border-radius:8px;font-size:13px;font-weight:600;z-index:9999;box-shadow:0 10px 30px rgba(0,0,0,0.5);animation:slideUp 0.3s ease;';
            toast.innerHTML = '<i class="fa-solid fa-bolt" style="color:#06b6d4;margin-right:8px;"></i> ' + scans + '/2 Free Scans Used';
            document.body.appendChild(toast);
            setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 3000);
            
            // Add keyframes if missing
            if (!document.getElementById('gate-styles')) {
                const style = document.createElement('style');
                style.id = 'gate-styles';
                style.textContent = '@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } } @keyframes modalFadeIn { from { opacity: 0; backdrop-filter: blur(0px); } to { opacity: 1; backdrop-filter: blur(10px); } } @keyframes modalPop { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }';
                document.head.appendChild(style);
            }
            
            return true;
        }

        // Limit reached, show blocking modal
        if (!document.getElementById('gate-modal')) {
            const overlay = document.createElement('div');
            overlay.id = 'gate-modal';
            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(10,10,15,0.8);backdrop-filter:blur(10px);z-index:10000;display:flex;align-items:center;justify-content:center;animation:modalFadeIn 0.3s ease;';
            
            const modal = document.createElement('div');
            modal.style.cssText = 'background:#12121a;border:1px solid rgba(255,255,255,0.1);padding:40px;border-radius:24px;width:90%;max-width:440px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.8);animation:modalPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);position:relative;';
            
            modal.innerHTML = `
                <button onclick="document.getElementById('gate-modal').remove()" style="position:absolute;top:20px;right:20px;background:none;border:none;color:#94a3b8;cursor:pointer;font-size:20px;transition:color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#94a3b8'"><i class="fa-solid fa-xmark"></i></button>
                <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg, rgba(6,182,212,0.2), rgba(139,92,246,0.2));display:flex;align-items:center;justify-content:center;margin:0 auto 24px auto;border:1px solid rgba(255,255,255,0.05);">
                    <i class="fa-solid fa-lock" style="font-size:28px;background:linear-gradient(135deg,#06b6d4,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"></i>
                </div>
                <h2 style="color:#fff;font-size:24px;margin-bottom:12px;font-family:inherit;font-weight:700;">Free Limit Reached</h2>
                <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin-bottom:32px;">You've used your 2 free anonymous scans. Create a free account to unlock unlimited scans, history, and detailed AI analysis reports.</p>
                
                <a href="/login.html" style="display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:14px;background:#fff;color:#0a0a0f;text-decoration:none;border-radius:12px;font-weight:600;font-size:15px;transition:transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">
                    <i class="fa-solid fa-right-to-bracket"></i> Sign In to Continue
                </a>
            `;
            overlay.appendChild(modal);
            document.body.appendChild(overlay);
        }

        return false; // Block scan
    };

})(window);


