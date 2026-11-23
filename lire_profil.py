import json
with open ("profil.json", encoding="utf-8") as f:
    profil=json.load(f)
print("OK :", len(profil["projets"]), "projets")
for projet in profil["projets"]:
    print("-", projet["titre"])