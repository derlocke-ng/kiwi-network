# kiwi-custodia

Contenedores de distribuciones en los que cada byte sale por una salida de
[kiwi-proxy](kiwi-proxy.md). *Piensa en distrobox, con la red bajo custodia.*

- Repositorio: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Última versión: **v0.2.3**. Está en el [catálogo de Kiwi](../desktop/catalogs.md), ámbito de usuario.
- Una CLI (`kiwi-custodia`) y una app GTK4 (**Kiwi Custodia**)

Una **box** es una distribución Linux en un contenedor Podman sin root, con un
home propio, unida al gateway sellado de una salida. Instala lo que quieras en
ella con su gestor de paquetes, ejecuta sus apps de escritorio en tu escritorio y
ponlas en la cuadrícula de aplicaciones. La box no tiene más ruta que la salida:
ni para `dnf`, ni para el cliente de un juego, ni para un binario estático que
nunca ha oído hablar de `$ALL_PROXY`. Si la salida desaparece, la box no tiene
ninguna ruta.

Eso hace de una box por red de cliente una forma limpia de trabajar: las
herramientas, las claves y el historial de shell del cliente A en una box, los
del cliente B en otra, y cada una llega solo a su propio cliente.

## Instalación { #install }

```bash
kiwi install kiwi-custodia   # trae consigo kiwi-proxy; o ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

Necesita Podman sin root con `catatonit`, kiwi-proxy, una sesión Wayland,
Python 3.12+ con pydantic, GTK4 + libadwaita para la app, y `/dev/net/tun`
utilizable por contenedores sin root. Las imágenes de las distribuciones se
descargan cuando una box arranca por primera vez. Vuelve a ejecutar
`kiwi-custodia setup` después de una actualización.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # una salida, definida una vez, en kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # una box en ella; el primer arranque instala una base
kiwi-custodia enter work                                   # una shell dentro: sudo dnf install …
kiwi-custodia run work -- firefox                          # un comando dentro
kiwi-custodia check work                                   # lo que el mundo ve desde dentro
kiwi-custodia apps work                                    # las apps de escritorio que tiene
kiwi-custodia export work firefox                          # "Firefox (work)" in the app grid
kiwi-custodia stop work
kiwi-custodia reset work                                   # vuelve a la imagen base; el home se queda
kiwi-custodia-gui
```

Distribuciones: `fedora` (por defecto), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine`, o `custom` con `--image`.

## Cómo se construye una box { #how-a-box-is-built }

Tres contenedores comparten un espacio de nombres de red: el **gateway** de
kiwi-proxy, un **sidecar de túnel** (tun2socks en un dispositivo TUN que se
convierte en la ruta por defecto) y la propia **box**. Todo el tráfico sale por
el TUN hacia el SOCKS5 de la salida, así que también quedan cubiertos los
programas que ignoran los ajustes de proxy.

- La box se ejecuta con tu usuario, con el mismo uid y `sudo` sin contraseña. Su
  home es `~/.local/share/kiwi-custodia/boxes/<id>/home`, uno por box en lugar de
  tu home real: dos boxes son dos identidades.
- Los cambios dentro de una box se guardan en una instantánea por box cuando se
  detiene, y `reset` vuelve a la imagen base.
- Se pasan Wayland, X11 (mediante Xwayland), PipeWire, el bus de sesión y
  `/dev/dri`, así que las apps de escritorio y los juegos funcionan.
- El DNS va a través del resolvedor del gateway (con bloqueo de anuncios), o a
  través del upstream en una salida con DNS remoto.

## Lo que no es { #what-it-is-not }

Una box es **custodia de red, no un sandbox respecto a tu escritorio**. Como
distrobox, recibe tu pantalla y tu bus de sesión, así que un programa de la box
puede mostrar ventanas, leer el portapapeles y usar los portales. Lo que no puede
hacer es llegar a la red salvo a través de su salida. UDP no tiene salida (ni
QUIC, ni medios WebRTC), e IPv6 no tiene ruta.

Las boxes que no deben compartir salida usan salidas distintas.
