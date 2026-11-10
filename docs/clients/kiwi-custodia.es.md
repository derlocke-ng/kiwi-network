# kiwi-custodia

kiwi-custodia te da un entorno Linux separado para cada red de cliente en la
que trabajas. Cada entorno es un contenedor con la distribución de Linux que
elijas, y todo su tráfico de red pasa por un exit de
[kiwi-proxy](kiwi-proxy.md). Un exit es una conexión guardada con un nombre y
con su propio contenedor, que va a un upstream, es decir, al proxy al que se
envía tu tráfico. Puede ser, por ejemplo, el proxy SOCKS5 que lleva a la red de
un cliente. Así puedes trabajar para diez clientes sin tener diez
conexiones VPN en el host, y las herramientas y claves de cada cliente se
quedan en el entorno de ese cliente. *Si conoces distrobox: es la misma idea,
pero el contenedor solo puede llegar a la red a través de su exit.*

- Repositorio: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Última versión: **v0.2.3**. Está en el [catálogo de Kiwi](../desktop/catalogs.md), en el ámbito de usuario.
- Tiene una herramienta de línea de comandos (`kiwi-custodia`) y una app GTK4 (**Kiwi Custodia**).

Una **box** es una distribución de Linux en un contenedor de Podman rootless,
es decir, un contenedor que se ejecuta con tu propio usuario y sin permisos de
root. La box tiene su propia carpeta personal y está conectada al gateway de un
exit. El gateway es el contenedor que kiwi-proxy arranca para un exit, y la
única ruta que sale de él lleva al upstream de ese exit. Dentro de la box
puedes instalar lo que quieras con el gestor de paquetes de la distribución.
Sus apps de escritorio se abren en tu escritorio, y puedes añadirlas a la
cuadrícula de aplicaciones. La box no tiene más ruta que el exit, y eso vale
para todos los programas que contiene: para `dnf`, para el cliente de un juego
y para un programa enlazado estáticamente que no hace caso de `$ALL_PROXY`. Si
el exit se detiene, la box se queda sin ninguna conexión.

Por eso es buena idea trabajar con una box para cada red de cliente. Las
herramientas, las claves y el historial de la shell del cliente A están en una
box, y los del cliente B, en otra, y cada box solo llega a su propio cliente.

## Instalación { #install }

```bash
kiwi install kiwi-custodia   # instala también kiwi-proxy; o ./install.sh install
kiwi-custodia setup          # la imagen del túnel, más la imagen del gateway y los datos de DNS de kiwi-proxy
```

kiwi-custodia necesita Podman rootless con `catatonit`, kiwi-proxy, una sesión
de Wayland y Python 3.12+ con pydantic. La app necesita GTK4 y libadwaita.
Además, los contenedores rootless tienen que poder usar `/dev/net/tun`. Las
imágenes de las distribuciones no se descargan durante la instalación: cada
imagen se descarga la primera vez que arranca una box que la usa. Después de
una actualización, vuelve a ejecutar `kiwi-custodia setup`.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # un exit, definido una vez, en kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # una box que lo usa; el primer arranque instala una base
kiwi-custodia enter work                                   # una shell dentro: sudo dnf install …
kiwi-custodia run work -- firefox                          # un comando dentro
kiwi-custodia check work                                   # qué ve el mundo desde dentro
kiwi-custodia apps work                                    # las apps de escritorio que tiene
kiwi-custodia export work firefox                          # "Firefox (work)" en la cuadrícula de aplicaciones
kiwi-custodia stop work
kiwi-custodia reset work                                   # volver a la imagen base; la carpeta personal se queda
kiwi-custodia-gui
```

Las distribuciones disponibles son `fedora` (la predeterminada),
`fedora-toolbox`, `ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`,
`kali`, `arch`, `arch-toolbox`, `opensuse`, `rocky` y `alpine`. También puedes
elegir `custom` e indicar tú una imagen con `--image`.

## Cómo está hecha una box { #how-a-box-is-built }

Una box en marcha se compone de tres contenedores que comparten un namespace
de red, es decir, las mismas interfaces de red, rutas y reglas de cortafuegos.
El primero es el **gateway** de kiwi-proxy. El segundo es un **sidecar de
túnel**, un contenedor auxiliar que ejecuta tun2socks sobre un dispositivo TUN.
Un dispositivo TUN es una interfaz de red virtual, y aquí se convierte en la
ruta por defecto. El tercer contenedor es la propia **box**. Todo el tráfico de
la box entra en el dispositivo TUN y de ahí va al proxy SOCKS5 del exit. Esto
funciona mediante la ruta por defecto y no mediante ajustes de proxy, así que
también quedan cubiertos los programas que no hacen caso de esos ajustes.

- La box se ejecuta con tu usuario, con el mismo uid, y dentro de ella `sudo`
  funciona sin contraseña. Su carpeta personal es
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Cada box tiene su propia
  carpeta personal y no usa la tuya de verdad, así que dos boxes son dos
  identidades separadas.
- Cuando una box se detiene, los cambios hechos dentro se guardan en un
  snapshot que pertenece a esa box. `reset` devuelve la box a la imagen base.
- Wayland, X11 (a través de Xwayland), PipeWire, el bus de sesión y `/dev/dri`
  están disponibles dentro de la box, para que funcionen las apps de escritorio
  y los juegos.
- Las consultas DNS las responde el resolvedor del gateway, que además bloquea
  los dominios publicitarios. En un exit que usa DNS remoto, es el upstream el
  que resuelve los nombres.

## Lo que no es { #what-it-is-not }

Una box **limita la red. No es un sandbox que proteja tu escritorio de los
programas que hay dentro.** Igual que un contenedor de distrobox, la box tiene
acceso a tu pantalla y a tu bus de sesión. Por eso, un programa de la box
puede mostrar ventanas, leer el portapapeles y usar los portales del
escritorio. Lo que no puede es llegar a la red de ninguna otra forma que no sea
su exit. UDP no se reenvía, así que QUIC y los medios de WebRTC no funcionan, y
no hay ruta para IPv6.

Las boxes que usan el mismo exit lo comparten. Las boxes que tienen que estar
separadas entre sí necesitan exits distintos.
