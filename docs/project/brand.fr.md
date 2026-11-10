# Icônes et couleurs

Cette page présente les icônes et les couleurs des applications Kiwi, et
indique où les trouver, par exemple si vous écrivez une application pour le
catalogue. Toutes les applications Kiwi ont le même type d’icône, une **coupe
de kiwi**, c’est-à-dire un kiwi coupé en deux. Le cœur du fruit porte un
symbole propre à l’application, et chaque application a sa propre couleur. Les
icônes se trouvent dans le dépôt
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons). Sa
[page d’aperçu](https://derlocke-ng.github.io/kiwi-icons/) permet de changer de
style et de thème, montre les palettes et propose des URL à copier.

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

Chaque icône existe en trois styles :

| Style | Aspect |
|---|---|
| **classic** (par défaut) | l’icône GTK soignée, avec la peau, la chair, les pépins et le cœur |
| **flat** | sans peau, avec un cœur plus grand |
| **night** | un dessin au trait inversé sur un disque sombre |

## Organisation des fichiers { #layout }

Le dépôt kiwi-icons contient les fichiers suivants :

| Chemin | Contenu |
|---|---|
| `svg/<style>/<icon>.svg` | les fichiers de référence (viewBox de 128×128) |
| `png/<style>/<size>/<icon>.png` | des exports PNG en 16, 32, 48, 64, 128, 256 et 512 px |
| `icons.json` | un index lisible par une machine, avec les identifiants, les noms, les descriptions, les couleurs et des modèles d’URL |
| `palette/kiwi-palette.css`, `.json` | six couleurs par application : `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## Dans une application { #in-an-app }

La plupart des applications Kiwi contiennent une copie identique, octet pour
octet, d’un SVG du style classic, et indiquent ce fichier avec `ICON=` dans
leur `kiwi.manifest`. gnome-monitor utilise l’icône `kiwi-os`, et syncman
l’icône `kiwi-cloud`. kiwi-custodia a sa propre icône. À partir de la
version 2.2, kiwi-updater prend l’icône dans sa copie locale (clone git) de
l’application : rien n’est donc téléchargé au moment de l’installation. Une
application qui a un lanceur `.desktop` installe aussi son icône dans le thème
d’icônes hicolor.

kiwi-icons n’indique pas encore de licence.
