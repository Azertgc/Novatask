import os
import django
from datetime import date, time, timedelta

# Configuration de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import des modèles
from novatask.models import Utilisateur, Projet, Tache_projet


def remplir_base():

    print("=== REMPLISSAGE DE LA BASE DE DONNÉES ===")

    # ==========================================================
    # 1. CRÉATION DES UTILISATEURS (20)
    # ==========================================================

    utilisateurs = [
        {"id_user": "U001", "nom": "KOFFI", "prenom": "Jean"},
        {"id_user": "U002", "nom": "TRAORE", "prenom": "Moussa"},
        {"id_user": "U003", "nom": "YAO", "prenom": "Marie"},
        {"id_user": "U004", "nom": "KOUASSI", "prenom": "Paul"},
        {"id_user": "U005", "nom": "OUATTARA", "prenom": "Fatou"},
        {"id_user": "U006", "nom": "BAMBA", "prenom": "Ibrahim"},
        {"id_user": "U007", "nom": "N'GUESSAN", "prenom": "Aya"},
        {"id_user": "U008", "nom": "DIABATE", "prenom": "Salif"},
        {"id_user": "U009", "nom": "KONE", "prenom": "Awa"},
        {"id_user": "U010", "nom": "AKA", "prenom": "Christian"},
        {"id_user": "U011", "nom": "GNAGNE", "prenom": "Solange"},
        {"id_user": "U012", "nom": "SORO", "prenom": "Abdoulaye"},
        {"id_user": "U013", "nom": "ADOU", "prenom": "Béatrice"},
        {"id_user": "U014", "nom": "COULIBALY", "prenom": "Mamadou"},
        {"id_user": "U015", "nom": "KRA", "prenom": "Nathalie"},
        {"id_user": "U016", "nom": "SANGARE", "prenom": "Yacouba"},
        {"id_user": "U017", "nom": "BROU", "prenom": "Chantal"},
        {"id_user": "U018", "nom": "DOSSO", "prenom": "Aboubacar"},
        {"id_user": "U019", "nom": "TANO", "prenom": "Estelle"},
        {"id_user": "U020", "nom": "KEITA", "prenom": "Lassina"},
    ]

    utilisateurs_crees = {}

    for data in utilisateurs:
        utilisateur, created = Utilisateur.objects.get_or_create(
            id_user=data["id_user"],
            defaults={
                "nom": data["nom"],
                "prenom": data["prenom"],
                "username": data["id_user"]
            }
        )

        utilisateurs_crees[data["id_user"]] = utilisateur

        if created:
            print(f"✓ Utilisateur créé : {utilisateur.nom} {utilisateur.prenom}")
        else:
            print(f"→ Utilisateur déjà existant : {utilisateur.nom}")

    # ==========================================================
    # 2. CRÉATION DES PROJETS (20)
    # ==========================================================

    projets = [
        {"id_proj": "P001",
         "intitule": "Développement du site web UIST",
         "date_fin": date(2026, 10, 30),
         "id_user": "U001",
         "resultat_attendu": "Mettre en place un site web moderne pour présenter l'UIST.",
         "description": "Conception et développement du site web officiel de l'UIST."},
        
        {"id_proj": "P002",
         "intitule": "Application de gestion des prestataires",
         "date_fin": date(2026, 11, 15),
         "id_user": "U002",
         "resultat_attendu": "Permettre la gestion centralisée des prestataires et des prestations.",
         "description": "Développement d'une application web permettant de gérer les prestataires."},
        
        {"id_proj": "P003",
         "intitule": "Mise en place du réseau informatique",
         "date_fin": date(2026, 12, 10),
         "id_user": "U003",
         "resultat_attendu": "Déployer une infrastructure réseau fonctionnelle.",
         "description": "Installation et configuration du réseau informatique de l'établissement."},
        
        {"id_proj": "P004",
         "intitule": "Digitalisation des documents administratifs",
         "date_fin": date(2027, 1, 20),
         "id_user": "U004",
         "resultat_attendu": "Réduire l'utilisation des documents papier.",
         "description": "Numérisation et organisation des documents administratifs."},
        
        {"id_proj": "P005",
         "intitule": "Refonte du système de gestion des notes",
         "date_fin": date(2026, 11, 5),
         "id_user": "U005",
         "resultat_attendu": "Automatiser le calcul et la publication des notes.",
         "description": "Modernisation de la plateforme de gestion des notes des étudiants."},
        
        {"id_proj": "P006",
         "intitule": "Plateforme de gestion des inscriptions",
         "date_fin": date(2026, 12, 1),
         "id_user": "U006",
         "resultat_attendu": "Simplifier le processus d'inscription des étudiants.",
         "description": "Développement d'un portail en ligne pour les inscriptions administratives."},
        
        {"id_proj": "P007",
         "intitule": "Application mobile de l'UIST",
         "date_fin": date(2027, 2, 10),
         "id_user": "U007",
         "resultat_attendu": "Offrir un accès mobile aux services de l'établissement.",
         "description": "Conception d'une application mobile pour les étudiants et le personnel."},
        
        {"id_proj": "P008",
         "intitule": "Système de gestion de la bibliothèque",
         "date_fin": date(2026, 10, 20),
         "id_user": "U008",
         "resultat_attendu": "Faciliter le suivi des emprunts et retours d'ouvrages.",
         "description": "Développement d'un logiciel de gestion du fonds documentaire."},
        
        {"id_proj": "P009",
         "intitule": "Mise en place d'un système de vidéosurveillance",
         "date_fin": date(2026, 11, 25),
         "id_user": "U009",
         "resultat_attendu": "Renforcer la sécurité du campus.",
         "description": "Installation de caméras et d'un poste de contrôle central."},
        
        {"id_proj": "P010",
         "intitule": "Portail de gestion des ressources humaines",
         "date_fin": date(2027, 1, 5),
         "id_user": "U010",
         "resultat_attendu": "Centraliser la gestion administrative du personnel.",
         "description": "Développement d'une plateforme RH interne."},
        
        {"id_proj": "P011",
         "intitule": "Système de gestion des emplois du temps",
         "date_fin": date(2026, 10, 15),
         "id_user": "U011",
         "resultat_attendu": "Automatiser la génération des emplois du temps.",
         "description": "Conception d'un outil de planification des cours et salles."},
        
        {"id_proj": "P012",
         "intitule": "Plateforme d'e-learning",
         "date_fin": date(2027, 2, 28),
         "id_user": "U012",
         "resultat_attendu": "Permettre les cours et évaluations à distance.",
         "description": "Mise en place d'une plateforme d'apprentissage en ligne."},
        
        {"id_proj": "P013",
         "intitule": "Système de gestion de la paie",
         "date_fin": date(2026, 12, 20),
         "id_user": "U013",
         "resultat_attendu": "Automatiser le traitement des salaires du personnel.",
         "description": "Développement d'un module de paie intégré."},
        
        {"id_proj": "P014",
         "intitule": "Refonte du site intranet",
         "date_fin": date(2026, 11, 30),
         "id_user": "U014",
         "resultat_attendu": "Améliorer la communication interne.",
         "description": "Modernisation de l'intranet de l'établissement."},
        
        {"id_proj": "P015",
         "intitule": "Système de gestion des stocks",
         "date_fin": date(2027, 1, 15),
         "id_user": "U015",
         "resultat_attendu": "Optimiser le suivi du matériel et des fournitures.",
         "description": "Développement d'un logiciel de gestion des stocks et achats."},
        
        {"id_proj": "P016",
         "intitule": "Mise en place d'un serveur de sauvegarde",
         "date_fin": date(2026, 10, 25),
         "id_user": "U016",
         "resultat_attendu": "Sécuriser les données de l'établissement.",
         "description": "Déploiement d'une solution de sauvegarde centralisée."},
        
        {"id_proj": "P017",
         "intitule": "Système de gestion des examens",
         "date_fin": date(2026, 12, 15),
         "id_user": "U017",
         "resultat_attendu": "Faciliter l'organisation et la correction des examens.",
         "description": "Développement d'une application dédiée aux examens."},
        
        {"id_proj": "P018",
         "intitule": "Portail des anciens étudiants",
         "date_fin": date(2027, 1, 30),
         "id_user": "U018",
         "resultat_attendu": "Maintenir le lien avec les anciens diplômés.",
         "description": "Création d'un réseau numérique des alumni."},
        
        {"id_proj": "P019",
         "intitule": "Système de gestion financière",
         "date_fin": date(2026, 11, 10),
         "id_user": "U019",
         "resultat_attendu": "Centraliser le suivi budgétaire et comptable.",
         "description": "Développement d'un module de gestion financière."},
        
        {"id_proj": "P020",
         "intitule": "Mise en place d'un chatbot d'assistance",
         "date_fin": date(2027, 2, 5),
         "id_user": "U020",
         "resultat_attendu": "Répondre automatiquement aux questions fréquentes des étudiants.",
         "description": "Développement d'un assistant virtuel pour le site de l'UIST."},
    
    ]

    projets_crees = {}

    for data in projets:
        date_debut = data.get("date_debut", data['date_fin']- timedelta(days=90))
        projet, created = Projet.objects.get_or_create(
            id_proj=data["id_proj"],
            defaults={
                "intitule": data["intitule"],
                "date_debut": date_debut,
                "date_fin": data["date_fin"],
                "resultat_attendu": data["resultat_attendu"],
                "id_user": utilisateurs_crees[data["id_user"]],
                "description": data["description"]
            }
        )

        projets_crees[data["id_proj"]] = projet

        if created:
            print(f"✓ Projet créé : {projet.intitule}")
        else:
            print(f"→ Projet déjà existant : {projet.intitule}")

    # ==========================================================
    # 3. CRÉATION DES TÂCHES (5 par projet = 100 tâches)
    # ==========================================================

    # Modèle générique des 5 phases appliquées à chaque projet.
    # (intitulé, résultat attendu, statut, décalage en jours depuis le début, heure_debut, heure_fin)
    phases = [
        ("Analyse des besoins",
         "Identifier les besoins fonctionnels du projet.",
         "terminee", 0, time(8, 0), time(10, 0)),
        ("Conception",
         "Élaborer les spécifications et l'architecture du projet.",
         "terminee", 4, time(9, 0), time(12, 0)),
        ("Développement",
         "Réaliser les fonctionnalités principales du projet.",
         "en_cours", 9, time(8, 0), time(13, 0)),
        ("Tests et validation",
         "Vérifier le bon fonctionnement des livrables.",
         "a_faire", 15, time(10, 0), time(12, 0)),
        ("Déploiement",
         "Mettre en production et clôturer le projet.",
         "a_faire", 20, time(8, 0), time(11, 0)),
    ]

    date_debut_base = date(2026, 9, 1)
    compteur_tache = 1

    for idx_projet, data_projet in enumerate(projets):
        projet = projets_crees[data_projet["id_proj"]]
        # décale légèrement le point de départ des tâches d'un projet à l'autre
        depart_projet = date_debut_base + timedelta(days=idx_projet * 2)

        for intitule, resultat_attendu, statut, decalage, heure_debut, heure_fin in phases:
            num_tache = f"T{compteur_tache:03d}"
            date_realisation = depart_projet + timedelta(days=decalage)

            tache, created = Tache_projet.objects.get_or_create(
                num_tache=num_tache,
                defaults={
                    "intitule": intitule,
                    "date_realisation": date_realisation,
                    "heure_debut": heure_debut,
                    "heure_fin": heure_fin,
                    "resultat_attendu": resultat_attendu,
                    "statut": statut,
                    "id_proj": projet
                }
            )

            if created:
                print(f"✓ Tâche créée : {tache.intitule} ({projet.intitule})")
            else:
                print(f"→ Tâche déjà existante : {tache.intitule}")

            compteur_tache += 1

    # ==========================================================
    # FIN
    # ==========================================================

    print("\n======================================")
    print("BASE DE DONNÉES REMPLIE AVEC SUCCÈS !")
    print("======================================")

    print(f"Utilisateurs : {Utilisateur.objects.count()}")
    print(f"Projets      : {Projet.objects.count()}")
    print(f"Tâches       : {Tache_projet.objects.count()}")


if __name__ == "__main__":
    remplir_base()