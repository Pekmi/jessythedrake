import json
import csv
import os

import datasetAnomalies



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
    features = {}

    print(f"Traitement de {json_data.get('gameId', 'inconnu')}", end='\r', flush=True)

    # 1. Champions picks et rôles (mapping Riot officiel)
    role_map = {}  # {teamId: {role: championId}}
    duo_candidates = {}

    for p in json_data["participants"]:
        team = p["teamId"]
        lane = p["timeline"].get("lane", "")
        role = p["timeline"].get("role", "")
        champ = p["championId"]

        role_name = None

        # Détermination du rôle basé sur la lane et le rôle
        if lane == "TOP":
            role_name = "TOP"
        elif lane == "JUNGLE":
            role_name = "JUNGLE"
        elif lane == "MIDDLE":
            role_name = "MIDDLE"
        elif lane == "BOTTOM":
            if role.upper() in ["CARRY", "DUO_CARRY"]:
                role_name = "BOTTOM"
            elif role.upper() in ["SUPPORT", "DUO_SUPPORT"]:
                role_name = "SUPPORT"
            elif role.upper() == "DUO":
                if team not in duo_candidates:
                    duo_candidates[team] = []
                duo_candidates[team].append(p)
                continue
            else:
                continue
        else:
            continue

        if role_name:
            if team not in role_map:
                role_map[team] = {}
            role_map[team][role_name] = champ



    # VERIFICATION DES LANES CORROMPUES
    all_none = all(p["timeline"].get("lane", "").upper() == "NONE" for p in json_data["participants"])
    if all_none:
        # On lève une exception explicite, qui sera attrapée et ignorera ce match
        # print(f"\n[gameId: {json_data.get('gameId', 'inconnu')}] : Toutes les lanes sont 'NONE', match ignoré.")
        return None # Ignore ce match

    
    # 2. Champions bannis
    bans = {}
    for team in json_data["teams"]:
        team_id = team["teamId"]
        bans[team_id] = [ban["championId"] for ban in team["bans"]]

    # 3. Label (ex : victoire team 100)
    label = 1 if json_data["teams"][0]["win"] == "Win" else 0  # team 100


    
    # CORRECTION DES ANOMALIES
    role_map = datasetAnomalies.repair_all(duo_candidates, role_map, json_data["participants"])



    # 4. Construction de la ligne (APRES corrections)
    for role in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"]:
        features[f"team100_{role.lower()}"] = role_map.get(100, {}).get(role, 0)
        features[f"team200_{role.lower()}"] = role_map.get(200, {}).get(role, 0)
    for i, ban in enumerate(bans.get(100, [])):
        features[f"team100_ban{i+1}"] = ban
    for i, ban in enumerate(bans.get(200, [])):
        features[f"team200_ban{i+1}"] = ban
    features["label_win_team100"] = label
    features["gameId"] = json_data.get("gameId", 0)

    return features





def save_features(features, output_path):
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=4)
    print(f"Features sauvegardées dans {output_path}")



def save_features_csv(features, output_path):
    if not features:
        print("Aucune donnée à sauvegarder en CSV.")
        return
    # On récupère toutes les clés pour l'en-tête CSV
    fieldnames = list(features[0].keys())
    with open(output_path, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in features:
            writer.writerow(row)
    print(f"Features sauvegardées dans {output_path}")





def make_dataset():
    
    print("Rassemblement des données")
    mother_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    match_data_path = os.path.join(mother_dir, "gameSniffer", "match_data")

    allJson = gather_data(match_data_path)

    # print les keys d'un match
    # print(f"keys d'un match: {list(allJson.values())[0].keys()}")

    print("\nExtraction des features")
    features_list = []
    for key, match_json in allJson.items():
        # affiche le progrès de l'extraction
        total_matches = len(allJson)
        current_match = list(allJson.keys()).index(key) + 1
        progress = (current_match / total_matches) * 100
        print(f" Progression: {progress:.2f}%", end='\r', flush=True)
        try:
            features = extract_features_from_match(match_json)
            if features is None:
                continue  # On saute ce match
            roles = ["top", "jungle", "middle", "bottom", "support"]
            doublon_detected = False
            for team in [100, 200]:
                champs = [features[f"team{team}_{r}"] for r in roles]
                # Vérifie la présence d’un champion par rôle (aucun 0)
                if any(champ == 0 for champ in champs):
                    missing_roles = [r for r, champ in zip(roles, champs) if champ == 0]
                    raise Exception(
                    #    f"[gameId: {features.get('gameId', 'inconnu')}] : Équipe {team} mapping incomplet, rôles manquants : {missing_roles}\nMapping trouvé : " +
                        str({r: features[f"team{team}_{r}"] for r in roles})
                    )
                # Vérifie s'il y a un doublon de championId
                if len(set(champs)) != 5:
                    # print(
                    #    f"[gameId: {features.get('gameId', 'inconnu')}] : Doublon de champions dans l'équipe {team} : {champs}\nMapping trouvé : " +
                    #     str({r: features[f"team{team}_{r}"] for r in roles})
                    # )
                    doublon_detected = True
                    break  # On arrête la boucle sur les équipes et skip ce matchMapping trouvé

            if doublon_detected:
                continue  # On ignore ce match

            # Si on arrive ici, le mapping est parfait, on ajoute le match
            features_list.append(features)
        except Exception as e:
            # print("\n========== ERREUR DE MAPPING ==========")
            # print(e)
            # print("Arrêt du script pour debug.")
            # exit(0)
            pass



    print("Enregistrement des features")
    save_features_csv(features_list, "features.csv")