import os


def clear_puuid_list(puuids):
    """
    retourne la liste sans les PUUIDs enregistrés dans le fichier puuidblacklist.txt
    """
    localpath = os.path.dirname(__file__)
    blacklist_path = os.path.join(localpath, "match_data", "puuidblacklist.txt")

    with open(blacklist_path, "r", encoding="utf-8") as f:
        blacklist = {line.strip() for line in f if line.strip()}

    # Filtrer les PUUIDs qui ne sont pas dans la blacklist
    filtered_puuids = [puuid for puuid in puuids if puuid not in blacklist]

    print(f"Filtrage des PUUIDs : {len(puuids)} -> {len(filtered_puuids)}", end='\r', flush=True)

    return filtered_puuids


def clear_json_list(json_files):
    """
    retourne la liste sans les fichiers JSON enregistrés dans le fichier jsonblacklist.txt
    """
    localpath = os.path.dirname(__file__)
    blacklist_path = os.path.join(localpath, "match_data", "jsonblacklist.txt")

    with open(blacklist_path, "r", encoding="utf-8") as f:
        blacklist = {line.strip() for line in f if line.strip()}

    # Filtrer les fichiers JSON qui ne sont pas dans la blacklist

    filtered_json_files = []
    for file in json_files:
        # Suppose each dict has a 'filename' key; adjust as needed
        filename = file if isinstance(file, str) else file.get('filename')
        if filename in blacklist:
            print(f"Fichier JSON {filename} est dans la blacklist, il sera ignoré.")
            continue
        filtered_json_files.append(file)


    # print(f"Filtrage des fichiers JSON : {len(json_files)} -> {len(filtered_json_files)}", end='\r', flush=True)

    return filtered_json_files


# def add_json_to_blacklist(json_file):
#     """
#     Ajoute un fichier JSON à la blacklist.
#     """
#     localpath = os.path.dirname(__file__)
#     blacklist_path = os.path.join(localpath, "match_data", "jsonblacklist.txt")


#     with open(blacklist_path, "a+", encoding="utf-8") as f:
#         f.write(json_file + "\n")

def add_jsons_to_blacklist(json_files):
    """
    Ajoute une liste de fichiers JSON à la blacklist.
    """
    localpath = os.path.dirname(__file__)
    blacklist_path = os.path.join(localpath, "match_data", "jsonblacklist.txt")

    with open(blacklist_path, "a+", encoding="utf-8") as f:
        for json_file in json_files:
            f.write(json_file + "\n")


# def add_puuid_to_blacklist(puuid):
#     """
#     Ajoute un PUUID à la blacklist.
#     """
#     localpath = os.path.dirname(__file__)
#     blacklist_path = os.path.join(localpath, "match_data", "puuidblacklist.txt")

#     with open(blacklist_path, "a+", encoding="utf-8") as f:
#         f.write(puuid + "\n")

def add_puuids_to_blacklist(puuids):
    """
    Ajoute une liste de PUUIDs à la blacklist.
    """
    localpath = os.path.dirname(__file__)
    blacklist_path = os.path.join(localpath, "match_data", "puuidblacklist.txt")

    with open(blacklist_path, "a+", encoding="utf-8") as f:
        for puuid in puuids:
            f.write(puuid + "\n")