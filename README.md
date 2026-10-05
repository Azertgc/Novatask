# NovaTask

NovaTask est une application web développée avec **Django** permettant de gérer des projets et les tâches associées, avec un système de notifications automatiques basé sur les échéances.

Projet personnel d'apprentissage pratique de Django — terrain d'expérimentation pour tester des solutions techniques (notifications temps réel, vérification automatique côté serveur, tests automatisés, sécurité) au fil de l'apprentissage.

## Fonctionnalités

* Gestion des utilisateurs et authentification (connexion insensible à la casse)
* Création, modification et suppression de projets
* Création, modification et suppression de tâches, avec niveau de priorité
* Statut des tâches (à faire / en cours / terminée), mis à jour automatiquement selon la date et l'heure
* Suivi de la progression des projets (calculée à partir du statut des tâches)
* Association stricte des tâches et projets à leur utilisateur propriétaire
* Recherche par titre (insensible aux accents), filtres multiples (statut, priorité, date) et tri, combinables
* Système de notifications : détection automatique du démarrage d'une tâche, notification maintenue jusqu'à l'heure de fin, Web Notifications API
* Vérification automatique des échéances côté serveur, indépendante des sessions utilisateur actives
* Suite de tests automatisés (modèles, formulaires, vues, sécurité, permissions)

Voir [FONCTIONNALITES.md](FONCTIONNALITES.md) pour le détail complet.

## Technologies utilisées

* **Python / Django**
* **SQLite**
* **HTML / Tailwind CSS**
* **JavaScript** (Flatpickr, Web Notifications API)

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/Azertgc/Novatask.git
cd Novatask
```

### 2. Créer un environnement virtuel

```bash
python -m venv .nova
```

### 3. Activer l'environnement virtuel

Sous Windows :

```bash
.nova\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configurer les variables d'environnement

```bash
copy .env.example .env
```

Renseigner `SECRET_KEY`, `DEBUG` et `ALLOWED_HOSTS` dans `.env`.

### 6. Effectuer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer un administrateur

```bash
python manage.py createsuperuser
```

### 8. (Optionnel) Remplir la base avec des données de démonstration

```bash
python remplir_base.py
```

### 9. Lancer le serveur

```bash
python manage.py runserver
```

L'application sera accessible à :

```text
http://127.0.0.1:8000/
```

## Lancer les tests

```bash
python manage.py test
```

## Administration

L'interface d'administration Django est accessible à :

```text
http://127.0.0.1:8000/admin/
```

## Vérification automatique des échéances

En complément des notifications dans l'interface, une commande vérifie les échéances côté serveur :

```bash
python manage.py verifier_taches
```

À planifier via le Planificateur de tâches Windows ou `cron` pour une exécution récurrente.

## Structure du projet

```text
Novatask/
│
├── .gitignore
├── .env.example
├── README.md
├── FONCTIONNALITES.md
├── INSTALL.md
├── requirements.txt
├── manage.py
├── remplir_base.py
│
├── config/
│   └── settings.py
│
├── novatask/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   │   └── novatask/
│   │       └── notifications.js
│   ├── tests/
│   ├── management/
│   │   └── commands/
│   │       └── verifier_taches.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── backends.py
│   ├── urls.py
│   └── admin.py
│
└── ...
```

## Auteur

**GONTY Tia Ben Emmanuel**
Projet personnel réalisé dans le cadre de mon apprentissage du développement web avec Django.