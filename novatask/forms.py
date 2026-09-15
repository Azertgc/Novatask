from django import forms
from .models import *

class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['id_proj', 'intitule', 'date_debut', 'date_fin', 'resultat_attendu', 'id_user', 'description']
        widgets = {
            'id_proj': forms.TextInput(attrs={'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'}),
            'intitule': forms.TextInput(attrs={'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'}),
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'}),
            'resultat_attendu': forms.Textarea(attrs={'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900', 'rows': 3}),
            'id_user': forms.Select(attrs={'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'}),
            'description': forms.Textarea(attrs={'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900', 'rows': 3}),
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
            'date_realisation': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'}),
            
            'heure_debut': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'
            }),
            'heure_fin': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'
            }),
            'id_proj': forms.Select(attrs={'class': 'w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900'})
        }