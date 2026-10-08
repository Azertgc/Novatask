"""
Serializers de l'API NovaTask.

Un serializer DRF fait le pont entre deux mondes :
- les objets Python de l'ORM Django (Projet, Tache_projet)
- le JSON échangé sur le réseau (requêtes/réponses HTTP)

Côté lecture (GET) : objet Python -> JSON
Côté écriture (POST/PUT/PATCH) : JSON reçu -> dictionnaire de données validées
(validated_data), que les vues utilisent ensuite pour construire/mettre à jour l'objet.

C'est l'équivalent, côté API, de ce qu'un ModelForm fait côté HTML.
"""

from rest_framework import serializers
from .models import Projet, Tache_projet


class ProjetSerializer(serializers.ModelSerializer):
    # 'statut' et 'progression' sont des @property du modèle Projet,
    # pas des colonnes en base (ce sont des valeurs calculées à partir
    # des tâches liées). ModelSerializer ne détecte automatiquement que
    # les vrais champs du modèle : sans cette déclaration explicite,
    # ces deux informations n'apparaîtraient jamais dans le JSON renvoyé.
    # read_only=True : on ne doit jamais pouvoir les écraser directement
    # depuis l'API, puisqu'elles se déduisent entièrement des tâches.
    statut = serializers.CharField(read_only=True)
    progression = serializers.FloatField(read_only=True)

    class Meta:
        model = Projet
        fields = [
            'id_proj', 'intitule', 'description', 'resultat_attendu',
            'date_debut', 'date_fin', 'statut', 'progression',
        ]
        # id_user n'apparaît volontairement jamais dans 'fields' :
        # impossible de l'envoyer ou de le modifier via l'API, exactement
        # comme les formulaires HTML existants ne l'exposent pas.
        # id_proj est listé (pour être visible en lecture) mais verrouillé
        # en lecture seule ci-dessous : c'est un identifiant auto-généré.
        read_only_fields = ['id_proj']


class TacheProjetSerializer(serializers.ModelSerializer):
    # Même logique que pour Projet : est_en_retard est une @property
    # calculée (comparaison de la date/heure de fin avec maintenant),
    # pas une colonne en base. Déclarée explicitement pour apparaître
    # dans le JSON, en lecture seule car calculée automatiquement.
    est_en_retard = serializers.BooleanField(read_only=True)

    # Redéclaration explicite de ces deux champs (au lieu de laisser
    # ModelSerializer les générer automatiquement à partir du modèle).
    # Nécessaire pour deux raisons :
    #   1. allow_blank=True : accepter une chaîne vide ('') en entrée,
    #      sans quoi DRF rejette '' avec "This field may not be blank"
    #      AVANT même d'atteindre validate() ci-dessous.
    #   2. required=False / allow_null=True : rendre chacun des deux
    #      champs facultatif, puisque la règle XOR impose que l'un des
    #      deux (jamais les deux, jamais aucun) soit rempli.
    resultat_attendu = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fonctionnalite = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Par défaut, pour une ForeignKey, ModelSerializer génère un
    # PrimaryKeyRelatedField qui attend la clé primaire TECHNIQUE de
    # Django (un entier auto-incrémenté, invisible côté utilisateur).
    # Ici, le client envoie l'identifiant MÉTIER (ex: "P001"), pas cet
    # entier interne. SlugRelatedField résout ce problème : il recherche
    # l'objet Projet via son champ 'id_proj' (le "slug") plutôt que via
    # sa clé primaire technique.
    # Le queryset est volontairement vide ici (Projet.objects.none()) :
    # il est redéfini dans __init__ ci-dessous pour être restreint aux
    # projets de l'utilisateur connecté (voir le commentaire associé).
    id_proj = serializers.SlugRelatedField(
        slug_field='id_proj',
        queryset=Projet.objects.none(),
    )

    class Meta:
        model = Tache_projet
        fields = [
            'num_tache', 'id_proj', 'intitule',
            'resultat_attendu', 'fonctionnalite',
            'date_realisation', 'heure_debut', 'heure_fin',
            'priorite', 'statut', 'est_en_retard',
        ]
        # num_tache est l'identifiant auto-généré (T001, T002...) :
        # jamais modifiable depuis l'API, uniquement affiché en lecture.
        read_only_fields = ['num_tache']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le ViewSet transmet toujours 'request' dans le contexte du
        # serializer (comportement par défaut de DRF pour un ModelViewSet).
        # On s'en sert ici pour restreindre les projets proposables pour
        # 'id_proj' à ceux de l'utilisateur connecté. Sans cette
        # restriction, un utilisateur pourrait rattacher une tâche au
        # projet de quelqu'un d'autre simplement en connaissant son
        # identifiant (ex: "P003" appartenant à un autre compte).
        request = self.context.get('request')
        if request:
            self.fields['id_proj'].queryset = Projet.objects.filter(
                id_user=request.user
            )

    def validate(self, data):
        # validate() est appelé par DRF après la validation de chaque
        # champ pris individuellement, juste avant que les données ne
        # soient transmises à la vue pour sauvegarde (validated_data).
        #
        # Problème réglé ici : un champ HTML laissé vide envoie une
        # CHAÎNE VIDE ('') au serveur, jamais None/null. Si les deux
        # champs 'resultat_attendu' et 'fonctionnalite' valent '' et
        # 'Livrer le rapport' par exemple, la contrainte XOR du modèle
        # (CheckConstraint soit_a_soit_b_pas_les_deux, qui vérifie qu'un
        # des deux champs est NULL) échoue quand même : une chaîne vide
        # n'est PAS NULL pour la base de données.
        #
        # On normalise donc explicitement : toute chaîne vide devient
        # None avant d'atteindre la validation du modèle (full_clean,
        # voir api_views.py) et l'écriture en base.
        if data.get('resultat_attendu') == '':
            data['resultat_attendu'] = None
        if data.get('fonctionnalite') == '':
            data['fonctionnalite'] = None
        return data