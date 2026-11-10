# Routers: toda una LAN en la mesh

En esta página se explica cómo conectar a tu Kiwi Network una red local (LAN)
entera, por ejemplo la de tu casa o la de la oficina, a través de su router. Un
dispositivo que está en la mesh, es decir, en la red WireGuard privada que
comparten tus máquinas, puede resolver todos los nombres de la fleet y llegar a
cualquier node. Los dispositivos de una LAN que está detrás de un router pueden
hacer lo mismo sin que cada uno de ellos tenga que usar WireGuard. Hay dos
maneras de conseguirlo:

- **El router es un cliente de la mesh.** El router usa WireGuard con una
  configuración emitida por wg-easy, el servidor WireGuard del master
  (`kiwi-server enroll fleet.yaml router --group routers`), y enruta la subred
  de la mesh (`10.8.0.0/16`) hacia el túnel. A esto se le llama túnel *split*,
  porque por él solo pasa el tráfico destinado a la mesh. Un túnel *full* lleva
  todo el tráfico, de modo que toda la LAN sale a Internet por la salida del
  master, que es su conexión con Internet.
- **El router tiene una ruta estática hacia un node `gateway`.** El router no
  tiene ningún túnel. Envía el tráfico destinado a la subred de la mesh a un
  node de la LAN que ejecuta el módulo `gateway`, y ese node lo reenvía a través
  de su cliente de VPN.

En ambos casos basta con una sola regla de DNS, sin entradas para cada host. La
regla reenvía las consultas del dominio de la fleet (`*.home`) al Pi-hole del
master, que conoce todos los nombres de host y de servicio. El resto del DNS del
router queda como estaba.

Hay una cosa que no funciona: un dispositivo de la LAN no puede llegar a un
dispositivo que está *detrás de otro router* usando la dirección que este tiene
en su LAN. Por la mesh solo circula tráfico dirigido a direcciones de la mesh, y
es así a propósito.

## OpenWrt { #openwrt }

Para OpenWrt, kiwi-server escribe toda la configuración en forma de script de
`uci`:

```bash
# el router como cliente de la mesh, con la configuración que emitió el wg-easy del master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: solo la mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: todo

# sin túnel en el router: una ruta estática hacia el node gateway lychee
# (lychee necesita una dirección de LAN estática en la fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copia la salida al router y ejecútala allí:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

El script instala el paquete de WireGuard si falta. Crea una interfaz llamada
`kiwi`, un nombre que puedes cambiar con `--name`. La interfaz usa como MTU el
valor `wg_mtu` de la fleet y tiene un único peer, el master. El peer se crea con
`route_allowed_ips`, así que OpenWrt añade las rutas por su cuenta. El script
crea también una zona del cortafuegos hacia la que la LAN puede reenviar
tráfico, con masquerading y MSS clamping. Por último, añade la regla de dnsmasq
que reenvía el dominio de la fleet al master (`server=/home/10.8.0.1`). Con
`--full`, dnsmasq envía todas las consultas DNS al Pi-hole del master. Cada
sección que escribe el script lleva un nombre, de modo que, si lo ejecutas otra
vez, sustituye lo que había escrito antes.

## FritzBox { #fritzbox }

Fritz!OS tiene un cliente de WireGuard y rutas estáticas, pero no puede reenviar
las consultas DNS de un solo dominio. Por eso, de la regla de DNS tiene que
encargarse un node:

1. **Túnel:** ve a Internet → Permit Access → VPN (WireGuard) → Add
   Connection, elige la opción para conectar con otro servicio WireGuard
   (connect to another WireGuard service) e importa la configuración que emitió
   el master. La línea `AllowedIPs` de esa
   configuración decide si el túnel es split o full.
2. **O bien una ruta estática:** ve a Home Network → Network → Network
   Settings → IPv4 Routes. Introduce `10.8.0.0` como destino, `255.255.0.0` como
   máscara de subred y, como puerta de enlace, la dirección de LAN del node
   `gateway`.
3. **DNS:** haz que la LAN use un Pi-hole como servidor DNS. Puedes indicar el
   node `gateway` como servidor DNS local, o dejar que el Pi-hole del node sea
   el servidor DHCP de la LAN (los ajustes `dns.dhcp_*` junto con el módulo
   dhcp-relay). El Pi-hole del node conoce los nombres de la fleet y reenvía
   todas las demás consultas al master.

Puedes usar el túnel y las rutas estáticas a la vez. En ese caso, el tráfico
destinado a la mesh va por el túnel.

## Cualquier otro router { #any-other-router }

Con cualquier otro router bastan tres cosas. Dale al router una configuración
de cliente de WireGuard, o bien añade una ruta estática para `10.8.0.0/16` que
apunte a la dirección de LAN del node `gateway`. Después, haz que la LAN use
como servidor DNS un Pi-hole que conozca la fleet. Cualquier node que ejecute
el módulo `dns` es uno de esos Pi-holes. Los routers basados en dnsmasq
(DD-WRT, Tomato, el forwarder de pfSense) aceptan también la regla de reenvío
de una sola línea `server=/home/10.8.0.1`.
