from django.urls import path
from . import views

urlpatterns = [
    path('', views.connexion, name='acceuil'),
    path('projet/', views.liste_projet, name='liste_projet'),
    path('projet/formulaire/', views.creer_projet, name='formulaire'),
    path('tache/<int:id>/modifier', views.modifier_tache, name='modifier_tache'),
    path('tache/<int:id>/supprimer', views.supprimer_tache, name='supprimer_tache'),
    path('tache/<int:id>/liste/', views.liste_tache, name='liste_tache'),
    path('projet/ajouter/', views.ajouter_tache, name= 'ajouter'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
]