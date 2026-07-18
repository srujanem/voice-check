import os
import subprocess
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import urllib.request
import json

app = FastAPI(title="AI Shield Admin Dashboard")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "ai_shield.db")
UI_DIR = os.path.join(BASE_DIR, "dashboard_ui")

# Ensure UI dir exists
os.makedirs(UI_DIR, exist_ok=True)

# Mount the UI directory as static
app.mount("/static", StaticFiles(directory=UI_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(UI_DIR, "index.html"))

@app.get("/api/status")
async def get_server_status():
    """Check if the main server on port 8000 is reachable"""
    try:
        urllib.request.urlopen("http://localhost:8000/docs", timeout=1)
        return {"status": "online"}
    except:
        return {"status": "offline"}

@app.post("/api/server/start")
async def start_server():
    """Start the main server using the bat file"""
    try:
        # Check if already running
        try:
            urllib.request.urlopen("http://localhost:8000/docs", timeout=1)
            return {"message": "Server is already running"}
        except:
            pass
            
        bat_file = os.path.join(BASE_DIR, "START_SERVER.bat")
        subprocess.Popen(['cmd.exe', '/c', bat_file], cwd=BASE_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return {"message": "Server starting..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/server/stop")
async def stop_server():
    """Stop the main server using the bat file"""
    try:
        bat_file = os.path.join(BASE_DIR, "STOP_SERVER.bat")
        subprocess.run(['cmd.exe', '/c', bat_file], cwd=BASE_DIR, check=True)
        return {"message": "Server stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users")
async def get_recent_users():
    """Read recent users from SQLite DB"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # We try to get users. If table doesn't exist yet, return empty.
        cursor.execute("SELECT id, username, email, is_active, created_at FROM users ORDER BY created_at DESC LIMIT 10")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except sqlite3.OperationalError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gpu")
async def get_gpu_status():
    """Fetch GPU status. If main server is up, proxy it. Otherwise mock or read locally."""
    try:
        # Proxy from main server if alive
        req = urllib.request.urlopen("http://localhost:8000/api/stats/gpu", timeout=1)
        data = json.loads(req.read())
        return data
    except:
        # Fallback to local python torch check if server offline
        try:
            import torch
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                return {
                    "cuda_available": True,
                    "device_name": props.name,
                    "total_memory_gb": round(props.total_memory / 1024**3, 2),
                    "status": "IDLE (Server Offline)"
                }
        except:
            pass
        
        return {"cuda_available": False, "status": "Unknown/Offline"}

if __name__ == "__main__":
    print("Starting Admin Dashboard on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")
