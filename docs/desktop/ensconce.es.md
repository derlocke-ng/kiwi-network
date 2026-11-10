# ensconce

Configuración modular posterior a la instalación para
[Bluefin-DX](https://projectbluefin.io/). ensconce convierte una instalación
nueva de Bluefin en tu estación de trabajo configurada a partir de archivos de
lista simples: paquetes por capas, Flatpaks, extensiones de GNOME,
sincronización con Nextcloud, una configuración SSH sincronizada, ajustes del
escritorio y de la pantalla de inicio de sesión, y tus apps de Kiwi.

- Repositorio: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (según su manifiesto; el README dice GPL-3.0)
- Última versión: **v2.5.0**. Está en el [catálogo de Kiwi](catalogs.md), ámbito
  de usuario.

```bash
kiwi install ensconce
ensconce --init          # crea ~/.config/ensconce a partir de los ejemplos
ensconce                 # ejecuta la configuración
```

O desde un clon: `./ensconce.sh --init`, edita `config/` y luego `./ensconce.sh`.

## Pasos { #steps }

Cada fase es un script de `steps/`, ejecutado en orden:

| # | Paso | Hace |
|---|---|---|
| 01 | `rebase` | cambia a Bluefin-DX |
| 02 | `ujust` | grupos de desarrollo y herramientas de CLI |
| 03 | `repos` | añade repositorios RPM |
| 04 | `packages` | añade paquetes RPM por capas |
| 05 | `flatpaks` | instala apps Flatpak (`FLATPAK_LANGUAGES` elige sus traducciones) |
| 06 | `overrides` | excepciones de permisos de Flatpak |
| 07 | `extensions` | extensiones de GNOME Shell |
| 08 | `cacert` | certificados de CA propios |
| 09 | `nextcloud` | preconfigura la sincronización de carpetas de Nextcloud |
| 10 | `dconf` | ajustes del escritorio GNOME |
| 11 | `gdm` | la pantalla de inicio de sesión |
| 12 | `ssh` | una configuración SSH sincronizada, con Bitwarden o GNOME como agente SSH |
| 13 | `kiwi` | instala kiwi-updater (`KIWI_INSTALL=recommended\|manual\|minimal`) y cada app de `kiwi-apps.list` |
| 14 | `sysctl` | archivos drop-in de `sysctl.d/` (un ejemplo limita el writeback de páginas sucias para SSD lentos) |
| 15 | `power` | `SYSTEM_SLEEP=off` enmascara los targets de suspensión |

ensconce comprueba primero el entorno (una imagen de Bluefin, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). Guarda su progreso y continúa tras los
reinicios, y mantiene la máquina despierta durante toda la ejecución,
restaurando después tus ajustes de energía.

```bash
ensconce --dry-run                  # vista previa sin cambiar nada
ensconce --skip rebase,ujust        # salta pasos
ensconce --only extensions,dconf    # ejecuta solo estos
ensconce --status | --list-steps | --reset
ensconce --log [file]               # guarda la salida
ensconce --config-dir               # imprime el directorio de configuración activo
```

## Configuración { #configuration }

El directorio de configuración es el primero que exista de: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (instalado con kiwi), `config/` en un clon y
`config.example/` (con una advertencia).

| Archivo / directorio | Para qué |
|---|---|
| `settings.sh` | URLs de servidores e interruptores: SSH, kiwi-updater, idiomas de Flatpak, suspensión |
| `packages.list`, `flatpaks.list`, `extensions.list` | un elemento por línea |
| `kiwi-apps.list` | las apps de Kiwi que instalar |
| `repos.d/`, `flatpak-overrides/` | archivos de repositorio; excepciones por app en el formato propio de Flatpak |
| `nextcloud/folders.list` | carpetas de sincronización como `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | exclusiones de sincronización globales y por carpeta (con etiqueta) |
| `certs/` | certificados de CA (`.pem`), por ejemplo el `kiwiCA.pem` de tu fleet |
| `sysctl.d/` | ajustes del kernel |
| `dconf-settings.ini`, `gtk3-bookmarks` | ajustes de GNOME, marcadores de Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | los ajustes y la distribución de pantallas de la pantalla de inicio de sesión |

Una etiqueta de exclusión por carpeta como `browser` coloca
`exclude.d/browser.lst` en esa carpeta, lo que evita que las bases de datos de un
perfil de navegador se sincronicen (y se corrompan) mientras `user.js` sigue
sincronizándose.

## Clonar una máquina { #cloning-a-machine }

`--export` lee el sistema en marcha y escribe un árbol de configuración de
ensconce, lo inverso de los pasos:

```bash
ensconce --export ./my-setup        # en la máquina configurada
ensconce --init                     # en la nueva
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Solo recoge lo que tú añadiste: los paquetes solicitados en lugar de toda la
imagen, las extensiones que de verdad vienen de extensions.gnome.org, tus propios
archivos de repositorio y subárboles de dconf seleccionados en lugar de un volcado
completo. Tómalo como punto de partida. `certs/` y `nextcloud/` pueden contener
material privado.

ensconce es una app de **ámbito de usuario**. Los pasos que necesitan root lo
piden ellos mismos. Añade tu propio paso como `steps/NN-<name>.sh` con una
función `step_<name>()`.
