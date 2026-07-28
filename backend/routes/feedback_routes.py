"""
Feedback route — receives feedback from the website and emails it to the owner.
"""

from flask import Blueprint, request, jsonify
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__)

# ── Email configuration ──────────────────────────────────────────────────────
OWNER_EMAIL    = os.environ.get("FEEDBACK_TO_EMAIL",   "srujanem222@gmail.com")
SENDER_EMAIL   = os.environ.get("FEEDBACK_FROM_EMAIL", "srujanem222@gmail.com")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASSWORD",  "")   # set via env var


def send_feedback_email(name: str, email: str, subject: str, message: str, rating: str = "") -> bool:
    """Send a formatted feedback email via Gmail SMTP."""
    if not GMAIL_APP_PASS:
        print("[Feedback] ERROR: GMAIL_APP_PASSWORD env var not set.")
        return False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── HTML email body ──────────────────────────────────────────────────────
    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; background: #0f0f1a; color: #e2e8f0; margin: 0; padding: 0;">
      <div style="max-width: 600px; margin: 0 auto; padding: 30px;">

        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px 12px 0 0; padding: 24px 30px;">
          <h1 style="margin: 0; color: #fff; font-size: 22px;">
            📬 New Feedback — AuthGuard
          </h1>
          <p style="margin: 6px 0 0; color: rgba(255,255,255,0.75); font-size: 13px;">{now}</p>
        </div>

        <!-- Body -->
        <div style="background: #1e1e2e; border-radius: 0 0 12px 12px;
                    padding: 28px 30px; border: 1px solid rgba(255,255,255,0.08);">

          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
                          color: #a0aec0; font-size: 13px; width: 120px; font-weight: 600;">👤 Name</td>
              <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
                          color: #e2e8f0; font-size: 14px;">{name or "—"}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
                          color: #a0aec0; font-size: 13px; font-weight: 600;">📧 Email</td>
              <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
                          color: #e2e8f0; font-size: 14px;">
                <a href="mailto:{email}" style="color: #667eea;">{email or "—"}</a>
              </td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
                          color: #a0aec0; font-size: 13px; font-weight: 600;">📌 Subject</td>
              <td style="padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
                          color: #e2e8f0; font-size: 14px;">{subject or "General Feedback"}</td>
            </tr>
            {"<tr><td style='padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.08);color:#a0aec0;font-size:13px;font-weight:600;'>⭐ Rating</td><td style='padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.08);color:#e2e8f0;font-size:14px;'>" + rating + "</td></tr>" if rating else ""}
          </table>

          <!-- Message box -->
          <div style="margin-top: 20px;">
            <p style="color: #a0aec0; font-size: 13px; font-weight: 600; margin-bottom: 8px;">💬 Message</p>
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 8px; padding: 16px; color: #e2e8f0; font-size: 14px;
                        line-height: 1.6; white-space: pre-wrap;">{message}</div>
          </div>

          <p style="margin-top: 24px; font-size: 12px; color: #4a5568; text-align: center;">
            Sent via AuthGuard AI Detection Platform feedback system
          </p>
        </div>
      </div>
    </body></html>
    """

    # ── Compose & send ───────────────────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[AuthGuard Feedback] {subject or 'New message'} — from {name or 'Anonymous'}"
    msg["From"]    = f"AuthGuard Feedback <{SENDER_EMAIL}>"
    msg["To"]      = OWNER_EMAIL
    msg["Reply-To"] = email if email else SENDER_EMAIL

    msg.attach(MIMEText(f"From: {name} <{email}>\n\n{message}", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(SENDER_EMAIL, GMAIL_APP_PASS)
            server.sendmail(SENDER_EMAIL, OWNER_EMAIL, msg.as_string())
        print(f"[Feedback] ✅ Email sent from {email} to {OWNER_EMAIL}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[Feedback] ❌ Gmail authentication failed — check GMAIL_APP_PASSWORD")
        return False
    except Exception as e:
        print(f"[Feedback] ❌ Failed to send email: {e}")
        return False


@feedback_bp.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """
    Accepts feedback from the website and emails it to the owner.

    JSON body:
      name    — sender's name (optional)
      email   — sender's email (optional)
      subject — subject/category (optional)
      message — feedback text (required)
      rating  — star rating string e.g. "5 ⭐" (optional)
    """
    data = request.get_json(silent=True) or {}

    name    = str(data.get("name",    "")).strip()[:100]
    email   = str(data.get("email",   "")).strip()[:100]
    subject = str(data.get("subject", "")).strip()[:200]
    message = str(data.get("message", "")).strip()[:3000]
    rating  = str(data.get("rating",  "")).strip()[:20]

    if not message:
        return jsonify({"error": "Message is required."}), 400

    # Basic email format check
    import re
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Invalid email address."}), 400

    success = send_feedback_email(name, email, subject, message, rating)

    if success:
        return jsonify({"success": True, "message": "Thank you! Your feedback has been sent."})
    else:
        # Store locally as fallback if email fails
        _save_feedback_locally(name, email, subject, message, rating)
        return jsonify({
            "success": True,
            "message": "Feedback received! (email delivery pending — check server config)"
        })


def _save_feedback_locally(name, email, subject, message, rating):
    """Fallback: save feedback to a local JSON file if email fails."""
    import json
    path = "feedback_backup.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "name": name, "email": email,
        "subject": subject, "message": message, "rating": rating
    }
    existing = []
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                existing = json.load(f)
        except Exception:
            pass
    existing.append(entry)
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"[Feedback] Saved locally to {path}")
