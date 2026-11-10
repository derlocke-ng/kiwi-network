# kiwi-updater

`kiwi` instala y actualiza apps de código abierto desde **catálogos git** en
Fedora Silverblue, Bluefin y otros sistemas ostree. Una app es un repo git con un
`kiwi.manifest` y un `install.sh`. kiwi lo clona, hace checkout de su último tag
de versión, ejecuta su instalador y lo mantiene actualizado en segundo plano,
incluido él mismo.

No hay cuentas, ni tienda, ni proveedor. Un catálogo es un repo que puedes leer,
del que puedes hacer un fork y al que puedes enviar una pull request.

- Repositorio: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Última versión: **v2.4.0**, una versión de seguridad
- **`kiwi`** es la CLI. Necesita `git`, coreutils, `util-linux` y `awk`, todos en
  la imagen base, más `ssh-keygen` para comprobar firmas.
- **Kiwi Apps** (`kiwi-gui`) es la app GTK4: búsqueda, filtros, una vista de
  detalle por app con su icono, capturas de pantalla y dependencias. Muestra el
  instalador y el diff de una actualización antes de ejecutar cualquiera de los
  dos, y pone en cola tus clics. Sus datos vienen de la CLI; los iconos y las
  capturas se leen de los clones de las apps, así que no se descarga nada para
  ellos.

## Instalación { #install }

```bash
# recomendado: ámbito de usuario más el ámbito de sistema propiedad de root, una sola petición de contraseña
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# mínimo: 100 % a nivel de usuario, solo ~/.local, sin root y sin contraseña, nunca
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# ninguna acción sin contraseña: cada cambio en el sistema pide una contraseña
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

La instalación registra el [catálogo de Kiwi](catalogs.md). Ve directamente a
`kiwi list` o abre **Kiwi Apps**.

Las apps que son solo archivos en tu home (las herramientas de CLI, ensconce,
syncman) quedan completas con la instalación mínima. Una app con una mitad de
root, como kiwi-killswitch, necesita el ámbito de sistema. En una instalación
mínima, `kiwi install kiwi-killswitch` lo configura en el momento con una
contraseña.

## Comandos { #commands }

```bash
kiwi list [--check]          # todas las apps que conoce esta máquina
kiwi search vpn              # busca una app en todos los catálogos registrados
kiwi info kiwi-killswitch    # qué es, qué instala, si necesita root
kiwi install <app>           # un nombre, o un --all explícito
kiwi update [<app>]          # todo lo que tenga una versión nueva
kiwi uninstall <app>         # --purge también borra su configuración
kiwi check                   # sale con 10 si algo tiene una actualización

kiwi add <https-url>         # sigue un repo directamente, sin catálogo
kiwi catalog add|list|remove # gestiona catálogos
kiwi sync                    # actualiza los catálogos ahora
kiwi self-update
kiwi trust --system <app>    # olvida la clave de firma fijada para una app de sistema
```

Antes de ejecutar algo, y cuando algo sale mal:

```bash
kiwi info --installer <app>  # el script que ejecutaría una instalación, antes de ejecutarlo
kiwi diff <app>              # lo que cambiaría una actualización, incluido su instalador
kiwi pin <app> v1.2.0        # quédate ahí; kiwi unpin <app> para volver a seguir las versiones
kiwi install <app> --dry-run # ámbito, URL, ref, ruta del instalador, y nada más
kiwi doctor                  # bloqueos obsoletos, versiones desfasadas, archivos de lista erróneos, temporizadores
```

## Las versiones son tags { #releases-are-tags }

Una app sigue su último **tag de versión**, uno que cumpla
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Las
preversiones y los tags de pruebas nunca adelantan a una versión. Un repo sin tag
de versión sigue su rama por defecto. `ref=<tag>` en una línea de lista pide uno
concreto.

## Dependencias { #dependencies }

`DEPENDS=` en un manifiesto nombra lo que necesita una app. Una palabra que es
una app de tu propio catálogo o lista se instala **primero**, en el mismo ámbito,
en el momento de la instalación. `kiwi install kiwi-plugin-tor`, por ejemplo,
trae consigo kiwi-proxy. Cualquier otra palabra es un programa, que se comprueba
con `command -v`.

## Una app, dos mitades { #one-app-two-halves }

Algunas apps son solo un binario en `~/.local/bin`. Otras, como un kill switch de
VPN, son un demonio de root **y** una app de escritorio **y** una extensión de
GNOME. Las mitades se instalan con privilegios distintos, porque **root nunca
debe ejecutar un archivo que el usuario pueda escribir**. La app lo declara:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Un catálogo enumera esa app una sola vez, y kiwi instala cada mitad
correctamente. Antes de pedirte la contraseña, muestra el `ROOT_REASON`.

| Pieza | Dónde | Por qué |
|---|---|---|
| `kiwi`, Kiwi Apps, apps de usuario | `~/.local` | no hace falta root; sobrevive a un rebase de ostree |
| la copia propia de kiwi de root | `/usr/local/bin`, clonada en `/var/lib/kiwi-updater/repos/` | root nunca ejecuta un archivo que tú puedas escribir |
| apps de sistema | `/var/lib`, `/etc` | escribibles en ostree, propiedad de root |
| listas | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | las entradas propias de una máquina ganan a cualquier catálogo |
| claves de firma fijadas | `/etc/kiwi-updater/signers/<app>` | ver más abajo |

El `/usr` inmutable nunca se toca.

## Root, contraseñas y firmas { #root-passwords-and-signatures }

| | Necesita root | Pide contraseña |
|---|---|---|
| cualquier cosa en el ámbito de usuario | no | no |
| **actualizar** una app de sistema | sí | **no**, para una versión firmada por la clave que root fijó para esa app. **Sí** para una versión sin firmar, y siempre en modo `manual` |
| **instalar** o **desinstalar** una app de sistema | sí | sí |

Desde la 2.4.0:

- **Versiones firmadas.** Root fija una clave de firma SSH por app de sistema, la
  primera que ve (confianza en el primer uso). Un tag de versión firmado por esa
  clave se actualiza sin contraseña. Una versión sin firmar pide una y dice que
  no pudo verificarla. Un tag firmado por otra clave, o un tag sin firmar después
  de otros firmados, se rechaza hasta que ejecutes `kiwi trust --system <app>`.
  Esto se aplica al ámbito de sistema.
- **Root solo instala fuentes que tiene en sus listas**:
  `/etc/kiwi-updater/apps.list` y los catálogos registrados para root. Para
  cualquier otra cosa, kiwi instala la mitad de usuario e indica el
  `kiwi add --system <https-url>` que hay que ejecutar. Kiwi Apps ofrece
  *Register and Install*.
- **Solo https.** Las fuentes `http://` se rechazan en todas partes.

Las actualizaciones de sistema sin contraseña pasan por un único ayudante de
propósito fijo, `/usr/local/libexec/kiwi-system-update`. Una regla de polkit lo
permite para sesiones activas de `wheel`, y solo acepta nombres de apps como una
selección de las listas propias de root.

## Actualizaciones en segundo plano { #background-updates }

Hay un solo temporizador, y es tuyo: `kiwi-updater.timer` ejecuta
`kiwi update --all` seis horas después de la última ejecución (diez minutos
después del arranque, con algo de retardo aleatorio). Actualiza las mitades de
usuario directamente, y las mitades de sistema a través del ayudante de arriba.
No hay temporizador de root. En modo `manual`, las mitades de sistema esperan a
tu siguiente `kiwi update` interactivo.

## Confianza { #trust }

Instalar una app **ejecuta el `install.sh` de ese repo**, y una app que declara
el ámbito de sistema lo ejecuta **como root**. Los catálogos están seleccionados,
no auditados. Añade aquellos en los que confíes, como añadirías un repositorio de
paquetes, y usa `kiwi info --installer`, `kiwi diff` y `kiwi pin` para decidir
con los ojos abiertos. Una firma acota *quién puede publicar*. No dice nada de
*lo que hace lo publicado*.

Aún previsto: un registro alojado de catálogos de confianza
(`kiwi catalog browse`) con las huellas de los firmantes por entrada.
