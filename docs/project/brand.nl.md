# Iconen en kleuren

Op deze pagina staat hoe de iconen en kleuren van de Kiwi-apps in elkaar zitten
en waar je ze vindt, bijvoorbeeld als je zelf een app voor de catalogus
schrijft. Alle Kiwi-apps hebben hetzelfde soort icoon: een **doorsnede van een
kiwi**, dus een kiwi die doormidden is gesneden. In het hart van de vrucht staat
een symbool voor de app, en elke app heeft een eigen kleur. De iconen staan in
de repository
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons). Op de
[voorbeeldpagina](https://derlocke-ng.github.io/kiwi-icons/) kun je van stijl
en thema wisselen, zie je de paletten en vind je URL’s die je kunt kopiëren.

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

Elk icoon is er in drie stijlen:

| Stijl | Uiterlijk |
|---|---|
| **classic** (standaard) | het verfijnde GTK-icoon, met rand, vruchtvlees, pitjes en hart |
| **flat** | zonder rand en met een groter hart |
| **night** | een geïnverteerde lijntekening op een donkere schijf |

## Indeling { #layout }

De repository kiwi-icons bevat deze bestanden:

| Pad | Wat |
|---|---|
| `svg/<style>/<icon>.svg` | de bronbestanden (viewBox van 128×128) |
| `png/<style>/<size>/<icon>.png` | PNG-versies van 16, 32, 48, 64, 128, 256 en 512 px |
| `icons.json` | een machineleesbare index met id’s, namen, beschrijvingen, kleuren en URL-sjablonen |
| `palette/kiwi-palette.css`, `.json` | zes kleuren per app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In een app { #in-an-app }

De meeste Kiwi-apps bevatten een byte-identieke kopie van een SVG in de stijl
classic en verwijzen naar dat bestand met `ICON=` in hun `kiwi.manifest`.
gnome-monitor gebruikt het icoon `kiwi-os` en syncman het icoon `kiwi-cloud`.
kiwi-custodia heeft een eigen icoon. Vanaf versie 2.2 haalt kiwi-updater het
icoon uit zijn kloon van de app, zodat er bij de installatie niets wordt
gedownload. Een app met een `.desktop`-starter installeert het icoon ook in het
icoonthema hicolor.

Voor kiwi-icons is nog geen licentie vermeld.
