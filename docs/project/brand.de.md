# Icons & Farben

Diese Seite beschreibt die Icons und Farben der Kiwi-Apps und wo du sie
bekommst, zum Beispiel wenn du eine App für den Katalog schreibst. Alle
Kiwi-Apps haben die gleiche Art von Icon, einen **Kiwi-Querschnitt**, also eine
halbierte Kiwi. In der Mitte der Frucht sitzt ein Symbol für die App, und jede
App hat ihre eigene Farbe. Die Icons liegen im Repository
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons). Auf seiner
[Vorschauseite](https://derlocke-ng.github.io/kiwi-icons/) kannst du Stil und
Theme umschalten, die Paletten ansehen und URLs zum Kopieren finden.

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

Jedes Icon gibt es in drei Stilen:

| Stil | Aussehen |
|---|---|
| **classic** (Standard) | das detailreiche GTK-Icon mit Schale, Fruchtfleisch, Kernen und Mitte |
| **flat** | ohne Schale und mit größerer Mitte |
| **night** | eine invertierte Strichzeichnung auf einer dunklen Scheibe |

## Aufbau { #layout }

Das Repository kiwi-icons enthält diese Dateien:

| Pfad | Inhalt |
|---|---|
| `svg/<style>/<icon>.svg` | die Originaldateien (viewBox 128×128) |
| `png/<style>/<size>/<icon>.png` | PNG-Versionen in 16, 32, 48, 64, 128, 256 und 512 px |
| `icons.json` | ein maschinenlesbarer Index mit IDs, Namen, Beschreibungen, Farben und URL-Vorlagen |
| `palette/kiwi-palette.css`, `.json` | sechs Farben pro App: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In einer App { #in-an-app }

Die meisten Kiwi-Apps enthalten eine byte-identische Kopie eines SVG im Stil
classic und nennen diese Datei in ihrem `kiwi.manifest` unter `ICON=`.
gnome-monitor verwendet das Icon `kiwi-os`, syncman das Icon `kiwi-cloud`.
kiwi-custodia hat ein eigenes Icon. Ab Version 2.2 nimmt kiwi-updater das Icon
aus seinem Klon der App, sodass bei der Installation nichts heruntergeladen
wird. Eine App mit einem `.desktop`-Starter installiert das Icon außerdem in das
Icon-Theme hicolor.

Für kiwi-icons gibt es noch keine Lizenzangabe.
