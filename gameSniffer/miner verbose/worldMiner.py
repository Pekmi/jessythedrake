import os

import worldPuuid
import worldCleaner
import sniffHistory
from timeTracker import Timer as tt


print("\n")
print("               _   _          _             ")
print(" _ _ _ ___ ___| |_| |   _____|_|___ ___ ___ ")
print("| | | | . |  _| | . |  |     | |   | -_|  _|")
print("|_____|___|_| |_|___|  |_|_|_|_|_|_|___|_|  ")
print("\n")


localpath = os.path.dirname(__file__)
match_data_path = os.path.join(localpath, "match_data")


# On crée le dossier match_data s'il n'existe pas
if not os.path.exists(match_data_path):
    os.makedirs(match_data_path)

# On crée le fichier puuidblacklist.txt s'il n'existe pas
if not os.path.exists(os.path.join(match_data_path, "puuidblacklist.txt")):
    with open(os.path.join(match_data_path, "puuidblacklist.txt"), "w", encoding="utf-8") as f:
        f.write("")  # Crée le fichier vide
        f.close()
# On crée le fichier jsonblacklist.txt s'il n'existe pas
if not os.path.exists(os.path.join(match_data_path, "jsonblacklist.txt")):  
    with open(os.path.join(match_data_path, "jsonblacklist.txt"), "w", encoding="utf-8") as f:
        f.write("")  # Crée le fichier vide
        f.close()


with open(os.path.join(match_data_path, "puuidblacklist.txt"), "a+", encoding="utf-8") as f:
    # 1 ligne = un puuid = 1 élément de la liste
    json_blacklist = [line.strip() for line in f if line.strip()]
    f.close()

def get_json_degree_1():
    """
    Récupère les fichiers JSON de niveau 1 (dans les dossiers à la racine uniquement) dans le dossier match_data.
    """
    # On récupère tous les dossiers dans le dossier match_data
    directories = [d for d in os.listdir(match_data_path) if os.path.isdir(os.path.join(match_data_path, d))]
    json_files = []
    # On parcourt chaque dossier pour trouver les fichiers JSON
    for directory in directories:
        dir_path = os.path.join(match_data_path, directory)
        files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
        json_files.extend([os.path.join(dir_path, f) for f in files])

    return json_files


def extract_puuids_from_json(json_files):
    """
    Extrait les PUUIDs des fichiers JSON de niveau 1.
    """
    puuids = []
    for file in json_files:
        puuids.append(worldPuuid.extract_other_puuids(file))
    
    # On a une liste de listes, on aplatit la liste
    puuids = [puuid for sublist in puuids for puuid in sublist]
    return puuids




if __name__ == "__main__":

    while True:

        #LECTURE

        # print("Récupération des fichiers JSON de niveau 1...")
        with tt("Récupération des fichiers JSON"):
            json_files = get_json_degree_1()
            print(f">> {len(json_files)} fichiers JSON trouvés dans match_data.")


        if json_files:

        #PUUIDS

            # print("Extraction des PUUIDs...")
            with tt("Extraction des PUUIDs"):
                puuids = extract_puuids_from_json(json_files)

                print(f">> {len(puuids)} PUUIDs extraits.")
            
            # print("Filtrage des PUUIDs...")
            with tt("Filtrage des PUUIDs"):
                puuids = worldCleaner.clear_puuid_list(puuids)

        else:

            print("Aucun fichier JSON trouvé dans match_data. \nOn démarre avec le puuid.")
            custom_puuid = "ed2c2fa0-709d-5177-b19a-57d940c10a6f"
            puuids = [custom_puuid]



        #JSON

        # print("Obtention des jsons liés aux PUUIDs...")
        print(f"\n\nOn part pour {len(puuids) * 19} matchs maximum.\nTemps estimé : {round(len(puuids) * 19 /2.65 /60)} minutes.\nPoids estimé : {round(len(puuids) * 19 * 0.052, 2)} Mo.\n")
        nofloop = 0


        for puuid in puuids:

            print("\n")

            if puuid in json_blacklist:
                print(f"Le PUUID {puuid} est dans la blacklist. On passe au suivant.")
                continue
            
            with tt("Bloc entier"):
                nofloop += 1

                with tt(f"Récupération des données pour le PUUID {nofloop}/{len(puuids)}"):
                    print(f"Récupération des données pour le PUUID : {puuid}", end='\r', flush=True)
                    print("\n-------------------------------")
                    newJson, game_ids = sniffHistory.get_json_from_puuid(puuid, puuids, nofloop)
                    if not newJson:
                        print(f"Aucune donnée trouvée pour le PUUID {puuid}. On passe au suivant.")
                        continue

                # print("Nettoyage des données JSON...")
                with tt("Nettoyage des données JSON"):
                    newJson = worldCleaner.clear_json_list(newJson)

                # print(f"Enregistrement des données Json...")
                with tt("Enregistrement des données JSON"):
                    for json_data in newJson:
                        game_id = json_data.get("gameId", "inconnu")
                        sniffHistory.save_match_json(game_id, json_data, puuid)


                #AJOUT A LA BLACKLIST

                with tt("Ajout des PUUIDs à la blacklist"):
                    # print(f"Ajout des Puuids à la blacklist...")

                    worldCleaner.add_puuids_to_blacklist(puuids)
                    # for puuid in puuids:
                    #     worldCleaner.add_puuid_to_blacklist(puuid)

                with tt("Ajout des JSON à la blacklist"):
                    # print("Ajout des Json à la blacklist...")
                    match_names = []
                    for json_data in newJson:
                        match_names.append("match_" + str(json_data.get("gameId", "inconnu")))
                    worldCleaner.add_jsons_to_blacklist(match_names)



        print("\n\n\n\n\n == Degré terminé! On passe au suivant. == \n\n\n\n")


