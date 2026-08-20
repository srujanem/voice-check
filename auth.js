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
                <div style="display:flex;align-items:center;gap:10px;font-family:inherit;">
                    <a href="/dashboard.html" style="text-decoration:none;"><div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#06b6d4,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0;box-shadow:0 0 10px rgba(6,182,212,0.3);transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform=''">${initials}</div></a>
                    <a href="/dashboard.html" class="hide-on-mobile" style="font-size:13px;font-weight:600;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary);text-decoration:none;transition:color 0.2s;" onmouseover="this.style.color='var(--accent-cyan)'" onmouseout="this.style.color='var(--text-primary)'">${user.email}</a>
                    <button onclick="authLogout()" style="background:none;border:1px solid rgba(239,68,68,0.3);color:#ef4444;padding:4px 10px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:600;font-family:inherit;transition:all 0.2s;" onmouseover="this.style.background='rgba(239,68,68,0.1)'" onmouseout="this.style.background='none'">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i> <span class="hide-on-mobile">Logout</span>
                    </button>
                </div>`;
        } else {
            containerEl.innerHTML = `
                <a href="/signin.html" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:8px;background:linear-gradient(135deg,#06b6d4,#8b5cf6);color:#fff;text-decoration:none;font-size:13px;font-weight:600;font-family:inherit;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform=''">
                    <i class="fa-solid fa-right-to-bracket"></i> Sign In
                </a>`;
        }
    };

})(window);


