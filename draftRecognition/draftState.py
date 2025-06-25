import time
import requests

# Fonction fournie
def get_champion_id_name_map():
    # Récupération de la dernière version du jeu
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    version = requests.get(version_url).json()[0]

    # Récupération des données des champions
    champs_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    champs_data = requests.get(champs_url).json()["data"]

    # Construction du dictionnaire: championId (int) -> name (str)
    champ_id_to_name = {}
    for champ in champs_data.values():
        champ_id_to_name[int(champ["key"])] = champ["id"]
    return champ_id_to_name

# Chargement au lancement
CHAMPION_ID_TO_NAME = get_champion_id_name_map()

def get_champion_name(champion_id):
    return CHAMPION_ID_TO_NAME.get(champion_id, f"ID {champion_id}")

def fetch_draft():
    try:
        response = requests.get("http://127.0.0.1:8000/draft")
        data = response.json()
        return data
    except Exception as e:
        print("Erreur lors de la récupération du draft:", e)
        return None

def parse_draft(data):
    if "error" in data:
        print("⛔", data["error"])
        return

    actions = data.get("actions", [])
    my_team = data.get("myTeam", [])
    their_team = data.get("theirTeam", [])

    return actions, my_team, their_team


def print_draft(actions):

    pick_ally, pick_enemy, ban_ally, bans_enemy = get_current_teams(actions)

    print("\n" + " === Draft actuelle === ")
    print("  Alliés  :", ", ".join(pick_ally) or "aucun")
    print("  Ennemis :", ", ".join(pick_enemy) or "aucun")
    print("  Banis Alliés  :", ", ".join(ban_ally) or "aucun")
    print("  Banis Ennemis :", ", ".join(bans_enemy) or "aucun")


def get_current_teams(actions):
    """
    Récupère les équipes actuelles à partir des actions de draft.
    Retourne deux listes : l'équipe alliée et l'équipe ennemie.
    """
    pick_ally = set()
    pick_enemy = set()
    ban_ally = set()
    bans_enemy = set()

    for action_group in actions:
        for action in action_group:
            if not action.get("completed", False):
                continue
            champ_id = action.get("championId", 0)
            if champ_id == 0:
                continue
            name = get_champion_name(champ_id)
            if action["type"] == "pick":
                if action["isAllyAction"]:
                    pick_ally.add(name)
                else:
                    pick_enemy.add(name)
            elif action["type"] == "ban":
                if action["isAllyAction"]:
                    ban_ally.add(name)
                else:
                    bans_enemy.add(name)

    return list(pick_ally), list(pick_enemy), list(ban_ally), list(bans_enemy)


def check_draft_complete(actions):
    """
    Vérifie si le draft est complet.
    Un draft est complet si toutes les actions de pick et de ban sont terminées.
    """
    for action_group in actions:
        for action in action_group:
            if not action.get("completed", False):
                return False
    return True



if __name__ == "__main__":

    DraftEnded = False

    while True:
        time.sleep(3)


        data = fetch_draft()
        if not data:
            print("Aucune donnée de draft récupérée.")
            continue    

        actions, my_team, their_team = parse_draft(data)
        if actions is None:
            print("Aucune action de draft trouvée.")
            continue


        if check_draft_complete(actions):
            finalAlly, finalEnemy, finalBansAlly, finalBansEnemy = get_current_teams(actions)
            if(finalAlly == [] and finalEnemy == []):
                print("Aucune draft en cours.", end="\r", flush=True)
                continue
            else:
                print("Draft terminée !")
                print_draft(actions)
                DraftEnded = True
                break

        
        print_draft(actions)

