import re

with open('c:/voice-check/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace onclick
content = content.replace(
    '''onclick="alert('Redirecting to Stripe Secure Checkout...')"''',
    '''onclick="upgradePlan('pro')"'''
)
content = content.replace(
    '''onclick="alert('Enterprise inquiry submitted! Our team will reach out.')"''',
    '''onclick="upgradePlan('enterprise')"'''
)

# Append script
script = '''
<script>
async function upgradePlan(plan) {
    if (!localStorage.getItem('token')) {
        alert('Please log in first to upgrade.');
        return;
    }
    
    // Create checkout session
    try {
        const response = await fetch(SERVER_URL + '/api/billing/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ plan: plan })
        });
        
        const data = await response.json();
        if (data.url) {
            window.location.href = data.url;
        } else {
            alert('Checkout error: ' + (data.error || 'Unknown error'));
        }
    } catch (e) {
        console.error(e);
        alert('Failed to connect to billing server. Is the server running?');
    }
}
</script>
'''

if 'upgradePlan' not in content:
    content = content.replace('</body>', script + '\n</body>')

with open('c:/voice-check/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated dashboard.html with Stripe integration script')
