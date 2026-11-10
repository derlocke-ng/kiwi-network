# Icons & Farben

Jede Kiwi-App hat dasselbe Zeichen: einen **Kiwi-Querschnitt**, dessen Kern das
Symbol der App trägt, in einer eigenen Farbe. Die Icons liegen in
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), mit einer
[Vorschauseite](https://derlocke-ng.github.io/kiwi-icons/), die einen Stil- und
Theme-Umschalter, die Paletten und kopierbare URLs hat.

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

## Drei Stile { #three-styles }

| Stil | Aussehen |
|---|---|
| **classic** (Standard) | das ausgefeilte GTK-Icon: Rand, Fruchtfleisch, Kerne und Kern |
| **flat** | kein Rand, ein größerer Kern |
| **night** | ein invertiertes Linienzeichen auf einer dunklen Scheibe |

## Aufbau { #layout }

| Pfad | Was |
|---|---|
| `svg/<style>/<icon>.svg` | die Vorlagen (128×128-viewBox) |
| `png/<style>/<size>/<icon>.png` | Renderings in 16, 32, 48, 64, 128, 256 und 512 px |
| `icons.json` | ein maschinenlesbarer Index: IDs, Namen, Beschreibungen, Farben, URL-Vorlagen |
| `palette/kiwi-palette.css`, `.json` | sechs Farben pro App: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In einer App { #in-an-app }

Die meisten Kiwi-Apps liefern eine byte-identische Kopie eines classic-SVG mit und
nennen es mit `ICON=` in ihrem `kiwi.manifest`. gnome-monitor und syncman nutzen
die Icons `kiwi-os` und `kiwi-cloud`, und kiwi-custodia bringt sein eigenes mit.
kiwi-updater ab 2.2 holt es aus dem eigenen Klon der App, sodass bei der
Installation nichts heruntergeladen wird. Eine App mit einem `.desktop`-Starter
installiert es außerdem ins hicolor-Icon-Theme.

kiwi-icons hat noch keine Lizenzangabe.
