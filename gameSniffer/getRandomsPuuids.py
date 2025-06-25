import requests

API_KEY = "RGAPI-5204b6a5-0dca-4874-b433-2a99934031eb"
region = "kr"  # serveur coréen
summoner_name = "Blue"  # pseudo officiel de Faker
tagLine = "KR33"  # tagLine de Faker, peut être vide si pas de tag

url = f"https://{region}.api.riotgames.com/lol/account/v1/accounts/by-riot-id/{summoner_name}/{tagLine}"
headers = {"X-Riot-Token": API_KEY}

res = requests.get(url, headers=headers)
data = res.json()

print("PUUID:", data.get("puuid"))