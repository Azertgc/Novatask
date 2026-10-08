from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil : réutilise directement la vue connexion (pas de
    # vue séparée pour "/") — un visiteur non connecté atterrit donc sur
    # le formulaire de connexion dès l'ouverture du site.
    path('', views.connexion, name='acceuil'),

    path('projet/', views.liste_projet, name='liste_projet'),
    path('projet/formulaire/', views.creer_projet, name='formulaire'),

    # <int:id> : capture un entier dans l'URL et le transmet comme
    # paramètre 'id' à la vue (ex: /tache/7/modifier -> modifier_tache(request, id=7)).
    # Il s'agit ici de la clé primaire technique de Django (l'entier auto-
    # incrémenté), pas de num_tache (l'identifiant métier T001...) utilisé
    # côté API (api_urls.py), qui lui utilise lookup_field='num_tache'.
    path('tache/<int:id>/modifier', views.modifier_tache, name='modifier_tache'),
    path('tache/<int:id>/supprimer', views.supprimer_tache, name='supprimer_tache'),
    path('tache/<int:id>/liste/', views.liste_tache, name='liste_tache'),

    path('projet/ajouter/', views.ajouter_tache, name= 'ajouter'),

    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # Endpoint JSON interrogé par notifications.js (polling, chapitre 17).
    path('api/taches/notifications/', views.taches_notifications_json, name='tache_notifications_json'),
    path('api/taches/notifications/', views.taches_notifications_json, name='taches_notifications_json'),
]