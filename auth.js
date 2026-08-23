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
     * - If not logged in: shows "Sign In" and "Get Started" buttons.
     */
    window.injectNavAuthState = function(containerEl) {
        if (!containerEl) return;
        const user = window.getCurrentUser();
        if (user) {
            const initials = (user.name || user.email || 'U').slice(0, 2).toUpperCase();
            containerEl.innerHTML = `
                <div style="display:flex;align-items:center;gap:12px;font-family:inherit;">
                    <span style="font-size:11px;font-weight:700;color:#10b981;background:rgba(16,185,129,0.12);padding:4px 10px;border-radius:20px;border:1px solid rgba(16,185,129,0.25);"><i class="fa-solid fa-shield-halved"></i> Active</span>
                    <a href="dashboard.html" style="text-decoration:none;"><div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#06b6d4,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0;box-shadow:0 0 12px rgba(6,182,212,0.4);">${initials}</div></a>
                    <a href="dashboard.html" class="hide-on-mobile" style="font-size:13px;font-weight:600;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#f1f5f9;text-decoration:none;">${user.email}</a>
                    <button onclick="authLogout()" style="background:none;border:1px solid rgba(239,68,68,0.3);color:#ef4444;padding:5px 12px;border-radius:8px;cursor:pointer;font-size:11px;font-weight:600;font-family:inherit;transition:all 0.2s;">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i> <span class="hide-on-mobile">Logout</span>
                    </button>
                </div>`;
        } else {
            containerEl.innerHTML = `
                <div style="display:flex;align-items:center;gap:10px;">
                    <a href="login.html" style="text-decoration:none;font-size:13px;font-weight:600;color:#f1f5f9;background:rgba(255,255,255,0.06);padding:7px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.12);transition:all 0.2s;display:inline-flex;align-items:center;gap:6px;">
                        <i class="fa-solid fa-right-to-bracket" style="color:#06b6d4;"></i> Sign In
                    </a>
                    <a href="login.html" class="hide-on-mobile" style="text-decoration:none;font-size:13px;font-weight:700;color:#fff;background:linear-gradient(135deg, #06b6d4, #8b5cf6);padding:7px 16px;border-radius:10px;box-shadow:0 0 15px rgba(6,182,212,0.3);transition:all 0.2s;">
                        Get Started
                    </a>
                </div>
            `;
        }
    };

    window.checkScanGate = function() {
        return true; // Free unlimited scanning enabled
    };

    // Auto-inject on DOM ready if container exists
    document.addEventListener('DOMContentLoaded', () => {
        const navAuth = document.getElementById('nav-auth');
        if (navAuth && window.injectNavAuthState) {
            window.injectNavAuthState(navAuth);
        }
    });

})(window);


