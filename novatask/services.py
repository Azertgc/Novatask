"""
Fonctions utilitaires "métier" de NovaTask, indépendantes des vues.

Regroupées ici plutôt que dans views.py car réutilisées à la fois côté
vues HTML classiques (views.py) et côté API (api_views.py) — par exemple
normaliser() pour la recherche insensible aux accents, ou les fonctions de
surveillance des échéances pour notifications.js (polling, chapitre 17).
"""

from django.utils import timezone
from .models import Tache_projet


def taches_a_surveiller():
    # Point d'entrée commun à verifier_echeances() et
    # taches_proches_echeance() : toutes les tâches encore actives
    # aujourd'hui, c'est-à-dire ni déjà terminées, ni prévues pour un jour
    # futur (date_realisation__lte=aujourd_hui exclut les tâches à venir
    # plus tard, pas celles du jour même).
    aujourd_hui = timezone.localdate()
    return Tache_projet.objects.exclude(
        statut='terminee'
    ).filter(
        date_realisation__lte=aujourd_hui
    # select_related('id_proj', 'id_proj__id_user') : précharge en une
    # seule requête SQL le projet de chaque tâche, ainsi que l'utilisateur
    # propriétaire de ce projet. Évite une requête supplémentaire par
    # tâche (N+1) quand l'appelant accède ensuite à tache.id_proj ou
    # tache.id_proj.id_user (ex: filtrage par utilisateur côté API).
    ).select_related('id_proj', 'id_proj__id_user')


def verifier_echeances():
    # Classe chaque tâche active dans l'une des trois catégories, en
    # comparant l'instant présent à la fenêtre [datetime_debut, datetime_fin)
    # de la tâche (propriétés calculées sur le modèle à partir de
    # date_realisation + heure_debut/heure_fin).
    maintenant = timezone.localtime()
    resultats = {'a_venir': [], 'en_cours': [], 'echeance_depassee': []}

    for tache in taches_a_surveiller():
        if maintenant < tache.datetime_debut:
            resultats['a_venir'].append(tache)
        elif tache.datetime_debut <= maintenant < tache.datetime_fin:
            resultats['en_cours'].append(tache)
        else:
            # Ni à venir, ni en cours : la tâche a dépassé son heure de
            # fin sans être marquée 'terminee' par l'utilisateur.
            resultats['echeance_depassee'].append(tache)

    return resultats

from datetime import timedelta

# Fenêtre de "proximité" utilisée par taches_proches_echeance() : une
# tâche est considérée comme imminente si son démarrage tombe dans les
# 15 minutes à venir. Valeur par défaut du paramètre seuil ci-dessous,
# modifiable à l'appel si besoin d'une fenêtre différente.
SEUIL_PROCHE_ECHEANCE = timedelta(minutes=15)


def taches_proches_echeance(seuil=SEUIL_PROCHE_ECHEANCE):
    # Sous-ensemble de taches_a_surveiller() dont le démarrage tombe
    # strictement entre maintenant et maintenant + seuil — utilisé pour
    # déclencher une notification avant le début d'une tâche, pas après.
    maintenant = timezone.localtime()
    limite = maintenant + seuil

    return [
        tache for tache in taches_a_surveiller()
        if maintenant < tache.datetime_debut <= limite
    ]

def taches_proches_echeance_non_notifiees(seuil=SEUIL_PROCHE_ECHEANCE):
    # Filtre supplémentaire sur rappel_envoye : évite de renvoyer une
    # notification pour une tâche déjà signalée lors d'un appel précédent
    # (le polling de notifications.js appelle cette fonction à intervalle
    # régulier, voir taches_notifications_json dans views.py).
    return [
        tache for tache in taches_proches_echeance(seuil)
        if not tache.rappel_envoye
    ]


def marquer_rappel_envoye(taches):
    # Appelée juste après l'envoi effectif des notifications, pour que
    # taches_proches_echeance_non_notifiees() ne les renvoie plus au
    # prochain appel. bulk_update() : une seule requête SQL pour mettre à
    # jour toutes les tâches de la liste, plutôt qu'un .save() par tâche.
    for tache in taches:
        tache.rappel_envoye = True
    Tache_projet.objects.bulk_update(taches, ['rappel_envoye'])

import unicodedata


def normaliser(texte):
    """Retire les accents et met en minuscule, pour une recherche insensible aux accents."""
    # Garde-fou : une valeur vide/None (champ de recherche non rempli, ou
    # intitule éventuellement vide) ne doit pas faire planter unicodedata.
    if not texte:
        return ''
    # NFD (Normalization Form Decomposed) décompose chaque caractère
    # accentué en deux caractères séparés : la lettre de base + un
    # caractère "accent" distinct (ex: 'é' -> 'e' + accent aigu).
    texte = unicodedata.normalize('NFD', texte)
    # category(c) != 'Mn' : ne garde que les caractères qui ne sont PAS
    # des "Marks, nonspacing" (accents, cédilles...), isolés par le NFD
    # ci-dessus. Il ne reste donc que les lettres de base.
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    return texte.lower()