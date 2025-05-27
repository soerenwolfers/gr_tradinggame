import time
import pyngrok
from pyngrok import ngrok
import subprocess
import requests


def get_url(token, force_restart):
    def kill_and_restart():
        subprocess.run(["pkill", "ngrok"])
        ngrok.install_ngrok()
        subprocess.Popen([pyngrok.conf.get_default().ngrok_path, 'http', '5000', '--authtoken', token], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

    def try_get_url():
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()['tunnels']
        public_url = tunnels[0]['public_url']
        return public_url.split('//')[1].split('.ngrok-free.app')[0]

    if force_restart:
        kill_and_restart()
    try:
        return try_get_url()
    except Exception:
        kill_and_restart()
        return try_get_url()
