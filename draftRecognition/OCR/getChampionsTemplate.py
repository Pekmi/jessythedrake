import os
import requests

champions = [   "Aatrox", "Ahri", "Akali", "Alistar", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe", "AurelionSol",
                "Azir", "Bard", "Belveth", "Blitzcrank", "Brand", "Briar", "Braum", "Caitlyn", "Camille", "Cassiopeia",
                "Chogath", "Corki", "Darius", "Diana", "DrMundo", "Draven", "Ekko", "Elise", "Evelynn", "Ezreal",
                "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas", "Graves", "Gwen",
                "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia", "Ivern", "Janna", "JarvanIV", "Jax", "Jayce",
                "Jhin", "Jinx", "Kaisa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina", "Kayle", "Kayn",
                "Kennen", "Khazix", "Kindred", "Kled", "KogMaw", "KSante", "Leblanc", "LeeSin", "Leona", "Lillia",
                "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai", "Milio", "MissFortune",
                "Mordekaiser", "Morgana", "Naafiri", "Nami", "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah",
                "Nocturne", "Nunu", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn",
                "Rakan", "Rammus", "RekSai", "Rell", "Renata", "Renekton", "Rengar", "Riven", "Rumble", "Ryze",
                "Samira", "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion",
                "Sivir", "Skarner", "Sona", "Soraka", "Swain", "Sylas", "Syndra", "TahmKench", "Taliyah", "Talon",
                "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", "TwistedFate", "Twitch", "Udyr",
                "Urgot", "Varus", "Vayne", "Veigar", "Velkoz", "Vex", "Vi", "Viego", "Viktor", "Vladimir",
                "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "XinZhao", "Yasuo", "Yone", "Yorick",
                "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"
            ]

print(len(champions), "champions found")


TEMPLATE_URL = "https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/"
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__),"championsTemplates")
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)

for champion in champions:
    if os.path.exists(os.path.join(TEMPLATE_FOLDER, champion + ".png")):
       print(f"Template for {champion} already exists, skipping download.                    ", end='\r', flush=True)
       continue
    url = TEMPLATE_URL + champion + ".png"
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(TEMPLATE_FOLDER, champion + ".png"), 'wb') as file:
            file.write(response.content)
        print(f"Downloaded template for {champion}                       ", end='\r', flush=True)
    else:
        print(f"\nFailed to download template for {champion}, status code: {response.status_code}\n")