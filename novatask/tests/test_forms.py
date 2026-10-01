from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from novatask.models import Utilisateur, Projet
from novatask.forms import ProjetForm, NouvelleTache, InscriptionForm


class InscriptionFormTest(TestCase):
    def test_formulaire_valide_avec_donnees_correctes(self):
        form = InscriptionForm(data={
            'username': 'nouvel_user',
            'nom': 'Nom',
            'prenom': 'Prenom',
            'password1': 'motdepasse123!',
            'password2': 'motdepasse123!',
        })
        self.assertTrue(form.is_valid())

    def test_formulaire_invalide_si_mots_de_passe_differents(self):
        form = InscriptionForm(data={
            'username': 'nouvel_user',
            'nom': 'Nom',
            'prenom': 'Prenom',
            'password1': 'motdepasse123!',
            'password2': 'autrechose456!',
        })
        self.assertFalse(form.is_valid())

    def test_formulaire_invalide_si_username_manquant(self):
        form = InscriptionForm(data={
            'nom': 'Nom',
            'prenom': 'Prenom',
            'password1': 'motdepasse123!',
            'password2': 'motdepasse123!',
        })
        self.assertFalse(form.is_valid())


class ProjetFormTest(TestCase):
    def test_formulaire_valide_avec_donnees_correctes(self):
        form = ProjetForm(data={
            'intitule': 'Projet test',
            'date_debut': timezone.localdate().isoformat(),
            'date_fin': (timezone.localdate() + timedelta(days=30)).isoformat(),
            'resultat_attendu': 'Résultat attendu',
            'description': 'Description',
        })
        self.assertTrue(form.is_valid())

    def test_formulaire_invalide_sans_intitule(self):
        form = ProjetForm(data={
            'intitule': '',
            'date_debut': timezone.localdate().isoformat(),
            'date_fin': (timezone.localdate() + timedelta(days=30)).isoformat(),
            'resultat_attendu': 'Résultat attendu',
            'description': 'Description',
        })
        self.assertFalse(form.is_valid())

    def test_id_user_absent_des_champs(self):
        """id_user ne doit jamais être un champ saisissable — assigné par la vue."""
        form = ProjetForm()
        self.assertNotIn('id_user', form.fields)

    def test_id_proj_absent_des_champs(self):
        """id_proj est généré automatiquement, jamais saisi par l'utilisateur."""
        form = ProjetForm()
        self.assertNotIn('id_proj', form.fields)


class NouvelleTacheFormTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='proprio', password='x', nom='P', prenom='P')
        self.projet = Projet.objects.create(
            intitule='Projet test',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )

    def _donnees_de_base(self):
        return {
            'intitule': 'Tâche test',
            'priorite': 'normale',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'statut': 'a_faire',
            'id_proj': self.projet.id,
        }

    def test_valide_avec_resultat_attendu_seul(self):
        donnees = self._donnees_de_base()
        donnees['resultat_attendu'] = 'Résultat'
        form = NouvelleTache(data=donnees)
        self.assertTrue(form.is_valid())

    def test_valide_avec_fonctionnalite_seule(self):
        donnees = self._donnees_de_base()
        donnees['fonctionnalite'] = 'Fonctionnalité'
        form = NouvelleTache(data=donnees)
        self.assertTrue(form.is_valid())

    def test_invalide_si_resultat_et_fonctionnalite_remplis(self):
        donnees = self._donnees_de_base()
        donnees['resultat_attendu'] = 'Résultat'
        donnees['fonctionnalite'] = 'Fonctionnalité'
        form = NouvelleTache(data=donnees)
        self.assertFalse(form.is_valid())

    def test_invalide_si_ni_resultat_ni_fonctionnalite(self):
        donnees = self._donnees_de_base()
        form = NouvelleTache(data=donnees)
        self.assertFalse(form.is_valid())

    def test_num_tache_absent_des_champs(self):
        form = NouvelleTache()
        self.assertNotIn('num_tache', form.fields)



class NouvelleTacheFormSecuriteTest(TestCase):
    def setUp(self):
        self.proprietaire = Utilisateur.objects.create_user(username='proprio', password='x', nom='P', prenom='P')
        self.intrus = Utilisateur.objects.create_user(username='intrus', password='x', nom='I', prenom='I')

        self.projet_proprietaire = Projet.objects.create(
            intitule='Projet protégé',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.proprietaire,
        )

    def test_formulaire_rejette_projet_hors_queryset_restreint(self):
        """
        Simule exactement ce que fait la vue : restreindre le queryset
        du champ id_proj aux projets de l'utilisateur AVANT validation.
        Un id valide en base mais hors queryset doit être rejeté.
        """
        form = NouvelleTache(data={
            'intitule': 'Tâche malveillante',
            'priorite': 'normale',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'resultat_attendu': 'Résultat',
            'statut': 'a_faire',
            'id_proj': self.projet_proprietaire.id,
        })
        # Simule la restriction appliquée par la vue pour l'intrus
        form.fields['id_proj'].queryset = Projet.objects.filter(id_user=self.intrus)

        self.assertFalse(form.is_valid())
        self.assertIn('id_proj', form.errors)        

class MotDePasseSecuriteTest(TestCase):
    def test_mot_de_passe_trop_court_refuse(self):
        form = InscriptionForm(data={
            'username': 'testuser',
            'nom': 'N',
            'prenom': 'P',
            'password1': 'abc',  # trop court
            'password2': 'abc',
        })
        self.assertFalse(form.is_valid())

    def test_mot_de_passe_uniquement_numerique_refuse(self):
        form = InscriptionForm(data={
            'username': 'testuser',
            'nom': 'N',
            'prenom': 'P',
            'password1': '123456789',
            'password2': '123456789',
        })
        self.assertFalse(form.is_valid())

    def test_mot_de_passe_trop_commun_refuse(self):
        form = InscriptionForm(data={
            'username': 'testuser',
            'nom': 'N',
            'prenom': 'P',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertFalse(form.is_valid())

    def test_mot_de_passe_similaire_au_username_refuse(self):
        form = InscriptionForm(data={
            'username': 'jeandupont',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'password1': 'jeandupont123',  # trop proche du username
            'password2': 'jeandupont123',
        })
        self.assertFalse(form.is_valid())

    def test_mot_de_passe_robuste_accepte(self):
        form = InscriptionForm(data={
            'username': 'testuser',
            'nom': 'N',
            'prenom': 'P',
            'password1': 'Xk9#mP2vLq8!',
            'password2': 'Xk9#mP2vLq8!',
        })
        self.assertTrue(form.is_valid())        