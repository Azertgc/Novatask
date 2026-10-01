import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet
from novatask.services import (
    taches_a_surveiller,
    verifier_echeances,
    taches_proches_echeance_non_notifiees,
    marquer_rappel_envoye,
    SEUIL_PROCHE_ECHEANCE,
)


class EndpointNotificationsJsonTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')
        self.client.login(username='testuser', password='motdepasse')

        self.projet = Projet.objects.create(
            intitule='Projet test',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        self.tache = Tache_projet.objects.create(
            intitule='Tâche notif',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=self.projet,
        )

    def test_endpoint_retourne_200(self):
        reponse = self.client.get(reverse('taches_notifications_json'))
        self.assertEqual(reponse.status_code, 200)

    def test_endpoint_retourne_json_valide(self):
        reponse = self.client.get(reverse('taches_notifications_json'))
        data = json.loads(reponse.content)
        self.assertIn('taches', data)

    def test_endpoint_contient_les_bons_champs(self):
        reponse = self.client.get(reverse('taches_notifications_json'))
        data = json.loads(reponse.content)
        tache_json = next(t for t in data['taches'] if t['intitule'] == 'Tâche notif')
        self.assertEqual(tache_json['projet'], 'Projet test')
        self.assertIn('date_realisation', tache_json)
        self.assertIn('heure_debut', tache_json)
        self.assertIn('heure_fin', tache_json)
        self.assertIn('statut', tache_json)

    def test_endpoint_ne_montre_pas_les_taches_des_autres(self):
        autre_user = Utilisateur.objects.create_user(username='autre', password='x', nom='A', prenom='A')
        autre_projet = Projet.objects.create(
            intitule='Projet autre',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=autre_user,
        )
        Tache_projet.objects.create(
            intitule='Tâche de autre',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=autre_projet,
        )

        reponse = self.client.get(reverse('taches_notifications_json'))
        data = json.loads(reponse.content)
        intitules = [t['intitule'] for t in data['taches']]
        self.assertNotIn('Tâche de autre', intitules)

    def test_endpoint_actualise_les_statuts(self):
        """L'appel à l'endpoint doit déclencher actualiser_statuts() automatiquement."""
        tache_imminente = Tache_projet.objects.create(
            intitule='Tâche qui commence',
            date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() - timedelta(minutes=5)).time(),
            heure_fin=(timezone.localtime() + timedelta(hours=1)).time(),
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=self.projet,
        )
        self.client.get(reverse('taches_notifications_json'))
        tache_imminente.refresh_from_db()
        self.assertEqual(tache_imminente.statut, 'en_cours')


class ServicesNotificationsTest(TestCase):
    """Tests du chapitre 18 : logique de vérification côté serveur (services.py)."""

    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='x', nom='N', prenom='P')
        self.projet = Projet.objects.create(
            intitule='Projet test',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )

    def test_taches_a_surveiller_exclut_les_terminees(self):
        Tache_projet.objects.create(
            intitule='Terminée', date_realisation=timezone.localdate(),
            heure_debut='09:00', heure_fin='10:00', resultat_attendu='R',
            statut='terminee', id_proj=self.projet,
        )
        Tache_projet.objects.create(
            intitule='Pas terminée', date_realisation=timezone.localdate(),
            heure_debut='09:00', heure_fin='10:00', resultat_attendu='R',
            statut='a_faire', id_proj=self.projet,
        )
        resultat = taches_a_surveiller()
        intitules = [t.intitule for t in resultat]
        self.assertNotIn('Terminée', intitules)
        self.assertIn('Pas terminée', intitules)

    def test_taches_a_surveiller_exclut_dates_futures(self):
        Tache_projet.objects.create(
            intitule='Future', date_realisation=timezone.localdate() + timedelta(days=5),
            heure_debut='09:00', heure_fin='10:00', resultat_attendu='R',
            statut='a_faire', id_proj=self.projet,
        )
        resultat = taches_a_surveiller()
        intitules = [t.intitule for t in resultat]
        self.assertNotIn('Future', intitules)

    def test_verifier_echeances_classe_correctement(self):
        Tache_projet.objects.create(
            intitule='En retard', date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() - timedelta(hours=2)).time(),
            heure_fin=(timezone.localtime() - timedelta(hours=1)).time(),
            resultat_attendu='R', statut='en_cours', id_proj=self.projet,
        )
        resultat = verifier_echeances()
        intitules_depassees = [t.intitule for t in resultat['echeance_depassee']]
        self.assertIn('En retard', intitules_depassees)

    def test_taches_proches_echeance_detecte_dans_le_seuil(self):
        Tache_projet.objects.create(
            intitule='Imminente', date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() + timedelta(minutes=5)).time(),
            heure_fin=(timezone.localtime() + timedelta(hours=1)).time(),
            resultat_attendu='R', statut='a_faire', id_proj=self.projet,
        )
        resultat = taches_proches_echeance_non_notifiees()
        intitules = [t.intitule for t in resultat]
        self.assertIn('Imminente', intitules)

    def test_taches_proches_echeance_ignore_hors_seuil(self):
        """Une tâche dans 2h ne doit pas apparaître si le seuil est de 15 minutes."""
        Tache_projet.objects.create(
            intitule='Trop loin', date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() + timedelta(hours=2)).time(),
            heure_fin=(timezone.localtime() + timedelta(hours=3)).time(),
            resultat_attendu='R', statut='a_faire', id_proj=self.projet,
        )
        resultat = taches_proches_echeance_non_notifiees()
        intitules = [t.intitule for t in resultat]
        self.assertNotIn('Trop loin', intitules)

    def test_marquer_rappel_envoye_empeche_re_notification(self):
        """Vérifie l'anti-répétition du 18.5."""
        tache = Tache_projet.objects.create(
            intitule='Imminente', date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() + timedelta(minutes=5)).time(),
            heure_fin=(timezone.localtime() + timedelta(hours=1)).time(),
            resultat_attendu='R', statut='a_faire', id_proj=self.projet,
        )
        resultat_avant = taches_proches_echeance_non_notifiees()
        self.assertEqual(len(resultat_avant), 1)

        marquer_rappel_envoye(resultat_avant)

        resultat_apres = taches_proches_echeance_non_notifiees()
        self.assertEqual(len(resultat_apres), 0)