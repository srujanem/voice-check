import os
import re

server_path = r'D:\Server\ai-training-panel\node_server\server.js'

with open(server_path, 'r', encoding='utf-8') as f:
    content = f.read()

stripe_code = '''
// ==========================================
// Stripe Payment Integration
// ==========================================
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY || 'sk_test_mock_secret_key');

app.post('/api/create-checkout-session', async (req, res) => {
    try {
        const { email } = req.body;
        
        // Mock Stripe Checkout for development if no real key provided
        if (!process.env.STRIPE_SECRET_KEY || process.env.STRIPE_SECRET_KEY === 'sk_test_mock_secret_key') {
            return res.json({ url: 'http://localhost:5000/mock_stripe_checkout?email=' + encodeURIComponent(email) });
        }
        
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            customer_email: email,
            line_items: [
                {
                    price_data: {
                        currency: 'usd',
                        product_data: {
                            name: 'AuthGuard Pro Subscription',
                            description: 'Unlimited AI Scans, PDF Reports, and Priority Processing.',
                        },
                        unit_amount: 900, // .00
                        recurring: { interval: 'month' }
                    },
                    quantity: 1,
                },
            ],
            mode: 'subscription',
            success_url: 'https://voice-check.vercel.app/dashboard.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url: 'https://voice-check.vercel.app/pricing.html',
        });
        
        res.json({ url: session.url });
    } catch (error) {
        console.error('[STRIPE] Error creating session:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/webhook', express.raw({ type: 'application/json' }), (req, res) => {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;
    
    let event;
    try {
        event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
        console.error('[STRIPE WEBHOOK ERROR]', err.message);
        return res.status(400).send(Webhook Error: );
    }
    
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object;
        console.log('[STRIPE] Payment successful for:', session.customer_email);
        
        // Upgrade user in local JSON database
        try {
            const usersPath = path.join(__dirname, 'users.json');
            if (fs.existsSync(usersPath)) {
                let users = JSON.parse(fs.readFileSync(usersPath, 'utf8'));
                let user = users.find(u => u.email === session.customer_email);
                if (user) {
                    user.is_pro = true;
                    fs.writeFileSync(usersPath, JSON.stringify(users, null, 2));
                    console.log([STRIPE] Upgraded user  to PRO);
                }
            }
        } catch (e) {
            console.error('[STRIPE] Error upgrading user:', e);
        }
    }
    
    res.json({ received: true });
});
'''

# Find the app.listen block
if 'app.listen(PORT' in content and 'create-checkout-session' not in content:
    content = content.replace('app.listen(PORT', stripe_code + '\n\napp.listen(PORT')
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Stripe endpoints injected into server.js")
else:
    print("Stripe endpoints already exist or app.listen not found.")
