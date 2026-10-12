# Installation de NovaTask

## Prérequis

- Python 3.12 ou supérieur
- pip
- Git

## Étapes

### 1. Cloner le dépôt

```
git clone https://github.com/Azertgc/Novatask.git
cd Novatask
```

### 2. Créer et activer un environnement virtuel

Windows :
```
python -m venv .nova
.nova\Scripts\activate
```

Linux / macOS :
```
python -m venv .nova
source .nova/bin/activate
```

### 3. Installer les dépendances

```
pip install -r requirements.txt
```

### 4. Clé secrète et configuration

> **État actuel** : `python-decouple` est listé dans `requirements.txt`, mais `config/settings.py` ne l'utilise pas encore — `SECRET_KEY` y est codée en dur, et les lignes `config('DEBUG', ...)` / `config('ALLOWED_HOST', ...)` sont commentées. Il n'y a donc pas de fichier `.env` à créer pour l'instant : rien à configurer à cette étape, le projet fonctionne tel quel en local.
>
> **À faire avant un déploiement réel** : externaliser `SECRET_KEY` (et `DEBUG`/`ALLOWED_HOSTS`) dans un fichier `.env` non versionné (déjà prévu dans `.gitignore`), lu via `python-decouple` dans `settings.py`. Cette étape sera à documenter ici une fois branchée.

### 5. Appliquer les migrations

```
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un superutilisateur

```
python manage.py createsuperuser
```

### 7. (Optionnel) Remplir la base avec des données de démonstration

Génère des utilisateurs, projets et tâches de test, mot de passe commun `novatask` :

```
python remplir_base.py
```

### 8. Lancer le serveur de développement

```
python manage.py runserver
```

L'application est accessible sur `http://127.0.0.1:8000/`.

## Lancer les tests

Suite complète :
```
python manage.py test
```

Un fichier de test en particulier :
```
python manage.py test novatask.tests.test_models
```

Autres fichiers disponibles dans `novatask/tests/` : `test_api`, `test_authentification`, `test_creation`, `test_forms`, `test_modification`, `test_notifications`, `test_permissions`, `test_securite`, `test_suppression`, `test_views`.

## Vérification automatique des échéances (optionnel)

En complément du système de notifications dans l'interface, une commande vérifie les échéances côté serveur, indépendamment de toute session utilisateur active :

```
python manage.py verifier_taches
```

Pour une exécution automatique et répétée, planifier cette commande via le Planificateur de tâches Windows ou `cron` (Linux), par exemple toutes les minutes.

## Problèmes courants

**`no such column` après un `git pull`** — une migration n'a pas été appliquée :
```
python manage.py makemigrations
python manage.py migrate
```

**Erreur de connexion avec un nom d'utilisateur en minuscules** — vérifier que `AUTHENTICATION_BACKENDS` dans `config/settings.py` inclut bien `novatask.backends.CaseInsensitiveModelBackend`.