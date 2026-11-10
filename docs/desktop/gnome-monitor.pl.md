# gnome-monitor

Zapisuj i przełączaj układy ekranów w GNOME (rozdzielczość, częstotliwość
odświeżania z VRR, pozycja, skala i ekran główny dla każdego monitora) oraz
**wyłączaj i włączaj** pojedyncze monitory, gdy używa ich inny komputer. CLI
plus panel GTK4.

- Repozytorium: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Najnowsze wydanie: **v0.3.2**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

Dwa komputery, trzy ekrany, jedno biurko. Gdy druga maszyna też potrzebuje
ekranu 4K, wyłącz go tutaj, pracuj i włącz z powrotem. Wraca tam, gdzie był,
w trybie, który miał, jako ekran główny, jeśli nim był. Albo zapisz każdy
układ raz i stosuj go jednym kliknięciem lub skrótem klawiszowym.

```bash
kiwi install gnome-monitor          # albo ./install.sh
```

```bash
gnome-monitor show                  # co jest podłączone, włączone, gdzie, w jakim trybie, z mapą
gnome-monitor save desk             # the current layout as profile "desk"
gnome-monitor list                  # profile; * oznacza używany
gnome-monitor apply desk
gnome-monitor off rog               # a screen by connector, part of its name, number or "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # włączone dokładnie te, wszystkie inne wyłączone
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # a GNOME shortcut that applies "desk"
gnome-monitor-panel                 # "Gnome Monitor" in the app grid
```

Rozmawia z API D-Bus `DisplayConfig` Muttera, na Waylandzie i X11, bez roota i
bez rozszerzenia. Profile to JSON w `~/.config/gnome-monitor/profiles/`, a
monitory są dopasowywane po EDID. Zmiany stosują się po cichu (albo, jeśli
wolisz, z pytaniem, czy je zachować), a układ jest przywracany przy
logowaniu. `--dry-run` pyta Muttera, czy układ jest poprawny, bez stosowania
go.
