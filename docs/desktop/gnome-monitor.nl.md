# gnome-monitor

gnome-monitor slaat de opstelling van je monitoren in GNOME op als schermindeling
en wisselt tussen opgeslagen schermindelingen. Een schermindeling legt per
monitor de resolutie vast, de verversingsfrequentie (ook variabele
verversingsfrequentie, VRR), de positie en de schaal, en welke monitor het
hoofdscherm is. gnome-monitor kan ook één monitor **uit- en aanzetten**. Dat is
handig als een andere computer op dezelfde monitor is aangesloten en hem nodig
heeft. Er is een opdrachtregeltool en een GTK4-paneel.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Nieuwste release: **v0.3.2**. Staat in de [Kiwi-catalogus](catalogs.md), scope user.

Een typisch voorbeeld is een bureau met twee computers en drie schermen. Heeft
de andere computer de 4K-monitor ook nodig, dan zet je die monitor op deze
computer uit en werk je verder op de overige schermen. Zet je hem weer aan, dan
krijgt hij dezelfde positie en modus als daarvoor, en is hij weer het
hoofdscherm als hij dat eerst ook was. Je kunt elke opstelling ook één keer als
profiel opslaan en daarna met één klik of een sneltoets toepassen.

```bash
kiwi install gnome-monitor          # of ./install.sh
```

```bash
gnome-monitor show                  # wat aangesloten is, aan staat, waar, in welke modus, met een plattegrond
gnome-monitor save desk             # de huidige indeling als profiel "desk"
gnome-monitor list                  # profielen; * markeert het actieve
gnome-monitor apply desk
gnome-monitor off rog               # een scherm via connector, deel van de naam, nummer of "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # precies deze aan, alle andere uit
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # een GNOME-sneltoets die "desk" toepast
gnome-monitor-panel                 # "Gnome Monitor" in het overzicht van apps
```

gnome-monitor gebruikt de D-Bus-API `DisplayConfig` van Mutter, de
vensterbeheerder van GNOME. Het werkt op Wayland en op X11, en heeft geen
rootrechten en geen GNOME-extensie nodig. Profielen zijn JSON-bestanden in
`~/.config/gnome-monitor/profiles/`. Een monitor wordt herkend aan zijn EDID,
de identificatiegegevens die de monitor zelf doorgeeft. Een nieuwe
schermindeling wordt zonder bevestigingsvenster toegepast. Wil je dat liever
wel, dan kun je een optie aanzetten die vraagt of je de nieuwe indeling wilt
houden. Bij het inloggen wordt de schermindeling hersteld. Met `--dry-run`
vraagt gnome-monitor aan Mutter of een indeling geldig is, zonder haar toe te
passen.
