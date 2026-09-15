from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projet/', views.liste_projet, name='liste_projet'),
    path('projet/formulaire/', views.creer_projet, name='formulaire'),
    path('tache/<int:id>/modifier', views.modifier_tache, name='modifier_tache'),
    path('tache/<int:id>/supprimer', views.supprimer_tache, name='supprimer_tache'),
    path('tache/<int:id>/liste/', views.liste_tache, name='liste_tache'),
    path('projet/ajouter/', views.ajouter_tache, name= 'ajouter')
]