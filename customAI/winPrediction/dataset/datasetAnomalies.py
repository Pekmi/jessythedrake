




def extract_duo_candidates(duo_candidates, role_map):
    """
    Extrait les candidats pour les rôles ADC et SUPPORT à partir des DUO
    """
    # Traitement des DUO / Séparation des ADC et SUPPORT
    for team, duo_list in duo_candidates.items():
        if len(duo_list) == 2:
            adc = max(duo_list, key=lambda x: x["stats"].get("totalMinionsKilled", 0))
            support = min(duo_list, key=lambda x: x["stats"].get("totalMinionsKilled", 0))
            if team not in role_map:
                role_map[team] = {}
            role_map[team]["BOTTOM"] = adc["championId"]
            role_map[team]["SUPPORT"] = support["championId"]
    return role_map  # Retourne role_map corrigé



def correct_jungle_duplicates(role_map, participants):
    """
    Corrige les cas où il y a des doublons dans les rôles JUNGLE et TOP/MIDDLE/BOTTOM
    """
    for team in [100, 200]:
        roles_found = {}
        for p in participants:
            if p["teamId"] != team:
                continue
            lane = p["timeline"].get("lane", "")
            role = p["timeline"].get("role", "")
            if lane in ["TOP", "MIDDLE", "BOTTOM"] and not (lane == "BOTTOM" and role.upper() == "DUO"):
                key = lane
                if key not in roles_found:
                    roles_found[key] = []
                roles_found[key].append(p)
        for lane, players in roles_found.items():
            if len(players) == 2:
                smite_player = None
                for p in players:
                    spell1 = p.get("spell1Id", 0)
                    spell2 = p.get("spell2Id", 0)
                    if spell1 == 11 or spell2 == 11:
                        smite_player = p
                        break
                if smite_player:
                    if team not in role_map:
                        role_map[team] = {}
                    role_map[team]["JUNGLE"] = smite_player["championId"]
                    other_player = [p for p in players if p != smite_player][0]
                    if lane not in role_map[team] or role_map[team][lane] != other_player["championId"]:
                        role_map[team][lane] = other_player["championId"]
    return role_map  # Retourne role_map corrigé




def resolve_double_lane_missing_other(role_map, participants, doublon_lane, missing_lane, doublon_lane_ids, missing_lane_ids):
    """
    Corrige pour toutes les équipes les cas où il y a deux joueurs sur 'doublon_lane' et aucun sur 'missing_lane'.
    """
    for team in [100, 200]:
        # Vérifie qu'on a deux joueurs sur doublon_lane et zéro sur missing_lane
        cands = [p for p in participants if p["teamId"] == team and p["timeline"].get("lane") == doublon_lane]
        missing = [p for p in participants if p["teamId"] == team and p["timeline"].get("lane") == missing_lane]
        if len(cands) == 2 and len(missing) == 0:
            champ1, champ2 = cands[0]["championId"], cands[1]["championId"]
            # Priorité : missing_lane_ids
            if champ1 in missing_lane_ids and champ2 not in missing_lane_ids:
                role_map[team][missing_lane] = champ1
                role_map[team][doublon_lane] = champ2
            elif champ2 in missing_lane_ids and champ1 not in missing_lane_ids:
                role_map[team][missing_lane] = champ2
                role_map[team][doublon_lane] = champ1
            # Sinon, doublon_lane_ids
            elif champ1 in doublon_lane_ids and champ2 not in doublon_lane_ids:
                role_map[team][doublon_lane] = champ1
                role_map[team][missing_lane] = champ2
            elif champ2 in doublon_lane_ids and champ1 not in doublon_lane_ids:
                role_map[team][doublon_lane] = champ2
                role_map[team][missing_lane] = champ1
            else:
                # Fallback : TP
                with_tp = None
                for p in cands:
                    if p.get("spell1Id", 0) == 12 or p.get("spell2Id", 0) == 12:
                        with_tp = p
                        break
                if with_tp:
                    role_map[team][missing_lane] = with_tp["championId"]
                    other = [p for p in cands if p != with_tp][0]
                    role_map[team][doublon_lane] = other["championId"]
                else:
                    # Farm
                    c1, c2 = cands
                    if c1["stats"].get("totalMinionsKilled", 0) >= c2["stats"].get("totalMinionsKilled", 0):
                        role_map[team][doublon_lane] = c1["championId"]
                        role_map[team][missing_lane] = c2["championId"]
                    else:
                        role_map[team][doublon_lane] = c2["championId"]
                        role_map[team][missing_lane] = c1["championId"]
    return role_map




def fix_bot_support_solo_cases(role_map, participants, team, support_ids):
    # S'il manque un ADC ou un support
    missing_adc = "BOTTOM" not in role_map.get(team, {})
    missing_support = "SUPPORT" not in role_map.get(team, {})
    if not (missing_adc or missing_support):
        return role_map

    # Cherche un BOTTOM/SOLO (pour ADC)
    adc_cand = [p for p in participants if p["teamId"] == team and p["timeline"].get("lane") == "BOTTOM" and p["timeline"].get("role","").upper() == "SOLO"]
    if missing_adc and adc_cand:
        role_map[team]["BOTTOM"] = adc_cand[0]["championId"]

    # Cherche un MIDDLE/SUPPORT (pour support roaming)
    supp_cand = [p for p in participants if p["teamId"] == team and p["timeline"].get("lane") == "MIDDLE" and p["timeline"].get("role","").upper() == "SUPPORT"]
    # Attention à ne pas écraser le vrai midlaner
    mid_id = role_map.get(team, {}).get("MIDDLE", None)
    if missing_support and supp_cand:
        for s in supp_cand:
            if s["championId"] != mid_id:
                role_map[team]["SUPPORT"] = s["championId"]
                break

    # Fallback : si toujours pas trouvé, prend le support typique non encore assigné
    if missing_support and "SUPPORT" not in role_map.get(team, {}):
        # Liste des champions déjà assignés
        already = set(role_map.get(team, {}).values())
        # Cherche un pick support typique
        supp_picks = [p for p in participants if p["teamId"] == team and p["championId"] in support_ids and p["championId"] not in already]
        if supp_picks:
            role_map[team]["SUPPORT"] = supp_picks[0]["championId"]
        else:
            # Sinon, prend le joueur restant avec le moins de farm
            not_assigned = [p for p in participants if p["teamId"] == team and p["championId"] not in already]
            if not_assigned:
                supp = min(not_assigned, key=lambda x: x["stats"].get("totalMinionsKilled", 0))
                role_map[team]["SUPPORT"] = supp["championId"]

    return role_map




def fill_single_missing_role(role_map, participants):
    """
    Si une seule lane est manquante et un seul champion non assigné, assigne-le à cette lane.
    """
    for team in [100, 200]:
        roles = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"]
        assigned = set(role_map.get(team, {}).values())
        missing_roles = [role for role in roles if role not in role_map.get(team, {})]
        team_champs = [p["championId"] for p in participants if p["teamId"] == team]
        unused = [c for c in team_champs if c not in assigned]
        if len(missing_roles) == 1 and len(unused) == 1:
            # Un seul rôle manquant, un seul champion non utilisé : on assigne
            role_map[team][missing_roles[0]] = unused[0]
    return role_map








def repair_all(duo_candidates, role_map, participants):

    role_map = extract_duo_candidates(duo_candidates, role_map)

    role_map = correct_jungle_duplicates(role_map, participants)

    TOP_LANE_CHAMPS, MID_LANE_CHAMPS, SUPPORT_CHAMPS = get_lane_list()

    # Double mid, 0 top
    role_map = resolve_double_lane_missing_other(role_map, participants, "MIDDLE", "TOP", MID_LANE_CHAMPS, TOP_LANE_CHAMPS)
    # Double top, 0 mid
    role_map = resolve_double_lane_missing_other(role_map, participants, "TOP", "MIDDLE", TOP_LANE_CHAMPS, MID_LANE_CHAMPS)
    
    role_map = fix_bot_support_solo_cases(role_map, participants, 100, SUPPORT_CHAMPS)
    role_map = fix_bot_support_solo_cases(role_map, participants, 200, SUPPORT_CHAMPS)


    role_map = fill_single_missing_role(role_map, participants)

    return role_map




def get_lane_list():
    """
    Retourne la liste des lanes possibles
    """
    TOP_LANE_CHAMPS = [
        266,  # Aatrox
        875,  # Sett
        41,   # Gangplank
        122,  # Darius
        164,  # Camille
        114,  # Fiora
        24,   # Jax
        82,   # Mordekaiser
        516,  # Ornn
        98,   # Shen
        39,   # Irelia
        6,    # Urgot
        420,  # Illaoi
        897,  # K'Sante
        887,  # Gwen
        86,   # Garen
        2,    # Olaf
        106,  # Volibear
        54,   # Malphite
    ]

    MID_LANE_CHAMPS = [
        103,  # Ahri
        238,  # Zed
        134,  # Syndra
        245,  # Ekko
        13,   # Ryze
        157,  # Yasuo
        268,  # Azir
        7,    # LeBlanc
        142,  # Zoe
        61,   # Orianna
        127,  # Lissandra
        777,  # Yone
        69,   # Cassiopeia
        517,  # Sylas
        84,   # Akali
        105,  # Fizz
        50,   # Swain
        91,   # Talon
        4,    # Twisted Fate
        55,   # Katarina
        268,  # Azir
        112,  # Viktor
    ]

    SUPPORT_CHAMPS = [16, 40, 412, 111, 53, 89, 43, 267, 497, 526, 555, 235, 201, 74, 44, 22, 25, 432, 350, 37, 63, 117]


    return TOP_LANE_CHAMPS, MID_LANE_CHAMPS, SUPPORT_CHAMPS