/**
 * auth.js — Shared auth helper used by all detection UIs
 *
 * Provides:
 *   getAuthHeaders()   → { Authorization: 'Bearer <token>' } or {}
 *   getBackendUrl()    → the active backend URL
 *   getCurrentUser()   → { email, name } or null
 *   authLogout()       → clears auth state
 *   injectNavAuthState(containerEl) → clean navigation state (no sign-in barrier)
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
        location.reload();
    };

    /**
     * Injects nav auth state.
     * Note: Sign-in / payment options are removed as requested.
     * If user is already logged in, shows a subtle user badge and logout.
     * If not logged in, leaves container clean (no sign-in button).
     */
    window.injectNavAuthState = function(containerEl) {
        if (!containerEl) return;
        const user = window.getCurrentUser();
        if (user) {
            const initials = user.name.slice(0, 2).toUpperCase();
            containerEl.innerHTML = `
                <div style="display:flex;align-items:center;gap:8px;font-family:inherit;">
                    <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#06b6d4,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;flex-shrink:0;">${initials}</div>
                    <span style="font-size:12px;font-weight:600;max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-secondary);">${user.name}</span>
                    <button onclick="authLogout()" style="background:none;border:1px solid rgba(239,68,68,0.3);color:#ef4444;padding:3px 8px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:600;font-family:inherit;transition:all 0.2s;touch-action:manipulation;" title="Sign out">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i>
                    </button>
                </div>`;
        } else {
            // Frictionless mode: completely remove Sign In button
            containerEl.innerHTML = '';
        }
    };

})(window);
