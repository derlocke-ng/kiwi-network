# Iconos y colores

En esta página se describen los iconos y los colores de las apps de Kiwi y dónde
conseguirlos, por ejemplo cuando escribes una app para el catálogo. Todas las
apps de Kiwi tienen el mismo tipo de icono: un **kiwi cortado por la mitad**.
En el centro de la fruta aparece un símbolo de la app, y cada app tiene su
propio color. Los iconos están en el repositorio
[derlocke-ng/kiwi-icons](https://github.com/derlocke-ng/kiwi-icons). Su
[página de vista previa](https://derlocke-ng.github.io/kiwi-icons/) te permite
cambiar el estilo y el tema, muestra las paletas y tiene URL que puedes copiar.

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

Cada icono existe en tres estilos:

| Estilo | Aspecto |
|---|---|
| **classic** (por defecto) | el icono GTK detallado, con piel, pulpa, semillas y centro |
| **flat** | sin piel y con el centro más grande |
| **night** | un dibujo de líneas invertido sobre un disco oscuro |

## Estructura del repositorio { #layout }

El repositorio kiwi-icons contiene estos archivos:

| Ruta | Qué es |
|---|---|
| `svg/<style>/<icon>.svg` | los archivos originales (viewBox de 128×128) |
| `png/<style>/<size>/<icon>.png` | versiones PNG en 16, 32, 48, 64, 128, 256 y 512 px |
| `icons.json` | un índice legible por máquina, con ids, nombres, descripciones, colores y plantillas de URL |
| `palette/kiwi-palette.css`, `.json` | seis colores por app: `rim`, `flesh`, `core`, `ink`, `deep`, `text` |

## En una app { #in-an-app }

La mayoría de las apps de Kiwi incluyen una copia idéntica, byte a byte, de un
SVG del estilo classic y nombran ese archivo con `ICON=` en su `kiwi.manifest`.
gnome-monitor usa el icono `kiwi-os`, y syncman, el icono `kiwi-cloud`.
kiwi-custodia tiene un icono propio. kiwi-updater 2.2 y posteriores toman el
icono de su clon de la app, así que durante la instalación no se descarga nada.
Una app que tiene un lanzador `.desktop` instala además el icono en el tema de
iconos hicolor.

kiwi-icons todavía no tiene ninguna declaración de licencia.
