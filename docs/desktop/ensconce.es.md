# ensconce

ensconce configura por ti un [Bluefin-DX](https://projectbluefin.io/) recién
instalado, para que no tengas que configurar a mano cada máquina nueva.
Describes tu estación de trabajo en archivos de listas sencillos, y ensconce
convierte la instalación limpia en esa estación de trabajo. Se encarga de los
paquetes en capas, los Flatpaks, las extensiones de GNOME, la sincronización
con Nextcloud, una configuración de SSH que se mantiene igual en todas tus
máquinas, los ajustes del escritorio y de la pantalla de inicio de sesión, y
tus apps de Kiwi. Los paquetes en capas (layered packages) son paquetes RPM que
se añaden encima de la imagen del sistema. La configuración es modular: se
compone de pasos separados que puedes ejecutar u omitir.

- Repositorio: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  Según su manifiesto, la licencia es GPL-3.0-or-later; el README dice
  GPL-3.0.
- Última versión: **v2.5.0**. Está en el [catálogo de Kiwi](catalogs.md) y se
  instala en el ámbito de usuario, es decir, en tu carpeta personal.

```bash
kiwi install ensconce
ensconce --init          # crear ~/.config/ensconce a partir de los ejemplos
ensconce                 # ejecutar la configuración
```

También puedes ejecutarlo desde un clon del repositorio: ejecuta
`./ensconce.sh --init`, edita los archivos de `config/` y después ejecuta
`./ensconce.sh`.

## Pasos { #steps }

La configuración se divide en pasos. Cada paso es un script de `steps/`, y se
ejecutan en este orden:

| # | Paso | Qué hace |
|---|---|---|
| 01 | `rebase` | cambia el sistema a Bluefin-DX |
| 02 | `ujust` | configura los grupos de desarrollo y las herramientas de línea de comandos |
| 03 | `repos` | añade repositorios RPM |
| 04 | `packages` | añade paquetes RPM en capas |
| 05 | `flatpaks` | instala apps Flatpak. `FLATPAK_LANGUAGES` elige los idiomas de sus traducciones |
| 06 | `overrides` | define excepciones a los permisos de los Flatpaks (overrides) |
| 07 | `extensions` | instala extensiones de GNOME Shell |
| 08 | `cacert` | instala certificados de CA propios |
| 09 | `nextcloud` | deja preparada la sincronización de carpetas con Nextcloud |
| 10 | `dconf` | aplica los ajustes del escritorio GNOME |
| 11 | `gdm` | configura la pantalla de inicio de sesión |
| 12 | `ssh` | prepara la configuración de SSH sincronizada, con Bitwarden o GNOME como agente SSH |
| 13 | `kiwi` | instala kiwi-updater de la forma que elija `KIWI_INSTALL=recommended\|manual\|minimal`, y después todas las apps de `kiwi-apps.list` |
| 14 | `sysctl` | instala los archivos de ajustes del kernel de `sysctl.d/`. Un archivo de ejemplo limita cuántos datos pendientes de escribir guarda el kernel en memoria, lo que ayuda con SSD lentos |
| 15 | `power` | con `SYSTEM_SLEEP=off`, enmascara los targets de suspensión, para que la máquina no pueda suspenderse |

Antes de empezar, ensconce comprueba el entorno: el sistema tiene que ser una
imagen de Bluefin, y tienen que estar disponibles `rpm-ostree`, `flatpak`,
`dconf`, `jq` y `curl`. ensconce guarda su avance, así que después de un
reinicio continúa donde se quedó. Mientras se ejecuta, impide que la máquina se
suspenda, y al terminar restaura tus ajustes de energía.

Estas opciones controlan una ejecución:

```bash
ensconce --dry-run                  # vista previa sin cambiar nada
ensconce --skip rebase,ujust        # omitir pasos
ensconce --only extensions,dconf    # ejecutar solo estos
ensconce --status | --list-steps | --reset
ensconce --log [file]               # guardar la salida
ensconce --config-dir               # mostrar el directorio de configuración activo
```

## Configuración { #configuration }

ensconce busca su directorio de configuración en cuatro sitios y usa el primero
que exista. Mira primero en `$ENSCONCE_CONFIG`, después en
`~/.config/ensconce/`, que es el que se usa si instalaste ensconce con kiwi,
después en `config/` dentro de un clon y, por último, en `config.example/`. Si
acaba usando `config.example/`, muestra un aviso.

| Archivo / directorio | Para qué sirve |
|---|---|
| `settings.sh` | las URL de los servidores, y los interruptores de SSH, kiwi-updater, los idiomas de Flatpak y la suspensión |
| `packages.list`, `flatpaks.list`, `extensions.list` | los paquetes, Flatpaks y extensiones de GNOME que hay que instalar, uno por línea |
| `kiwi-apps.list` | las apps de Kiwi que hay que instalar |
| `repos.d/`, `flatpak-overrides/` | archivos de repositorios, y excepciones para apps concretas en el formato propio de Flatpak |
| `nextcloud/folders.list` | las carpetas que se sincronizan, con el formato `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | lo que queda fuera de la sincronización, para todas las carpetas y para carpetas concretas que tienen una etiqueta |
| `certs/` | certificados de CA (`.pem`), por ejemplo el `kiwiCA.pem` de tu fleet |
| `sysctl.d/` | ajustes del kernel |
| `dconf-settings.ini`, `gtk3-bookmarks` | ajustes de GNOME y marcadores de Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | los ajustes y la disposición de las pantallas en la pantalla de inicio de sesión |

Una etiqueta en `nextcloud/folders.list` da a una carpeta sus propias
exclusiones. Por ejemplo, la etiqueta `browser` coloca `exclude.d/browser.lst`
en esa carpeta. Así no se sincronizan las bases de datos de un perfil del
navegador, que podrían corromperse al sincronizarlas, pero `user.js` sí se
sigue sincronizando.

## Clonar una máquina { #cloning-a-machine }

`--export` hace lo contrario que los pasos: lee el sistema en marcha y escribe
a partir de él un directorio de configuración de ensconce. Con ese directorio
puedes configurar después una máquina nueva:

```bash
ensconce --export ./my-setup        # en la máquina ya configurada
ensconce --init                     # en la nueva
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

La exportación solo contiene lo que tú has añadido al sistema. Recoge los
paquetes que pediste, no toda la imagen, y solo las extensiones que de verdad
vienen de extensions.gnome.org. Incluye tus propios archivos de repositorios y,
en lugar de un volcado completo de dconf, unas ramas seleccionadas. Toma la
exportación como punto de partida. `certs/` y `nextcloud/` pueden contener
material privado.

ensconce es una app del **ámbito de usuario**. Los pasos que necesitan
permisos de root los piden ellos mismos. Para añadir un paso propio, crea un
archivo `steps/NN-<name>.sh` con una función `step_<name>()`.
