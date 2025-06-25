import json

def extract_other_puuids(match_path):
    with open(match_path, "r", encoding="utf-8") as f:
        match = json.load(f)

    puuids = []
    identities = match.get("participantIdentities", [])
    for identity in identities:
        player = identity.get("player", {})
        puuid = player.get("puuid")
        if puuid:
            puuids.append(puuid)

    return puuids