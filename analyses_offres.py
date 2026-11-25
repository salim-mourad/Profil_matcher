from collections import Counter
from pathlib import Path

from outils import charger, mes_competences, mots_demandes, fabrique_poids

# ------------------------------------------------------------
# 1. Charger les données
# ------------------------------------------------------------
profil = charger("profil.json")
synonymes = charger("synonymes.json")
referentiel = charger("referentiel.json")

mes_mots = mes_competences(profil)
vocabulaire = sorted(mes_mots | set(referentiel["competences_marche"]))
poids = fabrique_poids(set(referentiel["generiques"]))

# ------------------------------------------------------------
# 2. Analyser chaque offre
# ------------------------------------------------------------
resultats = []
demandes = Counter()

for fichier in sorted(Path("offres").glob("*.txt")):
    texte = fichier.read_text(encoding="utf-8")
    titre = texte.splitlines()[0]

    demande = mots_demandes(texte, vocabulaire, synonymes)
    demandes.update(demande)

    acquis = [m for m in demande if m in mes_mots]
    manquants = [m for m in demande if m not in mes_mots]

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