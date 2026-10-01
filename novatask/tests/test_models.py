from datetime import date, time, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class UtilisateurModelTest(TestCase):
    def test_id_user_genere_automatiquement(self):
        """Le premier utilisateur créé doit recevoir l'id U001."""
        u = Utilisateur.objects.create_user(username='test1', password='x', nom='Test', prenom='Un')
        self.assertEqual(u.id_user, 'U001')

    def test_id_user_incremente(self):
        """Chaque nouvel utilisateur doit recevoir un id supérieur au précédent."""
        u1 = Utilisateur.objects.create_user(username='test1', password='x', nom='A', prenom='A')
        u2 = Utilisateur.objects.create_user(username='test2', password='x', nom='B', prenom='B')
        self.assertEqual(u1.id_user, 'U001')
        self.assertEqual(u2.id_user, 'U002')


class ProjetModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='proprio', password='x', nom='Proprio', prenom='P')

    def test_id_proj_genere_automatiquement(self):
        p = Projet.objects.create(
            intitule='Projet test',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        self.assertEqual(p.id_proj, 'P001')

    def test_date_debut_anterieure_a_aujourdhui_refusee(self):
        """clean() doit refuser une date de début dans le passé."""
        p = Projet(
            intitule='Projet invalide',
            date_debut=timezone.localdate() - timedelta(days=1),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        with self.assertRaises(ValidationError):
            p.clean()

    def test_date_fin_anterieure_a_date_debut_refusee(self):
        p = Projet(
            intitule='Projet invalide',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() - timedelta(days=1),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        with self.assertRaises(ValidationError):
            p.clean()

    def test_statut_sans_tache_est_a_faire(self):
        p = Projet.objects.create(
            intitule='Projet vide',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        self.assertEqual(p.statut, 'a_faire')

    def test_progression_sans_tache_est_zero(self):
        p = Projet.objects.create(
            intitule='Projet vide',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        self.assertEqual(p.progression, 0)


class TacheProjetModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='proprio', password='x', nom='Proprio', prenom='P')
        self.projet = Projet.objects.create(
            intitule='Projet test',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )

    def test_num_tache_genere_automatiquement(self):
        t = Tache_projet.objects.create(
            intitule='Tâche test',
            date_realisation=timezone.localdate(),
            heure_debut=time(9, 0),
            heure_fin=time(10, 0),
            resultat_attendu='Résultat',
            id_proj=self.projet,
        )
        self.assertEqual(t.num_tache, 'T001')

    def test_resultat_et_fonctionnalite_simultanes_refuses(self):
        """La contrainte XOR doit refuser si les deux champs sont remplis."""
        t = Tache_projet(
            intitule='Tâche invalide',
            date_realisation=timezone.localdate(),
            heure_debut=time(9, 0),
            heure_fin=time(10, 0),
            resultat_attendu='Résultat',
            fonctionnalite='Fonctionnalité',
            id_proj=self.projet,
        )
        with self.assertRaises(ValidationError):
            t.clean()

    def test_ni_resultat_ni_fonctionnalite_refuse(self):
        """La contrainte XOR doit refuser si aucun des deux n'est rempli."""
        t = Tache_projet(
            intitule='Tâche invalide',
            date_realisation=timezone.localdate(),
            heure_debut=time(9, 0),
            heure_fin=time(10, 0),
            id_proj=self.projet,
        )
        with self.assertRaises(ValidationError):
            t.clean()

    def test_datetime_debut_combine_date_et_heure(self):
        t = Tache_projet.objects.create(
            intitule='Tâche test',
            date_realisation=date(2026, 12, 25),
            heure_debut=time(14, 30),
            heure_fin=time(16, 0),
            resultat_attendu='Résultat',
            id_proj=self.projet,
        )
        self.assertEqual(t.datetime_debut.date(), date(2026, 12, 25))
        self.assertEqual(t.datetime_debut.time(), time(14, 30))

    def test_actualiser_statuts_passe_a_en_cours(self):
        """Une tâche dont l'heure de début est passée doit devenir 'en_cours'."""
        t = Tache_projet.objects.create(
            intitule='Tâche imminente',
            date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() - timedelta(minutes=5)).time(),
            heure_fin=(timezone.localtime() + timedelta(hours=1)).time(),
            resultat_attendu='Résultat',
            id_proj=self.projet,
            statut='a_faire',
        )
        Tache_projet.actualiser_statuts()
        t.refresh_from_db()
        self.assertEqual(t.statut, 'en_cours')

    def test_actualiser_statuts_ignore_tache_future(self):
        """Une tâche dont l'heure de début n'est pas encore atteinte reste 'a_faire'."""
        t = Tache_projet.objects.create(
            intitule='Tâche future',
            date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() + timedelta(hours=2)).time(),
            heure_fin=(timezone.localtime() + timedelta(hours=3)).time(),
            resultat_attendu='Résultat',
            id_proj=self.projet,
            statut='a_faire',
        )
        Tache_projet.actualiser_statuts()
        t.refresh_from_db()
        self.assertEqual(t.statut, 'a_faire')

    def test_est_en_retard_vrai_si_heure_fin_depassee(self):
        t = Tache_projet.objects.create(
            intitule='Tâche en retard',
            date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() - timedelta(hours=2)).time(),
            heure_fin=(timezone.localtime() - timedelta(hours=1)).time(),
            resultat_attendu='Résultat',
            id_proj=self.projet,
            statut='en_cours',
        )
        self.assertTrue(t.est_en_retard)

    def test_est_en_retard_faux_si_terminee(self):
        """Une tâche terminée n'est jamais considérée en retard, même après l'heure de fin."""
        t = Tache_projet.objects.create(
            intitule='Tâche terminée',
            date_realisation=timezone.localdate(),
            heure_debut=(timezone.localtime() - timedelta(hours=2)).time(),
            heure_fin=(timezone.localtime() - timedelta(hours=1)).time(),
            resultat_attendu='Résultat',
            id_proj=self.projet,
            statut='terminee',
        )
        self.assertFalse(t.est_en_retard)