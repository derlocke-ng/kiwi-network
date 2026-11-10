# Catálogos y publicación de apps

## El catálogo de Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) es el
catálogo de apps de la Kiwi Network. La instalación de kiwi-updater lo registra,
y `kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` lo registra
a mano.

| App | Versión | Ámbitos | Qué es |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | usuario | el propio actualizador |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | usuario + sistema | kill switch de VPN que falla cerrado para GNOME |
| [ensconce](ensconce.md) | v2.5.0 | usuario | configuración posterior a la instalación para Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | usuario | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | usuario | salidas SOCKS5/VPN selladas en Podman sin root |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | usuario | identidades de navegador aisladas en salidas de kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | usuario | distro boxes cuyo tráfico solo sale por una salida |
| [kiwi-server](../server/index.md) | v2.42.0 | usuario | construye y gestiona tu propia red |
| [syncman](syncman.md) | v0.4.1 | usuario | sincronización de carpetas en ambos sentidos |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | usuario | distribuciones de pantallas para GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | usuario | proveedor de kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | usuario | proveedor de kiwi-proxy: una VPN a través de gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | usuario | proveedor de kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | usuario | proveedor de kiwi-proxy: Mysterium |

kiwi sincroniza el catálogo antes de cada comprobación y actualización, así que
gestionar una flota de escritorios es simplemente git:

- **añadir una app**: añade su URL a `apps.list` y haz commit;
- **fijar o volver atrás**: añade `ref=<tag>` a su línea (en una sola máquina,
  `kiwi pin <app> <tag>` hace lo mismo);
- **quitarla**: borra la línea (las copias instaladas se quedan hasta que las
  desinstales).

## Tu propio catálogo { #your-own-catalog }

Un catálogo es un repo git con un `apps.list` y, opcionalmente, un
`catalog.manifest` que lo describe:

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

| Opción | Significado |
|---|---|
| `branch=<name>` | sigue una rama en lugar de los tags de versión |
| `ref=<tag>` | fija una versión exacta |
| `scope=user\|system` | instala solo esa mitad en las máquinas que usan esta lista. Es un *filtro*, no una declaración |

La lista propia de una máquina (`~/.config/kiwi-updater/apps.list`, o
`/etc/kiwi-updater/apps.list` para root) siempre gana a un catálogo.
`kiwi add <url>` le añade una línea.

## Publicar una app { #publishing-an-app }

Pon un `kiwi.manifest` y un `install.sh` en la raíz de tu repo. Hay plantillas en
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
de kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Otras claves: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (un archivo
que muestra Kiwi Apps), `DEPENDS` y, para todo lo que tenga una mitad de sistema,
`ROOT_REASON`. `ICON=` es un SVG o PNG de como mucho 1 MiB dentro del repo. La
mayoría de las apps de Kiwi toman el suyo de [kiwi-icons](../project/brand.md).

!!! warning "Los comentarios van en su propia línea"
    Un valor llega hasta el final de la línea. `COMPONENTS=cli  # … gui …` hace
    que el comentario forme parte del valor, y entonces la app se trata como si
    tuviera interfaz gráfica.

kiwi ejecuta tu instalador una vez **por cada ámbito declarado**, con:

| Variable | Valor |
|---|---|
| `KIWI_SCOPE` | `user` o `system` |
| `KIWI_PREFIX` | `~/.local` o `/usr/local` |
| `KIWI_APP_DIR` | ruta absoluta del clon |
| `KIWI_ACTION` | `install`, `update` o `uninstall` |
| `KIWI_GUI` | `0` en una máquina sin pantalla, o con `--cli-only` |
| `KIWI_PURGE` | `1` cuando el usuario pidió `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` primero; una ruta de sistema fija para el ámbito de sistema |

Un instalador de doble ámbito se bifurca según `KIWI_SCOPE` y cada vez hace solo
esa mitad. Sin `--purge`, deja la configuración del usuario donde está.

**Publica con un tag firmado**, para que una mitad de sistema se actualice sin
contraseña:

```bash
git config gpg.format ssh            # firma con tu clave SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

El `templates/release.yml` de kiwi-updater solo publica una release de GitHub
para un tag firmado por una clave de `.github/allowed_signers`, y nunca crea tags
por sí mismo. Después abre una pull request que añada tu URL al catálogo. Todo lo
que sea de código abierto y realmente usable sin cuenta, sin suscripción y sin
rastreador es bienvenido.

## Confianza { #trust }

El catálogo está **seleccionado, no auditado**. Estar en la lista significa que
alguien pensó que merecía la pena tener la app, no que se haya revisado su
código. Lee `kiwi info <app>` antes de instalar algo que no conozcas ya, y
`kiwi info --installer <app>` para ver exactamente qué se va a ejecutar.
