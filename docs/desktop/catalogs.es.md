# Catálogos y publicación de apps

Un catálogo es una lista de apps que kiwi-updater puede instalar. Es un
repositorio git, así que puedes leerlo, copiarlo y proponer cambios. Esta
página describe el catálogo de Kiwi, enseña a crear un catálogo propio, por
ejemplo para todos los escritorios que administras, y explica cómo publicar una
app para que otras personas puedan instalarla con kiwi.

## El catálogo de Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) es el
catálogo de apps de Kiwi Network. Se registra automáticamente al instalar
kiwi-updater. Para registrarlo a mano, ejecuta
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

La tabla recoge las apps del catálogo. La columna *Ámbitos* indica dónde se
instala cada app. El ámbito de usuario es tu carpeta personal. El ámbito del
sistema es una parte que pertenece a root.

| App | Versión | Ámbitos | Qué es |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | usuario | el propio actualizador |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | usuario + sistema | kill switch de VPN para GNOME. Es fail-closed: mientras la VPN no esté activa, todo el tráfico queda bloqueado |
| [ensconce](ensconce.md) | v2.5.0 | usuario | configura un Bluefin-DX recién instalado |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | usuario | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | usuario | exits para conexiones SOCKS5 y VPN. Un exit es un contenedor aislado en Podman rootless |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | usuario | identidades de navegador aisladas que usan exits de kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | usuario | boxes (contenedores con una distribución de Linux) cuyo tráfico solo sale por un exit |
| [kiwi-server](../server/index.md) | v2.42.0 | usuario | la herramienta con la que montas y mantienes tu propia red |
| [syncman](syncman.md) | v0.4.1 | usuario | sincroniza carpetas en ambos sentidos |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | usuario | guarda disposiciones de las pantallas en GNOME y cambia entre ellas |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | usuario | módulo de proveedor para kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | usuario | módulo de proveedor para kiwi-proxy: una VPN a través de gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | usuario | módulo de proveedor para kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | usuario | módulo de proveedor para kiwi-proxy: Mysterium |

Antes de cada comprobación y de cada actualización, kiwi descarga la versión
actual del catálogo. Por eso puedes gestionar las apps de todos tus escritorios
solo con git:

- **Para añadir una app**, añade su URL a `apps.list` y haz un commit.
- **Para fijar una app a una versión o volver a una anterior**, añade
  `ref=<tag>` al final de su línea. En una sola máquina, `kiwi pin <app> <tag>`
  hace lo mismo.
- **Para quitar una app**, borra su línea. Las copias ya instaladas siguen
  instaladas hasta que las desinstales.

## Tu propio catálogo { #your-own-catalog }

Un catálogo es un repositorio git con un archivo `apps.list`. También puede
contener un archivo `catalog.manifest`, en el que el catálogo se describe a sí
mismo:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: una línea por app, aunque tenga una mitad de root y una de usuario
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Una línea de `apps.list` puede llevar estas opciones detrás de la URL:

| Opción | Significado |
|---|---|
| `branch=<name>` | seguir una rama en lugar de las etiquetas de versión |
| `ref=<tag>` | quedarse exactamente en esta versión |
| `scope=user\|system` | instalar solo esa mitad de la app en las máquinas que usan esta lista. Esta opción es un *filtro*: no declara qué ámbitos tiene la app |

Además, cada máquina tiene su propia lista: `~/.config/kiwi-updater/apps.list`
para tu usuario y `/etc/kiwi-updater/apps.list` para root. Una entrada de la
lista propia de la máquina siempre tiene prioridad sobre un catálogo.
`kiwi add <url>` añade una línea a esa lista.

## Publicar una app { #publishing-an-app }

Para publicar una app, pon un archivo `kiwi.manifest` y un script `install.sh`
en el directorio raíz de tu repositorio. Tienes plantillas en el directorio
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
de kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system o ambos
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Un manifiesto puede tener más claves: `AUTHOR`, `CATEGORY`, `TAGS`,
`SCREENSHOTS`, `ABOUT` (un archivo que muestra Kiwi Apps), `DEPENDS` y
`ROOT_REASON`. Toda app con una mitad de sistema necesita `ROOT_REASON`.
`ICON=` indica un archivo SVG o PNG de 1 MiB como máximo dentro del
repositorio. La mayoría de las apps de Kiwi toman su icono de
[kiwi-icons](../project/brand.md).

!!! warning "Pon los comentarios en una línea aparte"
    Un valor llega hasta el final de su línea. Si escribes
    `COMPONENTS=cli  # … gui …`, el comentario pasa a formar parte del valor, y
    kiwi trata la app como si tuviera interfaz gráfica.

kiwi ejecuta tu instalador una vez **por cada ámbito que declara la app**, y le
pasa estas variables:

| Variable | Valor |
|---|---|
| `KIWI_SCOPE` | `user` o `system` |
| `KIWI_PREFIX` | `~/.local` o `/usr/local` |
| `KIWI_APP_DIR` | ruta absoluta del clon |
| `KIWI_ACTION` | `install`, `update` o `uninstall` |
| `KIWI_GUI` | `0` en una máquina headless (sin escritorio gráfico), o con `--cli-only` |
| `KIWI_PURGE` | `1` cuando el usuario ha pedido `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` va primero. El ámbito del sistema recibe una ruta de sistema fija |

El instalador de una app con los dos ámbitos tiene que comprobar `KIWI_SCOPE`
y, en cada ejecución, hacer solo el trabajo de esa mitad. Si el usuario no ha
pedido `--purge`, deja su configuración donde está.

**Publica cada versión como una etiqueta firmada.** Solo así se puede
actualizar una mitad de sistema sin pedir contraseña:

```bash
git config gpg.format ssh            # firmar con tu clave SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater incluye un flujo de trabajo para publicar versiones,
`templates/release.yml`. Solo publica una release de GitHub para una etiqueta
firmada con una clave que figure en `.github/allowed_signers`, y nunca crea
etiquetas por su cuenta. Por último, abre una pull request que añada tu URL al
catálogo. Es bienvenida cualquier app de código abierto que de verdad se pueda
usar sin cuenta, sin suscripción y sin rastreadores.

## Confianza { #trust }

El catálogo está **seleccionado, no auditado**. Que una app aparezca significa
que alguien pensó que merecía la pena, no que se haya revisado su código. Antes
de instalar una app que no conoces, lee lo que muestra `kiwi info <app>`.
Ejecuta `kiwi info --installer <app>` para ver exactamente qué se va a
ejecutar.
