import sys
import socket
import threading
import time
import webbrowser
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

def find_open_port(preferred: int = 8000) -> int:
    if not is_port_in_use(preferred):
        return preferred
    for port in range(preferred + 1, preferred + 20):
        if not is_port_in_use(port):
            return port
    return preferred

def open_browser_when_ready(url: str, port: int):
    for _ in range(30):
        time.sleep(0.3)
        if is_port_in_use(port):
            time.sleep(0.5)
            webbrowser.open(url)
            return

def main():
    import uvicorn
    from app.core.config import settings

    port = find_open_port(8000)
    url = f"http://localhost:{port}"

    print(f"\n==========================================================")
    print(f"  THANGAN // PERSONAL GAME DEV AI COMPANION")
    print(f"==========================================================")
    print(f"  Target Engine : Unreal Engine 5.4")
    print(f"  Web Interface : {url}")
    print(f"  Press CTRL+C in this window to stop the server.")
    print(f"==========================================================\n")

    # Launch browser only once the port is actively listening
    opener = threading.Thread(target=open_browser_when_ready, args=(url, port), daemon=True)
    opener.start()

    uvicorn.run("app.main:app", app_dir=str(backend_dir), host="127.0.0.1", port=port, reload=False)

if __name__ == "__main__":
    main()
