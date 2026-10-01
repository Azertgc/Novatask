from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Projet, Utilisateur, Tache_projet
from .forms import ProjetForm, NouvelleTache, InscriptionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

from django.utils import timezone
from novatask.services import normaliser
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
        return render(request, 'utilisateurs/connexion.html',{'erreur': "Nom d'utilisateur ou mot de passe incorect."})
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
    Tache_projet.actualiser_statuts(
        queryset=Tache_projet.objects.filter(id_proj__id_user=request.user)
    )
    projets = Projet.objects.filter(id_user=request.user)

    recherche = request.GET.get('q', '').strip()
    if recherche:
        terme = normaliser(recherche)
        projets = [p for p in projets if terme in normaliser(p.intitule)]

    statut_filtre = request.GET.get('statut', '').strip()
    if statut_filtre in ('a_faire', 'en_cours', 'termine'):
        projets = [p for p in projets if p.statut == statut_filtre] if isinstance(projets, list) \
            else [p for p in projets if p.statut == statut_filtre]

    return render(request, 'projets/liste.html', {
        'projets': projets,
        'recherche': recherche,
        'statut_filtre': statut_filtre,
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------                   

@login_required
def liste_tache(request, id):
    projetPer = get_object_or_404(Projet, id=id, id_user=request.user)
    Tache_projet.actualiser_statuts(queryset=projetPer.taches.all())
    taches = Tache_projet.objects.filter(id_proj=projetPer)

    recherche = request.GET.get('q', '').strip()
    if recherche:
        terme = normaliser(recherche)
        taches = [t for t in taches if terme in normaliser(t.intitule)]

    statuts_valides = ('a_faire', 'en_cours', 'terminee')
    statuts_filtre = [s for s in request.GET.getlist('statut') if s in statuts_valides]
    if statuts_filtre:
        taches = [t for t in taches if t.statut in statuts_filtre] if isinstance(taches, list) \
            else taches.filter(statut__in=statuts_filtre)

    priorites_valides = ('basse', 'normale', 'haute')
    priorites_filtre = [p for p in request.GET.getlist('priorite') if p in priorites_valides]
    if priorites_filtre:
        taches = [t for t in taches if t.priorite in priorites_filtre] if isinstance(taches, list) \
            else taches.filter(priorite__in=priorites_filtre)

    date_filtre = request.GET.get('date', '').strip()
    aujourd_hui_seulement = request.GET.get('aujourdhui', '') == '1'
    if aujourd_hui_seulement:
        date_filtre = timezone.localdate().isoformat()
    if date_filtre:
        taches = [t for t in taches if t.date_realisation.isoformat() == date_filtre] if isinstance(taches, list) \
            else taches.filter(date_realisation=date_filtre)

    en_retard_seulement = request.GET.get('retard', '') == '1'
    if en_retard_seulement:
        maintenant = timezone.localtime()
        taches = [t for t in taches if t.statut != 'terminee' and maintenant >= t.datetime_fin]

    # --- TRI ---
    tri = request.GET.get('tri', 'date_asc')
    taches = list(taches)  # uniformise en liste pour trier, que ce soit déjà une liste ou un queryset

    if tri == 'date_desc':
        taches.sort(key=lambda t: (t.date_realisation, t.heure_debut), reverse=True)
    else:  # date_asc par défaut
        taches.sort(key=lambda t: (t.date_realisation, t.heure_debut))

    return render(request, 'projets/liste_tache.html', {
        'projet': projetPer,
        'taches': taches,
        'recherche': recherche,
        'statuts_filtre': statuts_filtre,
        'priorites_filtre': priorites_filtre,
        'date_filtre': date_filtre,
        'aujourd_hui_seulement': aujourd_hui_seulement,
        'en_retard_seulement': en_retard_seulement,
        'tri': tri,
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------- 
@login_required
def creer_projet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.id_user = request.user
            projet.save()
            return redirect('liste_projet')
    else:
        form = ProjetForm()
    return render(request, 'projets/formulaire.html', {
        'form': form
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
        tache.priorite = request.POST.get('priorite')
        tache.save()
        return redirect('liste_tache', id=tache.id_proj.id)

    return render(request, 'projets/modifier_tache.html', {'tache': tache})
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
    projets_utilisateur = Projet.objects.filter(id_user=request.user)

    if request.method == 'POST':
        form = NouvelleTache(request.POST)
        form.fields['id_proj'].queryset = projets_utilisateur

        if form.is_valid():
            form.save()
            return redirect('liste_projet')
    else:
        form = NouvelleTache()
        form.fields['id_proj'].queryset = projets_utilisateur

    projets_dates = {
        p.id: {'debut': p.date_debut.isoformat(), 'fin': p.date_fin.isoformat()}
        for p in projets_utilisateur
    }

    return render(request, 'projets/ajouter_tache.html', {
        'form': form,
        'projets_dates_json': json.dumps(projets_dates),
    })

@login_required
def taches_notifications_json(request):
    Tache_projet.actualiser_statuts(
        queryset=Tache_projet.objects.filter(id_proj__id_user=request.user)
    )

    taches = Tache_projet.objects.filter(
        id_proj__id_user=request.user
    ).select_related('id_proj')

    data = [{
        'id': t.id,
        'intitule': t.intitule,
        'projet': t.id_proj.intitule,
        'date_realisation': t.date_realisation.isoformat(),
        'heure_debut': t.heure_debut.strftime('%H:%M:%S'),
        'heure_fin': t.heure_fin.strftime('%H:%M:%S'),
        'statut': t.statut,
    } for t in taches]

    return JsonResponse({'taches': data})