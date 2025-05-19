# requires
# pip install flask pyngrok flask-ngrok
# !ngrok config add-authtoken 2xKdM2iD98QgKJz9Pw8DQh9DalR_4EEYGbDiMWSdQR5os7Qa2

from flask import Flask, request, jsonify
from pyngrok import ngrok
from functools import wraps
import base64

# Set username and password
USERNAME = "colabuser"
PASSWORD = "secretcolab"

# Create Flask app
app = Flask(__name__)

# Auth decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Basic "):
            try:
                decoded = base64.b64decode(auth.split(" ")[1]).decode("utf-8")
                user, pw = decoded.split(":")
                if user == USERNAME and pw == PASSWORD:
                    return f(*args, **kwargs)
            except Exception:
                pass
        return jsonify({"error": "Unauthorized"}), 401
    return decorated

@app.route("/receive", methods=["POST"])
@require_auth
def receive():
    data = request.get_json()
    print("Received data:", data)
    return jsonify({"status": "success", "echo": data})

# Start ngrok tunnel before app.run()
public_url = ngrok.connect(5000)
print(f"🔗 Public URL: {public_url}/receive")

# Start Flask server
app.run(port=5000)
