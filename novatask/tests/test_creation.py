from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class CreationProjetTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')
        self.client.login(username='testuser', password='motdepasse')

    def test_creation_projet_via_formulaire(self):
        reponse = self.client.post(reverse('formulaire'), {
            'intitule': 'Nouveau projet',
            'date_debut': timezone.localdate().isoformat(),
            'date_fin': (timezone.localdate() + timedelta(days=30)).isoformat(),
            'resultat_attendu': 'Résultat attendu',
            'description': 'Description',
        })
        self.assertRedirects(reponse, reverse('liste_projet'))
        self.assertTrue(Projet.objects.filter(intitule='Nouveau projet').exists())

    def test_projet_cree_assigne_a_utilisateur_connecte(self):
        """id_user doit être assigné automatiquement par la vue, pas par le formulaire."""
        self.client.post(reverse('formulaire'), {
            'intitule': 'Projet assigné',
            'date_debut': timezone.localdate().isoformat(),
            'date_fin': (timezone.localdate() + timedelta(days=30)).isoformat(),
            'resultat_attendu': 'Résultat',
            'description': 'Description',
        })
        projet = Projet.objects.get(intitule='Projet assigné')
        self.assertEqual(projet.id_user, self.user)

    def test_creation_echoue_si_date_debut_passee(self):
        reponse = self.client.post(reverse('formulaire'), {
            'intitule': 'Projet invalide',
            'date_debut': (timezone.localdate() - timedelta(days=1)).isoformat(),
            'date_fin': (timezone.localdate() + timedelta(days=30)).isoformat(),
            'resultat_attendu': 'Résultat',
            'description': 'Description',
        })
        self.assertEqual(reponse.status_code, 200)  # reste sur la page, pas de redirection
        self.assertFalse(Projet.objects.filter(intitule='Projet invalide').exists())


class CreationTacheTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')
        self.client.login(username='testuser', password='motdepasse')

        self.projet = Projet.objects.create(
            intitule='Projet pour tâches',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )

    def _donnees_de_base(self):
        return {
            'intitule': 'Nouvelle tâche',
            'priorite': 'normale',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'statut': 'a_faire',
            'id_proj': self.projet.id,
        }

    def test_creation_tache_avec_resultat_attendu(self):
        donnees = self._donnees_de_base()
        donnees['resultat_attendu'] = 'Résultat de la tâche'
        reponse = self.client.post(reverse('ajouter'), donnees)
        self.assertRedirects(reponse, reverse('liste_projet'))
        self.assertTrue(Tache_projet.objects.filter(intitule='Nouvelle tâche').exists())

    def test_creation_tache_avec_fonctionnalite(self):
        """Reproduit le bug corrigé au 20.3 : fonctionnalité seule doit réussir."""
        donnees = self._donnees_de_base()
        donnees['fonctionnalite'] = 'Fonctionnalité de la tâche'
        reponse = self.client.post(reverse('ajouter'), donnees)
        self.assertRedirects(reponse, reverse('liste_projet'))
        self.assertTrue(Tache_projet.objects.filter(intitule='Nouvelle tâche').exists())

    def test_num_tache_genere_a_la_creation(self):
        donnees = self._donnees_de_base()
        donnees['resultat_attendu'] = 'Résultat'
        self.client.post(reverse('ajouter'), donnees)
        tache = Tache_projet.objects.get(intitule='Nouvelle tâche')
        self.assertTrue(tache.num_tache.startswith('T'))

    def test_ne_peut_pas_creer_tache_sur_projet_dun_autre_utilisateur(self):
        """Un utilisateur ne doit pas pouvoir rattacher une tâche au projet d'un autre."""
        autre_user = Utilisateur.objects.create_user(username='autre', password='x', nom='A', prenom='A')
        autre_projet = Projet.objects.create(
            intitule='Projet d\'un autre',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=autre_user,
        )
        donnees = self._donnees_de_base()
        donnees['id_proj'] = autre_projet.id
        donnees['resultat_attendu'] = 'Résultat'
        self.client.post(reverse('ajouter'), donnees)
        self.assertFalse(Tache_projet.objects.filter(id_proj=autre_projet).exists())