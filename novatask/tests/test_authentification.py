from django.test import TestCase
from django.urls import reverse

from novatask.models import Utilisateur


class InscriptionVueTest(TestCase):
    def test_inscription_cree_utilisateur(self):
        reponse = self.client.post(reverse('inscription'), {
            'username': 'nouveluser',
            'nom': 'Nom',
            'prenom': 'Prenom',
            'password1': 'motdepasse123!',
            'password2': 'motdepasse123!',
        })
        self.assertRedirects(reponse, reverse('liste_projet'))
        self.assertTrue(Utilisateur.objects.filter(username='nouveluser').exists())

    def test_inscription_connecte_automatiquement(self):
        """Après inscription, l'utilisateur doit être connecté sans repasser par /connexion/."""
        self.client.post(reverse('inscription'), {
            'username': 'nouveluser',
            'nom': 'Nom',
            'prenom': 'Prenom',
            'password1': 'motdepasse123!',
            'password2': 'motdepasse123!',
        })
        reponse = self.client.get(reverse('liste_projet'))
        self.assertEqual(reponse.status_code, 200)  # accessible sans login manuel

    def test_inscription_mot_de_passe_hashe(self):
        """Le mot de passe ne doit jamais être stocké en clair."""
        self.client.post(reverse('inscription'), {
            'username': 'nouveluser',
            'nom': 'Nom',
            'prenom': 'Prenom',
            'password1': 'motdepasse123!',
            'password2': 'motdepasse123!',
        })
        utilisateur = Utilisateur.objects.get(username='nouveluser')
        self.assertNotEqual(utilisateur.password, 'motdepasse123!')
        self.assertTrue(utilisateur.password.startswith('pbkdf2_'))

    def test_username_deja_pris_refuse(self):
        Utilisateur.objects.create_user(username='existant', password='x', nom='N', prenom='P')
        reponse = self.client.post(reverse('inscription'), {
            'username': 'existant',
            'nom': 'Autre',
            'prenom': 'Autre',
            'password1': 'motdepasse123!',
            'password2': 'motdepasse123!',
        })
        self.assertEqual(reponse.status_code, 200)  # reste sur la page, pas de redirection
        self.assertEqual(Utilisateur.objects.filter(username='existant').count(), 1)


class ConnexionCasLimitesTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')

    def test_connexion_username_insensible_a_la_casse(self):
        """Vérifie le CaseInsensitiveModelBackend mis en place précédemment."""
        reponse = self.client.post(reverse('connexion'), {
            'username': 'TESTUSER',
            'password': 'motdepasse',
        })
        self.assertRedirects(reponse, reverse('liste_projet'))

    def test_connexion_username_inexistant_echoue(self):
        reponse = self.client.post(reverse('connexion'), {
            'username': 'nexistepas',
            'password': 'nimportequoi',
        })
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, 'incorect')

    def test_acces_page_protegee_apres_deconnexion(self):
        """Après déconnexion, l'accès aux pages protégées doit à nouveau être bloqué."""
        self.client.login(username='testuser', password='motdepasse')
        self.client.get(reverse('deconnexion'))
        reponse = self.client.get(reverse('liste_projet'))
        self.assertEqual(reponse.status_code, 302)