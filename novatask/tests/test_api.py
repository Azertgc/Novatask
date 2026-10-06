from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from novatask.models import Utilisateur, Projet, Tache_projet
from datetime import date, timedelta


class APIProjetTests(APITestCase):
    def setUp(self):
        self.user1 = Utilisateur.objects.create_user(username='alice', password='test1234')
        self.user2 = Utilisateur.objects.create_user(username='bob', password='test1234')
        self.projet1 = Projet.objects.create(
            id_user=self.user1,
            intitule='Projet Alice',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=10),
        )
        self.projet2 = Projet.objects.create(
            id_user=self.user2,
            intitule='Projet Bob',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=10),
        )

    def test_liste_sans_authentification_refusee(self):
        response = self.client.get('/api/projets/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_liste_ne_montre_que_ses_propres_projets(self):
        self.client.login(username='alice', password='test1234')
        response = self.client.get('/api/projets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id_proj'] for p in response.data['results']]
        self.assertIn(self.projet1.id_proj, ids)
        self.assertNotIn(self.projet2.id_proj, ids)

    def test_acces_projet_dun_autre_user_refuse(self):
        self.client.login(username='alice', password='test1234')
        response = self.client.get(f'/api/projets/{self.projet2.id_proj}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_creation_projet_rattache_automatiquement_au_user(self):
        self.client.login(username='alice', password='test1234')
        response = self.client.post('/api/projets/', {
            'intitule': 'Nouveau projet',
            'description': 'Description du nouveau projet',
            'resultat_attendu': 'Livrer le projet',
            'date_debut': date.today(),
            'date_fin': date.today() + timedelta(days=5),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        projet = Projet.objects.get(id_proj=response.data['id_proj'])
        self.assertEqual(projet.id_user, self.user1)

    def test_creation_projet_date_fin_avant_debut_refusee(self):
        self.client.login(username='alice', password='test1234')
        response = self.client.post('/api/projets/', {
            'intitule': 'Projet invalide',
            'date_debut': date.today(),
            'date_fin': date.today() - timedelta(days=1),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class APITacheTests(APITestCase):
    def setUp(self):
        self.user1 = Utilisateur.objects.create_user(username='alice', password='test1234')
        self.user2 = Utilisateur.objects.create_user(username='bob', password='test1234')
        self.projet1 = Projet.objects.create(
            id_user=self.user1,
            intitule='Projet Alice',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=10),
        )
        self.projet2 = Projet.objects.create(
            id_user=self.user2,
            intitule='Projet Bob',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=10),
        )

    def test_impossible_de_creer_une_tache_sur_projet_dun_autre_user(self):
        self.client.login(username='alice', password='test1234')
        response = self.client.post('/api/taches/', {
            'id_proj': self.projet2.id_proj,
            'intitule': 'Intrusion',
            'resultat_attendu': 'test',
            'date_realisation': date.today(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'priorite': 'normale',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creation_tache_avec_resultat_et_fonctionnalite_refusee(self):
        self.client.login(username='alice', password='test1234')
        response = self.client.post('/api/taches/', {
            'id_proj': self.projet1.id_proj,
            'intitule': 'Tache invalide',
            'resultat_attendu': 'test',
            'fonctionnalite': 'test',
            'date_realisation': date.today(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'priorite': 'normale',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

   