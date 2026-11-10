# kiwi-fox

Identidades de navegador aisladas en Podman sin root.

Cada perfil es una identidad persistente: su propio almacenamiento y,
normalmente, una salida de [kiwi-proxy](kiwi-proxy.md) con su gateway sellado y
su resolvedor con bloqueo de anuncios, en uno de tres navegadores. Para una red
de cliente, eso significa un navegador que llega a las consolas web del cliente
a través de la salida del cliente, y a nada más.

- Repositorio: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Última versión: **v0.7.1**. Está en el [catálogo de Kiwi](../desktop/catalogs.md), ámbito de usuario.
- Los motores se descargan, nunca se redistribuyen: Camoufox (MPL-2.0) en la
  configuración inicial, Firefox y Tor Browser bajo petición
  (`kiwi-fox engine fetch`), con la firma verificada.

| Motor | Lo que ve una página |
|---|---|
| **Camoufox** (por defecto) | una máquina Windows 11 corriente y coherente con su propia región: una huella congelada y falsificada |
| **Firefox** | Mozilla Firefox estándar, sin falsificar nada: los valores propios de esta máquina, a través de la misma salida sellada |
| **Tor Browser** | Tor Browser, sin modificar, a través de una salida del módulo tor, con un circuito por sitio y nombres `.onion` |

kiwi-fox es para personas que gestionan varias cuentas que son suyas o que están
autorizadas a gestionar, y que no quieren que esas cuentas queden vinculadas
entre sí por la huella del navegador o la IP.

## Instalación { #install }

```bash
kiwi install kiwi-fox      # trae consigo kiwi-proxy; o ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # o torbrowser: con la firma verificada
```

Necesita Podman sin root y kiwi-proxy, una sesión Wayland (X11 funciona con un
límite más débil), Python 3.12+, GTK4 + libadwaita, `secret-tool`, y
`gpg`/`gpgv` para verificar Firefox y Tor Browser. Con el controlador propietario
de NVIDIA, necesita además `nvidia-container-toolkit` con su especificación CDI.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # una salida, definida una vez, en kiwi-proxy
kiwi-fox new work --exit client-a     # un perfil en ella: la sondea y genera una identidad acorde
kiwi-fox new plain --no-proxy         # this machine's own connection, nothing sealed
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # o la app
kiwi-fox stop work
kiwi-fox check                        # ¿sigue siendo coherente cada perfil?
kiwi-fox selfcheck work               # mide lo que ven las páginas y luego lo audita
kiwi-fox-gui                          # "Kiwi Fox" in the app grid
```

`--desktop-entry` pone un perfil en la cuadrícula de aplicaciones, y las
etiquetas agrupan perfiles.

## Perfiles y salidas { #profiles-and-exits }

Un perfil hace referencia a una salida, y las salidas se comparten: los perfiles
de una misma salida comparten su gateway (un espacio de nombres, una IP de
salida, un conjunto de circuitos Tor). Las identidades que no deben compartir
salida usan salidas distintas. Con `--no-proxy` no hay gateway: el contenedor del
navegador tiene una red propia sobre la conexión de esta máquina, y nada queda
sellado.

El contenedor del navegador se une al espacio de nombres del gateway con todas
las capabilities eliminadas salvo `SYS_CHROOT` (la propia sandbox de Firefox la
necesita). Se ejecuta con `no-new-privileges`, y el motor se monta en solo
lectura.

## Un perfil de Camoufox { #a-camoufox-profile }

Es la máquina más común que existe, porque los valores raros son lo que marcan
los detectores: una pantalla de 1920×1080, las fuentes que tiene todo Windows 11
y ninguna más, y la tarjeta gráfica propia de esta máquina tal como la nombra
Firefox en Windows. La región, el idioma, la zona horaria y las voces siguen a la
salida. Todo se puede cambiar después (`kiwi-fox set`, `kiwi-fox webgl`,
`kiwi-fox fonts`), y los cambios solo se guardan si el resultado sigue siendo
coherente.

## Lo que no hace { #what-it-does-not-do }

No promete ser «indetectable». Los perfiles están aislados en cuanto a
almacenamiento, IP y toda superficie que el motor puede falsificar, pero **no**
frente a identificadores de hardware entre navegadores: los fotogramas que dibuja
realmente la GPU y los tiempos del hardware vienen de la máquina real y son los
mismos para todos los perfiles de ella. El `docs/detection-notes.md` del
repositorio documenta lo que se mide.

No hay automatización: ni bots ni creación masiva de cuentas. Es solo para
navegación interactiva.
