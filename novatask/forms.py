from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from datetime import date

# Classes Tailwind communes à (presque) tous les widgets du site, pour un
# rendu visuel homogène sans répéter la même chaîne dans chaque formulaire.
INPUT_CLASSES = (
    "w-full border border-[#DEDEDA] bg-white px-3 py-2.5 text-sm text-[#1C1C1A] "
    "focus:outline-none focus:border-[#1C1C1A] transition-colors"
)

# Alias : mêmes classes que INPUT_CLASSES, mais nommés séparément pour
# rester libres de les faire diverger plus tard (ex: hauteur différente
# pour un <select> ou un <textarea>) sans toucher aux <input> classiques.
TEXTAREA_CLASSES = INPUT_CLASSES
SELECT_CLASSES = INPUT_CLASSES


class InscriptionForm(UserCreationForm):
    # Hérite de UserCreationForm (fourni par Django) plutôt que d'un
    # simple ModelForm : réutilise sa logique de création de compte
    # (hashage du mot de passe, vérification password1 == password2...),
    # tout en la branchant sur le modèle Utilisateur personnalisé du
    # projet plutôt que sur le User par défaut de Django.
    class Meta:
        model = Utilisateur
        fields = ['username', 'nom', 'prenom', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': "Entrez votre nom d'utilisateur",
            }),
            'nom': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': "Votre nom",
            }),
            'prenom': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': "Votre prénom",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # password1 et password2 ne sont pas des champs du modèle,
        # UserCreationForm les définit lui-même : on les stylise ici.
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': "Entrez votre mot de passe",
        })
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': "Confirmez votre mot de passe",
        })



class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['intitule', 'date_debut', 'date_fin', 'resultat_attendu', 'description']
        widgets = {
            'intitule': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'date_debut': forms.DateInput(attrs={
                'type': 'date',
                'class': INPUT_CLASSES,
                # min=aujourd'hui : empêche de choisir une date de début
                # dans le passé directement au niveau du sélecteur du
                # navigateur. Ne remplace pas la validation serveur dans
                # Projet.clean() (modifiable via les outils dev du
                # navigateur), juste un garde-fou côté UX.
                'min': date.today().isoformat(),
            }),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'resultat_attendu': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
        }


class NouvelleTache(forms.ModelForm):
    # Déclarés explicitement (hors Meta.widgets) pour forcer empty_value=None :
    # une chaîne vide '' envoyée par le toggle JS doit devenir NULL en base,
    # sinon la contrainte SQL "soit_a_soit_b_pas_les_deux" est violée même
    # quand un seul des deux champs est réellement rempli.
    resultat_attendu = forms.CharField(
        required=False,
        empty_value=None,
        widget=forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3})
    )
    fonctionnalite = forms.CharField(
        required=False,
        empty_value=None,
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )

    class Meta:
        model = Tache_projet
        fields = [
            'intitule',
            'priorite',
            'id_proj',
            'date_realisation',
            'heure_debut',
            'heure_fin',
            'resultat_attendu',
            'fonctionnalite',
            'statut',

        ]
        widgets = {
            'intitule': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'priorite': forms.Select(attrs={'class': SELECT_CLASSES}),
            'date_realisation': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES}),
            'statut': forms.Select(attrs={'class': SELECT_CLASSES}),
            # id_proj : liste déroulante des projets de l'utilisateur, pour
            # rattacher la nouvelle tâche à l'un d'eux (le queryset proposé
            # est filtré par utilisateur côté vue, pas ici).
            'id_proj': forms.Select(attrs={'class': SELECT_CLASSES}),
        }