from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


INPUT_CLASSES = (
    "w-full border border-[#DEDEDA] bg-white px-3 py-2.5 text-sm text-[#1C1C1A] "
    "focus:outline-none focus:border-[#1C1C1A] transition-colors"
)

TEXTAREA_CLASSES = INPUT_CLASSES
SELECT_CLASSES = INPUT_CLASSES


class InscriptionForm(UserCreationForm):
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
        fields = ['id_proj', 'intitule', 'date_debut', 'date_fin', 'resultat_attendu', 'id_user', 'description']
        widgets = {
            'id_proj': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'intitule': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'resultat_attendu': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
            'id_user': forms.Select(attrs={'class': SELECT_CLASSES}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
        }


class NouvelleTache(forms.ModelForm):
    class Meta:
        model = Tache_projet
        fields = [
            'num_tache',
            'intitule',
            'date_realisation',
            'heure_debut',
            'heure_fin',
            'resultat_attendu',
            'fonctionnalite',
            'statut',
            'id_proj',
        ]
        widgets = {
            'num_tache': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'intitule': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'date_realisation': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES}),
            'resultat_attendu': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3}),
            'fonctionnalite': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'statut': forms.Select(attrs={'class': SELECT_CLASSES}),
            'id_proj': forms.Select(attrs={'class': SELECT_CLASSES}),
        }