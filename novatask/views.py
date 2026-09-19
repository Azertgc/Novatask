from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Projet, Utilisateur, Tache_projet
from .forms import ProjetForm, NouvelleTache, InscriptionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        utilisateur = authenticate(
            request,
            username=username,
            password=password
        )
        if utilisateur is not None:
            login(request, utilisateur)
            return redirect('liste_projet')
        return render(request, 'utilisateurs/sonnexion.html',{'erreur': "Nom d'utilisateur ou mot de passe incorect."})
    return render(request, 'utilisateurs/connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion')

def inscription(request):
    if request.method =='POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_projet')
    else:
        form = InscriptionForm()
    return render(request, 'utilisateurs/inscription.html', {'form':form})        

def home(request):
    return HttpResponse("Django Fonctionne")
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
@login_required
def liste_projet(request):
    projets=Projet.objects.all()

    return render(request,'projets/liste.html',{
        'projets':projets
        })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
@login_required
def liste_tache(request, id):
    projetPer = get_object_or_404(
        Projet,
        id=id,
        id_user=request.user
    )


    return render(request, 'projets/liste_tache.html', {
        'projet':projetPer
    })
#----------------------------\----------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
@login_required
def creer_projet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = ProjetForm()
    return render(request, 'projets/formulaire.html',{
        'form' : form
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
@login_required
def modifier_tache(request, id):

    tache = get_object_or_404(
    Tache_projet,
    id=id,
    id_proj__id_user=request.user
    )

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
@login_required
def supprimer_tache(request, id):
    tache = get_object_or_404(
    Tache_projet,
    id=id,
    id_proj__id_user=request.user
    )

    if request.method == "POST":
        tache.delete()
        return redirect('liste_tache',id=tache.id_proj.id)
    return render(request, 'projets/confirmation_supression.html', {
        'tache':tache
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
@login_required
def ajouter_tache(request):

    if request.method == 'POST':
        form = NouvelleTache(request.POST)

        # On limite les projets aux projets de l'utilisateur connecté
        form.fields['id_proj'].queryset = Projet.objects.filter(
            id_user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('liste_projet')

    else:
        form = NouvelleTache()

        # Afficher uniquement les projets appartenant à l'utilisateur connecté
        form.fields['id_proj'].queryset = Projet.objects.filter(
            id_user=request.user
        )

    return render(request, 'projets/ajouter_tache.html', {
        'form': form,
    })