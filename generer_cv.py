"""Génère un CV adapté à une offre.

Usage :
    python generer_cv.py offres/offre_03.txt     -> un seul CV
    python generer_cv.py                         -> un CV par offre du dossier offres/

Le script ne fait que CHOISIR et RÉORDONNER le contenu vrai de profil.json.
Il n'invente rien et n'envoie rien.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from outils import charger, mes_competences, mots_demandes, fabrique_poids

NB_PROJETS = 4   # nombre de projets gardés sur le CV (pour tenir sur une page)

# ------------------------------------------------------------
# 1. Données communes à toutes les offres
# ------------------------------------------------------------
profil = charger("profil.json")
synonymes = charger("synonymes.json")
referentiel = charger("referentiel.json")

mes_mots = mes_competences(profil)
vocabulaire = sorted(mes_mots | set(referentiel["competences_marche"]))
poids = fabrique_poids(set(referentiel["generiques"]))


def pertinence(element, demande):
    """Score d'un élément du CV = somme des poids de ses mots demandés par l'offre."""
    mots = set(element.get("mots_cles", [])) | set(element.get("outils", []))
    return sum(poids(m) for m in mots if m in demande)


def meilleur(liste, demande):
    """L'élément le plus pertinent ; en cas d'égalité, le premier (= version générale)."""
    return max(liste, key=lambda e: pertinence(e, demande))


def adapter(demande):
    """Construit le contenu du CV pour une offre (liste `demande` de mots)."""
    # Titre et accroche : on choisit la variante la plus proche de l'offre
    titre = meilleur(profil["titres"], demande)["texte"]
    accroche = meilleur(profil["accroches"], demande)["texte"]

    # Expériences : on garde l'ordre chronologique, mais on trie les puces
    experiences = []
    for e in profil["experiences"]:
        puces = sorted(e["puces"], key=lambda p: pertinence(p, demande), reverse=True)
        experiences.append({**e, "puces": puces})

    # Projets : les NB_PROJETS plus pertinents
    projets = sorted(profil["projets"], key=lambda p: pertinence(p, demande), reverse=True)
    projets = projets[:NB_PROJETS]

    # Compétences : dans chaque catégorie, les mots demandés passent en premier ;
    # les catégories les plus demandées passent en premier aussi
    competences = []
    for bloc in profil["competences"]:
        elements = sorted(bloc["elements"], key=lambda m: m not in demande)
        score = sum(poids(m) for m in elements if m in demande)
        competences.append({"categorie": bloc["categorie"], "elements": elements, "score": score})
    competences.sort(key=lambda c: c["score"], reverse=True)

    return {
        "id": profil["identite"],
        "titre": titre,
        "accroche": accroche,
        "formation": profil["formation"],
        "experiences": experiences,
        "projets": projets,
        "competences": competences,
        "langues": profil["langues"],
        "soft_skills": profil["soft_skills"],
    }


# ------------------------------------------------------------
# 2. Conversion HTML -> PDF avec un navigateur sans fenêtre
# ------------------------------------------------------------
NAVIGATEURS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google-chrome", "chromium", "msedge",
]


def trouver_navigateur():
    for nav in NAVIGATEURS:
        if Path(nav).exists() or shutil.which(nav):
            return nav
    return None


def vers_pdf(html, pdf):
    nav = trouver_navigateur()
    if nav is None:
        print("   (aucun navigateur trouvé : ouvre le .html et fais Ctrl+P > PDF)")
        return
    subprocess.run([nav, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf.resolve()}", html.resolve().as_uri()],
                   check=True, capture_output=True)


# ------------------------------------------------------------
# 3. Programme principal
# ------------------------------------------------------------
env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
gabarit = env.get_template("cv.html")

fichiers = [Path(a) for a in sys.argv[1:]] or sorted(Path("offres").glob("*.txt"))
Path("sorties").mkdir(exist_ok=True)

for fichier in fichiers:
    texte = fichier.read_text(encoding="utf-8")
    demande = mots_demandes(texte, vocabulaire, synonymes)
    cv = adapter(demande)

    html = Path("sorties") / f"CV_{fichier.stem}.html"
    html.write_text(gabarit.render(**cv), encoding="utf-8")
    vers_pdf(html, html.with_suffix(".pdf"))

    manquants = [m for m in demande if m not in mes_mots]
    print(f"✔ {fichier.name} : {texte.splitlines()[0]}")
    print(f"   Titre   : {cv['titre']}")
    print(f"   Projets : {', '.join(p['titre'] for p in cv['projets'])}")
    print(f"   À ne PAS ajouter sans le maîtriser : {', '.join(manquants) or '-'}")
    print(f"   -> {html.with_suffix('.pdf')}\n")