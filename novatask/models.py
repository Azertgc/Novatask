"""
Modèles de données de NovaTask.

Trois modèles : Utilisateur (compte), Projet, et Tache_projet (une tâche
rattachée à un projet). Chacun génère son propre identifiant métier
auto-incrémenté (U001, P001, T001...) dans sa méthode save(), en plus de
la clé primaire technique de Django (un entier auto-incrémenté invisible,
géré par DEFAULT_AUTO_FIELD dans settings.py).
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Q, CheckConstraint
from django.utils import timezone
from datetime import datetime
# Create your models here.


class Utilisateur(AbstractUser):
    # AbstractUser fournit déjà username, password (hashé), email, etc.
    # On étend ce modèle plutôt que d'en créer un séparé, pour garder
    # l'authentification standard de Django (login, permissions...) tout
    # en ajoutant les champs propres à NovaTask.

    # Identifiant métier auto-généré (U001, U002...). unique=True empêche
    # deux comptes d'avoir le même ; editable=False le cache des formulaires
    # Django générés automatiquement (ModelForm, admin) — il ne doit jamais
    # être saisi à la main.
    id_user = models.CharField(max_length=5, unique=True, editable=False)
    nom = models.CharField(max_length=25)
    prenom = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Génération de l'identifiant uniquement à la création (quand
        # id_user est encore vide) — une fois assigné, il ne change plus,
        # même lors d'une modification ultérieure du compte.
        if not self.id_user:
            # Récupère tous les identifiants déjà utilisés au format "Uxxx",
            # pour en déduire le prochain numéro disponible.
            utilisateurs = Utilisateur.objects.filter(
                id_user__startswith='U'
            )

            dernier_numero = 0
            for utilisateur in utilisateurs:
                try:
                    # Extrait la partie numérique après le "U" (ex: "U007" -> 7)
                    numero = int(utilisateur.id_user[1:])
                    dernier_numero = max(dernier_numero, numero)
                except ValueError:
                    # Protection si un id_user mal formé existe en base
                    # (ne devrait pas arriver, mais évite un crash).
                    pass

            # :03d -> toujours 3 chiffres avec des zéros devant (1 -> "001")
            self.id_user = f"U{dernier_numero + 1:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        # Représentation textuelle utilisée par Django (admin, console...)
        # partout où l'objet doit s'afficher sous forme de texte.
        return self.nom

# --------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------
class Projet(models.Model):
    id_proj = models.CharField(max_length=5, unique=True, editable=False)
    intitule = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    resultat_attendu = models.TextField()

    # related_name="projets" : permet d'accéder depuis un Utilisateur à
    # tous ses projets via utilisateur.projets.all() (sans ça, Django
    # utiliserait par défaut "projet_set").
    id_user = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,  # si l'utilisateur est supprimé, ses
                                     # projets le sont aussi automatiquement
        related_name="projets"
    )
    description = models.TextField()

    def save(self, *args, **kwargs):
        # Même logique de génération d'identifiant que pour Utilisateur,
        # avec le préfixe "P" (P001, P002...).
        if not self.id_proj:
            projets = Projet.objects.filter(id_proj__startswith='P')

            dernier_numero = 0
            for projet in projets:
                try:
                    numero = int(projet.id_proj[1:])
                    dernier_numero = max(dernier_numero, numero)
                except ValueError:
                    pass

            self.id_proj = f"P{dernier_numero + 1:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.intitule

    @property
    def statut(self):
        # Valeur CALCULÉE à chaque accès (pas stockée en base), déduite
        # de l'état de toutes les tâches du projet. related_name="taches"
        # (défini sur Tache_projet.id_proj plus bas) permet cet accès via
        # self.taches.all().
        taches = self.taches.all()
        if not taches.exists():
            return 'a_faire'
        if all(tache.statut == 'terminee' for tache in taches):
            return 'termine'
        if any(tache.statut == 'en_cours' for tache in taches):
            return 'en_cours'
        return "a_faire"

    @property
    def progression(self):
        # Pourcentage de tâches terminées, arrondi à l'entier le plus proche.
        taches = self.taches.all()
        if not taches.exists():
            return 0
        terminee = taches.filter(
            statut='terminee'
        ).count()
        return round((terminee / taches.count()) * 100)

    def clean(self):
        # clean() : validation métier personnalisée, appelée uniquement
        # via full_clean() (jamais automatiquement par save() seul — voir
        # api_views.py et le formulaire HTML équivalent pour l'appel explicite).
        from django.utils import timezone

        # Garde "is not None" : évite un crash si date_debut n'est pas
        # encore renseignée au moment de l'appel (ex: validation partielle).
        if self.date_debut is not None and self.date_debut < timezone.localdate():
            raise ValidationError("La date de début ne peut pas être antérieure à aujourd'hui.")

        if self.date_debut is not None and self.date_fin is not None and self.date_fin < self.date_debut:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")

# --------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------
class Tache_projet(models.Model):
    # TextChoices : définit un ensemble fermé de valeurs possibles pour un
    # champ (ici statut et priorite), avec une valeur technique (stockée
    # en base, ex: 'a_faire') et un libellé humain (affiché, ex: 'A faire').
    class Statut(models.TextChoices):
        A_FAIRE = 'a_faire', 'A faire'
        EN_COURS = 'en_cours', 'En cours'
        TERMINEE = 'terminee', 'Terminee'

    class Priorite(models.TextChoices):
        BASSE = 'basse', 'Basse'
        NORMALE = 'normale', 'Normale'
        HAUTE = 'haute', 'Haute'

    # Sert à éviter d'envoyer plusieurs fois la même notification de
    # rappel pour une même tâche (voir la commande verifier_taches et
    # services.py, chapitres 17-18).
    rappel_envoye = models.BooleanField(default=False)

    num_tache = models.CharField(max_length=100, unique=True, editable=False)
    intitule = models.CharField(max_length=100)
    priorite = models.CharField(
        max_length=10,
        choices=Priorite.choices,
        default='normale'
    )
    date_realisation = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    # null=True, blank=True sur les deux : chacun est individuellement
    # facultatif au niveau base de données ET formulaire, car la règle
    # réelle (l'un des deux, jamais les deux, jamais aucun) est une
    # contrainte croisée entre les deux champs, pas une contrainte sur
    # un champ pris isolément — elle est imposée par clean() ci-dessous
    # et par la CheckConstraint définie dans Meta plus bas.
    resultat_attendu = models.TextField(null=True, blank=True)
    fonctionnalite = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        # Règle XOR : exactement un des deux champs doit être rempli.
        if self.resultat_attendu and self.fonctionnalite:
            raise ValidationError("Indiquer soit la FONCTIONNALITE soit le RESULTAT ATTENDU")
        if not self.resultat_attendu and not self.fonctionnalite:
            raise ValidationError("Vous devez renseigner soit la FONCTIONNALITE soit le RESULTAT ATTENDU.")

    @property
    def datetime_debut(self):
        # Combine la date et l'heure de début en un seul datetime complet,
        # nécessaire pour comparer "maintenant" à "quand la tâche commence"
        # (une DateField et une TimeField séparées ne se comparent pas
        # directement à un datetime).
        naive = datetime.combine(self.date_realisation, self.heure_debut)
        # make_aware : attache le fuseau horaire du projet (settings.TIME_ZONE)
        # à un datetime "naïf" (sans fuseau), requis par Django quand
        # USE_TZ=True, pour comparer correctement avec timezone.localtime().
        return timezone.make_aware(naive) if timezone.is_naive(naive) else naive

    @property
    def est_en_retard(self):
        # En retard si l'heure de fin est dépassée ET que la tâche n'est
        # pas marquée terminée (une tâche terminée en retard reste "terminée",
        # pas "en retard").
        return self.statut != 'terminee' and timezone.localtime() >= self.datetime_fin

    @property
    def datetime_fin(self):
        naive = datetime.combine(self.date_realisation, self.heure_fin)
        return timezone.make_aware(naive) if timezone.is_naive(naive) else naive

    @classmethod
    def actualiser_statuts(cls, queryset=None):
        """
        Fait passer automatiquement les tâches de 'a_faire' à 'en_cours'
        dès que leur date + heure de début est atteinte.
        """
        maintenant = timezone.localtime()
        # queryset=None -> traite toutes les tâches ; sinon, permet de
        # restreindre l'appel à un sous-ensemble (utile pour les tests,
        # ou un futur appel ciblé sur les tâches d'un seul utilisateur).
        taches = (queryset if queryset is not None else cls.objects.all()).filter(statut='a_faire')

        a_mettre_a_jour = []
        for tache in taches:
            if maintenant >= tache.datetime_debut:
                tache.statut = 'en_cours'
                a_mettre_a_jour.append(tache)

        if a_mettre_a_jour:
            # bulk_update : une seule requête SQL pour mettre à jour toutes
            # les tâches concernées, au lieu d'un .save() par tâche (bien
            # plus efficace si beaucoup de tâches changent de statut en
            # même temps, ex: lors de l'exécution périodique de verifier_taches).
            cls.objects.bulk_update(a_mettre_a_jour, ['statut'])

        return a_mettre_a_jour

    # ... reste inchangé (save, __str__, etc.) ...
    class Meta:
        constraints = [
            # Doublon, au niveau BASE DE DONNÉES, de la règle déjà vérifiée
            # dans clean() ci-dessus. Utile car clean()/full_clean() ne sont
            # jamais appelés automatiquement par Django — un code qui
            # appellerait .save() directement sans passer par full_clean()
            # (bug, script externe, oubli) serait quand même bloqué par
            # cette contrainte SQL, en dernier recours.
            # Attention : comme vu lors du développement de l'API, cette
            # contrainte se déclenche AU MOMENT de l'INSERT/UPDATE, avant
            # qu'une exception Python propre ne puisse être levée — d'où
            # l'importance de toujours valider avec full_clean() AVANT
            # d'appeler .save(), plutôt qu'après.
            CheckConstraint(
                condition=
                (Q(resultat_attendu__isnull=False) & Q(fonctionnalite__isnull=True))
                |
                (Q(resultat_attendu__isnull=True) & Q(fonctionnalite__isnull=False)),
                name="soit_a_soit_b_pas_les_deux"
            )
        ]

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default='a_faire'
    )
    # related_name="taches" : permet projet.taches.all() depuis un Projet
    # (utilisé par les @property statut/progression de Projet ci-dessus,
    # et par get_queryset() dans api_views.py : id_proj__id_user).
    id_proj = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name="taches"
    )

    # auto_now_add : fixé une seule fois à la création, jamais modifié ensuite.
    # auto_now : mis à jour automatiquement à CHAQUE save().
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Même logique de génération d'identifiant que Utilisateur/Projet,
        # avec le préfixe "T" (T001, T002...).
        if not self.num_tache:
            taches = Tache_projet.objects.filter(num_tache__startswith='T')

            dernier_numero = 0
            for tache in taches:
                try:
                    numero = int(tache.num_tache[1:])
                    dernier_numero = max(dernier_numero, numero)
                except ValueError:
                    pass

            self.num_tache = f"T{dernier_numero + 1:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.intitule