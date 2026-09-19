from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Q, CheckConstraint
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
    id_proj = models.CharField(max_length=5)
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
    

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------     
class Tache_projet(models.Model):
    class Statut(models.TextChoices):
        A_FAIRE = 'a_faire','A faire'
        EN_COURS = 'en_cours','En cours'
        TERMINEE = 'terminee','Terminee'

    num_tache = models.CharField(max_length=100)
    intitule = models.CharField(max_length=100)
    date_realisation = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    resultat_attendu = models.TextField(null = True, blank = True)
    fonctionnalite = models.CharField(max_length=255, null = True, blank = True)
    def clean(self):
        if self.resultat_attendu and self.fonctionnalite:
            raise ValidationError("Indiquer soit la FONCTIONNALITE soit le RESULTAT ATTENDU")
        if not self.resultat_attendu and not self.fonctionnalite:
            raise ValidationError("Vous devez renseigner soit la FONCTIONNALITE soit le RESULTAT ATTENDU.")
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

    def  __str__(self):
        return self.intitule       
        