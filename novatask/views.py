from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Projet, Utilisateur, Tache_projet
from .forms import ProjetForm, NouvelleTache
# Create your views here.

def home(request):
    return HttpResponse("Django Fonctionne")
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
def liste_projet(request):
    projets=Projet.objects.all()

    return render(request,'projets/liste.html',{
        'projets':projets
        })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
def liste_tache(request, id):
    projetPer =  Projet.objects.get(id=id)


    return render(request, 'projets/liste_tache.html', {
        'projet':projetPer
    })
#----------------------------\----------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
def creer_projet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_projet')
    else:
        form = ProjetForm()
    return render(request, 'projets/formulaire.html',{
        'form' : form
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
def modifier_tache(request, id):

    tache = get_object_or_404(Tache_projet, id=id)

    if request.method == "POST":
        tache.intitule = request.POST.get('intitule')
        tache.date_realisation = request.POST.get('date_realisation')
        tache.heure_debut = request.POST.get('heure_debut')
        tache.heure_fin = request.POST.get('heure_fin')
        tache.resultat_attendu = request.POST.get('resultat_attendu')
        tache.statut = request.POST.get('statut')
        tache.save()
        return redirect('liste_tache',id=tache.id_proj.id)

    return render(request, 'projets/modifier_tache.html',{'tache':tache})
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
def supprimer_tache(request, id):
    tache = get_object_or_404(Tache_projet, id=id)

    if request.method == "POST":
        tache.delete()
        return redirect('liste_tache',id=tache.id_proj.id)
    return render(request, 'projets/confirmation_supression.html', {
        'tache':tache
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
def ajouter_tache(request):
  
    if request.method == 'POST':
        form = NouvelleTache(request.POST)
        if form.is_valid():
            form.save()
            return redirect( 'liste_projet')
    else:
        form = NouvelleTache()
    return render(request, 'projets/ajouter_tache.html', {
        'form': form,
        
    })    