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

        # authenticate() vérifie les identifiants contre TOUS les backends
        # listés dans AUTHENTICATION_BACKENDS (settings.py), y compris
        # CaseInsensitiveModelBackend : retourne l'utilisateur si un des
        # backends valide la combinaison username/password, sinon None.
        utilisateur = authenticate(
            request,
            username=username,
            password=password
        )
        if utilisateur is not None:
            # login() : crée la session (cookie sessionid), sans préciser
            # de backend ici car authenticate() l'a déjà déterminé et l'a
            # attaché à l'objet utilisateur (utilisateur.backend).
            login(request, utilisateur)
            return redirect('liste_projet')
        return render(request, 'utilisateurs/connexion.html',{'erreur': "Nom d'utilisateur ou mot de passe incorect."})
    return render(request, 'utilisateurs/connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion')

from django.contrib.auth import login

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            # Connexion automatique juste après l'inscription, pour éviter
            # à l'utilisateur de devoir se reconnecter manuellement.
            # backend précisé explicitement ici (contrairement à connexion()
            # ci-dessus) car il n'y a pas eu d'appel à authenticate() avant
            # — Django ne sait donc pas quel backend utiliser parmi les
            # plusieurs configurés, et lève une erreur sans cette précision.
            login(request, utilisateur, backend='novatask.backends.CaseInsensitiveModelBackend')
            return redirect('liste_projet')
    else:
        form = InscriptionForm()
    return render(request, 'utilisateurs/inscription.html', {'form': form})
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
@login_required
def liste_projet(request):
    # Avant d'afficher la liste, on actualise les statuts des tâches de
    # l'utilisateur (a_faire -> en_cours si l'heure de début est atteinte),
    # pour que la page reflète toujours l'état réel au moment du chargement,
    # sans attendre le passage de la commande verifier_taches (chapitre 18).
    Tache_projet.actualiser_statuts(
        queryset=Tache_projet.objects.filter(id_proj__id_user=request.user)
    )
    # Scope de sécurité : uniquement les projets de l'utilisateur connecté.
    projets = Projet.objects.filter(id_user=request.user)

    # Recherche par intitulé, insensible aux accents (normaliser() vient
    # de services.py). Transforme ici 'projets' d'un queryset Django en
    # LISTE Python simple (comparaison via normaliser(), impossible à
    # exprimer directement en SQL).
    recherche = request.GET.get('q', '').strip()
    if recherche:
        terme = normaliser(recherche)
        projets = [p for p in projets if terme in normaliser(p.intitule)]

    # Filtre par statut (a_faire/en_cours/termine), une valeur à la fois.
    # statut étant une @property calculée (pas une colonne), ce filtre ne
    # peut pas être fait en SQL (.filter(statut=...)) et passe forcément
    # par une liste Python, d'où le test isinstance ci-dessous : il gère
    # le cas où 'projets' est encore un queryset (si la recherche
    # ci-dessus n'a pas transformé projets en liste) OU déjà une liste
    # (si elle l'a fait) — dans les deux cas, le résultat est filtré de
    # la même façon en Python, par compréhension de liste.
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
    # get_object_or_404 avec id_user=request.user dans le filtre :
    # vérifie en une seule requête que le projet existe ET appartient à
    # l'utilisateur connecté — sinon 404 (jamais de 403 qui révélerait
    # qu'un projet existe mais appartient à quelqu'un d'autre).
    projetPer = get_object_or_404(Projet, id=id, id_user=request.user)
    Tache_projet.actualiser_statuts(queryset=projetPer.taches.all())
    taches = Tache_projet.objects.filter(id_proj=projetPer)

    # Recherche par intitulé, insensible aux accents — même logique que
    # pour liste_projet ci-dessus, transforme 'taches' en liste Python.
    recherche = request.GET.get('q', '').strip()
    if recherche:
        terme = normaliser(recherche)
        taches = [t for t in taches if terme in normaliser(t.intitule)]

    # Filtres MULTIPLES et cumulables sur le statut (contrairement au
    # statut unique de liste_projet ci-dessus) : getlist() récupère
    # toutes les valeurs répétées dans l'URL (?statut=a&statut=b), et
    # statuts_valides filtre les valeurs reçues contre la liste blanche
    # autorisée, pour ignorer toute valeur invalide/inattendue dans l'URL.
    statuts_valides = ('a_faire', 'en_cours', 'terminee')
    statuts_filtre = [s for s in request.GET.getlist('statut') if s in statuts_valides]
    if statuts_filtre:
        # Ce champ-ci (statut) EST une vraie colonne en base (contrairement
        # à Projet.statut qui est calculé) : le filtre peut donc se faire
        # soit en Python (si 'taches' est déjà une liste, à cause de la
        # recherche ci-dessus) soit en SQL (.filter(statut__in=...), plus
        # efficace, si 'taches' est encore un queryset) — d'où le test
        # isinstance qui choisit la bonne méthode selon le cas.
        taches = [t for t in taches if t.statut in statuts_filtre] if isinstance(taches, list) \
            else taches.filter(statut__in=statuts_filtre)

    # Même principe pour la priorité : liste blanche + filtre cumulable.
    priorites_valides = ('basse', 'normale', 'haute')
    priorites_filtre = [p for p in request.GET.getlist('priorite') if p in priorites_valides]
    if priorites_filtre:
        taches = [t for t in taches if t.priorite in priorites_filtre] if isinstance(taches, list) \
            else taches.filter(priorite__in=priorites_filtre)

    # Filtre par date précise, ou raccourci "aujourd'hui" qui écrase toute
    # date_filtre déjà présente dans l'URL par la date du jour.
    date_filtre = request.GET.get('date', '').strip()
    aujourd_hui_seulement = request.GET.get('aujourdhui', '') == '1'
    if aujourd_hui_seulement:
        date_filtre = timezone.localdate().isoformat()
    if date_filtre:
        taches = [t for t in taches if t.date_realisation.isoformat() == date_filtre] if isinstance(taches, list) \
            else taches.filter(date_realisation=date_filtre)

    # Filtre "en retard" : passe nécessairement par une liste Python,
    # car est_en_retard est une @property calculée, pas une colonne SQL.
    en_retard_seulement = request.GET.get('retard', '') == '1'
    if en_retard_seulement:
        maintenant = timezone.localtime()
        taches = [t for t in taches if t.statut != 'terminee' and maintenant >= t.datetime_fin]

    # ======================================================
    # TRI (19.7 + 19.8)
    # ======================================================
    # Ordre de poids pour la priorité : plus le nombre est élevé, plus
    # la priorité est importante. Nécessaire car un tri alphabétique
    # classerait "haute" avant "normale" à tort.
    ORDRE_PRIORITE = {'basse': 0, 'normale': 1, 'haute': 2}

    tri = request.GET.get('tri', 'date_asc')
    # À ce stade, on force définitivement 'taches' en liste Python (même
    # si aucun filtre précédent ne l'avait déjà fait), car .sort() avec
    # une key= personnalisée (comme ORDRE_PRIORITE ci-dessous) n'existe
    # que sur les listes, pas sur les querysets Django.
    taches = list(taches)

    if tri == 'date_desc':
        taches.sort(key=lambda t: (t.date_realisation, t.heure_debut), reverse=True)
    elif tri == 'priorite_desc':
        # Haute priorité en premier
        taches.sort(key=lambda t: ORDRE_PRIORITE.get(t.priorite, 0), reverse=True)
    elif tri == 'priorite_asc':
        # Basse priorité en premier
        taches.sort(key=lambda t: ORDRE_PRIORITE.get(t.priorite, 0))
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
        # Listes utilisées côté template pour générer les cases à cocher
        # des filtres, avec le couple (valeur technique, libellé affiché).
        'statuts_disponibles': [('a_faire', 'À faire'), ('en_cours', 'En cours'), ('terminee', 'Terminée')],
        'priorites_disponibles': [('haute', 'Haute'), ('normale', 'Normale'), ('basse', 'Basse')],
    })
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
@login_required
def creer_projet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            # commit=False : construit l'objet Projet en mémoire SANS
            # l'écrire en base, pour pouvoir assigner id_user manuellement
            # avant la sauvegarde définitive. id_user n'est volontairement
            # pas un champ du formulaire (ProjetForm) : l'utilisateur ne
            # choisit jamais à qui appartient le projet, c'est automatique.
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
    # id_proj__id_user=request.user dans le filtre : garantit qu'on ne
    # peut récupérer (et donc modifier) que les tâches d'un projet
    # appartenant à l'utilisateur connecté.
    tache = get_object_or_404(
        Tache_projet,
        id=id,
        id_proj__id_user=request.user
    )

    if request.method == "POST":
        # Affectation manuelle champ par champ depuis request.POST (plutôt
        # qu'un ModelForm) : chaque champ modifiable doit être listé
        # explicitement ici, sinon il reste inchangé après l'enregistrement
        # — c'est exactement ce qui s'était produit pour 'priorite' avant
        # correction (champ ajouté au modèle mais oublié ici, provoquant
        # une erreur de contrainte NOT NULL).
        tache.intitule = request.POST.get('intitule')
        tache.date_realisation = request.POST.get('date_realisation')
        tache.heure_debut = request.POST.get('heure_debut')
        tache.heure_fin = request.POST.get('heure_fin')
        tache.resultat_attendu = request.POST.get('resultat_attendu')
        tache.statut = request.POST.get('statut')
        # Valeur par défaut = tache.priorite (valeur actuelle) si la clé
        # 'priorite' est absente du POST, pour éviter d'écraser le champ
        # par None si jamais le formulaire ne l'envoie pas.
        tache.priorite = request.POST.get('priorite', tache.priorite)
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
        # Suppression effective uniquement sur confirmation POST (le GET
        # ci-dessous affiche juste la page de confirmation, sans rien
        # supprimer) — évite qu'un simple clic sur un lien, un crawler,
        # ou un rechargement de page ne déclenche une suppression.
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
    # Restreint les projets proposables dans le formulaire aux projets
    # de l'utilisateur connecté, dans les deux branches (POST et GET) —
    # sans ça, le menu déroulant du formulaire listerait TOUS les projets
    # de TOUS les utilisateurs par défaut (comportement standard d'un
    # ModelChoiceField sans queryset restreint).
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

    # Dictionnaire {id_projet: {debut, fin}} transmis au template sous
    # forme de JSON, pour que le JavaScript (Flatpickr) puisse restreindre
    # dynamiquement la plage de dates sélectionnable selon le projet
    # choisi dans le formulaire, sans rechargement de page.
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
    # Endpoint JSON interrogé par notifications.js (polling toutes les
    # 30 secondes, chapitre 17) — pas une vue HTML classique, elle ne
    # renvoie jamais de template, uniquement des données.
    Tache_projet.actualiser_statuts(
        queryset=Tache_projet.objects.filter(id_proj__id_user=request.user)
    )

    # select_related('id_proj') : précharge le projet lié en une seule
    # requête SQL (JOIN), au lieu d'une requête séparée par tâche pour
    # accéder à t.id_proj.intitule dans la boucle ci-dessous (évite le
    # problème classique des "requêtes N+1").
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