# Iconen en kleuren

Elke Kiwi-app heeft hetzelfde merkteken: een **doorgesneden kiwi** waarvan het
hart het symbool van de app draagt, in een eigen kleur. De iconen staan in
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), met een
[voorbeeldpagina](https://derlocke-ng.github.io/kiwi-icons/) met een stijl- en
themakiezer, de paletten en kopieerbare URL's.

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

## Drie stijlen { #three-styles }

| Stijl | Uiterlijk |
|---|---|
| **classic** (standaard) | het verfijnde GTK-icoon: schil, vruchtvlees, pitjes en hart |
| **flat** | geen schil, een groter hart |
| **night** | een omgekeerd lijnteken op een donkere schijf |

## Indeling { #layout }

| Pad | Wat |
|---|---|
| `svg/<style>/<icon>.svg` | de originelen (viewBox van 128×128) |
| `png/<style>/<size>/<icon>.png` | renders op 16, 32, 48, 64, 128, 256 en 512 px |
| `icons.json` | een machineleesbare index: id's, namen, beschrijvingen, kleuren, URL-sjablonen |
| `palette/kiwi-palette.css`, `.json` | zes kleuren per app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In een app { #in-an-app }

De meeste Kiwi-apps leveren een byte-identieke kopie van een classic-SVG mee en
noemen die met `ICON=` in hun `kiwi.manifest`. gnome-monitor en syncman gebruiken
de iconen `kiwi-os` en `kiwi-cloud`, en kiwi-custodia heeft een eigen icoon.
kiwi-updater 2.2 en later haalt het uit de eigen clone van de app, zodat er bij
de installatie niets wordt opgehaald. Een app met een `.desktop`-starter
installeert het ook in het hicolor-icoonthema.

kiwi-icons heeft nog geen licentieverklaring.
