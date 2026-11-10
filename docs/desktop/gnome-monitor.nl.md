# gnome-monitor

Beeldschermindelingen op GNOME opslaan en wisselen (resolutie, verversingssnelheid
met VRR, positie, schaal en hoofdscherm per monitor), en losse monitoren **uit
en aan** zetten wanneer een andere computer ze gebruikt. Een CLI plus een GTK4-paneel.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Nieuwste release: **v0.3.2**. Het staat in de [Kiwi-catalogus](catalogs.md), gebruikersscope.

Twee computers, drie schermen, één bureau. Als de andere machine het 4K-scherm
ook nodig heeft, zet je het hier uit, werk je, en zet je het weer aan. Het komt
terug waar het was, in de modus die het had, als hoofdscherm als het dat was. Of
sla elke opstelling één keer op en pas haar toe met één klik of een sneltoets.

```bash
kiwi install gnome-monitor          # of ./install.sh
```

```bash
gnome-monitor show                  # wat er aangesloten is, aan, waar, in welke modus, met een kaartje
gnome-monitor save desk             # de huidige indeling als profiel "desk"
gnome-monitor list                  # profielen; * markeert het actieve
gnome-monitor apply desk
gnome-monitor off rog               # een scherm via connector, een deel van de naam, nummer of "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # precies deze aan, alle andere uit
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # een GNOME-sneltoets die "desk" toepast
gnome-monitor-panel                 # "Gnome Monitor" in het app-overzicht
```

Het praat met de `DisplayConfig`-D-Bus-API van Mutter, op Wayland en X11,
zonder root en zonder extensie. Profielen zijn JSON in
`~/.config/gnome-monitor/profiles/`, en monitoren worden herkend aan hun EDID.
Wijzigingen worden stil toegepast (of er wordt gevraagd of je ze wilt houden,
als je dat wilt), en de indeling wordt bij het inloggen hersteld. `--dry-run`
vraagt Mutter of een indeling geldig is zonder haar toe te passen.
