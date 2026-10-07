from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Projet, Tache_projet
from .serializers import ProjetSerializer, TacheProjetSerializer
from .services import normaliser


class ProjetViewSet(viewsets.ModelViewSet):
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id_proj'

    def get_queryset(self):
        return Projet.objects.filter(id_user=self.request.user).order_by('id_proj')

    def perform_create(self, serializer):
        projet = serializer.save(id_user=self.request.user)
        try:
            projet.full_clean()
        except DjangoValidationError as e:
            projet.delete()
            raise ValidationError(e.message_dict)

    def perform_update(self, serializer):
        projet = serializer.save()
        try:
            projet.full_clean()
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)


class TacheProjetViewSet(viewsets.ModelViewSet):
    serializer_class = TacheProjetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'num_tache'

    def get_queryset(self):
        qs = Tache_projet.objects.filter(id_proj__id_user=self.request.user)

        recherche = self.request.query_params.get('recherche')
        if recherche:
            recherche_norm = normaliser(recherche)
            ids = [
                t.num_tache for t in qs
                if recherche_norm in normaliser(t.intitule)
            ]
            qs = qs.filter(num_tache__in=ids)

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
        tache = Tache_projet(**serializer.validated_data)
        try:
            tache.full_clean()
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)
        tache.save()
        serializer.instance = tache

    def perform_update(self, serializer):
        for champ, valeur in serializer.validated_data.items():
            setattr(serializer.instance, champ, valeur)
        try:
            serializer.instance.full_clean()
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)
        serializer.instance.save()