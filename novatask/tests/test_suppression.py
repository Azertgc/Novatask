from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class SuppressionTacheTest(TestCase):
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
            intitule='Tâche à supprimer',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=self.projet,
        )

    def test_get_affiche_page_de_confirmation(self):
        """Un GET ne doit PAS supprimer — seulement afficher la confirmation."""
        reponse = self.client.get(reverse('supprimer_tache', args=[self.tache.id]))
        self.assertEqual(reponse.status_code, 200)
        self.assertTrue(Tache_projet.objects.filter(id=self.tache.id).exists())

    def test_post_supprime_la_tache(self):
        reponse = self.client.post(reverse('supprimer_tache', args=[self.tache.id]))
        self.assertRedirects(reponse, reverse('liste_tache', args=[self.projet.id]))
        self.assertFalse(Tache_projet.objects.filter(id=self.tache.id).exists())

    def test_ne_peut_pas_supprimer_tache_dun_autre_utilisateur(self):
        autre_user = Utilisateur.objects.create_user(username='autre', password='x', nom='A', prenom='A')
        self.client.logout()
        self.client.login(username='autre', password='x')

        reponse = self.client.post(reverse('supprimer_tache', args=[self.tache.id]))
        self.assertEqual(reponse.status_code, 404)
        self.assertTrue(Tache_projet.objects.filter(id=self.tache.id).exists())


class SuppressionCascadeTest(TestCase):
    """Vérifie le comportement on_delete=CASCADE : supprimer un projet supprime ses tâches."""

    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='x', nom='N', prenom='P')
        self.projet = Projet.objects.create(
            intitule='Projet avec tâches',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        self.tache = Tache_projet.objects.create(
            intitule='Tâche liée',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=self.projet,
        )

    def test_suppression_projet_supprime_ses_taches(self):
        self.projet.delete()
        self.assertFalse(Tache_projet.objects.filter(id=self.tache.id).exists())

class EntreesUtilisateurSecuriteTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='testuser', password='x', nom='N', prenom='P')
        self.client.login(username='testuser', password='x')

    def test_intitule_avec_script_est_echappe_a_laffichage(self):
        from datetime import timedelta
        from django.utils import timezone
        projet = Projet.objects.create(
            intitule='<script>alert("xss")</script>',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='R',
            description='D',
            id_user=self.user,
        )
        reponse = self.client.get(reverse('liste_projet'))
        self.assertNotContains(reponse, '<script>alert("xss")</script>')
        self.assertContains(reponse, '&lt;script&gt;')        