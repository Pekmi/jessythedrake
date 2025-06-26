import json
import os


def gather_data(path):
    allJson = {}

    print(f"Extraction d'environ {len(os.listdir(path))*20} matchs")

    for playerDir in os.listdir(path):
        player_path = os.path.join(path, playerDir)
        if not os.path.isdir(player_path):
            continue

        for matchFile in os.listdir(player_path):
            total_files = len(os.listdir(path))
            current_file = os.path.join(playerDir, matchFile)
            progress = (list(os.listdir(path)).index(playerDir) + 1) / total_files * 100

            if (list(os.listdir(path)).index(playerDir) + 1) % 5 == 0:
                print(f"Traitement: {progress:.2f}% - Traite {current_file}", end='\r', flush=True)

            if matchFile.endswith(".json"):
                match_path = os.path.join(player_path, matchFile)
                with open(match_path, 'r') as f:
                    try:
                        json_data = json.load(f)
                        # Use a unique key for each match, e.g., playerDir/matchFile
                        key = f"{playerDir}/{matchFile}"
                        allJson[key] = json_data
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from {matchFile}: {e}")

    return allJson



def extract_features_from_match(json_data):
    # Initialise la structure de la ligne
    features = {}

    print(f"Traitement de {len(json_data)} matchs", end='\r', flush=True)

    # 1. Champions picks et rôles
    role_map = {}  # {teamId: {role: championId}}
    for p in json_data["participants"]:
        team = p["teamId"]
        role = p["timeline"]["lane"]  # ou autre logique selon le mapping LoL
        champ = p["championId"]
        if team not in role_map:
            role_map[team] = {}
        role_map[team][role] = champ

    # 2. Champions bannis
    bans = {}
    for team in json_data["teams"]:
        team_id = team["teamId"]
        bans[team_id] = [ban["championId"] for ban in team["bans"]]

    # 3. Label (ex : victoire team 100)
    label = 1 if json_data["teams"][0]["win"] == "Win" else 0  # team 100

    # 4. Construction de la ligne
    for role in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"]:
        features[f"team100_{role.lower()}"] = role_map.get(100, {}).get(role, 0)
        features[f"team200_{role.lower()}"] = role_map.get(200, {}).get(role, 0)
    for i, ban in enumerate(bans.get(100, [])):
        features[f"team100_ban{i+1}"] = ban
    for i, ban in enumerate(bans.get(200, [])):
        features[f"team200_ban{i+1}"] = ban
    features["label_win_team100"] = label

    return features




def save_features(features, output_path):
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=4)
    print(f"Features sauvegardées dans {output_path}")





def make_dataset():
    
    print("Rassemblement des données")
    mother_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    match_data_path = os.path.join(mother_dir, "gameSniffer", "match_data")

    allJson = gather_data(match_data_path)

    #print les  keys d'un match
    # print(f"keys d'un match: {list(allJson.values())[0].keys()}")

    print("\nExtraction des features")
    features_list = []
    for key, match_json in allJson.items():
        try:
            feat = extract_features_from_match(match_json)
            features_list.append(feat)
        except Exception as e:
            print(f"Erreur dans {key} : {e}")


    print("Enregistrement des features")
    save_features(features_list, "features.json")