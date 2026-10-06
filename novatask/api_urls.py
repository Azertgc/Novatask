from rest_framework.routers import DefaultRouter
from .api_views import ProjetViewSet, TacheProjetViewSet

router = DefaultRouter()
router.register('projets', ProjetViewSet, basename='api-projet')
router.register('taches', TacheProjetViewSet, basename='api-tache')

urlpatterns = router.urls