import json
import re
from collections import Counter
from pathlib import Path


def contient(texte, mot):
    """True si `mot` apparaît dans `texte` comme mot entier (majuscules ignorées)."""
    motif = r"(?<!\w)" + re.escape(mot) + r"(?!\w)"
    return re.search(motif, texte, re.IGNORECASE) is not None


def charger(nom):
    with open(nom, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# 1. Charger les données
# ------------------------------------------------------------
profil = charger("profil.json")
synonymes = charger("synonymes.json")
referentiel = charger("referentiel.json")

# Mes compétences (outils + mots-clés de tous les projets), sans doublons
mes_mots = set()
for projet in profil["projets"]:
    mes_mots.update(projet["outils"])
    mes_mots.update(projet["mots_cles"])

# Toutes les compétences que l'on sait reconnaître = les miennes + celles du marché
vocabulaire = sorted(mes_mots | set(referentiel["competences_marche"]))

# Poids : un mot générique compte peu, un mot technique compte pleinement
generiques = set(referentiel["generiques"])
def poids(mot):
    return 0.2 if mot in generiques else 1.0


# ------------------------------------------------------------
# 2. Analyser chaque offre
# ------------------------------------------------------------
resultats = []
demandes = Counter()          # combien d'offres demandent chaque compétence

for fichier in sorted(Path("offres").glob("*.txt")):
    texte = fichier.read_text(encoding="utf-8")
    titre = texte.splitlines()[0]

    # compétences demandées par l'offre (parmi celles qu'on sait reconnaître)
    demande = [m for m in vocabulaire
               if any(contient(texte, v) for v in synonymes.get(m, [m]))]
    demandes.update(demande)

    acquis = [m for m in demande if m in mes_mots]
    manquants = [m for m in demande if m not in mes_mots]

    # score = part pondérée des compétences demandées que je possède
    total = sum(poids(m) for m in demande)
    score = 100 * sum(poids(m) for m in acquis) / total if total else 0

    resultats.append({"titre": titre, "fichier": fichier.name, "score": score,
                      "acquis": acquis, "manquants": manquants})


# ------------------------------------------------------------
# 3. Afficher le classement
# ------------------------------------------------------------
print("=== CLASSEMENT DES OFFRES ===\n")
for r in sorted(resultats, key=lambda r: r["score"], reverse=True):
    print(f"{r['score']:5.0f} % | {r['titre']}  ({r['fichier']})")
    print(f"        ✔ {', '.join(r['acquis']) or '-'}")
    print(f"        ✘ {', '.join(r['manquants']) or '-'}")
    print()

# ------------------------------------------------------------
# 4. Vue du marché : compétences les plus demandées
# ------------------------------------------------------------
print("=== COMPÉTENCES LES PLUS DEMANDÉES ===\n")
for mot, n in demandes.most_common(15):
    etat = "✔ j'ai" if mot in mes_mots else "✘ à mettre en avant ou à acquérir"
    print(f"{n:>2} offre(s) | {mot:<25} {etat}")