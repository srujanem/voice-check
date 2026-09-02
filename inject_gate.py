import os
import glob
import re

auth_js_path = r'D:\voice-check\voice-check\auth.js'

with open(auth_js_path, 'r', encoding='utf-8') as f:
    auth_content = f.read()

# Add the gate function if not there
if 'window.checkScanGate' not in auth_content:
    gate_code = '''

    // --- Premium Scan Gate ---
    window.checkScanGate = function() {
        if (window.getCurrentUser()) return true; // Logged in, unlimited

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
            
            modal.innerHTML = 
                <button onclick="document.getElementById('gate-modal').remove()" style="position:absolute;top:20px;right:20px;background:none;border:none;color:#94a3b8;cursor:pointer;font-size:20px;transition:color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#94a3b8'"><i class="fa-solid fa-xmark"></i></button>
                <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg, rgba(6,182,212,0.2), rgba(139,92,246,0.2));display:flex;align-items:center;justify-content:center;margin:0 auto 24px auto;border:1px solid rgba(255,255,255,0.05);">
                    <i class="fa-solid fa-lock" style="font-size:28px;background:linear-gradient(135deg,#06b6d4,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"></i>
                </div>
                <h2 style="color:#fff;font-size:24px;margin-bottom:12px;font-family:inherit;font-weight:700;">Free Limit Reached</h2>
                <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin-bottom:32px;">You've used your 2 free anonymous scans. Create a free account to unlock unlimited scans, history, and detailed AI analysis reports.</p>
                
                <a href="/login.html" style="display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:14px;background:#fff;color:#0a0a0f;text-decoration:none;border-radius:12px;font-weight:600;font-size:15px;transition:transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">
                    <i class="fa-solid fa-right-to-bracket"></i> Sign In to Continue
                </a>
            ;
            overlay.appendChild(modal);
            document.body.appendChild(overlay);
        }

        return false; // Block scan
    };
'''
    auth_content = auth_content.replace('})(window);', gate_code + '\n})(window);')
    with open(auth_js_path, 'w', encoding='utf-8') as f:
        f.write(auth_content)
    print("Updated auth.js with gate logic.")


# Now inject into scripts
script_files = glob.glob(r'D:\voice-check\voice-check\*-ui\script.js')
for sf in script_files:
    with open(sf, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to inject if (window.checkScanGate && !window.checkScanGate()) return;
    # at the top of the event listener callback
    
    # Regex to find event listener
    patterns = [
        r"(btnAnalyze\.addEventListener\('click',\s*async\s*\(\)\s*=>\s*\{)",
        r"(analyzeBtn\.addEventListener\('click',\s*\(\)\s*=>\s*\{)",
        r"(btnProtect\.addEventListener\('click',\s*async\s*\(\)\s*=>\s*\{)"
    ]
    
    changed = False
    for pat in patterns:
        if re.search(pat, content):
            if 'window.checkScanGate' not in content:
                content = re.sub(pat, r"\1\n        if (window.checkScanGate && !window.checkScanGate()) return;", content)
                changed = True
                
    if changed:
        with open(sf, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Injected gate into {os.path.basename(os.path.dirname(sf))}/script.js")

