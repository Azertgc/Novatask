import os
import django
import random
from datetime import date, time, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from novatask.models import Utilisateur, Projet, Tache_projet

random.seed(42)  # résultats reproductibles à chaque exécution

MOT_DE_PASSE = "novatask"


def remplir_base():

    print("=== REMPLISSAGE DE LA BASE DE DONNÉES ===")

    # ==========================================================
    # 1. UTILISATEURS (20) — mot de passe commun forcé
    # ==========================================================

    utilisateurs_data = [
        {"nom": "KOFFI", "prenom": "Jean"},
        {"nom": "TRAORE", "prenom": "Moussa"},
        {"nom": "YAO", "prenom": "Marie"},
        {"nom": "KOUASSI", "prenom": "Paul"},
        {"nom": "OUATTARA", "prenom": "Fatou"},
        {"nom": "BAMBA", "prenom": "Ibrahim"},
        {"nom": "N'GUESSAN", "prenom": "Aya"},
        {"nom": "DIABATE", "prenom": "Salif"},
        {"nom": "KONE", "prenom": "Awa"},
        {"nom": "AKA", "prenom": "Christian"},
        {"nom": "GNAGNE", "prenom": "Solange"},
        {"nom": "SORO", "prenom": "Abdoulaye"},
        {"nom": "ADOU", "prenom": "Béatrice"},
        {"nom": "COULIBALY", "prenom": "Mamadou"},
        {"nom": "KRA", "prenom": "Nathalie"},
        {"nom": "SANGARE", "prenom": "Yacouba"},
        {"nom": "BROU", "prenom": "Chantal"},
        {"nom": "DOSSO", "prenom": "Aboubacar"},
        {"nom": "TANO", "prenom": "Estelle"},
        {"nom": "KEITA", "prenom": "Lassina"},
    ]

    utilisateurs_crees = []

    for data in utilisateurs_data:
        username = data["nom"].lower()
        utilisateur, created = Utilisateur.objects.get_or_create(
            username=username,
            defaults={
                "nom": data["nom"],
                "prenom": data["prenom"],
            }
        )
        # Mot de passe forcé, que le compte soit neuf ou déjà existant
        utilisateur.set_password(MOT_DE_PASSE)
        utilisateur.save()

        utilisateurs_crees.append(utilisateur)

        if created:
            print(f"✓ Utilisateur créé : {utilisateur.nom} {utilisateur.prenom} (login: {utilisateur.username}, id: {utilisateur.id_user})")
        else:
            print(f"→ Utilisateur existant, mot de passe réinitialisé : {utilisateur.username}")

    # ==========================================================
    # 2. PROJETS (3 par utilisateur = 60 projets)
    # ==========================================================

    SUJETS = [
        "gestion des bibliothèques", "gestion des examens", "gestion des inscriptions",
        "gestion des emplois du temps", "gestion des stocks", "gestion de la paie",
        "gestion des prestataires", "gestion des ressources humaines",
        "gestion financière", "gestion des stages", "gestion des diplômes",
        "gestion des salles de classe", "gestion du courrier", "gestion des visiteurs",
        "gestion des équipements informatiques", "gestion des absences",
        "gestion des bourses d'études", "gestion des clubs étudiants",
        "gestion des événements du campus", "gestion des réclamations étudiantes",
        "suivi des mémoires de fin d'études", "suivi des stages professionnels",
        "suivi des paiements de scolarité", "suivi des présences en cours",
        "suivi des demandes administratives",
        "réservation des salles de réunion", "réservation du matériel audiovisuel",
        "digitalisation des dossiers étudiants", "digitalisation des archives",
        "modernisation du site web de l'UIST", "modernisation de l'intranet",
        "mise en place d'un chatbot d'assistance", "mise en place d'un réseau Wi-Fi campus",
        "mise en place d'un système de badges d'accès",
        "mise en place d'une plateforme d'e-learning",
        "mise en place d'un système de vidéosurveillance",
        "mise en place d'un serveur de sauvegarde",
        "développement d'une application mobile étudiants",
        "développement d'un portail des anciens élèves",
        "développement d'un tableau de bord administratif",
        "développement d'un système de notation en ligne",
        "développement d'un outil de sondage interne",
        "développement d'un système de messagerie interne",
        "sécurisation du réseau informatique",
        "optimisation de la base de données centrale",
        "automatisation des relances de paiement",
        "automatisation de la génération des certificats",
        "centralisation des emplois du temps enseignants",
        "amélioration du support technique étudiants",
        "amélioration de la communication interne",
        "cartographie numérique du campus",
        "gestion des fournitures de bureau",
        "gestion du parc automobile de l'UIST",
        "gestion des conventions de partenariat",
        "gestion des projets de recherche",
        "gestion des publications académiques",
        "gestion des demandes de congé du personnel",
        "gestion des accès laboratoires",
        "gestion du restaurant universitaire",
        "gestion des logements étudiants",
        "gestion du parc de licences logicielles",
        "suivi budgétaire des départements",
    ]

    random.shuffle(SUJETS)

    projets_crees = []  # liste de tuples (projet, date_debut, duree)
    idx_sujet = 0

    for utilisateur in utilisateurs_crees:
        for _ in range(3):
            sujet = SUJETS[idx_sujet % len(SUJETS)]
            idx_sujet += 1

            intitule = f"Système de {sujet}"

            date_debut = date(2026, 3, 1) + timedelta(days=random.randint(0, 180))
            duree = random.randint(60, 150)
            date_fin = date_debut + timedelta(days=duree)

            # L'intitulé + l'utilisateur suffisent comme clé d'idempotence
            # (id_proj est désormais auto-généré à la sauvegarde, non modifiable)
            projet, created = Projet.objects.get_or_create(
                intitule=intitule,
                id_user=utilisateur,
                defaults={
                    "date_debut": date_debut,
                    "date_fin": date_fin,
                    "resultat_attendu": f"Mettre en place un outil numérique pour améliorer {sujet} au sein de l'UIST.",
                    "description": f"Conception et développement d'une solution dédiée à la {sujet}.",
                }
            )
            projets_crees.append((projet, date_debut, duree))

            if created:
                print(f"✓ Projet créé : {projet.intitule} (id: {projet.id_proj}, {utilisateur.username})")
            else:
                print(f"→ Projet déjà existant : {projet.intitule} (id: {projet.id_proj})")

    # ==========================================================
    # 3. TÂCHES (4 par projet = 240 tâches) — progression logique
    # ==========================================================

    PHASES = [
        ("Analyse des besoins", "Identifier les besoins fonctionnels du projet.", time(8, 0), time(10, 0)),
        ("Conception", "Élaborer les spécifications et l'architecture du projet.", time(9, 0), time(12, 0)),
        ("Développement", "Réaliser les fonctionnalités principales du projet.", time(8, 0), time(13, 0)),
        ("Déploiement", "Mettre en production et clôturer le projet.", time(8, 0), time(11, 0)),
    ]

    PROGRESSIONS = [
        ["a_faire", "a_faire", "a_faire", "a_faire"],
        ["terminee", "a_faire", "a_faire", "a_faire"],
        ["terminee", "terminee", "en_cours", "a_faire"],
        ["terminee", "terminee", "terminee", "en_cours"],
        ["terminee", "terminee", "terminee", "terminee"],
    ]

    for projet, date_debut, duree in projets_crees:
        statuts = random.choice(PROGRESSIONS)
        jalons = sorted(random.sample(range(0, duree), 4))

        for (intitule, resultat_attendu, heure_debut, heure_fin), statut, decalage in zip(
            PHASES, statuts, jalons
        ):
            date_realisation = date_debut + timedelta(days=decalage)

            # L'intitulé (phase) + le projet suffisent comme clé d'idempotence
            # (num_tache est désormais auto-généré à la sauvegarde, non modifiable)
            tache, created = Tache_projet.objects.get_or_create(
                intitule=intitule,
                id_proj=projet,
                defaults={
                    "date_realisation": date_realisation,
                    "heure_debut": heure_debut,
                    "heure_fin": heure_fin,
                    "resultat_attendu": resultat_attendu,
                    "statut": statut,
                }
            )

            if created:
                print(f"✓ Tâche créée : {tache.intitule} ({projet.intitule}) — {statut} — id: {tache.num_tache}")
            else:
                print(f"→ Tâche déjà existante : {tache.intitule} ({projet.intitule})")

    # ==========================================================
    # FIN
    # ==========================================================

    print("\n======================================")
    print("BASE DE DONNÉES REMPLIE AVEC SUCCÈS !")
    print("======================================")
    print(f"Utilisateurs : {Utilisateur.objects.count()}")
    print(f"Projets      : {Projet.objects.count()}")
    print(f"Tâches       : {Tache_projet.objects.count()}")
    print(f"\nMot de passe pour tous les utilisateurs : {MOT_DE_PASSE}")


if __name__ == "__main__":
    remplir_base()