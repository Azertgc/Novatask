from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class PermissionsProjetTest(TestCase):
    def setUp(self):
        self.proprietaire = Utilisateur.objects.create_user(username='proprio', password='x', nom='P', prenom='P')
        self.intrus = Utilisateur.objects.create_user(username='intrus', password='x', nom='I', prenom='I')

        self.projet = Projet.objects.create(
            intitule='Projet du propriétaire',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.proprietaire,
        )

    def test_liste_projet_ne_montre_pas_les_projets_des_autres(self):
        self.client.login(username='intrus', password='x')
        reponse = self.client.get(reverse('liste_projet'))
        self.assertNotContains(reponse, 'Projet du propriétaire')

    def test_liste_tache_dun_projet_etranger_renvoie_404(self):
        self.client.login(username='intrus', password='x')
        reponse = self.client.get(reverse('liste_tache', args=[self.projet.id]))
        self.assertEqual(reponse.status_code, 404)


class PermissionsTacheTest(TestCase):
    def setUp(self):
        self.proprietaire = Utilisateur.objects.create_user(username='proprio', password='x', nom='P', prenom='P')
        self.intrus = Utilisateur.objects.create_user(username='intrus', password='x', nom='I', prenom='I')

        self.projet = Projet.objects.create(
            intitule='Projet du propriétaire',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.proprietaire,
        )
        self.tache = Tache_projet.objects.create(
            intitule='Tâche du propriétaire',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=self.projet,
        )

    def test_intrus_ne_peut_pas_voir_modifier_tache(self):
        self.client.login(username='intrus', password='x')
        reponse = self.client.get(reverse('modifier_tache', args=[self.tache.id]))
        self.assertEqual(reponse.status_code, 404)

    def test_intrus_ne_peut_pas_soumettre_modification(self):
        self.client.login(username='intrus', password='x')
        reponse = self.client.post(reverse('modifier_tache', args=[self.tache.id]), {
            'intitule': 'Piraté',
            'priorite': 'haute',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'resultat_attendu': 'Résultat',
            'statut': 'a_faire',
        })
        self.assertEqual(reponse.status_code, 404)
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.intitule, 'Tâche du propriétaire')  # inchangée

    def test_intrus_ne_peut_pas_supprimer_tache(self):
        self.client.login(username='intrus', password='x')
        self.client.post(reverse('supprimer_tache', args=[self.tache.id]))
        self.assertTrue(Tache_projet.objects.filter(id=self.tache.id).exists())

    def test_ajouter_tache_ne_propose_que_ses_propres_projets(self):
        """Le select id_proj du formulaire ne doit jamais lister les projets d'un autre."""
        self.client.login(username='intrus', password='x')
        reponse = self.client.get(reverse('ajouter'))
        self.assertNotContains(reponse, 'Projet du propriétaire')

    def test_intrus_ne_peut_pas_rattacher_tache_a_projet_etranger(self):
        """Même en forçant l'id dans le POST, la validation du formulaire doit refuser."""
        self.client.login(username='intrus', password='x')
        reponse = self.client.post(reverse('ajouter'), {
            'intitule': 'Intrusion',
            'priorite': 'normale',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'resultat_attendu': 'Résultat',
            'statut': 'a_faire',
            'id_proj': self.projet.id,  # projet qui n'appartient pas à l'intrus
        })
        self.assertFalse(Tache_projet.objects.filter(intitule='Intrusion').exists())


class PermissionsUtilisateurAnonymeTest(TestCase):
    """Vérifie que @login_required protège bien TOUTES les vues sensibles."""

    def test_toutes_les_vues_protegees_redirigent(self):
        urls_protegees = ['liste_projet', 'formulaire', 'ajouter']
        for nom_url in urls_protegees:
            with self.subTest(url=nom_url):
                reponse = self.client.get(reverse(nom_url))
                self.assertEqual(reponse.status_code, 302)