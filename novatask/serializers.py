from rest_framework import serializers
from .models import Projet, Tache_projet


class ProjetSerializer(serializers.ModelSerializer):
    statut = serializers.CharField(read_only=True)
    progression = serializers.FloatField(read_only=True)

    class Meta:
        model = Projet
        fields = [
            'id_proj', 'intitule', 'description', 'resultat_attendu',
            'date_debut', 'date_fin', 'statut', 'progression',
        ]
        read_only_fields = ['id_proj']

class TacheProjetSerializer(serializers.ModelSerializer):
    est_en_retard = serializers.BooleanField(read_only=True)
    resultat_attendu = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fonctionnalite = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
        read_only_fields = ['num_tache']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            self.fields['id_proj'].queryset = Projet.objects.filter(
                id_user=request.user
            )

    def validate(self, data):
        if data.get('resultat_attendu') == '':
            data['resultat_attendu'] = None
        if data.get('fonctionnalite') == '':
            data['fonctionnalite'] = None
        return data