import json
from pathlib import Path

# ------------------------------------------------------------
# 1. Charger le profil (le fichier JSON devient un dictionnaire)
# ------------------------------------------------------------
with open("profil.json", encoding="utf-8") as f:
    profil = json.load(f)

# ------------------------------------------------------------
# 2. Rassembler tous les mots-clés du profil dans une seule liste
# ------------------------------------------------------------
mes_mots = []
for projet in profil["projets"]:
    mes_mots.extend(projet["outils"])      # ajoute tous les outils du projet
    mes_mots.extend(projet["mots_cles"])   # ajoute tous les mots-clés du projet

# Un même mot peut apparaître dans plusieurs projets (ex. "Python") :
# set() supprime les doublons, sorted() remet la liste dans l'ordre alphabétique.
mes_mots = sorted(set(mes_mots))
print("Mots-clés dans mon profil :", len(mes_mots))
print()

# ------------------------------------------------------------
# 3. Analyser chaque offre du dossier offres/
# ------------------------------------------------------------
for fichier in sorted(Path("offres").glob("*.txt")):
    texte = fichier.read_text(encoding="utf-8")
    titre = texte.splitlines()[0]          # 1re ligne du fichier = titre du poste

    trouves = []
    for mot in mes_mots:
        # on compare en minuscules pour que "Python" et "python" correspondent
        if mot.lower() in texte.lower():
            trouves.append(mot)

    print(f"{fichier.name} | {titre}")
    print(f"   {len(trouves)} mots-clés trouvés : {', '.join(trouves)}")
    print()