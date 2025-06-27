import os
import json
import requests
import subprocess
from base64 import b64encode
import time
from concurrent.futures import ThreadPoolExecutor

import urllib3
urllib3.disable_warnings()

from timeTracker import Timer as tt

session = requests.Session()


# Connexion LCU 
def get_lcu_credentials(): 
    needFeedBack = True 
    while True:
        cmd = ['wmic', 'PROCESS', 'WHERE', "name='LeagueClientUx.exe'", 'GET', 'commandline'] 
        proc = subprocess.run(cmd, capture_output=True, text=True) 
        output = proc.stdout + proc.stderr

        if "Aucune instance disponible" in output or "No Instance" in output or not output.strip():
            print("ELC", end='\r', flush=True)
            needFeedBack = True
            continue

        try:
            token = output.split('--remoting-auth-token=')[1].split('"')[0]
            port = output.split('--app-port=')[1].split('"')[0]
            # print("port: "+port)
            if needFeedBack:
                print(f"VLC", end='\n', flush=True)
            return token, port
        except Exception:
            print("ELC", end='\n', flush=True)
            time.sleep(5)


def lcu_request(path):
    token, port = get_lcu_credentials()
    url = f"https://127.0.0.1:{port}{path}"
    headers = {
        "Authorization": "Basic " + b64encode(f"riot:{token}".encode()).decode(),
        "Accept": "application/json"
    }

    needFeedBack = True
    nOfTries = 0
    while True:
        try:
            r = session.get(url, headers=headers, verify=False)
            # r.raise_for_status()
            if needFeedBack:
                print(f"VRL", end='\n', flush=True)
            return r.json()
        except:
            print(f"ERL", end='\r', flush=True)
            needFeedBack = True
            nOfTries += 1
            time.sleep(0.5)




# Récupération des parties récentes

def get_recent_game_ids(puuid, count=10):

    data = lcu_request(f"/lol-match-history/v1/products/lol/{puuid}/matches")

    # essaie d'accéder à data["games"]["games"] si nécessaire
    games_raw = data.get("games")

    if isinstance(games_raw, dict) and "games" in games_raw:
        games = games_raw["games"]
    elif isinstance(games_raw, list):
        games = games_raw
    else:
        # print("\n\n"+games_raw)
        print("ESG")
        return []

    return [game["gameId"] for game in games[:count]]


def get_full_match_data(game_id):
    return lcu_request(f"/lol-match-history/v1/games/{game_id}")

def save_match_json(game_id, data, puuid):
    os.makedirs(os.path.join(os.path.dirname(__file__),"match_data",("player_"+puuid)), exist_ok=True)
    path = os.path.join(os.path.dirname(__file__),"match_data",("player_"+puuid), f"match_{game_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)







def get_json_from_puuid(puuid, puuids, nofloop):
    """
    Récupère les données de match complètes pour un joueur donné à partir de son PUUID.
    """
    startTime = time.time()
    localpath = os.path.dirname(__file__)
    blacklist_path = os.path.join(localpath, "match_data", "jsonblacklist.txt")
    with open(blacklist_path, "r", encoding="utf-8") as f:
        blacklist = {line.strip() for line in f if line.strip()}

    game_ids = get_recent_game_ids(puuid, count=20)
    filtered_game_ids = [gid for gid in game_ids if f"match_{gid}" not in blacklist]
    if not filtered_game_ids:
        print(f"Aucune partie à miner pour le PUUID {puuid} (tout déjà miné).")
        return [], [], 0

    def fetch(game_id):
        return get_full_match_data(game_id)

    with ThreadPoolExecutor(max_workers=20) as executor:
        data = list(executor.map(fetch, filtered_game_ids))

        
    print(f"MR:{len(puuids)-nofloop}")
    print(f"TR:{((len(puuids)-nofloop)*16/6/60):.2f}")
    print(f"PR:{((len(puuids)-nofloop)*19*0.052):.2f}")
    # print(f"NM:{len(data)}")
    print(f"TM:{(time.time()-startTime):.2f}", end='\n', flush=True)


    NM = len(data)
    return data, filtered_game_ids, NM





"""
if __name__ == "__main__":
    try:

        # Récupération du PUUID du joueur
        # puuid = summonerData.get_summoner_puuid()
        puuid = "19c9f526-577f-501f-a676-6f14d248eec4"
        print(f"PUUID détecté : {puuid}")

        # Récupération de l'ID des parties récentes et sauvegarde des données
        game_ids = get_recent_game_ids(puuid, count=20)
        print(f"Récupération des {len(game_ids)} dernières parties...")

        # Obtention des données complètes de chaque partie 
        for game_id in game_ids:
            print(f"🔄 Match {game_id}...")
            data = get_full_match_data(game_id)


            # Sauvegarde des données dans un fichier JSON
            save_match_json(game_id, data)
            print(f"✅ Sauvegardé : match_data/match_{game_id}.json")



    except Exception as e:
        print("Erreur :", e)
"""