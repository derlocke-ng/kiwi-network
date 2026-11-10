# kiwi-updater

kiwi-updater instala apps de código abierto en tu escritorio y las mantiene al
día. Su comando es `kiwi`. Obtiene las apps de **catálogos de git** y funciona
en Fedora Silverblue, Bluefin y otros sistemas ostree. Un catálogo es un
repositorio git con una lista de apps. Una app es un repositorio git con un
archivo `kiwi.manifest` y un script `install.sh`. kiwi clona el repositorio de
la app, se sitúa en su etiqueta de versión más reciente y ejecuta su
instalador. A partir de ahí actualiza la app en segundo plano, y se actualiza a
sí mismo de la misma manera.

No necesitas ninguna cuenta, y no hay tienda de apps ni ningún fabricante de
por medio. Un catálogo es un repositorio que puedes leer, del que puedes hacer
un fork y al que puedes enviar una pull request.

- Repositorio: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Última versión: **v2.4.0**, una versión de seguridad
- **`kiwi`** es la herramienta de línea de comandos (CLI). Necesita `git`,
  coreutils, `util-linux` y `awk`, que forman parte de la imagen base. Para
  comprobar firmas necesita además `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) es la app de escritorio, hecha con GTK4. Puedes
  buscar y filtrar las apps, y cada una tiene una vista de detalle con su
  icono, capturas de pantalla y dependencias. Antes de instalar una app, Kiwi
  Apps te enseña su instalador, y antes de actualizarla, lo que cambia la
  actualización. Si haces clic en varias acciones seguidas, las pone en cola.
  Sus datos los obtiene de la CLI. Los iconos y las capturas los lee de los
  clones locales de las apps, así que no descarga nada para mostrarlos.

## Instalación { #install }

kiwi trabaja en dos ámbitos. El ámbito de usuario es todo lo que está en tu
carpeta personal, y nunca necesita root. El ámbito del sistema es una parte que
pertenece a root, para las apps que necesitan permisos de root. Al instalar
kiwi eliges en qué medida quieres usar el ámbito del sistema:

```bash
# recomendado: ámbito de usuario más el ámbito del sistema de root, una sola petición de contraseña
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# mínimo: 100 % a nivel de usuario, solo ~/.local, nunca root ni contraseña
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# ninguna acción sin contraseña: cada cambio en el sistema pide la contraseña
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

La instalación registra el [catálogo de Kiwi](catalogs.md), así que puedes
ejecutar `kiwi list` o abrir **Kiwi Apps** enseguida.

Algunas apps se componen solo de archivos en tu carpeta personal, por ejemplo
las herramientas de línea de comandos, ensconce y syncman. Esas apps funcionan
completas con la instalación mínima. Una app con una mitad que se ejecuta como
root, como kiwi-killswitch, necesita el ámbito del sistema. En una instalación
mínima, `kiwi install kiwi-killswitch` prepara el ámbito del sistema en ese
momento y te pide la contraseña una vez.

## Comandos { #commands }

```bash
kiwi list [--check]          # todas las apps que conoce esta máquina
kiwi search vpn              # buscar una app en todos los catálogos registrados
kiwi info kiwi-killswitch    # qué es, qué instala, si necesita root
kiwi install <app>           # un nombre, o --all de forma explícita
kiwi update [<app>]          # todo lo que tenga una versión nueva
kiwi uninstall <app>         # --purge borra también su configuración
kiwi check                   # código de salida 10 si hay alguna actualización

kiwi add <https-url>         # seguir un repositorio directamente, sin catálogo
kiwi catalog add|list|remove # gestionar los catálogos
kiwi sync                    # actualizar los catálogos ahora
kiwi self-update
kiwi trust --system <app>    # olvidar la clave de firma fijada para una app del sistema
```

Los comandos siguientes te muestran qué va a hacer una app antes de ejecutarla,
y te ayudan cuando algo sale mal:

```bash
kiwi info --installer <app>  # el script que ejecutaría una instalación, antes de ejecutarlo
kiwi diff <app>              # qué cambiaría una actualización, instalador incluido
kiwi pin <app> v1.2.0        # quedarse ahí; kiwi unpin <app> para volver a seguir las versiones
kiwi install <app> --dry-run # ámbito, URL, ref, ruta del instalador, y nada más
kiwi doctor                  # bloqueos obsoletos, versiones desparejadas, listas mal escritas, temporizadores
```

## Las versiones son etiquetas { #releases-are-tags }

kiwi usa las etiquetas de git como versiones. Una app sigue su **etiqueta de
versión** más reciente. Una etiqueta de versión es una etiqueta que cumple
`^v?[0-9]+(\.[0-9]+){0,3}$`, por ejemplo `v1`, `v1.2`, `1.2.3` o `v1.2.3.4`.
Las etiquetas de versiones preliminares y las temporales no cumplen ese patrón,
así que nunca se usan en lugar de una versión. Un repositorio sin etiquetas de
versión sigue su rama por defecto. Para pedir una versión concreta, añade
`ref=<tag>` a la línea de la app en una lista.

## Dependencias { #dependencies }

La línea `DEPENDS=` de un manifiesto indica lo que necesita una app. Si una
palabra de esa línea es el nombre de una app de tu propio catálogo o de tu
lista, kiwi instala esa app **antes**, en el mismo ámbito, en el momento en que
instalas la app que la necesita. Por ejemplo, `kiwi install kiwi-plugin-tor`
instala también kiwi-proxy. Cualquier otra palabra la trata kiwi como el nombre
de un programa, y comprueba con `command -v` si ese programa está presente.

## Una app, dos mitades { #one-app-two-halves }

Algunas apps son un único programa en `~/.local/bin`. Otras, como un kill
switch de VPN, se componen de un daemon que se ejecuta como root, **más** una
app de escritorio **más** una extensión de GNOME. Una app así tiene dos
mitades, una de usuario y otra de sistema, y cada mitad se instala con
privilegios distintos. El motivo es que **root nunca debe ejecutar un archivo
que el usuario pueda modificar**. La app declara sus partes y sus ámbitos en su
manifiesto:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Un catálogo incluye una app así una sola vez, y kiwi instala cada mitad en el
ámbito que le corresponde. Antes de pedirte la contraseña, kiwi te muestra el
`ROOT_REASON`.

| Pieza | Dónde | Por qué |
|---|---|---|
| `kiwi`, Kiwi Apps, apps de usuario | `~/.local` | no necesita root, y se conserva cuando el sistema cambia (rebase) a otra imagen ostree |
| la copia de kiwi propia de root | `/usr/local/bin`, clonada en `/var/lib/kiwi-updater/repos/` | root nunca ejecuta un archivo que tú puedas modificar |
| apps del sistema | `/var/lib`, `/etc` | en los sistemas ostree estos directorios se pueden escribir y pertenecen a root |
| listas | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | las entradas de la lista propia de una máquina tienen prioridad sobre cualquier catálogo |
| claves de firma fijadas | `/etc/kiwi-updater/signers/<app>` | consulta la sección siguiente |

kiwi nunca modifica nada en el `/usr` inmutable.

## Root, contraseñas y firmas { #root-passwords-and-signatures }

La tabla muestra qué acciones necesitan root y cuáles piden contraseña.

| | Necesita root | Pide contraseña |
|---|---|---|
| cualquier cosa del ámbito de usuario | no | no |
| **actualizar** una app del sistema | sí | **no**, si la versión está firmada con la clave que root ha fijado para esa app. **Sí**, si la versión no está firmada, y siempre en el modo `manual` |
| **instalar** o **desinstalar** una app del sistema | sí | sí |

Desde la versión 2.4.0 se aplican estas reglas:

- **Versiones firmadas.** Para cada app del sistema, root fija una clave de
  firma SSH. Fijar una clave significa recordarla y, a partir de ese momento,
  aceptar solo esa clave. Root fija la primera clave que ve para la app, lo que
  se conoce como confianza en el primer uso (trust on first use). Si una
  etiqueta de versión está firmada con la clave fijada, la actualización se
  instala sin contraseña. Si una versión no está firmada, kiwi te pide la
  contraseña y te avisa de que no ha podido verificarla. kiwi rechaza una
  etiqueta firmada con otra clave, y también una etiqueta sin firmar cuando las
  anteriores sí estaban firmadas. Las rechaza hasta que ejecutes
  `kiwi trust --system <app>`. Estas reglas se aplican al ámbito del sistema.
- **Root solo instala desde fuentes que figuran en sus propias listas.** Esas
  fuentes son `/etc/kiwi-updater/apps.list` y los catálogos registrados para
  root. Si una app viene de cualquier otra fuente, kiwi solo instala la mitad
  de usuario y te indica el comando `kiwi add --system <https-url>` que tienes
  que ejecutar. En ese caso, Kiwi Apps ofrece el botón *Register and Install*,
  que registra la fuente para root e instala la app.
- **Solo https.** kiwi rechaza las fuentes `http://` en todos los casos.

Las actualizaciones del sistema sin contraseña las hace un único programa
auxiliar, `/usr/local/libexec/kiwi-system-update`, que solo sirve para eso. Una
regla de polkit permite ejecutarlo a los usuarios del grupo `wheel` cuando su
sesión está activa. El programa auxiliar solo acepta nombres de apps, y un
nombre solo puede elegir una app de las listas propias de root.

## Actualizaciones en segundo plano { #background-updates }

Para las actualizaciones en segundo plano hay un solo temporizador, y es un
temporizador (timer) de usuario de systemd, así que se ejecuta con tu usuario y
no como root. `kiwi-updater.timer` ejecuta `kiwi update --all` seis horas
después de la última ejecución y diez minutos después del arranque, con un
pequeño retraso aleatorio. En esa ejecución, las mitades de usuario se
actualizan directamente, y las mitades de sistema, a través del programa
auxiliar descrito arriba. No hay ningún temporizador de root. En el modo
`manual`, el temporizador no actualiza las mitades de sistema: esperan hasta
que ejecutes `kiwi update` tú mismo.

## Confianza { #trust }

Al instalar una app, kiwi **ejecuta el `install.sh` del repositorio de esa
app**. Si la app declara el ámbito del sistema, kiwi ejecuta ese script **como
root**. Los catálogos están seleccionados, no auditados: alguien ha elegido las
apps, pero eso no significa que se haya revisado su código. Añade solo los
catálogos en los que confíes, igual que harías con un repositorio de paquetes.
Usa `kiwi info --installer`, `kiwi diff` y `kiwi pin` para ver qué hace una app
antes de decidirte. Una firma limita *quién puede publicar* una versión, pero
no dice nada sobre *qué hace la versión publicada*.

Queda una cosa prevista: un registro alojado de catálogos de confianza,
con el comando `kiwi catalog browse` y con las huellas de los firmantes de cada
entrada.
