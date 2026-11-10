# gnome-monitor

Salva e cambia le disposizioni degli schermi su GNOME (risoluzione, frequenza di aggiornamento con VRR,
posizione, scala e schermo principale per ogni monitor), e **spegni e riaccendi** i singoli monitor
quando li usa un altro computer. Una CLI più un pannello GTK4.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Ultima release: **v0.3.2**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

Due computer, tre schermi, una scrivania. Quando anche l'altra macchina ha bisogno del 4K,
spegnilo qui, lavora, e riaccendilo. Torna dov'era,
con la modalità che aveva, come schermo principale se lo era. Oppure salva ogni
disposizione una volta e applicala con un clic o una scorciatoia da tastiera.

```bash
kiwi install gnome-monitor          # oppure ./install.sh
```

```bash
gnome-monitor show                  # cosa è collegato, acceso, dove, in quale modalità, con una mappa
gnome-monitor save desk             # the current layout as profile "desk"
gnome-monitor list                  # i profili; * indica quello in uso
gnome-monitor apply desk
gnome-monitor off rog               # a screen by connector, part of its name, number or "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # accesi esattamente questi, tutti gli altri spenti
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # a GNOME shortcut that applies "desk"
gnome-monitor-panel                 # "Gnome Monitor" in the app grid
```

Parla con l'API D-Bus `DisplayConfig` di Mutter, su Wayland e X11, senza root
e senza estensioni. I profili sono file JSON in `~/.config/gnome-monitor/profiles/`, e
i monitor vengono riconosciuti dal loro EDID. Le modifiche si applicano senza chiedere (oppure chiedono se
mantenerle, se preferisci), e la disposizione viene ripristinata al login. `--dry-run` chiede
a Mutter se una disposizione è valida senza applicarla.
