"""
Vues de l'API NovaTask, basées sur les ModelViewSet de DRF.

Un ModelViewSet regroupe automatiquement les 5 actions CRUD (liste, détail,
création, modification, suppression) à partir d'un seul bloc de code, en
s'appuyant sur le serializer associé (serializer_class) et le queryset de
base (get_queryset). Pas besoin d'écrire une vue séparée par action comme
en Django classique.
"""

from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Projet, Tache_projet
from .serializers import ProjetSerializer, TacheProjetSerializer
from .services import normaliser


class ProjetViewSet(viewsets.ModelViewSet):
    serializer_class = ProjetSerializer
    # Filet de sécurité : accès refusé à tout utilisateur non connecté,
    # même si on oubliait de le préciser ailleurs (settings.py le fait
    # déjà par défaut, cette ligne le rend explicite pour cette vue).
    permission_classes = [permissions.IsAuthenticated]
    # Par défaut, DRF identifie un objet dans l'URL via sa clé primaire
    # technique (ex: /api/projets/1/). On préfère utiliser l'identifiant
    # métier généré automatiquement (P001, P002...), cohérent avec le
    # reste de l'application : /api/projets/P001/
    lookup_field = 'id_proj'

    def get_queryset(self):
        # Appelé par DRF avant CHAQUE requête (liste, détail, modification,
        # suppression), pour déterminer quels objets l'utilisateur a le
        # droit de voir/toucher. En filtrant par id_user=request.user, on
        # reproduit exactement la règle d'isolation des données déjà en
        # place côté vues HTML : impossible de voir ou modifier les
        # projets d'un autre utilisateur, y compris via l'API.
        #
        # order_by('id_proj') : nécessaire pour un résultat stable avec
        # la pagination (voir settings.py). Sans tri explicite, Django ne
        # garantit pas le même ordre entre deux requêtes, ce qui peut
        # faire apparaître/disparaître des éléments d'une page à l'autre.
        return Projet.objects.filter(id_user=self.request.user).order_by('id_proj')

    def perform_create(self, serializer):
        # Hook appelé par DRF juste après la validation du serializer,
        # au moment de la création (POST). On y rattache automatiquement
        # le projet à l'utilisateur connecté (id_user), sans jamais lui
        # laisser le choix via l'API (id_user n'est pas dans les champs
        # exposés par le serializer).
        projet = serializer.save(id_user=self.request.user)
        # full_clean() n'est JAMAIS appelé automatiquement, ni par .save()
        # sur un modèle Django, ni par DRF. Il faut l'appeler à la main
        # pour déclencher le clean() personnalisé du modèle (vérification
        # des dates : date_debut pas dans le passé, date_fin >= date_debut).
        try:
            projet.full_clean()
        except DjangoValidationError as e:
            # Le projet est déjà écrit en base à ce stade (serializer.save()
            # l'a fait avant full_clean()). S'il est invalide, on le
            # supprime immédiatement pour ne pas laisser une donnée
            # incohérente trainer, puis on relance une erreur DRF (et non
            # Django) : c'est elle que DRF sait convertir automatiquement
            # en réponse HTTP 400 avec le détail en JSON.
            projet.delete()
            raise ValidationError(e.message_dict)

    def perform_update(self, serializer):
        projet = serializer.save()
        try:
            projet.full_clean()
        except DjangoValidationError as e:
            # Pas de .delete() ici : contrairement à la création, l'objet
            # existait déjà avant la modification — on ne veut pas le
            # supprimer, juste refuser la modification invalide.
            raise ValidationError(e.message_dict)


class TacheProjetViewSet(viewsets.ModelViewSet):
    serializer_class = TacheProjetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'num_tache'

    def get_queryset(self):
        # Même principe d'isolation que pour les projets, mais la relation
        # est indirecte : une tâche appartient à un projet, qui appartient
        # à un utilisateur. id_proj__id_user traverse cette relation en
        # une seule requête (notation Django classique à double underscore).
        qs = Tache_projet.objects.filter(id_proj__id_user=self.request.user)

        # --- Filtres optionnels, pilotés par les paramètres de l'URL ---
        # Reproduisent côté API les mêmes filtres que la page HTML de
        # recherche/filtre (chapitre 19), combinables librement entre eux.

        # Recherche insensible aux accents, réutilisant la fonction
        # normaliser() déjà utilisée côté vues HTML (services.py).
        # Note : ce filtre charge les tâches en Python pour comparer les
        # versions normalisées (une recherche accent-insensible n'est pas
        # directement exprimable en SQL standard), puis ne garde que les
        # identifiants correspondants.
        recherche = self.request.query_params.get('recherche')
        if recherche:
            recherche_norm = normaliser(recherche)
            ids = [
                t.num_tache for t in qs
                if recherche_norm in normaliser(t.intitule)
            ]
            qs = qs.filter(num_tache__in=ids)

        # getlist() (et non get()) car ces filtres sont répétables dans
        # l'URL : ?statut=a_faire&statut=en_cours sélectionne les deux.
        statuts = self.request.query_params.getlist('statut')
        if statuts:
            qs = qs.filter(statut__in=statuts)

        priorites = self.request.query_params.getlist('priorite')
        if priorites:
            qs = qs.filter(priorite__in=priorites)

        tri = self.request.query_params.get('tri')
        if tri == 'date_asc':
            qs = qs.order_by('date_realisation', 'heure_debut')
        elif tri == 'date_desc':
            qs = qs.order_by('-date_realisation', '-heure_debut')
        elif tri == 'priorite_asc':
            qs = qs.order_by('priorite')
        elif tri == 'priorite_desc':
            qs = qs.order_by('-priorite')

        return qs

    def perform_create(self, serializer):
        # IMPORTANT : ici on NE fait PAS serializer.save() directement.
        #
        # Raison : la contrainte XOR (CheckConstraint soit_a_soit_b_pas_les_deux)
        # est définie au niveau de la base de données elle-même. Si on
        # appelait serializer.save() (qui écrit immédiatement en base)
        # avec des données invalides, SQLite refuserait l'INSERT à
        # l'intérieur même de save() — avant que Python n'ait la main pour
        # lever une exception propre. Résultat : une erreur 500 brute et
        # incompréhensible pour le client, au lieu d'un 400 avec le détail.
        #
        # On inverse donc l'ordre : construire l'objet EN MÉMOIRE (sans
        # toucher la base), le valider avec full_clean(), et ne l'écrire
        # qu'une fois certain qu'il est valide.
        tache = Tache_projet(**serializer.validated_data)
        try:
            tache.full_clean()
        except DjangoValidationError as e:
            # Rien n'a été écrit en base à ce stade : pas besoin de nettoyer,
            # juste renvoyer l'erreur.
            raise ValidationError(e.message_dict)
        tache.save()
        # On indique au serializer quel objet a finalement été créé, pour
        # que la réponse JSON renvoyée au client reflète bien la tâche
        # réellement enregistrée (avec son num_tache auto-généré par
        # exemple, assigné dans la méthode save() du modèle).
        serializer.instance = tache

    def perform_update(self, serializer):
        # Même principe que perform_create : on applique les champs
        # modifiés sur l'instance existante EN MÉMOIRE, on valide, et on
        # ne sauvegarde qu'ensuite.
        for champ, valeur in serializer.validated_data.items():
            setattr(serializer.instance, champ, valeur)
        try:
            serializer.instance.full_clean()
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)
        serializer.instance.save()