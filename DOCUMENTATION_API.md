# API NovaTask

Référence technique de l'API REST, basée sur Django REST Framework (DRF).

## Installation

```bash
pip install djangorestframework
```

`config/settings.py` :
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'novatask',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/minute',
    },
}
```

`config/urls.py` :
```python
from django.urls import path, include

urlpatterns = [
    ...
    path('api/', include('novatask.api_urls')),
]
```

## Authentification

`SessionAuthentication` : réutilise le cookie de session du site (connexion via `/connexion/`). Les requêtes `POST`/`PUT`/`PATCH`/`DELETE` nécessitent le header CSRF, sauf depuis l'interface navigable DRF.

`IsAuthenticated` par défaut sur toutes les routes : accès anonyme refusé.

## Isolation des données

Chaque `ViewSet` filtre son `get_queryset()` par `id_user=request.user` (projets) ou `id_proj__id_user=request.user` (tâches) : un utilisateur ne peut jamais lister, consulter, modifier ou supprimer les données d'un autre utilisateur, y compris via l'API.

## Identifiants métier dans les relations (`id_proj`)

Le champ `id_proj` du `TacheProjetSerializer` utilise `SlugRelatedField(slug_field='id_proj', ...)`, et non le `PrimaryKeyRelatedField` généré par défaut. Sans ça, DRF attend la clé primaire technique auto-incrémentée de Django (un entier invisible), pas l'identifiant métier (`P001`) — toute requête envoyant `id_proj: "P001"` échouerait avec `Incorrect type. Expected pk value, received str.`

## Validation avant écriture (pas après)

`perform_create`/`perform_update` sur `TacheProjetViewSet` construisent et valident l'instance (`full_clean()`) **avant** tout appel à `.save()`, plutôt que de sauvegarder puis valider après coup. Une tentative d'écriture invalide déclenche directement la `CheckConstraint` de la base (`IntegrityError` non gérée, erreur 500) avant même que Python n'ait la main — valider après `save()` ne suffit pas quand une contrainte existe au niveau base de données.

## Endpoints

| Méthode | URL | Action |
|---|---|---|
| `GET` | `/api/projets/` | Liste des projets de l'utilisateur connecté |
| `POST` | `/api/projets/` | Créer un projet |
| `GET` | `/api/projets/{id_proj}/` | Détail d'un projet |
| `PUT` / `PATCH` | `/api/projets/{id_proj}/` | Modifier un projet |
| `DELETE` | `/api/projets/{id_proj}/` | Supprimer un projet |
| `GET` | `/api/taches/` | Liste des tâches de l'utilisateur connecté |
| `POST` | `/api/taches/` | Créer une tâche |
| `GET` | `/api/taches/{num_tache}/` | Détail d'une tâche |
| `PUT` / `PATCH` | `/api/taches/{num_tache}/` | Modifier une tâche |
| `DELETE` | `/api/taches/{num_tache}/` | Supprimer une tâche |

## Paramètres de requête (`/api/taches/`)

| Paramètre | Exemple | Effet |
|---|---|---|
| `recherche` | `?recherche=systeme` | Recherche dans l'intitulé, insensible aux accents |
| `statut` (répétable) | `?statut=a_faire&statut=en_cours` | Filtre par statut(s) |
| `priorite` (répétable) | `?priorite=haute` | Filtre par priorité(s) |
| `tri` | `?tri=date_asc` | `date_asc`, `date_desc`, `priorite_asc`, `priorite_desc` |
| `page` | `?page=2` | Pagination |

Combinables : `GET /api/taches/?statut=en_cours&priorite=haute&tri=date_asc&page=2`

## Codes de statut

| Code | Signification |
|---|---|
| `200 OK` | Succès (lecture, modification) |
| `201 Created` | Ressource créée |
| `204 No Content` | Suppression réussie |
| `400 Bad Request` | Données invalides (validation modèle échouée) |
| `401 Unauthorized` | Non authentifié |
| `403 Forbidden` | Authentifié mais accès refusé |
| `404 Not Found` | Ressource inexistante ou n'appartenant pas à l'utilisateur |
| `429 Too Many Requests` | Quota de requêtes dépassé (100/minute/utilisateur) |

## Pagination

Réponse de liste :
```json
{
  "count": 47,
  "next": "http://127.0.0.1:8000/api/taches/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

## Validation XOR résultat/fonctionnalité

Le serializer `TacheProjetSerializer` normalise les chaînes vides (`''`) en `None` pour `resultat_attendu` et `fonctionnalite` avant sauvegarde (méthode `validate()`). Sans ça, un formulaire envoyant l'un des deux champs vide sous forme de `''` (plutôt que `null`) fait échouer la `CheckConstraint soit_a_soit_b_pas_les_deux` au niveau base de données, car une chaîne vide n'est pas `NULL` pour SQLite.

```python
def validate(self, data):
    if data.get('resultat_attendu') == '':
        data['resultat_attendu'] = None
    if data.get('fonctionnalite') == '':
        data['fonctionnalite'] = None
    return data
```

## Fichiers du projet

| Fichier | Rôle |
|---|---|
| `novatask/serializers.py` | Conversion modèles ↔ JSON |
| `novatask/api_views.py` | Vues API (CRUD, filtres, validation) |
| `novatask/api_urls.py` | Routes de l'API |
| `novatask/tests/test_api.py` | Tests automatisés |

## Tests

```bash
python manage.py test novatask.tests.test_api
```

Couverture : authentification requise, isolation des données entre utilisateurs, rattachement automatique à l'utilisateur à la création, validation (dates, XOR résultat/fonctionnalité, tâche sur projet d'un autre utilisateur, normalisation chaîne vide → `None`).

## Tester manuellement

Interface navigable DRF (connecté sur le site) :
```
http://127.0.0.1:8000/api/projets/
http://127.0.0.1:8000/api/taches/
```