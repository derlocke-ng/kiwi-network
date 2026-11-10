# Ikony i kolory

Ta strona opisuje ikony i kolory aplikacji Kiwi i podpowiada, skąd je wziąć,
na przykład gdy piszesz aplikację do katalogu aplikacji Kiwi. Każda aplikacja
Kiwi ma ten sam rodzaj ikony: **przekrój kiwi**, czyli owoc kiwi przecięty na
pół. W środku owocu widać symbol aplikacji, a każda aplikacja ma własny kolor.
Ikony są w repozytorium
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons). Na jego
[stronie z podglądem](https://derlocke-ng.github.io/kiwi-icons/) możesz
przełączać styl i motyw, obejrzeć palety i skopiować adresy URL.

<div class="kiwi-icons-row" markdown>
![kiwi-updater](../assets/icons/kiwi-updater.svg){ width=56 }
![kiwi-server](../assets/icons/kiwi-server.svg){ width=56 }
![kiwi-killswitch](../assets/icons/kiwi-killswitch.svg){ width=56 }
![kiwi-proxy](../assets/icons/kiwi-proxy.svg){ width=56 }
![kiwi-fox](../assets/icons/kiwi-fox.svg){ width=56 }
![ensconce](../assets/icons/ensconce.svg){ width=56 }
![kiwi-cli-tools-desktop](../assets/icons/kiwi-cli-tools-desktop.svg){ width=56 }
![kiwi-network](../assets/icons/kiwi-network.svg){ width=56 }
</div>

## Trzy style { #three-styles }

Każda ikona istnieje w trzech stylach:

| Styl | Wygląd |
|---|---|
| **classic** (domyślny) | dopracowana ikona GTK ze skórką, miąższem, pestkami i środkiem |
| **flat** | bez skórki, z większym środkiem |
| **night** | odwrócony rysunek konturowy na ciemnym kole |

## Układ repozytorium { #layout }

Repozytorium kiwi-icons zawiera te pliki:

| Ścieżka | Co to jest |
|---|---|
| `svg/<style>/<icon>.svg` | pliki źródłowe (viewBox 128×128) |
| `png/<style>/<size>/<icon>.png` | wersje PNG w rozmiarach 16, 32, 48, 64, 128, 256 i 512 px |
| `icons.json` | indeks do odczytu maszynowego z identyfikatorami, nazwami, opisami, kolorami i szablonami adresów URL |
| `palette/kiwi-palette.css`, `.json` | sześć kolorów na aplikację: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## W aplikacji { #in-an-app }

Większość aplikacji Kiwi zawiera identyczną co do bajtu kopię ikony SVG
w stylu classic i wskazuje ten plik wpisem `ICON=` w swoim `kiwi.manifest`.
gnome-monitor używa ikony `kiwi-os`, a syncman ikony `kiwi-cloud`.
kiwi-custodia ma własną ikonę. kiwi-updater od wersji 2.2 bierze ikonę
ze sklonowanego repozytorium aplikacji, więc przy instalacji niczego nie pobiera.
Aplikacja z plikiem uruchamiającym `.desktop` instaluje też ikonę w motywie
ikon hicolor.

kiwi-icons nie ma jeszcze informacji o licencji.
