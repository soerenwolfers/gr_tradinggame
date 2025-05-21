import time
import requests
import os
import signal
import subprocess
import requests


def get_url(token, force_restart):
    def kill_and_restart():
        subprocess.run(["pkill", "ngrok"])
        # ngrok.set_auth_token(token)
        # ngrok_connection = ngrok.connect(5000)
        subprocess.Popen(['ngrok', 'http', '5000', '--authtoken', token], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
