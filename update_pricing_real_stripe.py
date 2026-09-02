import os
import re

pricing_path = r'D:\voice-check\voice-check\pricing.html'

with open(pricing_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the checkout.html link with a real API call button
old_button = '<a href="checkout.html" class="btn-pricing btn-primary">Upgrade to Pro</a>'
new_button = '''<button class="btn-pricing btn-primary" onclick="initiateStripeCheckout(this)">Upgrade to Pro</button>'''

script = '''
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            if (window.injectNavAuthState) {
                window.injectNavAuthState(document.getElementById('nav-auth'));
            }
        });

        async function initiateStripeCheckout(btn) {
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Loading Secure Checkout...';
            btn.style.opacity = '0.8';
            btn.disabled = true;

            try {
                let userEmail = 'guest@example.com';
                if (window.getCurrentUser) {
                    const user = window.getCurrentUser();
                    if (user && user.email) userEmail = user.email;
                }

                // Call the real Node.js backend
                let backendUrl = (localStorage.getItem('zrok_url') || 'http://localhost:5000').replace(/\/$/, '');
                if (backendUrl === 'http://localhost:8000') backendUrl = 'http://localhost:5000';

                const response = await fetch(${backendUrl}/api/create-checkout-session, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: userEmail })
                });

                const data = await response.json();
                
                if (data.url) {
                    // Redirect to Official Stripe Checkout
                    window.location.href = data.url;
                } else {
                    throw new Error('No checkout URL returned');
                }
            } catch (err) {
                console.error(err);
                alert('Checkout failed to initialize. Please try again.');
                btn.innerHTML = 'Upgrade to Pro';
                btn.style.opacity = '1';
                btn.disabled = false;
            }
        }
    </script>
'''

if old_button in content:
    content = content.replace(old_button, new_button)
    # Replace the existing script tag with the new one
    content = re.sub(r'<script>\s*document\.addEventListener[\s\S]*?</script>', script, content)
    
    with open(pricing_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated pricing.html for REAL Stripe checkout!")
else:
    print("Could not find old button.")
