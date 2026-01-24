import time
import subprocess
import requests
from pyngrok import ngrok, conf

NGROK_API = "http://localhost:4040/api/tunnels"

def _cleanup_local_tunnels():
    try:
        r = requests.get(NGROK_API, timeout=1)
        for t in r.json().get("tunnels", []):
            old_url = t["public_url"]
            print(f"NOTE: disconnecting and cleaning up {old_url} before serving new session.")
            ngrok.disconnect(old_url)
    except Exception:
        pass

def _ensure_ngrok_running():
    try:
        requests.get(NGROK_API, timeout=1)
    except Exception:
        ngrok.install_ngrok()
        subprocess.Popen(
            [conf.get_default().ngrok_path, "http", "5000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        time.sleep(5)

def get_url(force_restart=False):
    if force_restart:
        _cleanup_local_tunnels()

    _ensure_ngrok_running()

    try:
        r = requests.get(NGROK_API)
        tunnels = r.json()["tunnels"]
        public_url = tunnels[0]["public_url"]
        return public_url.split('//')[1].split('.ngrok-free.app')[0]
    except Exception as e:
        raise RuntimeError("ngrok tunnel not available") from e
