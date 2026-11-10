# Icons & colours

This page describes the icons and colours of the Kiwi apps and where to get
them, for example when you write an app for the catalog. Every Kiwi app has
the same kind of icon, a **kiwi cross-section**, which is a kiwi fruit cut in
half. The core of the fruit shows a symbol for the app, and each app has a
colour of its own. The icons are in the
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons)
repository. Its [preview page](https://derlocke-ng.github.io/kiwi-icons/)
lets you switch the style and the theme, shows the palettes and has URLs that
you can copy.

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

Every icon exists in three styles:

| Style | Look |
|---|---|
| **classic** (default) | the refined GTK icon, with rim, flesh, seeds and core |
| **flat** | has no rim and a larger core |
| **night** | an inverted line drawing on a dark disc |

## Layout

The kiwi-icons repository contains these files:

| Path | What |
|---|---|
| `svg/<style>/<icon>.svg` | the master files (128×128 viewBox) |
| `png/<style>/<size>/<icon>.png` | PNG renders at 16, 32, 48, 64, 128, 256 and 512 px |
| `icons.json` | a machine-readable index with ids, names, descriptions, colours and URL templates |
| `palette/kiwi-palette.css`, `.json` | six colours per app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## In an app

Most Kiwi apps contain a byte-identical copy of a classic SVG and name that
file with `ICON=` in their `kiwi.manifest`. gnome-monitor uses the `kiwi-os`
icon and syncman uses the `kiwi-cloud` icon. kiwi-custodia has an icon of its
own. kiwi-updater 2.2 and later takes the icon from its clone of the app, so
nothing is downloaded at install time. An app that has a `.desktop` launcher
also installs the icon into the hicolor icon theme.

kiwi-icons has no license statement yet.
