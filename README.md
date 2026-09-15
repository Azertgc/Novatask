# NovaTask

NovaTask est une application web développée avec **Django** permettant de gérer des projets et les tâches associées.

## Fonctionnalités

* Gestion des utilisateurs
* Authentification
* Création de projets
* Création de tâches
* Modification des tâches
* Suppression des tâches
* Gestion du statut des tâches
* Suivi de la progression des projets
* Association des tâches aux utilisateurs

## Technologies utilisées

* **Python**
* **Django**
* **SQLite**
* **HTML / CSS**
* **JavaScript**

## Installation

### 1. Cloner le projet

```bash
git clone URL_DU_REPOSITORY
cd NOVATASK
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

### 5. Effectuer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un administrateur

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

L'application sera accessible à :

```text
http://127.0.0.1:8000/
```

## Administration

L'interface d'administration Django est accessible à :

```text
http://127.0.0.1:8000/admin/
```

## Structure du projet

```text
NOVATASK/
│
├── .gitignore
├── README.md
├── requirements.txt
├── manage.py
│
├── novatask/
│   ├── migrations/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
└── ...
```

## Auteur

Projet personnel réalisé dans le cadre de mon apprentissage du développement web avec Django.
