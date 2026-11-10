# kiwi-proxy

Salidas SOCKS5 y VPN selladas en Podman sin root, para navegadores, herramientas
de pruebas, aplicaciones del host y máquinas de kiwi-server.

- Repositorio: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Última versión: **v0.7.3**. Está en el [catálogo de Kiwi](../desktop/catalogs.md), ámbito de usuario.
- Una CLI (`kiwi-proxy`), una app GTK4 (**Kiwi Proxy**) y unidades de usuario de
  systemd. Es el motor de proxy que antes vivía en kiwi-fox, separado para que
  sirva a más de una app.

Una **salida** es un upstream, con nombre: un SOCKS5 que te dieron, o uno que
produce un [módulo de proveedor](providers.md) (Tor, un túnel VPN, 9proxy,
Mysterium). Una salida son solo datos. Levantarla crea un **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Lo que se une al espacio de nombres del gateway (un navegador de kiwi-fox, una
box de kiwi-custodia, un contenedor de herramientas) no tiene más ruta que ese
upstream. Si el gateway muere, sus miembros pierden su ruta.

## Instalación { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox y kiwi-custodia lo traen consigo
kiwi-proxy setup             # la imagen del gateway, datos de DNS, imágenes de los módulos de proveedores
```

Necesita Podman sin root, Python 3.12+ con pydantic, y GTK4 + libadwaita para la
app. Las contraseñas van al llavero del escritorio (`secret-tool`), o a archivos
0600 en una máquina que no tenga llavero.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # una salida; todavía no se ejecuta nada
kiwi-proxy add tor-de --module tor --country de        # una salida de un módulo de proveedor
kiwi-proxy list
kiwi-proxy check client-a      # lo que el mundo ve a través de ella
kiwi-proxy up client-a         # levanta su gateway y lo mantiene levantado
kiwi-proxy down client-a       # lo derriba, junto con quien se haya unido
kiwi-proxy ps                  # gateways en marcha, sea cual sea la app que los inició
kiwi-proxy reap                # derriba los gateways que nadie usa
kiwi-proxy-gui                 # "Kiwi Proxy" in the app grid
```

Los endpoints son `socks5://user:pass@host:port`, `http://…`, `https://…` o el
formato del proveedor `host:port:user:pass`. `kiwi-proxy test ENDPOINT` prueba
uno sin crear nada.

### Salidas para aplicaciones del host { #exits-for-host-applications }

Cualquier programa del host puede usar una salida a través de un puerto SOCKS5
publicado, un puerto por salida:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Por defecto, el puerto escucha en `127.0.0.1`. Otra dirección necesita un nombre
de usuario (`--expose-user`) o un `--expose-open` explícito.
`systemctl --user enable --now kiwi-proxy@NAME` mantiene una salida levantada
desde el inicio de sesión.

### DNS { #dns }

- **Modo resolvedor** (el valor por defecto): dnscrypt-proxy resuelve por DoH a
  través de la salida (Google, Cloudflare, Quad9 o Mullvad como upstream), con
  listas de bloqueo (OISD) actualizadas a diario.
- **Modo remoto** (`--dns remote`): los nombres van al propio upstream, para Tor
  y los nombres `.onion`. Las listas de bloqueo se siguen aplicando.

### Reglas del gateway { #rules-of-the-gateway }

- UDP no sale por ninguna parte: ni QUIC, ni medios WebRTC, ni DNS en texto
  plano.
- Para el mundo, una salida es IPv4. Un nombre sin dirección IPv4 se rechaza.
- Un gateway que levantó un consumidor desaparece cuando se va su último
  miembro. Uno levantado con `kiwi-proxy up` se queda hasta `kiwi-proxy down`.
- Una salida, un gateway, cualquier número de miembros. Los miembros que deben
  seguir separados usan salidas distintas.

## La app { #the-app }

**Kiwi Proxy** añade y edita salidas (un SOCKS5 que te dieron, o un módulo de
proveedor, con una lista de países con búsqueda o un selector de nodos), las
levanta y las baja, ofrece una como puerto SOCKS5 en este ordenador y copia su
dirección, comprueba lo que ve el mundo, muestra quién se unió a un gateway y sus
logs, e instala y configura módulos de proveedores.

## En una máquina de kiwi-server { #on-a-kiwi-server-machine }

kiwi-proxy también lleva un módulo de kiwi-server que aloja salidas para toda la
malla (un gateway por salida, publicado en la dirección de malla del host).
Todavía no está en el árbol de kiwi-server y no se ha ejecutado en ninguna
máquina, como dice su documentación. Los módulos de proveedores son un mecanismo
de escritorio y no funcionan allí.

Para saber más: [arquitectura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumidores](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[sistema de plugins](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
