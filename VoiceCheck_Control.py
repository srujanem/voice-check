import tkinter as tk
from tkinter import scrolledtext, font
import subprocess
import threading
import sys
import os
import webbrowser
import requests
import time

# ─── Config ───────────────────────────────────────────────────────────────────
SERVER_DIR  = os.path.dirname(os.path.abspath(__file__))
SERVER_CMD  = [sys.executable, "run.py"]
HEALTH_URL  = "http://localhost:5000/api/health"
WEBSITE_URL = "https://authguard.vercel.app"

# ─── Colors ───────────────────────────────────────────────────────────────────
BG_MAIN  = "#0a0a0f"
BG_CARD  = "#0f172a"
BG_HOVER = "#1e293b"
CYAN     = "#06b6d4"
PURPLE   = "#8b5cf6"
GREEN    = "#10b981"
RED      = "#ef4444"
AMBER    = "#f59e0b"
TEXT_PRI = "#f1f5f9"
TEXT_SEC = "#94a3b8"

process    = None
log_thread = None
running    = False


class VoiceCheckControl(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VoiceCheck — Server Control Panel")
        self.geometry("720x580")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.iconbitmap(default='') 

        self.f_title  = font.Font(family="Segoe UI", size=17, weight="bold")
        self.f_sub    = font.Font(family="Segoe UI", size=10)
        self.f_btn    = font.Font(family="Segoe UI", size=12, weight="bold")
        self.f_status = font.Font(family="Segoe UI", size=11, weight="bold")
        self.f_log    = font.Font(family="Consolas",  size=9)
        self.f_label  = font.Font(family="Segoe UI", size=9)

        self._build_ui()
        self._poll_status()

    # ─── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG_CARD, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="⚡ VoiceCheck", font=self.f_title,
                 bg=BG_CARD, fg=CYAN).place(x=20, y=12)
        tk.Label(header, text="AI Detection Server Control Panel",
                 font=self.f_sub, bg=BG_CARD, fg=TEXT_SEC).place(x=22, y=46)

        # Status strip
        self.status_frame = tk.Frame(self, bg=BG_HOVER, height=44)
        self.status_frame.pack(fill="x")
        self.status_frame.pack_propagate(False)

        self.status_dot = tk.Label(self.status_frame, text="●", font=("Segoe UI", 14),
                                   bg=BG_HOVER, fg=AMBER)
        self.status_dot.place(x=18, y=10)
        self.status_lbl = tk.Label(self.status_frame, text="Checking...",
                                   font=self.f_status, bg=BG_HOVER, fg=AMBER)
        self.status_lbl.place(x=42, y=12)

        # Server URL label
        self.url_lbl = tk.Label(self.status_frame, text="localhost:5000",
                                font=self.f_label, bg=BG_HOVER, fg=TEXT_SEC)
        self.url_lbl.place(x=600, y=15)

        # ── Action Buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(pady=18)

        self.btn_start = tk.Button(
            btn_frame, text="▶  Start Server", font=self.f_btn,
            bg=GREEN, fg="white", activebackground="#059669",
            relief="flat", cursor="hand2", width=14, height=2,
            command=self.start_server
        )
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = tk.Button(
            btn_frame, text="■  Stop Server", font=self.f_btn,
            bg=RED, fg="white", activebackground="#dc2626",
            relief="flat", cursor="hand2", width=14, height=2,
            state="disabled", command=self.stop_server
        )
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.btn_restart = tk.Button(
            btn_frame, text="↺  Restart", font=self.f_btn,
            bg=AMBER, fg="white", activebackground="#d97706",
            relief="flat", cursor="hand2", width=12, height=2,
            command=self.restart_server
        )
        self.btn_restart.grid(row=0, column=2, padx=10)

        self.btn_web = tk.Button(
            btn_frame, text="🌐  Open Website", font=self.f_btn,
            bg=PURPLE, fg="white", activebackground="#7c3aed",
            relief="flat", cursor="hand2", width=14, height=2,
            command=lambda: webbrowser.open(WEBSITE_URL)
        )
        self.btn_web.grid(row=0, column=3, padx=10)

        # ── Quick Links ───────────────────────────────────────────────────────
        link_frame = tk.Frame(self, bg=BG_CARD, bd=0)
        link_frame.pack(fill="x", padx=16, pady=(0, 10))

        links = [
            ("Voice Detector",   "http://localhost:5000/voice-ui/"),
            ("Image Detector",   "http://localhost:5000/deepfake-ui/"),
            ("Text Detector",    "http://localhost:5000/text-ui/"),
            ("Video Detector",   "http://localhost:5000/video-ui/"),
            ("URL Scanner",      "http://localhost:5000/url-ui/"),
            ("Watermark",        "http://localhost:5000/watermark-ui/"),
        ]

        tk.Label(link_frame, text="Quick Open:", font=self.f_label,
                 bg=BG_CARD, fg=TEXT_SEC).pack(side="left", padx=(10,8), pady=8)

        for name, url in links:
            tk.Button(
                link_frame, text=name, font=self.f_label,
                bg=BG_HOVER, fg=CYAN, activebackground="#1e293b",
                relief="flat", cursor="hand2", padx=8, pady=4,
                command=lambda u=url: webbrowser.open(u)
            ).pack(side="left", padx=4, pady=8)

        # ── Log Area ──────────────────────────────────────────────────────────
        log_label_frame = tk.Frame(self, bg=BG_MAIN)
        log_label_frame.pack(fill="x", padx=16)
        tk.Label(log_label_frame, text="Server Logs", font=self.f_label,
                 bg=BG_MAIN, fg=TEXT_SEC).pack(side="left")

        self.btn_clear = tk.Button(
            log_label_frame, text="Clear", font=self.f_label,
            bg=BG_HOVER, fg=TEXT_SEC, relief="flat", cursor="hand2",
            padx=6, pady=2, command=self._clear_log
        )
        self.btn_clear.pack(side="right")

        self.log_box = scrolledtext.ScrolledText(
            self, font=self.f_log, bg="#020617", fg="#94a3b8",
            insertbackground=CYAN, relief="flat", bd=0,
            height=14, wrap="word", state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        # Color tags
        self.log_box.tag_config("INFO",  foreground=TEXT_SEC)
        self.log_box.tag_config("OK",    foreground=GREEN)
        self.log_box.tag_config("ERROR", foreground=RED)
        self.log_box.tag_config("WARN",  foreground=AMBER)
        self.log_box.tag_config("CYAN",  foreground=CYAN)

    # ─── Logging ──────────────────────────────────────────────────────────────
    def _log(self, msg, tag="INFO"):
        ts = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ─── Server Control ───────────────────────────────────────────────────────
    def start_server(self):
        global process, running
        if running:
            self._log("Server is already running!", "WARN")
            return
        self._log("Starting server...", "CYAN")
        self.btn_start.config(state="disabled")

        def _run():
            global process, running
            try:
                process = subprocess.Popen(
                    SERVER_CMD,
                    cwd=SERVER_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                running = True
                for line in process.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    tag = "ERROR" if "error" in line.lower() else \
                          "OK"    if "running on" in line.lower() else "INFO"
                    self.after(0, self._log, line, tag)
                running = False
                self.after(0, self._log, "Server stopped.", "WARN")
                self.after(0, self._update_status, False)
            except Exception as e:
                self.after(0, self._log, f"Failed to start: {e}", "ERROR")
                running = False
                self.after(0, self._update_status, False)

        log_thread = threading.Thread(target=_run, daemon=True)
        log_thread.start()

    def stop_server(self):
        global process, running
        if process:
            self._log("Stopping server...", "WARN")
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
            process = None
        running = False
        self._update_status(False)
        self._log("Server stopped.", "WARN")

    def restart_server(self):
        self._log("Restarting...", "CYAN")
        self.stop_server()
        self.after(1500, self.start_server)

    # ─── Status Polling ───────────────────────────────────────────────────────
    def _poll_status(self):
        def _check():
            try:
                r = requests.get(HEALTH_URL, timeout=2)
                ok = r.status_code == 200
            except:
                ok = False
            self.after(0, self._update_status, ok)

        threading.Thread(target=_check, daemon=True).start()
        self.after(5000, self._poll_status)

    def _update_status(self, ok):
        if ok:
            self.status_dot.config(fg=GREEN)
            self.status_lbl.config(text="Server Online", fg=GREEN)
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
        else:
            self.status_dot.config(fg=RED)
            self.status_lbl.config(text="Server Offline", fg=RED)
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")

    # ─── Close ────────────────────────────────────────────────────────────────
    def on_close(self):
        if running:
            if tk.messagebox.askyesno(
                "Server Running",
                "Server is still running.\nStop the server and exit?"
            ):
                self.stop_server()
                self.destroy()
        else:
            self.destroy()


if __name__ == "__main__":
    from tkinter import messagebox
    app = VoiceCheckControl()
    app.mainloop()
