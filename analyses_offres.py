import json
import re
from pathlib import Path


def contient(texte, mot):
    """Renvoie True si `mot` apparaît dans `texte` comme mot entier (sans tenir compte des majuscules)."""
    # (?<!\w) : pas de lettre/chiffre juste avant ; (?!\w) : pas de lettre/chiffre juste après
    motif = r"(?<!\w)" + re.escape(mot) + r"(?!\w)"
    return re.search(motif, texte, re.IGNORECASE) is not None


# ------------------------------------------------------------
# 1. Charger le profil et le dictionnaire de synonymes
# ------------------------------------------------------------
with open("profil.json", encoding="utf-8") as f:
    profil = json.load(f)

with open("synonymes.json", encoding="utf-8") as f:
    synonymes = json.load(f)

# ------------------------------------------------------------
# 2. Rassembler tous les mots-clés du profil (sans doublons)
# ------------------------------------------------------------
mes_mots = []
for projet in profil["projets"]:
    mes_mots.extend(projet["outils"])
    mes_mots.extend(projet["mots_cles"])
mes_mots = sorted(set(mes_mots))
print("Mots-clés dans mon profil :", len(mes_mots))
print()

# ------------------------------------------------------------
# 3. Analyser chaque offre et garder les résultats dans une liste
# ------------------------------------------------------------
resultats = []
for fichier in sorted(Path("offres").glob("*.txt")):
    texte = fichier.read_text(encoding="utf-8")
    titre = texte.splitlines()[0]

    trouves = []
    for mot in mes_mots:
        # toutes les écritures possibles du mot ; s'il n'a pas de synonymes, juste lui-même
        variantes = synonymes.get(mot, [mot])
        # any(...) vaut True si AU MOINS UNE variante est présente dans le texte
        if any(contient(texte, v) for v in variantes):
            trouves.append(mot)

    resultats.append({"fichier": fichier.name, "titre": titre, "trouves": trouves})

# ------------------------------------------------------------
# 4. Afficher les offres de la meilleure à la moins bonne
# ------------------------------------------------------------
# key=... : on trie selon le nombre de mots trouvés ; reverse=True : du plus grand au plus petit
resultats = sorted(resultats, key=lambda r: len(r["trouves"]), reverse=True)

for r in resultats:
    print(f"{len(r['trouves']):>2} | {r['titre']}  ({r['fichier']})")
    print(f"     {', '.join(r['trouves'])}")
    print()