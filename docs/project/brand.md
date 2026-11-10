# Icons & colours

Every Kiwi app has the same mark: a **kiwi cross-section** whose core carries
the app's glyph, in a colour of its own. The icons live in
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), with a
[preview page](https://derlocke-ng.github.io/kiwi-icons/) that has a style and
theme switcher, the palettes and copyable URLs.

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

## Three styles

| Style | Look |
|---|---|
| **classic** (default) | the refined GTK icon: rim, flesh, seeds and core |
| **flat** | no rim, a larger core |
| **night** | an inverted line mark on a dark disc |

## Layout

| Path | What |
|---|---|
| `svg/<style>/<icon>.svg` | the masters (128×128 viewBox) |
| `png/<style>/<size>/<icon>.png` | renders at 16, 32, 48, 64, 128, 256 and 512 px |
| `icons.json` | a machine-readable index: ids, names, descriptions, colours, URL templates |
| `palette/kiwi-palette.css`, `.json` | six colours per app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In an app

Most Kiwi apps ship a byte-identical copy of a classic SVG and name it with
`ICON=` in their `kiwi.manifest`. gnome-monitor and syncman use the `kiwi-os`
and `kiwi-cloud` icons, and kiwi-custodia carries its own. kiwi-updater 2.2 and later draws it from
the app's own clone, so nothing is fetched at install time. An app with a
`.desktop` launcher also installs it into the hicolor icon theme.

kiwi-icons has no license statement yet.
