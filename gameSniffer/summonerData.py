import requests
import os
from base64 import b64encode
import urllib3

urllib3.disable_warnings()

def get_lcu_credentials():
    cmd = 'wmic PROCESS WHERE "name=\'LeagueClientUx.exe\'" GET commandline'
    proc = os.popen(cmd).read()
    token = proc.split('--remoting-auth-token=')[1].split('"')[0]
    port = proc.split('--app-port=')[1].split('"')[0]
    return token, port

def get_summoner_puuid():
    token, port = get_lcu_credentials()
    url = f"https://127.0.0.1:{port}/lol-summoner/v1/current-summoner"
    headers = {
        "Authorization": "Basic " + b64encode(f"riot:{token}".encode()).decode(),
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers, verify=False)
    data = resp.json()
    return data.get("puuid")

# Exemple
if __name__ == "__main__":
    puuid = get_summoner_puuid()
    print("Ton PUUID :", puuid)
