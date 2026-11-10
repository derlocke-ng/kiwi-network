# Iconos y colores

Todas las apps de Kiwi tienen la misma marca: un **corte transversal de kiwi**
cuyo centro lleva el glifo de la app, en un color propio. Los iconos viven en
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), con una
[página de vista previa](https://derlocke-ng.github.io/kiwi-icons/) que tiene un
selector de estilo y de tema, las paletas y URLs para copiar.

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

## Tres estilos { #three-styles }

| Estilo | Aspecto |
|---|---|
| **classic** (por defecto) | el icono GTK refinado: piel, pulpa, semillas y centro |
| **flat** | sin piel, con un centro más grande |
| **night** | una marca de líneas invertida sobre un disco oscuro |

## Estructura { #layout }

| Ruta | Qué |
|---|---|
| `svg/<style>/<icon>.svg` | los originales (viewBox de 128×128) |
| `png/<style>/<size>/<icon>.png` | renderizados a 16, 32, 48, 64, 128, 256 y 512 px |
| `icons.json` | un índice legible por máquina: ids, nombres, descripciones, colores, plantillas de URL |
| `palette/kiwi-palette.css`, `.json` | seis colores por app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## En una app { #in-an-app }

La mayoría de las apps de Kiwi incluyen una copia idéntica byte a byte de un SVG
classic y lo nombran con `ICON=` en su `kiwi.manifest`. gnome-monitor y syncman
usan los iconos `kiwi-os` y `kiwi-cloud`, y kiwi-custodia lleva el suyo propio.
kiwi-updater 2.2 y posteriores lo toman del clon propio de la app, así que no se
descarga nada al instalar. Una app con un lanzador `.desktop` también lo instala
en el tema de iconos hicolor.

kiwi-icons todavía no tiene declaración de licencia.
