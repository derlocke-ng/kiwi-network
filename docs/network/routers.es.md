# Routers: una LAN entera en la malla

Un dispositivo de la malla resuelve todos los nombres de la fleet y llega a todos
los nodes. Una LAN detrás de un router puede hacer lo mismo sin que cada
dispositivo ejecute WireGuard, de una de estas dos formas:

- **El router es un cliente de la malla.** Ejecuta WireGuard con una
  configuración que emitió el wg-easy del master
  (`kiwi-server enroll fleet.yaml router --group routers`) y enruta la subred de
  la malla (`10.8.0.0/16`) hacia el túnel. Ese es el túnel *dividido* (split):
  solo el tráfico de la malla pasa por él. El túnel *completo* (full) lo envía
  todo, así que toda la LAN sale a Internet por la salida del master.
- **Una ruta estática a un node gateway.** El router no tiene túnel. Envía la
  subred de la malla a un node de la LAN que ejecuta el módulo `gateway`, que la
  reenvía a través de su cliente VPN.

En ambos casos, una sola regla DNS sustituye a las excepciones por host: el
dominio de la fleet (`*.home`) se reenvía al Pi-hole del master, que conoce todos
los nombres de host y de servicio. Nada más cambia en el DNS del router.

Lo que la LAN no puede hacer es llegar a un dispositivo *detrás de otro router*
por su dirección LAN. La malla solo transporta direcciones de malla, por diseño.

## OpenWrt { #openwrt }

kiwi-server escribe toda la configuración como un script `uci`:

```bash
# el router como cliente de la malla, con la configuración que emitió el wg-easy del master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: solo la malla
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: todo

# sin túnel en el router: una ruta estática al node gateway lychee
# (lychee necesita una dirección LAN estática en la fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copia la salida al router y ejecútala:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

El script instala el paquete de WireGuard si falta. Crea una interfaz `kiwi`
(cambia el nombre con `--name`), con el `wg_mtu` de la fleet como MTU y un peer
para el master y `route_allowed_ips`, una zona de cortafuegos hacia la que la LAN
puede reenviar (con enmascaramiento y MSS clamping) y el reenvío de dnsmasq para
el dominio de la fleet (`server=/home/10.8.0.1`). Con `--full`, dnsmasq envía
todas las consultas al Pi-hole del master. Cada sección tiene nombre, así que
volver a ejecutar el script sustituye lo que escribió antes.

## FritzBox { #fritzbox }

Fritz!OS tiene un cliente WireGuard y rutas estáticas, pero no reenvío DNS por
dominio, así que la regla DNS pasa a un node:

1. **Túnel:** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   conectar a otro servicio WireGuard → importar la configuración que emitió el
   master. Su `AllowedIPs` decide si es split o full.
2. **O una ruta estática:** Home Network → Network → Network Settings → IPv4
   Routes. Destino `10.8.0.0`, máscara de subred `255.255.0.0`, puerta de enlace
   la dirección LAN del node gateway.
3. **DNS:** apunta la LAN a un Pi-hole. O bien pon el node gateway como servidor
   DNS local, o bien deja que el Pi-hole del node sea el servidor DHCP de la LAN
   (ajustes `dns.dhcp_*` más el módulo dhcp-relay). El Pi-hole del node lleva los
   nombres de la fleet y reenvía el resto al master.

El túnel y las rutas estáticas pueden convivir. Para la malla gana el túnel.

## Cualquier otro router { #any-other-router }

Bastan tres datos. O le das al router una configuración de cliente WireGuard, o
añades una ruta estática para `10.8.0.0/16` hacia la dirección LAN del node
gateway. Después apuntas el DNS de la LAN a un Pi-hole que conozca la fleet, que
es cualquier node que ejecute el módulo `dns`. Los routers con dnsmasq por debajo
(DD-WRT, Tomato, el forwarder de pfSense) también aceptan el reenvío de una línea
`server=/home/10.8.0.1`.
