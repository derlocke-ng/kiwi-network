# kiwi-proxy

kiwi-proxy es para quienes trabajan en las redes de muchos clientes y llegan a
cada una con su propia conexión VPN o SOCKS. Guardas cada conexión como un
**exit** con nombre y solo la activas cuando la necesitas. Cada exit está
separado de los demás, y un programa que usa un exit solo puede llegar a la red
a través de él. Así, diez clientes no significan diez conexiones VPN
funcionando a la vez en el host. Pueden usar un exit los navegadores, las
herramientas de pruebas, los programas del host y las máquinas de
kiwi-server. kiwi-proxy funciona en Podman rootless, es decir, en contenedores
que se ejecutan con tu propio usuario y sin permisos de root.

- Repositorio: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Última versión: **v0.7.3**. Está en el [catálogo de Kiwi](../desktop/catalogs.md), en el ámbito de usuario.
- Se compone de una herramienta de línea de comandos (`kiwi-proxy`), una app
  GTK4 (**Kiwi Proxy**) y unidades de usuario de systemd. Es el motor de proxy
  que antes formaba parte de kiwi-fox. Se separó en un proyecto propio para
  que lo pueda usar más de una app.

Un **exit** es una conexión a un upstream, guardada con un nombre. El upstream
es el proxy al que se envía el tráfico: o bien un proxy SOCKS5 que te han
dado, o bien uno que te crea un [módulo de proveedor](providers.md) a través
de Tor, de un túnel VPN, de 9proxy o de Mysterium. Un exit, por sí solo, no es
más que una entrada guardada: mientras no lo actives, no se ejecuta nada. Cuando activas
un exit, kiwi-proxy arranca para él un contenedor **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

El gateway tiene su propio namespace de red, es decir, un conjunto propio de
interfaces, direcciones, rutas y reglas de cortafuegos. Un navegador de
kiwi-fox, una box de kiwi-custodia o un contenedor de herramientas entra en ese
namespace y pasa a ser miembro del gateway. A partir de ahí, su única ruta
lleva al upstream del exit. Si el gateway se detiene, sus miembros se quedan
sin conexión. Esto es lo que se llama fail-closed: un fallo corta la conexión y
nunca abre otro camino.

## Instalación { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox y kiwi-custodia lo instalan también
kiwi-proxy setup             # la imagen del gateway, los datos de DNS, las imágenes de los módulos de proveedor
```

kiwi-proxy necesita Podman rootless y Python 3.12+ con pydantic. La app
necesita además GTK4 y libadwaita. Las contraseñas se guardan en el llavero del
escritorio mediante `secret-tool`. En una máquina sin llavero se guardan en
archivos con permisos 0600, que solo puede leer tu usuario.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # un exit; todavía no funciona nada
kiwi-proxy add tor-de --module tor --country de        # un exit de un módulo de proveedor
kiwi-proxy list
kiwi-proxy check client-a      # qué ve el mundo a través de él
kiwi-proxy up client-a         # activar su gateway y mantenerlo activo
kiwi-proxy down client-a       # detenerlo, junto con quien lo esté usando
kiwi-proxy ps                  # gateways en marcha, los haya arrancado la app que sea
kiwi-proxy reap                # detener los gateways que nadie usa
kiwi-proxy-gui                 # "Kiwi Proxy" en la cuadrícula de aplicaciones
```

Un endpoint es la dirección de un upstream. Puedes escribirlo como
`socks5://user:pass@host:port`, `http://…` o `https://…`, o en el formato del
proveedor, `host:port:user:pass`. `kiwi-proxy test ENDPOINT` prueba un
endpoint sin crear ningún exit.

### Exits para programas del host { #exits-for-host-applications }

Un programa del host no tiene que funcionar en un contenedor para usar un exit.
kiwi-proxy puede ofrecer un exit como puerto SOCKS5 en el host, con un puerto
por exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Por defecto, el puerto solo escucha en `127.0.0.1`. Si lo pones a escuchar en
otra dirección, tienes que definir un nombre de usuario con `--expose-user` o
permitir el acceso abierto de forma explícita con `--expose-open`. Para que un
exit esté activo desde que inicias sesión, ejecuta
`systemctl --user enable --now kiwi-proxy@NAME`.

### DNS { #dns }

- **El modo resolvedor** es el predeterminado. dnscrypt-proxy resuelve los
  nombres con DNS sobre HTTPS (DoH) y envía esas consultas a través del exit.
  El resolvedor DoH puede ser Google, Cloudflare, Quad9 o Mullvad. Se aplican
  listas de bloqueo (OISD), que se actualizan a diario.
- **El modo remoto** (`--dns remote`) pasa los nombres al upstream, que los
  resuelve él mismo. Este modo está pensado para Tor y los nombres `.onion`.
  Las listas de bloqueo también se aplican en este modo.

### Reglas del gateway { #rules-of-the-gateway }

- UDP no se reenvía. Eso significa que no hay QUIC, ni medios de WebRTC, ni
  DNS sin cifrar.
- Un exit solo llega al exterior por IPv4. Un nombre que no tiene dirección
  IPv4 se rechaza.
- Un gateway que ha arrancado otra app, como kiwi-fox o kiwi-custodia, se
  elimina cuando se va su último miembro. Un gateway que has arrancado tú con
  `kiwi-proxy up` sigue funcionando hasta que ejecutas `kiwi-proxy down`.
- Cada exit tiene exactamente un gateway, y puede tener cualquier número de
  miembros. Los miembros que tienen que estar separados entre sí usan exits
  distintos.

## La app { #the-app }

En la app **Kiwi Proxy** puedes añadir y editar exits, ya sea a partir de un
proxy SOCKS5 que te han dado o de un módulo de proveedor. Para un exit de un
módulo, eliges en una lista de países con búsqueda o en una lista de nodos.
Puedes activar y detener exits, ofrecer un exit como puerto SOCKS5 en este
ordenador y copiar su dirección, y comprobar qué ve el mundo exterior cuando te
conectas a través de él. La app también muestra qué miembros usan un gateway y
sus registros, y además instala y configura los módulos de proveedor.

## En una máquina de kiwi-server { #on-a-kiwi-server-machine }

El repositorio de kiwi-proxy contiene también un módulo para kiwi-server. Con
él, una máquina de kiwi-server ofrece exits a toda la mesh, es decir, a la red
WireGuard privada que comparten todas tus máquinas de kiwi-server. El módulo
ejecuta un gateway por cada exit y lo publica en la dirección de la máquina en
la mesh. Según su documentación, el módulo todavía no está en el código fuente
de kiwi-server y aún no se ha ejecutado en ninguna máquina. Los módulos de
proveedor solo funcionan en el escritorio y no se ejecutan en una máquina de
kiwi-server.

Para saber más: [arquitectura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumidores](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[sistema de plugins](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
