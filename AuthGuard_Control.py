import tkinter as tk
from tkinter import scrolledtext, font
import subprocess
import threading
import sys
import os
import webbrowser
import requests
import time

# ─── Config ──────────────────────────────────────────────────────────────────
SERVER_DIR  = os.path.dirname(os.path.abspath(__file__))
SERVER_CMD  = [sys.executable, "run.py"]
HEALTH_URL  = "http://localhost:5000/api/health"
WEBSITE_URL = "https://authguard.vercel.app"

# ─── Colors ───────────────────────────────────────────────────────────────────
BG_MAIN    = "#0a0a0f"
BG_CARD    = "#0f172a"
BG_HOVER   = "#1e293b"
BORDER     = "#1e293b"
CYAN       = "#00f3ff"
PURPLE     = "#bc13fe"
GREEN      = "#10b981"
RED        = "#ef4444"
AMBER      = "#f59e0b"
TEXT_PRI   = "#f1f5f9"
TEXT_SEC   = "#94a3b8"

process    = None
log_thread = None
running    = False


class AuthGuardControl(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AuthGuard Server Control")
        self.geometry("700x560")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Fonts
        self.f_title  = font.Font(family="Segoe UI", size=18, weight="bold")
        self.f_sub    = font.Font(family="Segoe UI", size=10)
        self.f_btn    = font.Font(family="Segoe UI", size=13, weight="bold")
        self.f_status = font.Font(family="Segoe UI", size=11, weight="bold")
        self.f_log    = font.Font(family="Consolas",  size=9)
        self.f_label  = font.Font(family="Segoe UI", size=9)

        self._build_ui()
        self._poll_status()

    # ─── UI BUILD ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header bar
        header = tk.Frame(self, bg=BG_CARD, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🛡️  AuthGuard", font=self.f_title,
                 bg=BG_CARD, fg=TEXT_PRI).place(x=24, y=14)
        tk.Label(header, text="AI Detection Server Control Panel",
                 font=self.f_sub, bg=BG_CARD, fg=TEXT_SEC).place(x=28, y=46)

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Status row
        status_row = tk.Frame(self, bg=BG_MAIN)
        status_row.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(status_row, text="SERVER STATUS", font=self.f_label,
                 bg=BG_MAIN, fg=TEXT_SEC).pack(side="left")

        self.dot_canvas = tk.Canvas(status_row, width=14, height=14,
                                    bg=BG_MAIN, highlightthickness=0)
        self.dot_canvas.pack(side="left", padx=(12, 6))
        self.dot = self.dot_canvas.create_oval(2, 2, 12, 12, fill=AMBER, outline="")

        self.status_lbl = tk.Label(status_row, text="Checking...",
                                   font=self.f_status, bg=BG_MAIN, fg=AMBER)
        self.status_lbl.pack(side="left")

        # Port info
        tk.Label(status_row, text="  Port: 5000", font=self.f_label,
                 bg=BG_MAIN, fg=TEXT_SEC).pack(side="left", padx=(20, 0))

        # Card with big START/STOP button
        card = tk.Frame(self, bg=BG_CARD, bd=0, relief="flat",
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=24, pady=(16, 0))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(pady=24)

        self.main_btn = tk.Button(
            btn_frame,
            text="▶  START SERVER",
            font=self.f_btn,
            bg=GREEN, fg="#ffffff",
            activebackground="#059669", activeforeground="#ffffff",
            relief="flat", bd=0,
            padx=40, pady=16,
            cursor="hand2",
            command=self.toggle_server
        )
        self.main_btn.pack(side="left", padx=(0, 12))

        self.ngrok_btn = tk.Button(
            btn_frame,
            text="🔗 CONNECT TUNNEL",
            font=self.f_btn,
            bg="#2563eb", fg="#ffffff",
            activebackground="#1d4ed8", activeforeground="#ffffff",
            relief="flat", bd=0,
            padx=20, pady=16,
            cursor="hand2",
            command=self.start_tunnel
        )
        self.ngrok_btn.pack(side="left", padx=(0, 12))

        self.open_btn = tk.Button(
            btn_frame,
            text="🌐  Open Website",
            font=self.f_btn,
            bg=BG_HOVER, fg=CYAN,
            activebackground=BORDER, activeforeground=CYAN,
            relief="flat", bd=0,
            padx=24, pady=16,
            cursor="hand2",
            command=lambda: webbrowser.open(WEBSITE_URL)
        )
        self.open_btn.pack(side="left")

        # Quick links row
        links_frame = tk.Frame(card, bg=BG_CARD)
        links_frame.pack(pady=(0, 20))

        pages = [
            ("🎤 Voice",    "/voice-ui/index.html"),
            ("🖼️ Image",   "/deepfake-ui/index.html"),
            ("💬 Text",    "/text-ui/index.html"),
            ("🎬 Video",   "/video-ui/index.html"),
            ("🔗 URL",     "/url-ui/index.html"),
            ("📦 Batch",   "/batch-ui/index.html"),
        ]
        for name, path in pages:
            def _open(p=path):
                webbrowser.open("http://localhost:5000" + p)
            tk.Button(links_frame, text=name, font=self.f_label,
                      bg=BG_HOVER, fg=TEXT_SEC,
                      activebackground=BORDER, activeforeground=TEXT_PRI,
                      relief="flat", padx=12, pady=6, cursor="hand2",
                      command=_open).pack(side="left", padx=4)

        # Log section
        log_header = tk.Frame(self, bg=BG_MAIN)
        log_header.pack(fill="x", padx=24, pady=(16, 4))
        tk.Label(log_header, text="SERVER LOGS", font=self.f_label,
                 bg=BG_MAIN, fg=TEXT_SEC).pack(side="left")
        tk.Button(log_header, text="Clear", font=self.f_label,
                  bg=BG_HOVER, fg=TEXT_SEC, relief="flat", padx=8, pady=2,
                  cursor="hand2", activebackground=BORDER,
                  command=self._clear_log).pack(side="right")

        self.log_box = scrolledtext.ScrolledText(
            self, font=self.f_log, bg="#060912", fg="#64ffda",
            insertbackground=CYAN, relief="flat",
            highlightbackground=BORDER, highlightthickness=1,
            state="disabled", wrap="word"
        )
        self.log_box.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self._log("AuthGuard Control Panel ready.\n")
        self._log(f"Server directory: {SERVER_DIR}\n")
        self._log("Click ▶ START SERVER to launch the backend.\n")

    # ─── TOGGLE ──────────────────────────────────────────────────────────────
    def toggle_server(self):
        global running
        if not running:
            self._start_server()
        else:
            self._stop_server()

    def _start_server(self):
        global process, log_thread, running
        self._log("\n── Starting server... ──────────────────────────\n")
        self.main_btn.config(state="disabled", text="Starting...")

        def do_start():
            global process, log_thread, running
            try:
                process = subprocess.Popen(
                    SERVER_CMD,
                    cwd=SERVER_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                running = True
                self.after(0, self._set_running_ui)

                for line in process.stdout:
                    self.after(0, self._log, line)

                process.wait()
                running = False
                self.after(0, self._set_stopped_ui)
                self.after(0, self._log, "\n── Server stopped ──────────────────────────────\n")
            except Exception as e:
                running = False
                self.after(0, self._set_stopped_ui)
                self.after(0, self._log, f"\nERROR: {e}\n")

        log_thread = threading.Thread(target=do_start, daemon=True)
        log_thread.start()

    def start_tunnel(self):
        self._log("\n── Starting Cloudflare tunnel... ────────────────\n")
        self.ngrok_btn.config(state="disabled", text="Connecting...", bg=AMBER)

        def run_tunnel():
            try:
                tunnel_proc = subprocess.Popen(
                    [os.path.join(SERVER_DIR, "cloudflared.exe"),
                     "tunnel", "--url", "http://localhost:5000", "--no-autoupdate"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in tunnel_proc.stdout:
                    line = line.strip()
                    if "trycloudflare.com" in line or "https://" in line.lower():
                        self.after(0, self._log, f"\n✅ TUNNEL LIVE: {line}\n")
                        self.after(0, lambda: self.ngrok_btn.config(
                            text="🔗 TUNNEL ACTIVE", bg=GREEN))
                    elif line:
                        self.after(0, self._log, line + "\n")
                tunnel_proc.wait()
                self.after(0, lambda: self.ngrok_btn.config(
                    state="normal", text="🔗 CONNECT TUNNEL", bg="#2563eb"))
            except Exception as e:
                self.after(0, lambda: self.ngrok_btn.config(
                    state="normal", text="🔗 CONNECT TUNNEL", bg="#2563eb"))
                self.after(0, self._log, f"Tunnel error: {e}\n")

        threading.Thread(target=run_tunnel, daemon=True).start()

    def _stop_server(self):
        global process, running
        self._log("\n── Stopping server... ──────────────────────────\n")
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        running = False
        self._set_stopped_ui()

    # ─── STATUS POLL ─────────────────────────────────────────────────────────
    def _poll_status(self):
        def check():
            try:
                r = requests.get(HEALTH_URL, timeout=1.5)
                online = r.status_code == 200
            except Exception:
                online = False
            self.after(0, self._update_dot, online)
        threading.Thread(target=check, daemon=True).start()
        self.after(5000, self._poll_status)

    def _update_dot(self, online):
        if online:
            self.dot_canvas.itemconfig(self.dot, fill=GREEN)
            self.status_lbl.config(text="Online", fg=GREEN)
        elif running:
            self.dot_canvas.itemconfig(self.dot, fill=AMBER)
            self.status_lbl.config(text="Starting...", fg=AMBER)
        else:
            self.dot_canvas.itemconfig(self.dot, fill=RED)
            self.status_lbl.config(text="Offline", fg=RED)

    # ─── UI STATE HELPERS ────────────────────────────────────────────────────
    def _set_running_ui(self):
        self.main_btn.config(
            state="normal", text="⏹  STOP SERVER",
            bg=RED, activebackground="#b91c1c"
        )

    def _set_stopped_ui(self):
        self.main_btn.config(
            state="normal", text="▶  START SERVER",
            bg=GREEN, activebackground="#059669"
        )
        self.dot_canvas.itemconfig(self.dot, fill=RED)
        self.status_lbl.config(text="Offline", fg=RED)

    # ─── LOG ─────────────────────────────────────────────────────────────────
    def _log(self, text):
        self.log_box.config(state="normal")
        self.log_box.insert("end", text)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    # ─── CLOSE ───────────────────────────────────────────────────────────────
    def on_close(self):
        if running:
            self._stop_server()
        self.destroy()


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        import requests

    app = AuthGuardControl()
    app.mainloop()
