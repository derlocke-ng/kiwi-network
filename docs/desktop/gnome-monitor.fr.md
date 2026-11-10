# gnome-monitor

gnome-monitor enregistre la disposition de vos écrans sous GNOME et permet de
passer d’une disposition enregistrée à une autre. Une disposition retient,
pour chaque écran, la résolution, la fréquence de rafraîchissement (y compris
la fréquence variable, VRR), la position et l’échelle, ainsi que l’écran
principal. gnome-monitor peut aussi **éteindre et rallumer** un seul écran, ce
qui est utile quand un autre ordinateur est branché sur le même écran et en a
besoin. Il se compose d’un outil en ligne de commande et d’un panneau GTK4.

- Dépôt : [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Dernière version : **v0.3.2**. Il figure dans le [catalogue Kiwi](catalogs.md), en portée utilisateur.

Cas typique : un bureau avec deux ordinateurs et trois écrans. Quand l’autre
ordinateur a lui aussi besoin de l’écran 4K, vous éteignez cet écran sur cet
ordinateur-ci et vous travaillez sur les écrans restants. Quand vous le
rallumez, il retrouve la position et le mode qu’il avait avant, et il redevient
l’écran principal s’il l’était. Vous pouvez aussi enregistrer chaque
disposition une fois pour toutes sous forme de profil, et l’appliquer en un
clic ou par un raccourci clavier.

```bash
kiwi install gnome-monitor          # ou ./install.sh
```

```bash
gnome-monitor show                  # ce qui est branché, allumé, où, dans quel mode, avec un plan
gnome-monitor save desk             # la disposition actuelle, sous le profil « desk »
gnome-monitor list                  # les profils ; * marque celui qui est utilisé
gnome-monitor apply desk
gnome-monitor off rog               # un écran par connecteur, partie de son nom, numéro ou « main »
gnome-monitor on rog
gnome-monitor only odyssey hp       # exactement ceux-ci allumés, tous les autres éteints
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # un raccourci GNOME qui applique « desk »
gnome-monitor-panel                 # « Gnome Monitor » dans la grille d’applications
```

gnome-monitor utilise l’API D-Bus `DisplayConfig` de Mutter, le gestionnaire de
fenêtres de GNOME. Il fonctionne sous Wayland et sous X11, et n’a besoin ni des
droits root ni d’une extension GNOME. Les profils sont des fichiers JSON dans
`~/.config/gnome-monitor/profiles/`. Un écran est reconnu à son EDID, les
données d’identification qu’il transmet sur lui-même. Un changement de
disposition est appliqué sans boîte de dialogue de confirmation. Si vous
préférez, vous pouvez activer une option qui vous demande si vous voulez
garder la nouvelle disposition. La disposition est rétablie à l’ouverture de
session. Avec `--dry-run`, gnome-monitor demande à Mutter si une disposition
est valide, sans l’appliquer.
