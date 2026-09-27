from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Q, CheckConstraint
from django.utils import timezone
from datetime import datetime
# Create your models here.

class Utilisateur(AbstractUser):
    id_user = models.CharField(max_length=5, unique=True, editable=False)
    nom = models.CharField(max_length=25)
    prenom = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        if not self.id_user:
            utilisateurs = Utilisateur.objects.filter(
                id_user__startswith='U'
            )

            dernier_numero = 0

            for utilisateur in utilisateurs:
                try:
                    numero = int(utilisateur.id_user[1:])
                    dernier_numero = max(dernier_numero, numero)
                except ValueError:
                    pass

            self.id_user = f"U{dernier_numero + 1:03d}"

        super().save(*args, **kwargs)      

    def  __str__(self):
        return self.nom
    
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------     
class Projet(models.Model):
    id_proj = models.CharField(max_length=5, unique=True, editable=False)
    intitule = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    resultat_attendu = models.TextField()

    id_user = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="projets"
        )
    description = models.TextField()

    def save(self, *args, **kwargs):
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

    def  __str__(self):
        return self.intitule

    @property
    def statut(self):
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
        taches = self.taches.all()
        if not taches.exists():
            return 0
        terminee = taches.filter(
            statut = 'terminee'
        ).count()
        return round((terminee / taches.count())*100)
    
    def clean(self):
        from django.utils import timezone

        if self.date_debut is not None and self.date_debut < timezone.localdate():
            raise ValidationError("La date de début ne peut pas être antérieure à aujourd'hui.")

        if self.date_debut is not None and self.date_fin is not None and self.date_fin < self.date_debut:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------     
class Tache_projet(models.Model):
    class Statut(models.TextChoices):
        A_FAIRE = 'a_faire','A faire'
        EN_COURS = 'en_cours','En cours'
        TERMINEE = 'terminee','Terminee'
    rappel_envoye = models.BooleanField(default=False)
    num_tache = models.CharField(max_length=100, unique=True, editable=False)
    intitule = models.CharField(max_length=100)
    date_realisation = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    resultat_attendu = models.TextField(null=True, blank=True)
    fonctionnalite = models.CharField(max_length=255, null=True, blank=True)
    
    def clean(self):
        if self.resultat_attendu and self.fonctionnalite:
            raise ValidationError("Indiquer soit la FONCTIONNALITE soit le RESULTAT ATTENDU")
        if not self.resultat_attendu and not self.fonctionnalite:
            raise ValidationError("Vous devez renseigner soit la FONCTIONNALITE soit le RESULTAT ATTENDU.")

    @property
    def datetime_debut(self):
        naive = datetime.combine(self.date_realisation, self.heure_debut)
        return timezone.make_aware(naive) if timezone.is_naive(naive) else naive

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
        taches = (queryset if queryset is not None else cls.objects.all()).filter(statut='a_faire')

        a_mettre_a_jour = []
        for tache in taches:
            if maintenant >= tache.datetime_debut:
                tache.statut = 'en_cours'
                a_mettre_a_jour.append(tache)

        if a_mettre_a_jour:
            cls.objects.bulk_update(a_mettre_a_jour, ['statut'])

        return a_mettre_a_jour

    # ... reste inchangé (save, __str__, etc.) ...
    class Meta:
        constraints = [
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
    id_proj = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name="taches"
        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
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
        

    def  __str__(self):
        return self.intitule