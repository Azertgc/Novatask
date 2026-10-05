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

### 4. Configurer les variables d'environnement

Copier le fichier d'exemple et renseigner les valeurs :

Windows :
```
copy .env.example .env
```

Linux / macOS :
```
cp .env.example .env
```

Ouvrir `.env` et définir au minimum :
```
SECRET_KEY=une-cle-secrete-a-generer
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

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