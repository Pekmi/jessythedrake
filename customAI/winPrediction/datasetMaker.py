import json

def extract_features_from_match(json_data):
    # Initialise la structure de la ligne
    features = {}

    print(f"Traitement de {len(json_data)} matchs")

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
