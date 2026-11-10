# Cómo funciona la red

Una Kiwi Network es una **malla WireGuard con un hub**, el *kiwi-master*. Todas
las demás máquinas (nodes en casa o en la oficina, portátiles, teléfonos,
routers) se conectan al master y se encuentran con las demás en la malla. Todo
se describe en un solo archivo fleet y lo construye
[kiwi-server](../server/index.md).

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

El rol `master` ejecuta cinco módulos. Pi-hole, Tor y nginx viven dentro del
espacio de nombres de red del servidor WireGuard y vuelven con él.

- **vpn-server** (wg-easy) es el punto de entrada de todos los clientes y nodes,
  y emite sus configuraciones WireGuard. kiwi-server puede crearlas por ti
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) se conecta a un proveedor comercial de VPN: Mullvad
  en el preset, cualquier proveedor de gluetun en general. La ruta por defecto
  del servidor WireGuard apunta a él, así que el tráfico de la malla sale por el
  proveedor, no por la dirección propia del master. Eso es el **doble salto**.
  Un master sin vpn-client sale directamente.
- **dns** (Pi-hole 6) responde en la dirección de malla del master,
  `10.8.0.1`. Consulta [DNS, nombres y certificados](dns.md).
- **tor** ofrece SOCKS5 en `10.8.0.1:9050` a los clientes de la malla, con nodos
  de entrada y de salida fijados a un conjunto de países (por defecto
  `de,ch,at,nl,fr`, `StrictNodes`).
- **reverse-proxy** (nginx) sirve las páginas de administración, `wg.<master>`
  y `pihole.<master>`, a los grupos de administración de la malla.

Un master también puede llevar un **relay nostr** y un **hub** para
[las personas de tu red](../people/hubs.md#on-a-kiwi-network), además de
Portainer y copias de seguridad.

### Qué es accesible desde Internet { #what-is-reachable-from-the-internet }

Por defecto, el master publica **un puerto**: WireGuard, UDP 51820. Las páginas
de administración solo responden a la malla. Dos ajustes añaden más:

- `reverse-proxy.public: true` publica el 80 y el 443, con certificados de
  Let's Encrypt para nombres fuera del dominio de la fleet. Todo lo demás sigue
  respondiendo solo a la malla, y las páginas de administración responden 403
  desde fuera. Esto es para un hub o un relay públicos.
- `vpn-server.unlock_relay` abre los puertos TCP de los
  [anillos Tang](../server/operations.md#encrypted-disks-and-unlocking) para
  máquinas detrás de NAT.

SSH se queda como lo tiene el sistema operativo (solo claves, por defecto).
kiwi-server lo usa para `apply` y `status`.

## Grupos de clientes { #client-groups }

Los clientes de wg-easy se reparten en **grupos** según su dirección. Cada grupo
decide a qué pueden llegar sus miembros:

| Grupo | Subred | Llega a | Ve a otros clientes | Páginas de administración |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | los nodes | no | no |
| `pentest` | `10.8.2.0/24` | nada de la malla | no | no |
| `devices` | `10.8.3.0/24` | todo | sí | sí |
| `routers` | `10.8.4.0/24` | todo | sí | no |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # un código QR para la app de WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # solo la malla pasa por el túnel
```

Todos los grupos pueden salir a Internet por la salida, salvo que pongas
`internet: false`. Los clientes que no están en ningún grupo (`10.8.0.x`) son la
malla simple: llegan a todo y ven las páginas de administración mientras
`admin_from_mesh` esté activado. Los grupos son un ajuste del módulo vpn-server
(`groups`), así que puedes cambiarlos o añadir los tuyos (`reach` admite `all`,
`nodes`, nombres de host, direcciones o subredes). El antiguo
`isolated_subnet` único sigue existiendo, pero está desactivado por defecto.

## Nodes { #nodes }

El vpn-client de un node no habla con una VPN comercial. Usa la configuración
WireGuard que el master emitió para él (`kiwi-server enroll` escribe
`secrets/<hostname>.conf`, y el node la recoge por sí solo). Un node no necesita
ningún puerto abierto en Internet: se conecta al master, así que funciona detrás
del NAT de un router doméstico.

El rol `node` tiene tres presets:

| Preset | En qué se convierte la máquina |
|---|---|
| `gateway` (por defecto) | Una puerta de enlace de LAN. Los clientes de la LAN que la usan como puerta de enlace predeterminada salen por la VPN y pueden llegar a la malla. Pi-hole sirve a la LAN (opcionalmente como su servidor DHCP). Transmission y JDownloader se ejecutan *dentro* del espacio de nombres de red del cliente VPN, así que no tienen ninguna ruta cuando el túnel está caído. Con nginx, Portainer y SFTP. |
| `cloud` | Nextcloud (con los contenedores del proyecto AIO, sin el contenedor maestro de AIO) con Collabora, más Vaultwarden, detrás de nginx, más Portainer |
| `minimal` | Solo el cliente VPN y nginx, para los módulos que tú elijas |

Los nodes también pueden ejecutar copias de seguridad, un servidor de copias de
seguridad, Tang y (para probar) OpenCloud, Immich y Paperless-ngx. Consulta la
[lista de módulos](../server/modules.md).

Los servicios de un node son accesibles en su LAN y en su **dirección de malla**
(p. ej., `10.8.0.25`). El tráfico de la malla hacia esa dirección en el 80 y el
443 se reenvía al proxy inverso.

## Nombres { #names }

Las máquinas toman su nombre del huerto: **los masters, de postres de fruta**
(`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`,
`cider`), y **los nodes, de frutas** (`papaya`, `lychee`, `guava`, `quince`,
`damson`), de modo que el tipo de máquina se lee en cada línea de log. Es una
convención, y cualquier nombre sirve. Los servicios cuelgan de su host:
`cloud.papaya.home`, `vault.papaya.home`, `wg.sorbet.home`. Consulta
[DNS, nombres y certificados](dns.md).

## Salidas { #ways-out }

Un master es un servidor WireGuard con una salida, y la salida tiene tres modos:

| Modo | Cómo llega la malla a Internet | Estado |
|---|---|---|
| **provider** | a través de una VPN comercial (gluetun): el doble salto, y el preset del master | construido |
| **direct** | directamente por el enlace de subida del propio master. Enumera los módulos del master sin `vpn-client` | construido |
| **master** | a través del *master de otra red*, como cliente de uno de sus grupos que puede llegar a Internet y a nada más: multi-hop | diseñado; necesita altas entre redes, es decir, federación |

Todo master ofrece además el SOCKS5 de Tor a la malla, sea cual sea su salida.

## Una malla por red { #one-mesh-per-network }

Cada red tiene su propia malla. Por defecto es `10.8.0.0/16`: masters y nodes en
`10.8.0.0/24`, luego guests `.1`, pentest `.2`, devices `.3` y routers `.4`. Una
segunda red toma otro rango, por ejemplo `10.9.0.0/16`, para que un dispositivo
que está en ambas pueda distinguirlas. Hoy el rango está repartido entre varios
ajustes (`mesh_subnet`, el `server_ip` del vpn-server, `wg_subnet`,
`wg_default_address` y `groups`, y `socks_policy_accept` de Tor), y el archivo
fleet los fija todos.

## Direccionamiento { #addressing }

| Qué | Por defecto |
|---|---|
| Toda la malla (enrutada en cada host) | `10.8.0.0/16` por defecto (`mesh_subnet`) |
| Clientes de wg-easy | `10.8.0.0/24`; el servidor es `10.8.0.1` |
| Grupos de clientes | `10.8.1.0/24` … `10.8.4.0/24` |
| Red del stack | `172.64.0.0/24` en un master, `172.128.0.0/24` en un node |
| MTU de WireGuard | `1376` (`wg_mtu`), medida con [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU del bridge del stack | `1500` (`bridge_mtu`) |

Cada host del stack enruta la malla a través de su cliente VPN (en el master, a
través del servidor WireGuard), así que el host y sus contenedores llegan a
todos los nodes.

## Mantenerla al día { #keeping-it-fresh }

Cada máquina recibe dos temporizadores de sus ajustes de stack: un **reinicio
diario de la VPN** (`07:00`, para tener una dirección de salida nueva) y una
**actualización semanal** (domingo a las 00:00, que ejecuta `podman auto-update`
mientras `auto_update: registry` esté puesto). El sistema operativo se actualiza
solo y solo se reinicia en [tu ventana](../server/machines.md#updates).

## Una LAN entera en la malla { #a-whole-lan-in-the-mesh }

Un router puede unirse a la malla como cliente WireGuard en el grupo `routers`, o
enviar la subred de la malla a un node gateway con una ruta estática. Así, cada
dispositivo de esa LAN llega a todos los nodes sin ejecutar WireGuard. Consulta
[Routers](routers.md).
