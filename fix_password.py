import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from novatask.models import Utilisateur

MOT_DE_PASSE_PAR_DEFAUT = "novatask"

utilisateurs = Utilisateur.objects.all()
compteur = 0

for u in utilisateurs:
    u.set_password(MOT_DE_PASSE_PAR_DEFAUT)
    u.save()
    compteur += 1
    print(f"Mot de passe défini pour : {u.username}")

print(f"\n{compteur} utilisateur(s) mis à jour sur {utilisateurs.count()}.")
for u in utilisateurs:
    if u.is_superuser:
        continue
    u.set_password(MOT_DE_PASSE_PAR_DEFAUT)
    u.save()
    compteur += 1