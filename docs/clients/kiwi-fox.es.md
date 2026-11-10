# kiwi-fox

kiwi-fox te da un navegador separado para cada red de cliente en la que
trabajas y para cada cuenta que gestionas. Un perfil del navegador para un
cliente llega a las consolas web de ese cliente a través de su conexión y no
puede salir por ningún otro camino. Para eso no necesitas ninguna conexión VPN en el
host.

Cada perfil es una identidad permanente. Tiene su propio almacenamiento,
ejecuta uno de tres navegadores en un contenedor de Podman rootless (un
contenedor que se ejecuta con tu propio usuario y sin permisos de root) y
normalmente usa un exit de [kiwi-proxy](kiwi-proxy.md). Un exit es una conexión
guardada con un nombre y con su propio contenedor, que va a un upstream (el
proxy al que se envía tu tráfico), como el proxy SOCKS5 de un cliente. Para cada exit, kiwi-proxy arranca un contenedor
gateway. La única ruta que sale del gateway lleva a ese upstream, y el gateway
incluye un resolvedor DNS que bloquea los dominios publicitarios.

- Repositorio: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Última versión: **v0.7.1**. Está en el [catálogo de Kiwi](../desktop/catalogs.md), en el ámbito de usuario.
- Los navegadores, que kiwi-fox llama motores, se descargan en tu máquina y
  nunca se redistribuyen. Camoufox (MPL-2.0) se descarga durante la
  instalación. Firefox y Tor Browser se descargan cuando los pides
  (`kiwi-fox engine fetch`), y se verifican sus firmas.

| Motor | Qué ve una página |
|---|---|
| **Camoufox** (predeterminado) | Un ordenador corriente con Windows 11 y su propia región, cuyos valores encajan todos entre sí. Esta huella digital (el conjunto de valores que una página puede leer de un navegador para reconocerlo después) es falsa y no cambia |
| **Firefox** | Mozilla Firefox sin modificar, que no falsea nada. Una página ve los valores reales de esta máquina. Aun así, la conexión pasa por el exit del perfil |
| **Tor Browser** | Tor Browser sin modificar, conectado a través de un exit del módulo tor. Cada sitio tiene su propio circuito (su propio camino por la red Tor), y los nombres `.onion` funcionan |

kiwi-fox es para quienes gestionan varias cuentas que son suyas o que están
autorizados a llevar, y no quieren que esas cuentas se puedan relacionar entre
sí por la huella digital del navegador o por la dirección IP.

## Instalación { #install }

```bash
kiwi install kiwi-fox      # instala también kiwi-proxy; o ./install.sh install
kiwi-fox setup             # imágenes, un motor de navegador de ~630 MB, datos de DNS; ejecuta también el setup de kiwi-proxy
kiwi-fox engine fetch --engine firefox     # o torbrowser: con la firma verificada
```

kiwi-fox necesita Podman rootless, kiwi-proxy, Python 3.12+, GTK4 con
libadwaita y `secret-tool`. Está pensado para una sesión de Wayland. Con X11
también funciona, pero el aislamiento es más débil. Para verificar Firefox y
Tor Browser hacen falta `gpg`/`gpgv`. Con el controlador propietario de
NVIDIA, kiwi-fox necesita además `nvidia-container-toolkit` con su
especificación CDI.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # un exit, definido una vez, en kiwi-proxy
kiwi-fox new work --exit client-a     # un perfil que lo usa: lo mide y genera una identidad que encaje
kiwi-fox new plain --no-proxy         # la conexión propia de esta máquina, sin aislar
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # o la app
kiwi-fox stop work
kiwi-fox check                        # ¿siguen siendo coherentes todos los perfiles?
kiwi-fox selfcheck work               # medir lo que ven las páginas y revisarlo
kiwi-fox-gui                          # "Kiwi Fox" en la cuadrícula de aplicaciones
```

Con `--desktop-entry`, un perfil tiene su propia entrada en la cuadrícula de
aplicaciones. Con etiquetas puedes agrupar los perfiles.

## Perfiles y exits { #profiles-and-exits }

Un perfil no es dueño de un exit: hace referencia a uno, y varios perfiles
pueden usar el mismo exit. Los perfiles que usan el mismo exit comparten su
gateway y, con él, un namespace de red, una dirección IP de salida y un
conjunto de circuitos de Tor. Las identidades que no deben compartir un exit
necesitan exits distintos. Un perfil creado con `--no-proxy` no tiene gateway:
su contenedor del navegador tiene una red propia y usa la conexión de esta
máquina. En ese caso no hay ningún aislamiento, es decir, su tráfico no está
limitado a una sola ruta.

El contenedor del navegador entra en el namespace de red del gateway. Se le
quitan todas las capabilities de Linux excepto `SYS_CHROOT`, que necesita el
propio sandbox de Firefox. El contenedor se ejecuta con `no-new-privileges`, y
el motor se monta en modo de solo lectura.

## Un perfil de Camoufox { #a-camoufox-profile }

Un perfil de Camoufox se presenta como el ordenador más corriente que existe,
porque los sistemas de detección señalan los valores poco habituales. Indica
una pantalla de 1920×1080, las fuentes que trae cualquier instalación de
Windows 11 y ninguna más, y la tarjeta gráfica real de esta máquina, con el
nombre que le da Firefox en Windows. La región, el idioma, la zona horaria y
las voces se ajustan al exit. Todo esto lo puedes cambiar después con
`kiwi-fox set`, `kiwi-fox webgl` y `kiwi-fox fonts`. Un cambio solo se guarda
si el perfil sigue siendo coherente, es decir, si sus valores siguen encajando
entre sí.

## Lo que no hace { #what-it-does-not-do }

kiwi-fox no promete que un perfil sea «indetectable». Los perfiles están
separados entre sí en su almacenamiento, en su dirección IP y en todos los
valores que el motor puede falsear. **No** lo están en los identificadores que
vienen del hardware y que son iguales en cualquier navegador. Los fotogramas
que de verdad dibuja la GPU y los tiempos del hardware vienen de la máquina
real, así que son iguales para todos los perfiles que hay en ella. El archivo
`docs/detection-notes.md` del repositorio documenta lo que se mide.

kiwi-fox no tiene automatización. No ejecuta bots ni crea cuentas en masa.
Está pensado solo para navegar de forma interactiva.
