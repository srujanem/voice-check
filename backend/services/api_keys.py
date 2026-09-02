import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from backend.config import Config

DB_PATH = os.path.join(Config.BASE_DIR, "api_keys.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'free',
            key_hash TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Insert a demo key for frontend testing
    demo_key = "demo_key_123"
    demo_hash = hashlib.sha256(demo_key.encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO api_keys (user_id, tier, key_hash, created_at) VALUES (?, ?, ?, ?)",
              ("demo_user", "free", demo_hash, datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()

init_db()

def generate_api_key(user_id, tier="free"):
    raw_key = "authguard_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO api_keys (user_id, tier, key_hash, created_at) VALUES (?, ?, ?, ?)",
              (user_id, tier, key_hash, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    
    return raw_key

def validate_api_key(raw_key):
    if not raw_key:
        return None
        
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, tier FROM api_keys WHERE key_hash = ?", (key_hash,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {"user_id": result[0], "tier": result[1]}
    return None

def get_rate_limit(tier):
    if tier == "enterprise":
        return "1000 per minute"
    elif tier == "pro":
        return "100 per minute"
    else:
        return "5 per minute"
