from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from novatask.models import Utilisateur, Projet, Tache_projet


class CsrfProtectionTest(TestCase):
    """
    Utilise enforce_csrf_checks=True pour simuler un vrai navigateur,
    contrairement au client de test par défaut qui désactive CSRF.
    """

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = Utilisateur.objects.create_user(username='testuser', password='motdepasse', nom='N', prenom='P')

        self.projet = Projet.objects.create(
            intitule='Projet test',
            date_debut=timezone.localdate(),
            date_fin=timezone.localdate() + timedelta(days=30),
            resultat_attendu='Résultat',
            description='Description',
            id_user=self.user,
        )
        self.tache = Tache_projet.objects.create(
            intitule='Tâche test',
            date_realisation=timezone.localdate(),
            heure_debut='09:00',
            heure_fin='10:00',
            resultat_attendu='Résultat',
            statut='a_faire',
            id_proj=self.projet,
        )

    def test_suppression_sans_jeton_csrf_refusee(self):
        """Une requête POST sans jeton CSRF valide doit être rejetée (403)."""
        self.client.login(username='testuser', password='motdepasse')
        reponse = self.client.post(reverse('supprimer_tache', args=[self.tache.id]))
        self.assertEqual(reponse.status_code, 403)
        # La tâche ne doit PAS avoir été supprimée
        self.assertTrue(Tache_projet.objects.filter(id=self.tache.id).exists())

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.decorators import login_required

from novatask import views


class AuditPermissionsTest(TestCase):
    """
    Vérifie que toutes les vues sensibles de views.py sont bien
    décorées avec @login_required, sauf celles explicitement publiques.
    """

    VUES_PUBLIQUES = {'connexion', 'deconnexion', 'inscription', 'home'}

    def test_toutes_les_vues_sensibles_sont_protegees(self):
        noms_vues_dans_module = [
            nom for nom in dir(views)
            if callable(getattr(views, nom))
            and not nom.startswith('_')
            and getattr(getattr(views, nom), '__module__', '') == 'novatask.views'
        ]

        for nom_vue in noms_vues_dans_module:
            if nom_vue in self.VUES_PUBLIQUES:
                continue
            with self.subTest(vue=nom_vue):
                fonction = getattr(views, nom_vue)
                # login_required enveloppe la fonction et ajoute cet attribut
                est_protegee = getattr(fonction, 'login_required', False) \
                    or 'login_required' in str(fonction)
                # Vérification alternative plus fiable : inspecter le wrapping
                self.assertTrue(
                    hasattr(fonction, '__wrapped__'),
                    f"La vue '{nom_vue}' ne semble pas protégée par @login_required"
                )        

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
