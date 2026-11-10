# gnome-monitor

Enregistrer et changer de disposition d’écrans sous GNOME (résolution, fréquence de
rafraîchissement avec VRR, position, échelle et écran principal pour chaque
moniteur), et **éteindre et rallumer** des moniteurs un par un quand un autre
ordinateur les utilise. Une CLI plus un panneau GTK4.

- Dépôt : [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Dernière version : **v0.3.2**. Elle figure dans le [catalogue Kiwi](catalogs.md), portée utilisateur.

Deux ordinateurs, trois écrans, un bureau. Quand l’autre machine a aussi besoin de
l’écran 4K, éteignez-le ici, travaillez, puis rallumez-le. Il revient là où il
était, dans le mode qu’il avait, comme écran principal s’il l’était. Ou bien
enregistrez chaque agencement une fois et appliquez-le d’un clic ou d’un raccourci
clavier.

```bash
kiwi install gnome-monitor          # ou ./install.sh
```

```bash
gnome-monitor show                  # ce qui est branché, allumé, où, dans quel mode, avec un plan
gnome-monitor save desk             # the current layout as profile "desk"
gnome-monitor list                  # profils ; * marque celui en cours
gnome-monitor apply desk
gnome-monitor off rog               # a screen by connector, part of its name, number or "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exactement ceux-là allumés, tous les autres éteints
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # a GNOME shortcut that applies "desk"
gnome-monitor-panel                 # "Gnome Monitor" in the app grid
```

Il dialogue avec l’API D-Bus `DisplayConfig` de Mutter, sous Wayland et X11, sans
root et sans extension. Les profils sont en JSON dans
`~/.config/gnome-monitor/profiles/`, et les moniteurs sont reconnus par leur EDID.
Les changements s’appliquent sans bruit (ou demandent s’il faut les garder, si vous
le souhaitez), et la disposition est restaurée à la connexion. `--dry-run` demande à
Mutter si une disposition est valide sans l’appliquer.
