# Fonctionnalités de NovaTask

Ce document détaille les fonctionnalités de l'application, organisées par domaine.

## Sommaire

1. [Authentification et gestion des comptes](#1-authentification-et-gestion-des-comptes)
2. [Gestion des projets](#2-gestion-des-projets)
3. [Gestion des tâches](#3-gestion-des-tâches)
4. [Recherche, filtres et tri](#4-recherche-filtres-et-tri)
5. [Notifications](#5-notifications)
6. [API REST](#6-api-rest)
7. [Sécurité](#7-sécurité)
8. [Qualité](#8-qualité)

## 1. Authentification et gestion des comptes

- Inscription avec validation de robustesse du mot de passe (longueur, similarité avec le nom d'utilisateur, mots de passe trop communs, mots de passe uniquement numériques)
- Connexion insensible à la casse du nom d'utilisateur
- Connexion automatique après inscription
- Déconnexion
- Chaque compte dispose d'un identifiant interne généré automatiquement (`U001`, `U002`, ...), non modifiable

## 2. Gestion des projets

- Création d'un projet (intitulé, dates de début et de fin, description, résultat attendu)
- La date de début ne peut pas être antérieure à la date du jour
- La date de fin ne peut pas être antérieure à la date de début
- Un projet est automatiquement rattaché à l'utilisateur connecté — aucun choix d'utilisateur n'est exposé dans le formulaire
- Identifiant de projet généré automatiquement (`P001`, `P002`, ...), non modifiable
- Statut du projet calculé automatiquement à partir du statut de ses tâches (à faire / en cours / terminé)
- Barre de progression basée sur la proportion de tâches terminées
- Recherche de projets par intitulé, insensible aux accents
- Filtre par statut

## 3. Gestion des tâches

- Création d'une tâche rattachée à un projet de l'utilisateur connecté uniquement
- Choix exclusif entre un « résultat attendu » et une « fonctionnalité » (l'un ou l'autre, jamais les deux, jamais aucun des deux), appliqué à la fois côté interface et côté base de données
- Date de réalisation d'une tâche contrainte à l'intervalle de dates du projet parent, avec sélection impossible en dehors de cet intervalle, y compris au clavier
- Niveau de priorité (basse, normale, haute)
- Statut (à faire, en cours, terminée), avec passage automatique de « à faire » à « en cours » dès que l'heure de début est atteinte
- Identifiant de tâche généré automatiquement (`T001`, `T002`, ...), non modifiable
- Modification et suppression, avec confirmation avant suppression
- Une tâche en retard (échéance dépassée sans être marquée terminée) est signalée visuellement

## 4. Recherche, filtres et tri

- Recherche par titre, insensible aux accents
- Filtres multiples et cumulables par statut et par priorité (plusieurs valeurs sélectionnables à la fois)
- Filtre par date précise, ou raccourci « tâches du jour »
- Filtre « tâches en retard »
- Tri par date (croissant / décroissant) et par priorité (croissant / décroissant)
- Tous les filtres et le tri sont combinables simultanément, via un formulaire unique

## 5. Notifications

- Détection automatique du passage d'une tâche de « à faire » à « en cours », dès que la date et l'heure de début sont atteintes
- Notification affichée dans l'interface dès le déclenchement, maintenue obligatoirement jusqu'à l'heure de fin prévue
- Bouton de fermeture indisponible avant l'heure de fin
- Une seule notification affichée à la fois ; la suivante apparaît automatiquement après fermeture de la précédente
- Notification système du navigateur via la Web Notifications API, en complément de la notification affichée dans l'application
- Vérification automatique des échéances côté serveur, indépendante de toute session utilisateur active (commande `verifier_taches`), avec mécanisme empêchant l'envoi répété d'un même rappel

## 6. API REST

- API REST complète (Django REST Framework) en plus de l'interface web : CRUD sur les projets et les tâches
- Authentification par session (même connexion que le site, pas de système séparé)
- Mêmes règles d'isolation des données et de validation (dates, XOR résultat/fonctionnalité) que l'interface web, appliquées côté serveur dans les vues de l'API
- Recherche, filtres (statut, priorité) et tri disponibles via paramètres de requête, pagination des listes (20 résultats par page)
- Throttling : 100 requêtes par minute et par utilisateur
- Détail complet : voir [`API.md`](./API.md)

## 7. Sécurité

- Protection CSRF sur tous les formulaires de modification de données
- Isolation stricte des données : un utilisateur ne peut jamais consulter, modifier ou supprimer les projets ou tâches d'un autre utilisateur
- Mots de passe hashés, jamais stockés en clair
- Validation systématique côté serveur, indépendante de toute validation côté navigateur
- **À faire avant tout déploiement réel** : la clé secrète Django (`SECRET_KEY`) est actuellement codée en dur dans `settings.py`, pas encore externalisée en variable d'environnement — correct pour un usage local/développement, à corriger avant mise en production

## 8. Qualité

- Suite de tests automatisés couvrant les modèles, les formulaires, les vues, l'API REST, les opérations de création/modification/suppression, l'authentification, les permissions et le système de notifications
- Plusieurs anomalies réelles détectées et corrigées grâce à cette suite de tests au cours du développement