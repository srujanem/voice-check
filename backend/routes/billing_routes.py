from flask import Blueprint, request, jsonify, redirect
import os
import stripe
from backend.decorators import require_api_key

billing_bp = Blueprint("billing_bp", __name__)

# Configure Stripe (User can add their real key to env vars)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock_key")

@billing_bp.route("/api/billing/create-checkout-session", methods=["POST"])
@require_api_key
def create_checkout_session():
    try:
        data = request.json
        plan_type = data.get("plan", "pro")
        
        # If no real Stripe key is configured, simulate the checkout process for the demo
        if stripe.api_key == "sk_test_mock_key":
            return jsonify({
                "url": "/billing-success.html?session_id=mock_session_123&plan=" + plan_type
            })

        # Real Stripe Integration
        price_id = "price_pro_19_mo" if plan_type == "pro" else "price_enterprise_99_mo"
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=request.host_url + "billing-success.html?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.host_url + "dashboard.html",
            client_reference_id=request.user.get("uid", "guest")
        )
        return jsonify({"url": session.url})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
