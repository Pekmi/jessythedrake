import json
import time
import os

import datasetMaker

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
            print(f"Progress: {progress:.2f}% - Processing {current_file}", end='\r', flush=True)

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


def save_features(features, output_path):
    with open(output_path, 'w') as f:
        json.dump(features, f, indent=4)
    print(f"Features saved to {output_path}")



if __name__ == "__main__":

    print("Rassemblement des données")
    mother_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    match_data_path = os.path.join(mother_dir, "gameSniffer", "match_data")

    allJson = gather_data(match_data_path)

    #print les  keys d'un match
    print(f"keys d'un match: {list(allJson.values())[0].keys()}")

    print("Extraction des features")
    features = {}

    features = datasetMaker.extract_features_from_match(allJson)

    print("Enregistrement des features")
    save_features(features, "features.json")