# gnome-monitor

gnome-monitor salva la disposizione dei tuoi monitor in GNOME e ti fa passare da
una disposizione salvata all’altra. Per ogni monitor una disposizione registra
risoluzione, frequenza di aggiornamento (compresa quella variabile, VRR),
posizione e scala, oltre a quale monitor è lo schermo principale. gnome-monitor
sa anche **spegnere e riaccendere** un singolo monitor, cosa utile quando allo
stesso monitor è collegato un altro computer che ne ha bisogno. Ha uno strumento
da riga di comando e un pannello GTK4.

- Repository: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Ultima release: **v0.3.2**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

Un caso tipico è una scrivania con due computer e tre schermi. Quando anche
l’altro computer ha bisogno del monitor 4K, lo spegni su questo computer e
continui a lavorare con gli schermi che restano. Quando lo riaccendi, torna nella
posizione e nella modalità di prima, e torna a essere lo schermo principale se lo
era già. Puoi anche salvare una volta per tutte ogni disposizione come profilo e
applicarla con un clic o con una scorciatoia da tastiera.

```bash
kiwi install gnome-monitor          # oppure ./install.sh
```

```bash
gnome-monitor show                  # che cosa è collegato e acceso, dove, in quale modalità, con una mappa
gnome-monitor save desk             # la disposizione attuale come profilo "desk"
gnome-monitor list                  # i profili; * indica quello in uso
gnome-monitor apply desk
gnome-monitor off rog               # uno schermo per connettore, parte del nome, numero oppure "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # accende esattamente questi e spegne tutti gli altri
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # una scorciatoia di GNOME che applica "desk"
gnome-monitor-panel                 # "Gnome Monitor" nella griglia delle applicazioni
```

gnome-monitor usa l’API D-Bus `DisplayConfig` di Mutter, il window manager di
GNOME. Funziona sia su Wayland sia su X11, e non ha bisogno né dei permessi di
root né di un’estensione di GNOME. I profili sono file JSON in
`~/.config/gnome-monitor/profiles/`. Un monitor viene riconosciuto dal suo EDID,
cioè dai dati di identificazione che il monitor stesso comunica. Un cambio di
disposizione viene applicato senza finestra di conferma. Se preferisci, puoi
attivare un’opzione che ti chiede se vuoi tenere la nuova disposizione. Al
login la disposizione viene ripristinata. Con `--dry-run`, gnome-monitor chiede
a Mutter se una disposizione è valida, senza applicarla.
