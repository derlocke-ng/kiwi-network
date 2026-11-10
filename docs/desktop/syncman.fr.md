# syncman

Synchronisation bidirectionnelle de dossiers, par paires, pour Linux. Elle a été
conçue pour les sauvegardes de jeux et fonctionne pour n’importe quels dossiers.
**rsync est la seule dépendance** (inotify-tools est facultatif), et elle tourne
uniquement dans votre portée utilisateur.

- Dépôt : [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Dernière version : **v0.4.1**. Elle figure dans le [catalogue Kiwi](catalogs.md), portée utilisateur.

Un **job** est un simple fichier texte avec une paire par ligne. Il n’y a pas de
YAML ni de guillemets, et les espaces dans les chemins fonctionnent tels quels :

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Chaque job tourne comme un service utilisateur systemd, `syncjob@<name>.service`.
Tous les `INTERVAL` (30 secondes par défaut), il lance `rsync -a --update` dans les
deux sens : le fichier le plus récent l’emporte, et **rien n’est jamais
supprimé**. Avec `inotifywait` installé, les changements se synchronisent
immédiatement.

```bash
kiwi install syncman            # ou ./install.sh
syncman add game-saves          # créer et modifier un job
syncman start game-saves        # un service en arrière-plan qui survit aux redémarrages
syncman list                    # les jobs et l’état de leur service
syncman sync all                # une seule fois, sans service
syncman stop all
syncman log game-saves
syncman-panel                   # panneau GTK4 : un interrupteur par job, des boutons de synchronisation immédiate
```

Les réglages se trouvent dans `~/.config/syncman/syncman.conf` (`INTERVAL`, et en
option `JOBS_DIR`). Une désinstallation conserve vos jobs, sauf si vous passez
`--purge`.
