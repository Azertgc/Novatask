from rest_framework import serializers
from .models import Tache_projet

class TacheProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tache_projet
        fields = [
            'id',
            'intitule',
            'description',
            'date_realisation',
            'heure_debut',
            'heure_fin',
            'degre_importance',
            'statut',
            'id_proj',
        ]