# Ikony i kolory

Każda aplikacja Kiwi ma ten sam znak: **przekrój kiwi**, którego środek nosi
glif aplikacji, we własnym kolorze. Ikony są w
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), razem ze
[stroną podglądu](https://derlocke-ng.github.io/kiwi-icons/), która ma
przełącznik stylu i motywu, palety oraz adresy URL do skopiowania.

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

| Styl | Wygląd |
|---|---|
| **classic** (domyślny) | dopracowana ikona GTK: skórka, miąższ, pestki i środek |
| **flat** | bez skórki, większy środek |
| **night** | odwrócony znak liniowy na ciemnym kole |

## Układ { #layout }

| Ścieżka | Co |
|---|---|
| `svg/<style>/<icon>.svg` | wzorce (viewBox 128×128) |
| `png/<style>/<size>/<icon>.png` | rendery w 16, 32, 48, 64, 128, 256 i 512 px |
| `icons.json` | indeks do odczytu maszynowego: id, nazwy, opisy, kolory, szablony URL |
| `palette/kiwi-palette.css`, `.json` | sześć kolorów na aplikację: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## W aplikacji { #in-an-app }

Większość aplikacji Kiwi dostarcza bajt w bajt identyczną kopię klasycznego
SVG i wskazuje ją przez `ICON=` w swoim `kiwi.manifest`. gnome-monitor i
syncman używają ikon `kiwi-os` i `kiwi-cloud`, a kiwi-custodia ma własną.
kiwi-updater od wersji 2.2 bierze ją z własnego klona aplikacji, więc przy
instalacji nic nie jest pobierane. Aplikacja z programem uruchamiającym
`.desktop` instaluje ją też w motywie ikon hicolor.

kiwi-icons nie ma jeszcze informacji o licencji.
