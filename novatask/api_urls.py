"""
Routes de l'API NovaTask.

Le DefaultRouter de DRF génère automatiquement toutes les routes CRUD
(liste, détail, création, modification, suppression) à partir du
lookup_field défini dans chaque ViewSet — pas besoin d'écrire une ligne
par route comme dans urls.py (routes des vues HTML classiques).

Il fournit aussi une page HTML racine listant les endpoints disponibles,
accessible sur /api/ une fois ce fichier branché dans config/urls.py
(voir le README ou API.md pour le réglage correspondant).
"""

from rest_framework.routers import DefaultRouter
from .api_views import ProjetViewSet, TacheProjetViewSet

router = DefaultRouter()
# Premier argument : le préfixe d'URL (/api/projets/, /api/taches/)
# Deuxième argument : le ViewSet associé
# basename : préfixe utilisé en interne par DRF pour nommer les routes
# générées (ex: 'api-projet-list', 'api-projet-detail') — obligatoire ici
# car get_queryset() ne référence pas directement .objects.all(), DRF ne
# peut donc pas déduire ce nom tout seul à partir du modèle.
router.register('projets', ProjetViewSet, basename='api-projet')
router.register('taches', TacheProjetViewSet, basename='api-tache')

urlpatterns = router.urls