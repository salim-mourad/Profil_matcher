"""Fonctions partagées par analyse_offres.py et generer_cv.py."""
import json
import re


def charger(nom):
    """Lit un fichier JSON et renvoie son contenu (dict ou liste)."""
    with open(nom, encoding="utf-8") as f:
        return json.load(f)


def contient(texte, mot):
    """True si `mot` apparaît dans `texte` comme mot entier (majuscules ignorées)."""
    motif = r"(?<!\w)" + re.escape(mot) + r"(?!\w)"
    return re.search(motif, texte, re.IGNORECASE) is not None


def mes_competences(profil):
    """Tous les mots (outils + mots-clés) présents quelque part dans le profil."""
    mots = set()
    for projet in profil["projets"]:
        mots.update(projet["outils"])
        mots.update(projet["mots_cles"])
    for experience in profil["experiences"]:
        for puce in experience["puces"]:
            mots.update(puce["outils"])
            mots.update(puce["mots_cles"])
    for bloc in profil["competences"]:
        mots.update(bloc["elements"])
    mots.update(profil["langues_mots_cles"])
    return mots


def mots_demandes(texte, vocabulaire, synonymes):
    """Liste des mots du vocabulaire que l'offre `texte` demande (via les synonymes)."""
    return [m for m in vocabulaire
            if any(contient(texte, v) for v in synonymes.get(m, [m]))]


def fabrique_poids(generiques):
    """Renvoie une fonction poids(mot) : 0.2 pour un mot générique, 1 sinon."""
    def poids(mot):
        return 0.2 if mot in generiques else 1.0
    return poids