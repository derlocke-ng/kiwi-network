# gnome-monitor

gnome-monitor speichert die Anordnung deiner Monitore unter GNOME als Layout
und wechselt zwischen gespeicherten Layouts. Ein Layout hält für jeden Monitor
die Auflösung, die Bildwiederholrate (auch die variable Bildwiederholrate,
VRR), die Position und die Skalierung fest und außerdem, welcher Monitor der
Hauptbildschirm ist. gnome-monitor kann auch einen einzelnen Monitor **aus- und
wieder einschalten**. Das ist praktisch, wenn ein anderer Rechner am selben
Monitor hängt und ihn gerade braucht. Es gibt ein Kommandozeilenwerkzeug und
ein GTK4-Panel.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Aktuelles Release: **v0.3.2**. Es steht im [Kiwi-Katalog](catalogs.md), Scope user.

Ein typischer Fall ist ein Schreibtisch mit zwei Rechnern und drei
Bildschirmen. Braucht der andere Rechner den 4K-Monitor, schaltest du ihn auf
diesem Rechner aus und arbeitest auf den übrigen Bildschirmen weiter. Schaltest
du ihn wieder ein, bekommt er seine vorherige Position und seinen vorherigen
Modus zurück, und war er vorher der Hauptbildschirm, ist er es wieder. Du
kannst jede Anordnung auch einmal als Profil speichern und sie dann mit einem
Klick oder einem Tastenkürzel anwenden.

```bash
kiwi install gnome-monitor          # oder ./install.sh
```

```bash
gnome-monitor show                  # was angeschlossen ist, ob an, wo, in welchem Modus, mit Übersichtskarte
gnome-monitor save desk             # das aktuelle Layout als Profil "desk"
gnome-monitor list                  # Profile; * markiert das aktive
gnome-monitor apply desk
gnome-monitor off rog               # ein Bildschirm per Anschluss, Namensteil, Nummer oder "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # genau diese an, alle anderen aus
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # ein GNOME-Tastenkürzel, das "desk" anwendet
gnome-monitor-panel                 # "Gnome Monitor" in der Anwendungsübersicht
```

gnome-monitor verwendet die D-Bus-Schnittstelle `DisplayConfig` von Mutter,
dem Fenstermanager von GNOME. Es läuft unter Wayland und X11 und braucht weder
Root-Rechte noch eine GNOME-Erweiterung. Profile sind JSON-Dateien in
`~/.config/gnome-monitor/profiles/`. Ein Monitor wird an seiner EDID erkannt,
den Kenndaten, die der Monitor über sich selbst meldet. Ein neues Layout wird
ohne Rückfrage übernommen. Wenn dir das lieber ist, kannst du eine Option
einschalten, die fragt, ob du das neue Layout behalten willst. Beim Anmelden
wird das Layout wiederhergestellt. Mit `--dry-run` fragt gnome-monitor bei
Mutter nur nach, ob ein Layout gültig ist, und wendet es nicht an.
