# API NovaTask

Référence technique de l'API REST, basée sur Django REST Framework (DRF).

## Sommaire

- [Installation](#installation)
- [Authentification](#authentification)
- [Isolation des données](#isolation-des-données)
- [Identifiants métier dans les relations (`id_proj`)](#identifiants-métier-dans-les-relations-id_proj)
- [Validation avant écriture (pas après)](#validation-avant-écriture-pas-après)
- [Endpoints](#endpoints)
- [Ressource Projet](#ressource-projet)
- [Ressource Tâche](#ressource-tâche)
- [Paramètres de requête (`/api/taches/`)](#paramètres-de-requête-apitaches)
- [Codes de statut](#codes-de-statut)
- [Pagination](#pagination)
- [Validation XOR résultat/fonctionnalité](#validation-xor-résultatfonctionnalité)
- [Fichiers du projet](#fichiers-du-projet)
- [Tests](#tests)
- [Tester manuellement](#tester-manuellement)

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

`SessionAuthentication` : réutilise le cookie de session du site (connexion via `/connexion/`) — pas de système d'authentification séparé à gérer. Les requêtes `POST`/`PUT`/`PATCH`/`DELETE` nécessitent le header `X-CSRFToken`, sauf depuis l'interface navigable DRF qui s'en charge automatiquement.

`IsAuthenticated` par défaut sur toutes les routes : accès anonyme refusé (`403 Forbidden`), même pour une route qui oublierait de préciser ses permissions.

## Isolation des données

Chaque `ViewSet` filtre son `get_queryset()` :
- **Projets** : `id_user=request.user`
- **Tâches** : `id_proj__id_user=request.user` (relation traversée via le projet parent)

Un utilisateur ne peut donc jamais lister, consulter, modifier ou supprimer les données d'un autre utilisateur, y compris via l'API — une tentative d'accès à un objet d'autrui renvoie `404 Not Found` (et non `403`, pour ne pas révéler que l'objet existe).

## Identifiants métier dans les relations (`id_proj`)

Le champ `id_proj` du `TacheProjetSerializer` utilise `SlugRelatedField(slug_field='id_proj', ...)`, et non le `PrimaryKeyRelatedField` généré par défaut. Sans ça, DRF attendrait la clé primaire technique auto-incrémentée de Django (un entier invisible côté utilisateur), pas l'identifiant métier (`P001`) — toute requête envoyant `id_proj: "P001"` échouerait avec `Incorrect type. Expected pk value, received str.`

Le queryset autorisé pour ce champ est en plus restreint aux projets de l'utilisateur connecté (voir `__init__` du serializer) : impossible de rattacher une tâche au projet de quelqu'un d'autre en devinant son identifiant.

## Validation avant écriture (pas après)

`perform_create`/`perform_update` sur `TacheProjetViewSet` construisent et valident l'instance (`full_clean()`) **avant** tout appel à `.save()`, plutôt que de sauvegarder puis valider après coup. Raison : la `CheckConstraint` XOR est définie au niveau base de données. Un `.save()` sur des données invalides ferait échouer l'`INSERT` directement en SQLite (`IntegrityError`, erreur `500` brute), avant même que Python n'ait la main pour renvoyer une réponse `400` propre.

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

## Ressource Projet

| Champ | Type | Lecture seule | Détail |
|---|---|---|---|
| `id_proj` | string | oui | Identifiant métier auto-généré (`P001`, `P002`...) |
| `intitule` | string | — | |
| `description` | string | — | |
| `resultat_attendu` | string | — | |
| `date_debut` | date (`YYYY-MM-DD`) | — | Ne peut pas être dans le passé |
| `date_fin` | date (`YYYY-MM-DD`) | — | Doit être ≥ `date_debut` |
| `statut` | string | oui | Calculé à partir des tâches liées (`a_faire`, `en_cours`, `terminee`) |
| `progression` | number | oui | Calculé, pourcentage de tâches terminées |

`id_user` n'est jamais exposé : rattachement automatique à l'utilisateur connecté à la création, impossible à modifier via l'API.

Créer un projet :
```bash
curl -X POST http://127.0.0.1:8000/api/projets/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  --cookie "sessionid=<session>" \
  -d '{
    "intitule": "Refonte du site",
    "description": "Nouvelle version de la vitrine",
    "resultat_attendu": "Site en ligne",
    "date_debut": "2026-10-10",
    "date_fin": "2026-11-15"
  }'
```

Réponse `201 Created` :
```json
{
  "id_proj": "P004",
  "intitule": "Refonte du site",
  "description": "Nouvelle version de la vitrine",
  "resultat_attendu": "Site en ligne",
  "date_debut": "2026-10-10",
  "date_fin": "2026-11-15",
  "statut": "a_faire",
  "progression": 0.0
}
```

## Ressource Tâche

| Champ | Type | Lecture seule | Détail |
|---|---|---|---|
| `num_tache` | string | oui | Identifiant métier auto-généré (`T001`, `T002`...) |
| `id_proj` | string | — | Identifiant métier du projet parent (voir ci-dessus) |
| `intitule` | string | — | |
| `resultat_attendu` | string | — | Mutuellement exclusif avec `fonctionnalite` (voir plus bas) |
| `fonctionnalite` | string | — | Mutuellement exclusif avec `resultat_attendu` |
| `date_realisation` | date (`YYYY-MM-DD`) | — | |
| `heure_debut` | time (`HH:MM`) | — | |
| `heure_fin` | time (`HH:MM`) | — | |
| `priorite` | string | — | `basse`, `normale` (défaut), `haute` |
| `statut` | string | — | `a_faire` (défaut), `en_cours`, `terminee` |
| `est_en_retard` | boolean | oui | Calculé : `statut != 'terminee'` et heure de fin dépassée |

Créer une tâche :
```bash
curl -X POST http://127.0.0.1:8000/api/taches/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  --cookie "sessionid=<session>" \
  -d '{
    "id_proj": "P004",
    "intitule": "Maquette page d'\''accueil",
    "resultat_attendu": "Maquette validée par le client",
    "date_realisation": "2026-10-12",
    "heure_debut": "09:00",
    "heure_fin": "11:00",
    "priorite": "haute"
  }'
```

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
| `401 Unauthorized` | Non authentifié (hors session navigateur, ex. requête sans cookie) |
| `403 Forbidden` | Authentifié mais accès refusé, ou aucune authentification fournie |
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

20 résultats par page (`PAGE_SIZE`). `next`/`previous` valent `null` quand il n'y a pas de page suivante/précédente.

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

Exactement un des deux champs doit être rempli : les deux vides, ou les deux remplis, renvoient `400 Bad Request`.

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