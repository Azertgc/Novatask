# novatask/services.py
from django.utils import timezone
from .models import Tache_projet


def taches_a_surveiller():
    aujourd_hui = timezone.localdate()
    return Tache_projet.objects.exclude(
        statut='terminee'
    ).filter(
        date_realisation__lte=aujourd_hui
    ).select_related('id_proj', 'id_proj__id_user')


def verifier_echeances():
    maintenant = timezone.localtime()
    resultats = {'a_venir': [], 'en_cours': [], 'echeance_depassee': []}

    for tache in taches_a_surveiller():
        if maintenant < tache.datetime_debut:
            resultats['a_venir'].append(tache)
        elif tache.datetime_debut <= maintenant < tache.datetime_fin:
            resultats['en_cours'].append(tache)
        else:
            resultats['echeance_depassee'].append(tache)

    return resultats

from datetime import timedelta

SEUIL_PROCHE_ECHEANCE = timedelta(minutes=15)


def taches_proches_echeance(seuil=SEUIL_PROCHE_ECHEANCE):
    maintenant = timezone.localtime()
    limite = maintenant + seuil

    return [
        tache for tache in taches_a_surveiller()
        if maintenant < tache.datetime_debut <= limite
    ]

def taches_proches_echeance_non_notifiees(seuil=SEUIL_PROCHE_ECHEANCE):
    return [
        tache for tache in taches_proches_echeance(seuil)
        if not tache.rappel_envoye
    ]


def marquer_rappel_envoye(taches):
    for tache in taches:
        tache.rappel_envoye = True
    Tache_projet.objects.bulk_update(taches, ['rappel_envoye'])