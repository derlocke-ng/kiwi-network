# Cómo funciona la red

Una Kiwi Network une tus máquinas en una sola red privada, estén donde estén:
servidores en casa o en la oficina, portátiles, teléfonos y redes domésticas
enteras detrás de un router. Las máquinas se comunican entre sí como si
estuvieran en la misma red local, y solo una de ellas tiene que ser accesible
desde Internet. En esta página se explica cómo está montada esa red y para qué
sirve cada una de sus partes.

La red privada es una **mesh de WireGuard**. WireGuard es el software de VPN que
cifra las conexiones, y *la mesh* es el nombre que damos en estas páginas a la
red privada que comparten todas tus máquinas. La mesh tiene una máquina central,
el *kiwi-master*. Todas las demás (los nodes de casa o de la oficina, los
portátiles, los teléfonos, los routers) abren ellas mismas la conexión con el
master y, a partir de ahí, pueden llegar a las otras a través de la mesh. Toda
la red se describe en un único archivo, el archivo fleet (`fleet.yaml`), y
[kiwi-server](../server/index.md) la construye a partir de él.

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## El master { #the-master }

El master es la máquina a la que se conectan todas las demás. Su rol, `master`,
ejecuta los cinco módulos que se describen a continuación. Pi-hole, Tor y nginx
comparten el namespace de red del servidor WireGuard. Un namespace de red es el
conjunto propio de interfaces, direcciones y rutas de un contenedor, de modo que
estos tres servicios usan la red del servidor WireGuard en lugar de tener una
propia. Por eso se reinician siempre junto con él.

- **vpn-server** (wg-easy) es el servidor WireGuard. A él se conectan todos los
  clientes y todos los nodes, y es él quien emite sus configuraciones de
  WireGuard. kiwi-server puede crearlas por ti (`kiwi-server enroll`).
- **vpn-client** (gluetun) conecta el master con un proveedor de VPN comercial.
  El preset del master usa Mullvad, pero sirve cualquier proveedor compatible
  con gluetun. La ruta por defecto del servidor WireGuard apunta a este cliente
  de VPN, así que el tráfico de la mesh hacia Internet pasa por el proveedor, y
  los sitios web ven la dirección del proveedor y no la del master. Esta
  conexión es la *salida* del master, es decir, el camino por el que el tráfico
  de la mesh llega a Internet. Como el tráfico pasa por dos VPN seguidas,
  primero la tuya y después la del proveedor, esta configuración se llama
  **doble salto** (double hop). Un master sin vpn-client envía el tráfico a
  Internet directamente, desde su propia dirección.
- **dns** (Pi-hole 6) es el servidor DNS de la mesh. Responde en la dirección
  del master en la mesh, `10.8.0.1`. Consulta
  [DNS, nombres y certificados](dns.md).
- **tor** ofrece a los clientes de la mesh un proxy SOCKS5 en `10.8.0.1:9050`.
  Los nodos de entrada y de salida de Tor se limitan a una lista de países (por
  defecto `de,ch,at,nl,fr`, impuesta con `StrictNodes`).
- **reverse-proxy** (nginx) sirve las páginas de administración, es decir, las
  interfaces web de wg-easy y Pi-hole: `wg.<master>` y `pihole.<master>`. Solo
  las sirve dentro de la mesh, y solo a los clientes que tienen permiso para
  verlas (consulta «Grupos de clientes», más abajo).

En un master también pueden funcionar un **relay de nostr** y un **hub** para
[la gente de tu red](../people/hubs.md#on-a-kiwi-network). Un hub es el sitio
de una comunidad, que funciona en el navegador, y un relay de nostr es el tipo
de servidor a través del cual se sincronizan los hubs. A un master se le pueden
añadir, además, Portainer y las copias de seguridad.

### Qué es accesible desde Internet { #what-is-reachable-from-the-internet }

Por defecto, el master tiene **un solo puerto** abierto a Internet: el de
WireGuard, UDP 51820. Las páginas de administración solo se pueden abrir desde
dentro de la mesh. Hay dos ajustes que abren más puertos:

- `reverse-proxy.public: true` abre los puertos 80 y 443 y obtiene certificados
  de Let's Encrypt para los nombres que no pertenecen al dominio de la fleet.
  Todo lo demás sigue siendo accesible solo desde la mesh, y las páginas de
  administración responden con el error 403 a las peticiones que llegan de
  fuera. Este ajuste está pensado para un hub o un relay públicos.
- `vpn-server.unlock_relay` abre los puertos TCP de los
  [anillos Tang](../server/operations.md#encrypted-disks-and-unlocking) para
  las máquinas que están detrás de NAT. Tang es un servidor que permite a una
  máquina con el disco cifrado desbloquearlo al arrancar, y un anillo es un
  servidor Tang con sus propias claves.

kiwi-server no toca SSH: lo deja tal como lo configura el sistema operativo, lo
que por defecto significa que solo se puede entrar con claves. El propio
kiwi-server usa SSH para `apply` y `status`.

## Grupos de clientes { #client-groups }

Los clientes del servidor WireGuard (wg-easy) se reparten en **grupos** según su
dirección. Cada grupo determina a qué pueden acceder sus miembros:

| Grupo | Subred | Accede a | Ve a otros clientes | Páginas de administración |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | los nodes | no | no |
| `pentest` | `10.8.2.0/24` | nada de la mesh | no | no |
| `devices` | `10.8.3.0/24` | todo | sí | sí |
| `routers` | `10.8.4.0/24` | todo | sí | no |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # un código QR para la app de WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # solo la mesh pasa por el túnel
```

Los miembros de cualquier grupo pueden, además, salir a Internet por la salida
del master, salvo que pongas `internet: false` en el grupo. Un cliente cuya
dirección no pertenece a ningún grupo (`10.8.0.x`) es un miembro corriente de la
mesh: puede acceder a todo, y puede abrir las páginas de administración
mientras `admin_from_mesh` esté activado.

Los grupos son un ajuste del módulo vpn-server (`groups`), así que puedes
cambiarlos o añadir los tuyos. El ajuste `reach` de un grupo admite `all`,
`nodes`, nombres de host, direcciones o subredes. El ajuste antiguo
`isolated_subnet`, que definía un único grupo aislado, sigue existiendo, pero
viene desactivado por defecto.

## Nodes { #nodes }

Un node es una máquina de casa o de la oficina en la que funcionan tus
servicios. También tiene un módulo vpn-client, pero en un node este módulo no se
conecta a un proveedor de VPN comercial, sino al master, con la configuración
de WireGuard que el master ha emitido para él. `kiwi-server enroll` guarda esa
configuración en `secrets/<hostname>.conf`, y el node la usa sin que haya que
ajustar nada más. Un node no necesita ningún puerto abierto a Internet, porque
es él quien abre la conexión con el master. Por eso funciona también detrás del
NAT de un router doméstico.

El rol `node` tiene tres presets, es decir, tres listas de módulos ya
preparadas:

| Preset | En qué se convierte la máquina |
|---|---|
| `gateway` (por defecto) | Una puerta de enlace para la red local (LAN). Los dispositivos de la LAN que usan esta máquina como puerta de enlace predeterminada salen a Internet por la VPN y pueden acceder a la mesh. Pi-hole es el servidor DNS de la LAN y, si quieres, también su servidor DHCP. Los programas de descarga Transmission y JDownloader funcionan *dentro* del namespace de red del cliente de VPN, así que no tienen ninguna ruta mientras el túnel está caído. El preset incluye también nginx, Portainer y SFTP. |
| `cloud` | Tu propia nube: Nextcloud con Collabora para archivos, calendarios y documentos, y Vaultwarden para las contraseñas. Estos servicios están detrás de nginx, y también se incluye Portainer. Nextcloud se monta con los contenedores del proyecto AIO, pero sin el contenedor maestro de AIO. |
| `minimal` | Solo el cliente de VPN y nginx. Los módulos que quieras los añades tú. |

En un node también pueden funcionar las copias de seguridad, un servidor de
copias de seguridad y Tang. OpenCloud, Immich y Paperless-ngx están incluidos
para que los pruebes. Consulta la [lista de módulos](../server/modules.md).

A los servicios de un node se llega desde su LAN y también por la **dirección
del node en la mesh** (por ejemplo, `10.8.0.25`). El tráfico que llega desde la
mesh a esa dirección por los puertos 80 y 443 se reenvía al proxy inverso del
node.

## Nombres { #names }

Los nombres de las máquinas siguen una convención. **Los masters llevan nombres
de platos hechos con fruta** (`crumble`, `sorbet`, `compote`, `chutney`,
`strudel`, `cobbler`, `trifle`, `cider`) y **los nodes, nombres de frutas**
(`papaya`, `lychee`, `guava`, `quince`, `damson`). Así, en cualquier línea de un
log se ve enseguida qué tipo de máquina hay detrás de un nombre. No es más que
una convención: vale cualquier nombre. Cada servicio recibe un nombre que cuelga
del de la máquina en la que funciona: `cloud.papaya.home`, `vault.papaya.home`,
`wg.sorbet.home`. Consulta [DNS, nombres y certificados](dns.md).

## Cómo sale la mesh a Internet { #ways-out }

Un master es un servidor WireGuard con una salida, que es el camino por el que
el tráfico de la mesh llega a Internet. La salida tiene tres modos:

| Modo | Cómo sale la mesh a Internet | Estado |
|---|---|---|
| **provider** | Por un proveedor de VPN comercial (gluetun). Es el doble salto, y es lo que configura el preset del master. | implementado |
| **direct** | Directamente por la conexión a Internet del propio master. Para usar este modo, indica los módulos del master sin `vpn-client`. | implementado |
| **master** | Por *el master de otra red*. Tu master es cliente allí, en uno de sus grupos que puede salir a Internet y a nada más. A esto se le llama multi-hop. | diseñado; hace falta poder dar de alta máquinas entre redes, es decir, la federación |

Sea cual sea su modo de salida, todo master ofrece además a la mesh el proxy
SOCKS5 de Tor.

## Una mesh por red { #one-mesh-per-network }

Cada red tiene su propia mesh, con su propio rango de direcciones. El rango por
defecto es `10.8.0.0/16`. Los masters y los nodes están en `10.8.0.0/24`, y a
continuación van los grupos: guests en `.1`, pentest en `.2`, devices en `.3` y
routers en `.4`. Una segunda red usa otro rango, por ejemplo `10.9.0.0/16`, para
que un dispositivo que pertenece a las dos pueda distinguirlas. Hoy por hoy el
rango no se define en un solo ajuste, sino que está repartido entre varios:
`mesh_subnet`; `server_ip`, `wg_subnet`, `wg_default_address` y `groups` del
vpn-server; y `socks_policy_accept` de Tor. El archivo fleet los establece
todos.

## Direcciones { #addressing }

| Qué | Valor por defecto |
|---|---|
| Toda la mesh (enrutada en cada host) | `10.8.0.0/16` por defecto (`mesh_subnet`) |
| Clientes de wg-easy | `10.8.0.0/24`; el servidor es `10.8.0.1` |
| Grupos de clientes | `10.8.1.0/24` … `10.8.4.0/24` |
| Red del stack | `172.64.0.0/24` en un master, `172.128.0.0/24` en un node |
| MTU de WireGuard | `1376` (`wg_mtu`), medida con [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU del bridge del stack | `1500` (`bridge_mtu`) |

El stack de una máquina es el conjunto de contenedores que ejecutan sus módulos.
Toda máquina con un stack enruta el rango de direcciones de la mesh a través de
su cliente de VPN o, en el caso del master, a través del servidor WireGuard.
Así, la máquina y sus contenedores pueden llegar a cualquier node.

## Reinicios y actualizaciones automáticos { #keeping-it-fresh }

Cada máquina recibe dos temporizadores, que se configuran en los ajustes de su
stack. El primero **reinicia la VPN todos los días** a las `07:00`, con lo que
la máquina obtiene una nueva dirección de salida. El segundo es una
**actualización semanal**, los domingos a las 00:00, que ejecuta
`podman auto-update` siempre que esté puesto `auto_update: registry`. El sistema
operativo también se actualiza solo, y únicamente se reinicia en
[las horas que tú hayas permitido](../server/machines.md#updates).

## Toda una LAN en la mesh { #a-whole-lan-in-the-mesh }

Un router puede entrar en la mesh como cliente de WireGuard, en el grupo
`routers`. Otra posibilidad es que el router envíe el tráfico destinado a la
subred de la mesh a un node `gateway` mediante una ruta estática. En ambos
casos, todos los dispositivos de la LAN de ese router pueden llegar a cualquier
node sin tener que usar WireGuard ellos mismos. Consulta [Routers](routers.md).
