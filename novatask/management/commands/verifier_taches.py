from django.core.management.base import BaseCommand
from django.utils import timezone

from novatask.models import Tache_projet
from novatask.services import (
    verifier_echeances,
    taches_proches_echeance_non_notifiees,
    marquer_rappel_envoye,
)


class Command(BaseCommand):
    help = "Vérifie automatiquement les échéances des tâches et actualise leurs statuts."

    def handle(self, *args, **options):
        maintenant = timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')
        self.stdout.write(f"[{maintenant}] Vérification des échéances...")

        # 1. Actualisation des statuts (a_faire -> en_cours), logique du chapitre 17
        mises_a_jour = Tache_projet.actualiser_statuts()
        if mises_a_jour:
            self.stdout.write(self.style.SUCCESS(
                f"  → {len(mises_a_jour)} tâche(s) passée(s) à 'en_cours'"
            ))

        # 2. Classification des échéances (18.3)
        resultats = verifier_echeances()
        self.stdout.write(
            f"  → À venir : {len(resultats['a_venir'])} | "
            f"En cours : {len(resultats['en_cours'])} | "
            f"Échéance dépassée : {len(resultats['echeance_depassee'])}"
        )

        # 3. Tâches proches de l'échéance, non encore notifiées (18.4 + 18.5)
        proches = taches_proches_echeance_non_notifiees()
        if proches:
            for tache in proches:
                self.stdout.write(self.style.WARNING(
                    f"  ⏰ Rappel : « {tache.intitule} » commence à "
                    f"{tache.heure_debut.strftime('%H:%M')}"
                ))
            marquer_rappel_envoye(proches)

        self.stdout.write(self.style.SUCCESS("Vérification terminée."))