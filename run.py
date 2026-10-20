"""
SMSHARE — NEO-BRUTALISM RUNNER
One-click launcher for the SMSHARE privacy-first temporary file & text sharing server.
"""

import sys
import os
import socket
import webbrowser
import threading
import time

# Reconfigure output encoding for Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn

BANNER = """
=============================================================
  S M S H A R E   -   N E O - B R U T A L I S M   E D I T I O N
  Privacy-First Temporary File & Text Sharing Without Signup
  [ Zero Logging * Self-Destructs on Expiry * 4-Char Codes ]
=============================================================
"""

def open_browser(port):
    time.sleep(1.2)
    url = f"http://localhost:{port}"
    print(f"\n[Browser] Opening your browser at: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[Browser] Could not auto-open browser: {e}")

def main():
    print(BANNER)
    # Read cloud port if available, else fallback to 8000/8080
    env_port = os.environ.get("PORT")
    if env_port:
        port = int(env_port)
    else:
        port = 8000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                port = 8080

    print(f"[Server] Starting SMSHARE server at: http://localhost:{port}")
    print(f"[Server] Local storage directory: {os.path.abspath('uploads')}")
    print("[Server] Auto-wipe worker: Active (cleans expired files every 20s)")
    print("[Server] Press Ctrl+C in this terminal to shut down.\n")

    # Launch browser only on local interactive runs
    if not env_port and not os.environ.get("RENDER"):
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Start Uvicorn ASGI server
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
