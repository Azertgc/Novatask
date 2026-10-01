from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class ModificationTacheTest(TestCase):
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
            intitule='Tâche originale',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat original',
            statut='a_faire',
            id_proj=self.projet,
        )

    def test_modification_change_intitule(self):
        reponse = self.client.post(reverse('modifier_tache', args=[self.tache.id]), {
            'intitule': 'Tâche modifiée',
            'priorite': 'normale',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'resultat_attendu': 'Résultat original',
            'statut': 'a_faire',
        })
        self.assertRedirects(reponse, reverse('liste_tache', args=[self.projet.id]))
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.intitule, 'Tâche modifiée')
    def test_modification_change_statut(self):
        self.client.post(reverse('modifier_tache', args=[self.tache.id]), {
            'intitule': self.tache.intitule,
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'resultat_attendu': 'Résultat original',
            'statut': 'terminee',
        })
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.statut, 'terminee')

    def test_num_tache_ne_change_pas_apres_modification(self):
        """num_tache est généré une seule fois à la création — jamais régénéré."""
        num_tache_avant = self.tache.num_tache
        self.client.post(reverse('modifier_tache', args=[self.tache.id]), {
            'intitule': 'Tâche modifiée',
            'date_realisation': timezone.localdate().isoformat(),
            'heure_debut': '09:00',
            'heure_fin': '10:00',
            'resultat_attendu': 'Résultat original',
            'statut': 'a_faire',
        })
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.num_tache, num_tache_avant)

    def test_ne_peut_pas_modifier_tache_dun_autre_utilisateur(self):
        """Sécurité : get_object_or_404 avec id_proj__id_user doit bloquer l'accès."""
        autre_user = Utilisateur.objects.create_user(username='autre', password='x', nom='A', prenom='A')
        self.client.logout()
        self.client.login(username='autre', password='x')

        reponse = self.client.get(reverse('modifier_tache', args=[self.tache.id]))
        self.assertEqual(reponse.status_code, 404)

    def test_formulaire_prerempli_avec_valeurs_existantes(self):
        reponse = self.client.get(reverse('modifier_tache', args=[self.tache.id]))
        self.assertContains(reponse, 'Tâche originale')
        self.assertContains(reponse, 'Résultat original')