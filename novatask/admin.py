from django.contrib import admin
from .models import Utilisateur,Projet,Tache_projet
# Register your models here.

#admin.site.register(Utilisateur)
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = (
        'id_user',
        'nom',
        'prenom',
        'password',
    )

#admin.site.register(Projet)
@admin.register(Projet)
class ProjetAmin(admin.ModelAdmin):
    list_display = (
        'id_proj',
        'intitule',
        'date_debut',
        'date_fin',
        'resultat_attendu',
        'id_user',
        'statut',
        'progression'
    )

    

#admin.site.register(Tache_projet)

@admin.register(Tache_projet)
class Tache_admin(admin.ModelAdmin):
    fields = (
        'num_tache',
        'intitule',
        'heure_debut',
        'heure_fin',
        'resultat_attendu',
        'statut'
    )
    list_filter = (
        'statut',
        'id_proj'
    )
    search_fields = (
        'num_tache',
        
    )   
    list_display = (
        'num_tache',
        'intitule',
        'heure_debut',
        'heure_fin',
        'resultat_attendu',
        'statut',
        'id_proj'
    )