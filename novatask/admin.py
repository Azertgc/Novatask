"""
Configuration de l'interface d'administration Django pour NovaTask.

L'admin Django est une interface générée automatiquement à partir des
modèles, pour gérer les données en base sans passer par le site ni l'API
(utile en développement, ou pour une intervention ponctuelle). Chaque
classe ci-dessous personnalise l'affichage d'un modèle dans cette interface.
"""

from django.contrib import admin
from .models import Utilisateur, Projet, Tache_projet
# Register your models here.


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste des utilisateurs de l'admin.
    list_display = (
        'id_user',
        'nom',
        'prenom',
        'password',
    )
    # Attention : afficher 'password' ici montre le hash du mot de passe
    # (jamais le mot de passe en clair, Django le hash toujours), mais
    # reste une information sensible à exposer dans une liste. À réserver
    # à un usage interne/développement, pas à une interface accessible à
    # d'autres administrateurs non habilités.


@admin.register(Projet)
class ProjetAmin(admin.ModelAdmin):
    list_display = (
        'id_proj',
        'intitule',
        'date_debut',
        'date_fin',
        'resultat_attendu',
        'id_user',
        'statut',       # @property calculée : affichable en lecture,
        'progression',  # mais jamais triable ni filtrable nativement
                         # par l'admin (ce ne sont pas de vraies colonnes
                         # en base, voir plus bas pour list_filter).
    )
    # list_filter ajoute des filtres cliquables dans la colonne de droite
    # de l'admin. 'id_user' filtre par utilisateur (affiche sa représentation
    # __str__ dans la liste des choix) ; 'id_user__nom' traverse la relation
    # pour filtrer directement par le champ 'nom' de l'utilisateur lié,
    # ce qui est redondant avec 'id_user' si celui-ci affiche déjà le nom,
    # mais permet un filtre plus direct si le nom seul suffit.
    list_filter = (
        'id_user',
        'id_user__nom',
    )


@admin.register(Tache_projet)
class Tache_admin(admin.ModelAdmin):
    # 'fields' restreint les champs visibles/modifiables sur la page de
    # détail d'une tâche dans l'admin (le formulaire d'édition). Ici,
    # 'priorite' et 'fonctionnalite' ne sont pas listés : ils existent
    # dans le modèle mais ne seront ni affichés ni modifiables depuis
    # cette page d'édition admin (volontaire, ou à vérifier si oubli).
    fields = (
        'num_tache',
        'intitule',
        'heure_debut',
        'heure_fin',
        'resultat_attendu',
        'statut',
    )
    # Filtres cliquables dans la liste des tâches : par statut, et par
    # projet parent (id_proj) — pratique pour isoler rapidement les
    # tâches d'un projet donné en développement.
    list_filter = (
        'statut',
        'id_proj',
    )
    # Ajoute une barre de recherche en haut de la liste, qui interroge
    # le(s) champ(s) listés ici. Un seul champ ici : 'num_tache' (ex:
    # taper "T001" retrouve directement la tâche correspondante).
    search_fields = (
        'num_tache',
    )
    # Colonnes affichées dans la liste de toutes les tâches (vue d'ensemble,
    # différente de la page de détail configurée par 'fields' ci-dessus).
    list_display = (
        'num_tache',
        'intitule',
        'heure_debut',
        'heure_fin',
        'resultat_attendu',
        'statut',
        'id_proj',
    )