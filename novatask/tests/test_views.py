from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class VuesAuthRequiseTest(TestCase):
    """Vérifie que les pages protégées redirigent un visiteur non connecté."""

    def test_liste_projet_redirige_si_non_connecte(self):
        response = self.client.get(reverse('liste_projet'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/connexion/', response.url)

    def test_ajouter_tache_redirige_si_non_connecte(self):
        response = self.client.get(reverse('ajouter'))
        self.assertEqual(response.status_code, 302)


class ListeProjetVueTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')
        self.client.login(username='testuser', password='motdepasse')

        self.projet = Projet.objects.create(
            intitule='Mon projet',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )

    def test_page_accessible_si_connecte(self):
        response = self.client.get(reverse('liste_projet'))
        self.assertEqual(response.status_code, 200)

    def test_contient_intitule_du_projet(self):
        response = self.client.get(reverse('liste_projet'))
        self.assertContains(response, 'Mon projet')

    def test_recherche_filtre_les_projets(self):
        Projet.objects.create(
            intitule='Autre chose',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        response = self.client.get(reverse('liste_projet'), {'q': 'Mon projet'})
        self.assertContains(response, 'Mon projet')
        self.assertNotContains(response, 'Autre chose')


class ConnexionVueTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')

    def test_connexion_avec_bons_identifiants_redirige_vers_liste_projet(self):
        response = self.client.post(reverse('connexion'), {
            'username': 'testuser',
            'password': 'motdepasse',
        })
        self.assertRedirects(response, reverse('liste_projet'))

    def test_connexion_avec_mauvais_mot_de_passe_echoue(self):
        response = self.client.post(reverse('connexion'), {
            'username': 'testuser',
            'password': 'mauvais_mot_de_passe',
        })
        self.assertEqual(response.status_code, 200)  # reste sur la page, pas de redirection
        self.assertContains(response, 'incorect')  # message d'erreur affiché

    def test_deconnexion_redirige_vers_connexion(self):
        self.client.login(username='testuser', password='motdepasse')
        response = self.client.get(reverse('deconnexion'))
        self.assertRedirects(response, reverse('connexion'))