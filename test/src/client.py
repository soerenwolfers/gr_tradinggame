import requests
from requests.auth import HTTPBasicAuth

server_url = "https://ac1b-34-85-182-46.ngrok-free.app/receive"  # use the printed public URL

response = requests.post(
    server_url,
    json={"message": "Hi securely"},
    auth=HTTPBasicAuth("colabuser", "secretcolab")
)

print(response.text)
