import requests

def is_flask_server_running():
    try:
        response = requests.get("http://127.0.0.1:5001/api/health", timeout=2)
        return response.status_code == 200 and response.json().get("status") == "ok"
    except requests.exceptions.RequestException:
        return False