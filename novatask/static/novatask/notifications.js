(function() {
    const POLL_INTERVAL = 30000;
    const STORAGE_KEY = 'novatask_notifications_state';

    // ---------- État persistant (survit au rechargement de page) ----------
    function chargerEtat() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { affichees: [], fermees: [] };
        } catch {
            return { affichees: [], fermees: [] };
        }
    }
    function sauverEtat(etat) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(etat));
    }

    let etat = chargerEtat();
    let file = [];          // tâches déclenchées en attente d'affichage (17.5)
    let tacheActive = null; // tâche actuellement affichée
    let minuteur = null;

    // ---------- 17.6 — Permission navigateur ----------
    function demanderPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    // ---------- 17.7 — Web Notifications API ----------
    function notifierNavigateur(tache) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(`Tâche en cours : ${tache.intitule}`, {
                body: `${tache.projet} — jusqu'à ${tache.heure_fin.slice(0, 5)}`,
                tag: `tache-${tache.id}`,
            });
        }
    }

    // ---------- Carte NovaTask (contrôle total : 17.3 + 17.4) ----------
    function creerCarte() {
        if (document.getElementById('novatask-notif-card')) return;

        const carte = document.createElement('div');
        carte.id = 'novatask-notif-card';
        carte.style.cssText = `
            position: fixed; bottom: 20px; right: 20px; z-index: 9999;
            width: 320px; max-width: calc(100vw - 40px);
            background: #FAFAF8; border: 1px solid #1C1C1A;
            font-family: 'IBM Plex Sans', sans-serif;
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
            display: none;
        `;
        carte.innerHTML = `
            <div style="padding:14px 16px;border-bottom:1px solid #DEDEDA;display:flex;align-items:center;gap:8px;">
                <span style="width:8px;height:8px;background:#B8862E;flex-shrink:0;"></span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#8A8A82;">
                    Tâche en cours
                </span>
            </div>
            <div style="padding:14px 16px;">
                <p id="novatask-notif-projet" style="font-family:'IBM Plex Mono',monospace;font-size:11px;text-transform:uppercase;color:#8A8A82;margin:0 0 4px;"></p>
                <p id="novatask-notif-titre" style="font-weight:600;font-size:15px;color:#1C1C1A;margin:0 0 8px;"></p>
                <p id="novatask-notif-horaire" style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#8A8A82;margin:0;"></p>
            </div>
            <div style="padding:12px 16px 16px;">
                <button id="novatask-notif-fermer" disabled style="
                    width:100%;font-family:'IBM Plex Mono',monospace;font-size:11px;
                    text-transform:uppercase;letter-spacing:0.05em;padding:10px;
                    border:1px solid #DEDEDA;background:#EAEAE5;color:#B0B0A8;
                    cursor:not-allowed;transition:all 0.15s;">
                    Disponible à l'heure de fin
                </button>
            </div>
        `;
        document.body.appendChild(carte);
        document.getElementById('novatask-notif-fermer').addEventListener('click', fermerNotificationActive);
    }

    function afficherNotification(tache) {
        tacheActive = tache;
        creerCarte();

        const carte = document.getElementById('novatask-notif-card');
        document.getElementById('novatask-notif-projet').textContent = tache.projet;
        document.getElementById('novatask-notif-titre').textContent = tache.intitule;
        document.getElementById('novatask-notif-horaire').textContent = `Jusqu'à ${tache.heure_fin.slice(0, 5)}`;
        carte.style.display = 'block';

        notifierNavigateur(tache);

        if (!etat.affichees.includes(tache.id)) {
            etat.affichees.push(tache.id);
            sauverEtat(etat);
        }

        surveillerHeureFin(tache);
    }

    // ---------- 17.4 — Bouton Fermer conditionnel à l'heure de fin ----------
    function surveillerHeureFin(tache) {
        clearInterval(minuteur);

        function verifier() {
            const maintenant = new Date();
            const fin = new Date(`${tache.date_realisation}T${tache.heure_fin}`);
            const bouton = document.getElementById('novatask-notif-fermer');

            if (maintenant >= fin) {
                bouton.disabled = false;
                bouton.textContent = 'Fermer';
                bouton.style.background = '#1C1C1A';
                bouton.style.color = '#fff';
                bouton.style.cursor = 'pointer';
                clearInterval(minuteur);
            }
        }

        verifier();
        minuteur = setInterval(verifier, 1000);
    }

    function fermerNotificationActive() {
        if (!tacheActive) return;

        const maintenant = new Date();
        const fin = new Date(`${tacheActive.date_realisation}T${tacheActive.heure_fin}`);
        if (maintenant < fin) return; // sécurité : impossible de fermer avant l'heure de fin

        if (!etat.fermees.includes(tacheActive.id)) {
            etat.fermees.push(tacheActive.id);
            sauverEtat(etat);
        }

        document.getElementById('novatask-notif-card').style.display = 'none';
        clearInterval(minuteur);
        tacheActive = null;

        afficherProchaineNotification();
    }

    // ---------- 17.5 — Enchaînement séquentiel ----------
    function afficherProchaineNotification() {
        if (tacheActive || file.length === 0) return;
        const suivante = file.shift();
        afficherNotification(suivante);
    }

    // ---------- 17.2 — Boucle de détection ----------
    async function verifierTaches() {
        try {
            const reponse = await fetch('/api/taches/notifications/');
            const { taches } = await reponse.json();

            for (const tache of taches) {
                if (tache.statut !== 'en_cours') continue;
                if (etat.fermees.includes(tache.id)) continue;
                if (tacheActive && tacheActive.id === tache.id) continue;
                if (file.some(t => t.id === tache.id)) continue;

                file.push(tache);
            }

            afficherProchaineNotification();
        } catch (e) {
            console.error('Erreur de vérification des tâches :', e);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        demanderPermission();
        verifierTaches();
        setInterval(verifierTaches, POLL_INTERVAL);
    });
})();