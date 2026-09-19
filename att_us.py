import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from novatask.models import Projet, Utilisateur


# Récupérer les utilisateurs existants
utilisateurs = list(Utilisateur.objects.all())

if not utilisateurs:
    print("Aucun utilisateur trouvé.")
    exit()

# Récupérer tous les projets
projets = Projet.objects.all()

# Attribuer un utilisateur aléatoire à chaque projet
for projet in projets:
    projet.id_user = random.choice(utilisateurs)
    projet.save()

print(f"{projets.count()} projet(s) ont été attribués aléatoirement.")