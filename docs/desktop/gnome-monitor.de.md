# gnome-monitor

Bildschirm-Layouts unter GNOME speichern und wechseln (Auflösung, Bildwiederholrate
mit VRR, Position, Skalierung und Hauptbildschirm pro Monitor) und einzelne Monitore
**aus- und einschalten**, wenn ein anderer Computer sie nutzt. Eine CLI plus ein
GTK4-Panel.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Aktuelles Release: **v0.3.2**. Es steht im [Kiwi-Katalog](catalogs.md), Benutzerbereich.

Zwei Computer, drei Bildschirme, ein Schreibtisch. Wenn die andere Maschine den
4K-Bildschirm auch braucht, schaltest du ihn hier aus, arbeitest und schaltest ihn
wieder ein. Er kommt dorthin zurück, wo er war, im Modus, den er hatte, als
Hauptbildschirm, falls er einer war. Oder du speicherst jede Anordnung einmal und
wendest sie mit einem Klick oder einem Tastenkürzel an.

```bash
kiwi install gnome-monitor          # oder ./install.sh
```

```bash
gnome-monitor show                  # what is connected, on, where, at what mode, with a map
gnome-monitor save desk             # the current layout as profile "desk"
gnome-monitor list                  # profiles; * marks the one in use
gnome-monitor apply desk
gnome-monitor off rog               # a screen by connector, part of its name, number or "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exactly these on, every other off
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # a GNOME shortcut that applies "desk"
gnome-monitor-panel                 # "Gnome Monitor" in the app grid
```

Es spricht mit Mutters D-Bus-API `DisplayConfig`, unter Wayland und X11, ohne Root
und ohne Erweiterung. Profile sind JSON in `~/.config/gnome-monitor/profiles/`, und
Monitore werden über ihre EDID erkannt. Änderungen werden still angewendet (oder,
wenn du willst, mit Rückfrage, ob sie bleiben sollen), und das Layout wird beim
Anmelden wiederhergestellt. `--dry-run` fragt Mutter, ob ein Layout gültig ist,
ohne es anzuwenden.
