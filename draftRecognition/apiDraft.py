from fastapi import FastAPI
import requests
import os
from base64 import b64encode
import urllib3

urllib3.disable_warnings()

app = FastAPI()

def get_lcu_credentials():
    process = os.popen('wmic PROCESS WHERE "name=\'LeagueClientUx.exe\'" GET commandline').read()
    try:
        auth_token = process.split('--remoting-auth-token=')[1].split('"')[0]
        port = process.split('--app-port=')[1].split('"')[0]
        return auth_token, port
    except IndexError:
        return None, None

def get_champ_select_data():
    auth_token, port = get_lcu_credentials()
    if not auth_token or not port:
        return {"error": "League Client not running or unable to parse credentials."}

    url = f"https://127.0.0.1:{port}/lol-champ-select/v1/session"
    headers = {
        "Authorization": "Basic " + b64encode(f"riot:{auth_token}".encode()).decode(),
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/draft")
def get_draft():
    data = get_champ_select_data()
    return data
