# syncman

syncman synchronise des paires de dossiers sur une machine Linux, dans les deux
sens. Quel que soit le dossier de la paire dans lequel un fichier apparaît ou
change, ce fichier est copié dans l’autre. syncman a été écrit pour les
parties enregistrées des jeux, mais il fonctionne pour n’importe quels dossiers. **rsync
est sa seule dépendance**, et inotify-tools est facultatif. syncman s’installe
et tourne uniquement dans votre portée utilisateur, c’est-à-dire pour votre
propre compte.

- Dépôt : [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Dernière version : **v0.4.1**. Il figure dans le [catalogue Kiwi](catalogs.md), en portée utilisateur.

Vous décrivez ce qu’il faut synchroniser dans une **tâche** (job). Une tâche est
un simple fichier texte avec une paire de dossiers par ligne. Le format n’est
pas du YAML et ne demande pas de guillemets : vous pouvez écrire tel quel un
chemin qui contient des espaces.

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Chaque tâche tourne comme un service utilisateur systemd nommé
`syncjob@<name>.service`. À chaque `INTERVAL`, 30 secondes par défaut, le
service lance `rsync -a --update` dans les deux sens. Quand un fichier existe
des deux côtés, le plus récent remplace le plus ancien, et **rien n’est jamais
supprimé**. Si `inotifywait` est installé, les modifications sont
synchronisées dès qu’elles se produisent.

```bash
kiwi install syncman            # ou ./install.sh
syncman add game-saves          # créer et modifier une tâche
syncman start game-saves        # un service en arrière-plan qui survit aux redémarrages
syncman list                    # les tâches et l’état de leur service
syncman sync all                # une seule fois, sans service
syncman stop all
syncman log game-saves
syncman-panel                   # panneau GTK4 : un interrupteur par tâche, des boutons pour synchroniser tout de suite
```

Les réglages se trouvent dans `~/.config/syncman/syncman.conf`. Ce fichier
définit `INTERVAL` et, si vous le souhaitez, `JOBS_DIR`. Quand vous
désinstallez syncman, vos tâches sont conservées, sauf si vous passez
`--purge`.
