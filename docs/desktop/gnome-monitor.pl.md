# gnome-monitor

gnome-monitor zapisuje ustawienie twoich monitorów w GNOME jako układ ekranów
i przełącza się między zapisanymi układami. Układ obejmuje rozdzielczość,
częstotliwość odświeżania (także zmienną częstotliwość odświeżania, VRR),
położenie i skalowanie każdego monitora oraz to, który monitor jest ekranem
głównym. gnome-monitor potrafi też **wyłączyć i z powrotem włączyć** pojedynczy
monitor. Przydaje się to, gdy do tego samego monitora podłączony jest drugi
komputer, który go akurat potrzebuje. Narzędzie ma wersję wiersza poleceń
i panel GTK4.

- Repozytorium: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Najnowsze wydanie: **v0.3.2**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

Typowa sytuacja to biurko z dwoma komputerami i trzema ekranami. Gdy drugi
komputer też potrzebuje monitora 4K, wyłączasz ten monitor na tym komputerze
i pracujesz na pozostałych ekranach. Gdy włączysz go ponownie, wraca na swoje
poprzednie miejsce i do poprzedniego trybu, a jeśli wcześniej był ekranem
głównym, znów nim zostaje. Każde ustawienie możesz też raz zapisać jako profil
i potem przywracać jednym kliknięciem albo skrótem klawiszowym.

```bash
kiwi install gnome-monitor          # albo ./install.sh
```

```bash
gnome-monitor show                  # co jest podłączone i włączone, gdzie, w jakim trybie, z mapą
gnome-monitor save desk             # bieżący układ jako profil „desk”
gnome-monitor list                  # profile; * oznacza używany
gnome-monitor apply desk
gnome-monitor off rog               # ekran wskazany przez złącze, część nazwy, numer albo „main”
gnome-monitor on rog
gnome-monitor only odyssey hp       # dokładnie te włączone, wszystkie pozostałe wyłączone
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # skrót GNOME, który przywraca układ „desk”
gnome-monitor-panel                 # „Gnome Monitor” w siatce aplikacji
```

gnome-monitor korzysta z API D-Bus `DisplayConfig` w Mutterze, menedżerze okien
GNOME. Działa w Waylandzie i w X11 i nie potrzebuje ani uprawnień roota, ani
rozszerzenia GNOME. Profile to pliki JSON w `~/.config/gnome-monitor/profiles/`.
Monitor jest rozpoznawany po EDID, czyli danych identyfikacyjnych, które sam
o sobie podaje. Zmiana układu jest wprowadzana bez okna z prośbą
o potwierdzenie. Jeśli wolisz, możesz włączyć opcję, która zapyta, czy chcesz
zachować nowy układ. Po zalogowaniu układ zostaje przywrócony. Z opcją
`--dry-run` gnome-monitor pyta Muttera, czy układ jest poprawny, ale go nie
wprowadza.
