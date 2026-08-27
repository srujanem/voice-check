"""
AuthGuard Watchdog -- Keeps Flask + Cloudflare Tunnel alive 24/7.
Run once: python watchdog.py
It will auto-restart both processes if they crash, and update server-config.js
with the new tunnel URL automatically.
"""

import subprocess
import time
import re
import os
import sys
import signal
import threading

FLASK_CMD = [sys.executable, "run.py"]
CLOUDFLARED = r"C:\voice-check\cloudflared.exe"
TUNNEL_CMD = [CLOUDFLARED, "tunnel", "--url", "http://localhost:5000", "--no-autoupdate"]
SERVER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "server-config.js")

flask_proc = None
tunnel_proc = None
tunnel_url = None
running = True


def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def update_server_config(url):
    """Patch server-config.js with the new tunnel URL."""
    try:
        with open(SERVER_CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = re.sub(
            r"const DEFAULT_URL = '[^']*'",
            f"const DEFAULT_URL = '{url}'",
            content
        )
        with open(SERVER_CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        log(f"server-config.js updated -> {url}")
    except Exception as e:
        log(f"WARNING: Could not update server-config.js: {e}")


def start_flask():
    global flask_proc
    log("Starting Flask backend...")
    flask_proc = subprocess.Popen(
        FLASK_CMD,
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    log(f"Flask PID: {flask_proc.pid}")


def start_tunnel():
    global tunnel_proc, tunnel_url
    log("Starting Cloudflare Tunnel...")
    tunnel_proc = subprocess.Popen(
        TUNNEL_CMD,
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    log(f"Tunnel PID: {tunnel_proc.pid}")

    def read_tunnel_output():
        global tunnel_url
        for line in tunnel_proc.stdout:
            line = line.strip()
            if "trycloudflare.com" in line:
                match = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", line)
                if match:
                    tunnel_url = match.group(0)
                    log(f"TUNNEL URL: {tunnel_url}")
                    update_server_config(tunnel_url)
            if line:
                print(f"  [tunnel] {line}", flush=True)

    t = threading.Thread(target=read_tunnel_output, daemon=True)
    t.start()


def is_alive(proc):
    return proc is not None and proc.poll() is None


def shutdown(signum, frame):
    global running
    log("Shutting down watchdog...")
    running = False
    if flask_proc:
        flask_proc.terminate()
    if tunnel_proc:
        tunnel_proc.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


def main():
    log("=" * 55)
    log("  AuthGuard Watchdog -- 24/7 Auto-Restart")
    log("  Press Ctrl+C to stop")
    log("=" * 55)

    # Start Flask first, wait for models to load, then tunnel
    start_flask()
    time.sleep(20)  # Wait 20s for ML models to load
    start_tunnel()

    check_interval = 20  # Check every 20 seconds

    while running:
        time.sleep(check_interval)

        if not is_alive(flask_proc):
            log("ALERT: Flask crashed! Restarting in 5s...")
            time.sleep(5)
            start_flask()
            time.sleep(20)

        if not is_alive(tunnel_proc):
            log("ALERT: Tunnel crashed! Restarting in 5s...")
            time.sleep(5)
            start_tunnel()

        flask_ok = "UP" if is_alive(flask_proc) else "DOWN"
        tunnel_ok = "UP" if is_alive(tunnel_proc) else "DOWN"
        url_str = tunnel_url or "pending..."
        log(f"Heartbeat | Flask:{flask_ok}  Tunnel:{tunnel_ok}  URL:{url_str}")


if __name__ == "__main__":
    main()
