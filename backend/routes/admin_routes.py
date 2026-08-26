from flask import Blueprint, jsonify, request
import sqlite3
import os
from datetime import datetime

admin_bp = Blueprint("admin_bp", __name__)

DB_PATH = "c:/voice-check/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create users table for lead capture
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid TEXT PRIMARY KEY,
            email TEXT,
            name TEXT,
            plan TEXT DEFAULT 'free',
            scans_used INTEGER DEFAULT 0,
            last_login TIMESTAMP
        )
    ''')
    # Insert a dummy user just so the table isn't empty for the demo
    c.execute("INSERT OR IGNORE INTO users (uid, email, name, plan, scans_used, last_login) VALUES (?, ?, ?, ?, ?, ?)",
              ("demo_1", "investor@example.com", "John Doe", "pro", 42, datetime.now()))
    conn.commit()
    conn.close()

init_db()

@admin_bp.route("/api/admin/stats", methods=["GET"])
def get_admin_stats():
    # In a real app, you'd secure this with an admin token check
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE plan='pro'")
        pro_users = c.fetchone()[0]
        
        c.execute("SELECT SUM(scans_used) FROM users")
        total_scans = c.fetchone()[0] or 0
        
        c.execute("SELECT email, name, plan, scans_used FROM users ORDER BY last_login DESC LIMIT 10")
        recent_users = [{"email": r[0], "name": r[1], "plan": r[2], "scans": r[3]} for r in c.fetchall()]
        
        conn.close()
        
        return jsonify({
            "total_users": total_users,
            "pro_users": pro_users,
            "total_scans": total_scans,
            "mrr": pro_users * 19, # Monthly Recurring Revenue
            "recent_users": recent_users
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/admin/register_login", methods=["POST"])
def register_login():
    """Captures lead info when someone logs in via Google"""
    data = request.json
    uid = data.get("uid")
    email = data.get("email")
    name = data.get("name")
    
    if not uid or not email:
        return jsonify({"error": "Missing data"}), 400
        
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT uid FROM users WHERE uid=?", (uid,))
        if c.fetchone():
            c.execute("UPDATE users SET last_login=?, name=?, email=? WHERE uid=?", (datetime.now(), name, email, uid))
        else:
            c.execute("INSERT INTO users (uid, email, name, last_login) VALUES (?, ?, ?, ?)", 
                      (uid, email, name, datetime.now()))
                      
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
