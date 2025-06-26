import time
import json
import subprocess
import requests
from base64 import b64encode

session = requests.Session()


import urllib3
urllib3.disable_warnings()


# NETWORK

def get_lcu_credentials(): 
    while True:
        cmd = ['wmic', 'PROCESS', 'WHERE', "name='LeagueClientUx.exe'", 'GET', 'commandline'] 
        proc = subprocess.run(cmd, capture_output=True, text=True) 
        output = proc.stdout + proc.stderr

        if "Aucune instance disponible" in output or "No Instance" in output or not output.strip():
            print("ELC", end='\r', flush=True)
            continue

        try:
            token = output.split('--remoting-auth-token=')[1].split('"')[0]
            port = output.split('--app-port=')[1].split('"')[0]
            return token, port
        except Exception:
            # print("ELC", end='\n', flush=True)
            time.sleep(5)


def lcu_request(path):
    token, port = get_lcu_credentials()
    url = f"https://127.0.0.1:{port}{path}"
    headers = {
        "Authorization": "Basic " + b64encode(f"riot:{token}".encode()).decode(),
        "Accept": "application/json"
    }

    nOfTries = 0
    while True:
        try:
            r = session.get(url, headers=headers, verify=False)
            return r.json()
        except:
            nOfTries += 1
            time.sleep(0.5)



# JSON

def get_full_match_data(game_id):
    return lcu_request(f"/lol-match-history/v1/games/{game_id}")



# PUUIDS

def extract_other_puuids(match):
    puuids = []
    identities = match.get("participantIdentities", [])
    for identity in identities:
        player = identity.get("player", {})
        puuid = player.get("puuid")
        if puuid:
            puuids.append(puuid)

    return puuids

# def extract_puuids_from_json(json_files):
#     puuids = []
#     for file in json_files:
#         puuids.append(extract_other_puuids(file))
    
#     # On a une liste de listes, on aplatit la liste
#     puuids = [puuid for sublist in puuids for puuid in sublist]
#     return puuids










if __name__ == "__main__":
    
    puuids = {} #dictionnaire des puuids, format: {puuid: N}, avec N le nombre de fois qu'il a été trouvé

    while True:
    
        game_id = input("game_ID: ")
        json_file = get_full_match_data(game_id)

        extracted_puuids =  extract_other_puuids(json_file) 


        for puuid in extracted_puuids:
            if puuid not in puuids:
                puuids[puuid] = 1
            else:
                puuids[puuid] += 1


        highest_score = 0
        for puuid, count in puuids.items():
            if count > highest_score:
                highest_score = count
                suspicious_puuids = [puuid]
            elif count == highest_score:
                suspicious_puuids.append(puuid)




        print(f"N PUUIDs: {len(puuids)}")

        if( len(suspicious_puuids) != 1):
            suspicious_puuids = []
            print(f"N suspicious PUUIDs: {len(suspicious_puuids)}")
        else:
            print("PUUID: " + suspicious_puuids[0])
            exit(0)


    


# if __name__ == "__main__":
    
    # puuids = []
    # new_suspicious_puuids = []
    # suspicious_puuids = []

    # while True:
    
    #     game_id = input("game_ID: ")
    #     json_file = get_full_match_data(game_id)

    #     extracted_puuids =  extract_other_puuids(json_file) 

    #     for puuid in extracted_puuids:
    #         if puuid not in puuids:
    #             puuids.append(puuid)
    #         else:
    #             new_suspicious_puuids.append(puuid)

        


    #     print(f"N PUUIDs: {len(puuids)}")

    #     if( len(suspicious_puuids) != 1):
    #         suspicious_puuids = new_suspicious_puuids
    #         new_suspicious_puuids = []
    #         print(f"N suspicious PUUIDs: {len(suspicious_puuids)}")
    #     else:
    #         print("PUUID: " + puuids[0])
    #         exit(0)


    