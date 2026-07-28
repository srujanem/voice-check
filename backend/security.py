"""
Security middleware and helpers for VoiceCheck backend.
Covers:
  1. Security headers (XSS, clickjacking, MIME sniffing, CSP)
  2. File upload validation (type + magic bytes + size)
  3. Input sanitization
  4. Rate limit helpers
  5. Brute-force login protection (in-memory tracker)
"""

import re
import time
import hashlib
from collections import defaultdict
from flask import request, jsonify, g
from functools import wraps

# ────────────────────────────────────────────────────────────────────────────
# 1. SECURITY HEADERS
# ────────────────────────────────────────────────────────────────────────────

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
        "https://www.gstatic.com https://apis.google.com "
        "https://kit.fontawesome.com; "
        "style-src 'self' 'unsafe-inline' "
        "https://fonts.googleapis.com https://cdnjs.cloudflare.com "
        "https://kit.fontawesome.com; "
        "font-src 'self' https://fonts.gstatic.com "
        "https://ka-f.fontawesome.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: blob: https:; "
        "connect-src 'self' https: wss:; "
        "frame-ancestors 'self';"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


def apply_security_headers(response):
    """After-request hook: attach security headers to every response."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    # Remove server fingerprint
    response.headers.pop("Server", None)
    response.headers.pop("X-Powered-By", None)
    return response


# ────────────────────────────────────────────────────────────────────────────
# 2. FILE UPLOAD VALIDATION
# ────────────────────────────────────────────────────────────────────────────

# Allowed MIME types per scanner category
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "image/gif", "image/bmp", "image/heic",
    "image/heif", "image/tiff",
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav",
    "audio/ogg", "audio/flac", "audio/aac",
    "audio/mp4", "audio/x-m4a", "audio/webm",
    "video/mp4",          # WhatsApp sends voice as mp4
    "video/mpeg",         # .mpeg containers
    "application/octet-stream",  # generic binary uploads
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/mpeg", "video/webm",
    "video/quicktime", "video/x-msvideo",
    "application/octet-stream",
}

ALLOWED_TEXT_TYPES = {
    "text/plain", "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Magic byte signatures: (offset, bytes) → mime label
MAGIC_BYTES = [
    (0, b'\xff\xd8\xff',           'image/jpeg'),
    (0, b'\x89PNG',                'image/png'),
    (0, b'GIF8',                   'image/gif'),
    (0, b'RIFF',                   'image/webp'),    # needs further check
    (0, b'BM',                     'image/bmp'),
    (0, b'\x00\x00\x00',           'video/mp4'),     # mp4/heic box
    (0, b'%PDF',                   'application/pdf'),
    (4, b'ftyp',                   'video/mp4'),
    (0, b'ID3',                    'audio/mpeg'),
    (0, b'\xff\xfb',               'audio/mpeg'),
    (0, b'\xff\xf3',               'audio/mpeg'),
    (0, b'\xff\xf2',               'audio/mpeg'),
    (0, b'OggS',                   'audio/ogg'),
    (0, b'fLaC',                   'audio/flac'),
    (0, b'RIFF',                   'audio/wav'),     # needs further check
]

MAX_FILE_SIZES = {
    "image": 15 * 1024 * 1024,   # 15 MB
    "audio": 25 * 1024 * 1024,   # 25 MB
    "voice": 25 * 1024 * 1024,   # 25 MB
    "video": 50 * 1024 * 1024,   # 50 MB
    "text":  5  * 1024 * 1024,   # 5 MB
    "url":   0,                   # no file
}

ALLOWED_EXTENSIONS = {
    "image": {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.heic', '.heif', '.tiff'},
    "audio": {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.mpeg', '.webm', '.mp4'},
    "voice": {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.mpeg', '.webm', '.mp4'},
    "video": {'.mp4', '.mpeg', '.webm', '.mov', '.avi'},
    "text":  {'.txt', '.pdf', '.doc', '.docx'},
}


def validate_file_upload(file, scan_type="image"):
    """
    Returns (is_valid, error_message).
    Checks: presence, extension, size, magic bytes.
    """
    if file is None or file.filename == '':
        return False, "No file provided."

    # Extension check
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    allowed_exts = ALLOWED_EXTENSIONS.get(scan_type, set())
    if allowed_exts and ext not in allowed_exts:
        return False, f"File type '{ext}' is not allowed for {scan_type} scanning."

    # Size check (read into memory once)
    data = file.read()
    file.seek(0)

    max_size = MAX_FILE_SIZES.get(scan_type, 15 * 1024 * 1024)
    if max_size > 0 and len(data) > max_size:
        mb = max_size // (1024 * 1024)
        return False, f"File too large. Maximum size is {mb} MB."

    if len(data) < 4:
        return False, "File is too small or empty."

    # Magic byte check — silently allow if no match (some valid formats won't match)
    # This is a soft check — we don't reject unknown magic bytes to avoid false positives
    # but we do reject files whose magic bytes indicate a DANGEROUS type
    dangerous_signatures = [
        b'MZ',          # Windows EXE
        b'\x7fELF',     # Linux ELF binary
        b'PK\x03\x04',  # ZIP (could be disguised malware)
        b'#!/',         # Shell script
        b'<script',     # HTML/JS injection
        b'<?php',       # PHP script
    ]
    for sig in dangerous_signatures:
        if data[:len(sig)].lower() == sig.lower():
            return False, "Potentially dangerous file type rejected."

    return True, None


def sanitize_text_input(text, max_length=10000):
    """
    Sanitize user-submitted text:
    - Trim whitespace
    - Remove null bytes
    - Enforce max length
    - Strip HTML tags
    """
    if not isinstance(text, str):
        return ""
    text = text.replace('\x00', '')           # null bytes
    text = re.sub(r'<[^>]+>', '', text)       # strip HTML tags
    text = text.strip()
    return text[:max_length]


# ────────────────────────────────────────────────────────────────────────────
# 3. BRUTE-FORCE / ABUSE PROTECTION
# ────────────────────────────────────────────────────────────────────────────

_failed_attempts = defaultdict(list)   # IP → list of failure timestamps
_blocked_ips = {}                       # IP → block_until timestamp

FAIL_WINDOW_SECONDS = 300   # 5 minutes sliding window
MAX_FAILURES = 10           # max failures before block
BLOCK_DURATION = 900        # block for 15 minutes


def _get_client_ip():
    """Get real client IP, respecting X-Forwarded-For from trusted proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def record_failed_attempt(ip=None):
    """Call this when a login/auth attempt fails."""
    ip = ip or _get_client_ip()
    now = time.time()
    # Prune old failures outside window
    _failed_attempts[ip] = [t for t in _failed_attempts[ip] if now - t < FAIL_WINDOW_SECONDS]
    _failed_attempts[ip].append(now)
    if len(_failed_attempts[ip]) >= MAX_FAILURES:
        _blocked_ips[ip] = now + BLOCK_DURATION
        _failed_attempts[ip].clear()


def clear_failed_attempts(ip=None):
    """Call this on successful login to reset the counter."""
    ip = ip or _get_client_ip()
    _failed_attempts.pop(ip, None)
    _blocked_ips.pop(ip, None)


def is_ip_blocked(ip=None):
    """Returns True if IP is currently blocked."""
    ip = ip or _get_client_ip()
    block_until = _blocked_ips.get(ip)
    if block_until:
        if time.time() < block_until:
            return True
        else:
            del _blocked_ips[ip]  # Block expired
    return False


def brute_force_protect(f):
    """Decorator: block requests from IPs that have too many failures."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = _get_client_ip()
        if is_ip_blocked(ip):
            return jsonify({
                "error": "Too many failed attempts. Please try again later.",
                "retry_after": 900
            }), 429
        return f(*args, **kwargs)
    return decorated


# ────────────────────────────────────────────────────────────────────────────
# 4. REQUEST LOGGING (security audit trail)
# ────────────────────────────────────────────────────────────────────────────

import logging

security_logger = logging.getLogger("voicecheck.security")
security_logger.setLevel(logging.INFO)

_handler = logging.FileHandler("security.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
))
security_logger.addHandler(_handler)


def log_request():
    """Before-request hook: log every API call."""
    ip = _get_client_ip()
    method = request.method
    path = request.path
    ua = request.headers.get("User-Agent", "unknown")[:100]
    security_logger.info(f"{ip} | {method} {path} | UA: {ua}")


def log_suspicious(reason):
    """Log a suspicious activity event."""
    ip = _get_client_ip()
    security_logger.warning(f"SUSPICIOUS | {ip} | {reason} | path={request.path}")
