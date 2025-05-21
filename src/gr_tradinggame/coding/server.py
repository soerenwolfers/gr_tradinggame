# pip install flask pyngrok flask-ngrok plotly==5.10

import uuid
from flask import Flask, request, jsonify
from functools import wraps
import json
import base64
from collections import defaultdict
import threading

from blackbox import generate_function
from util import get_url


class GameServer:
    def __init__(self, token):
        self.name = str(uuid.uuid4())
        self.submission_lock = threading.Lock()
        self.USERNAME = "colabuser"
        self.PASSWORD = "secretcolab"

        self.submissions = defaultdict(lambda: defaultdict(dict))
        try:
            with open("submissions.json", 'r') as f:
                submissions_loaded = json.load(f)
            for team, team_submissions in submissions_loaded.items():
                for time, team_submission in team_submissions.items():
                    self.submissions[team][time] = team_submission
        except FileNotFoundError:
            pass
                
        self.app = Flask(self.name)

        def require_auth(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                auth = request.headers.get("Authorization")
                error = None
                if auth and auth.startswith("Basic "):
                    try:
                        decoded = base64.b64decode(auth.split(" ")[1]).decode("utf-8")
                        user, pw = decoded.split(":")
                        if user == self.USERNAME and pw == self.PASSWORD:
                            return f(*args, **kwargs)
                    except Exception as e:
                        print(e)
                        error = e
                return jsonify({"error": "Unauthorized"}), 401 if error is None else jsonify({'error': str(error)}), 500
            return decorated
        
        @self.app.route("/receive", methods=["POST"])
        @require_auth
        def receive():
            data = request.get_json()
            print("Received data:", data)
            generate_function(data['submission'])
            with self.submission_lock:
                self.submissions[data['team']][data['time']] = data['submission']
                with open("submissions.json", "w") as f:
                    json.dump(dict(self.submissions), f, indent=4)
                print(json.dumps(self.submissions, indent=4))
            return jsonify({"status": "success"})
        self.token = token

    def run(self, force_restart=False):
        server_id = get_url(self.token, force_restart)
        print('Serving', server_id)
        self.app.run(port=5000)
