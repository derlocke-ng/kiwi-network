# Icônes et couleurs

Chaque application Kiwi porte la même marque : une **coupe de kiwi** dont le cœur
porte le glyphe de l’application, dans une couleur qui lui est propre. Les icônes
se trouvent dans [derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons),
avec une [page d’aperçu](https://derlocke-ng.github.io/kiwi-icons/) qui propose un
sélecteur de style et de thème, les palettes et des URL à copier.

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

## Trois styles { #three-styles }

| Style | Apparence |
|---|---|
| **classic** (par défaut) | l’icône GTK soignée : écorce, chair, pépins et cœur |
| **flat** | sans écorce, un cœur plus grand |
| **night** | une marque au trait inversée sur un disque sombre |

## Organisation { #layout }

| Chemin | Contenu |
|---|---|
| `svg/<style>/<icon>.svg` | les originaux (viewBox de 128×128) |
| `png/<style>/<size>/<icon>.png` | rendus en 16, 32, 48, 64, 128, 256 et 512 px |
| `icons.json` | un index lisible par machine : ids, noms, descriptions, couleurs, modèles d’URL |
| `palette/kiwi-palette.css`, `.json` | six couleurs par application : `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## Dans une application { #in-an-app }

La plupart des applications Kiwi livrent une copie identique à l’octet près d’un SVG
classic et la désignent avec `ICON=` dans leur `kiwi.manifest`. gnome-monitor et
syncman utilisent les icônes `kiwi-os` et `kiwi-cloud`, et kiwi-custodia porte la
sienne. kiwi-updater 2.2 et les versions suivantes la prennent dans le clone propre
à l’application, si bien que rien n’est téléchargé au moment de l’installation. Une
application avec un lanceur `.desktop` l’installe aussi dans le thème d’icônes
hicolor.

kiwi-icons n’a pas encore de mention de licence.
