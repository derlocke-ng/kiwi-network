# Operaciones

El trabajo del día a día en una fleet en marcha, todo desde la máquina del
operador.

## Estado { #status }

```bash
kiwi-server status fleet.yaml            # todos los hosts
kiwi-server status fleet.yaml papaya        # uno
```

Cada máquina informa por SSH (solo lectura): su rol, su stack, los problemas (un
rol fallido, un contenedor parado), sus discos y si están cifrados o bloqueados,
sus copias de seguridad y cuánto les queda a sus certificados. Un node de copias
de seguridad informa además de su capacidad. La app Kiwi Server muestra lo mismo
en la *Overview* de cada host.

## Secretos { #secrets }

Todo lo secreto vive en `secrets/`, junto al archivo fleet: la semilla de la que
derivan todas las contraseñas generadas, la CA de la fleet, las configuraciones
WireGuard, las claves LUKS y las claves de host SSH.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ pasa a ser un solo archivo cifrado con age
kiwi-server secrets unlock fleet.yaml    # lo abre en memoria (--for 8h; 0 lo deja abierto)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` guarda una clave en el GNOME Keyring y muestra una **clave de
recuperación** una sola vez. Mientras el almacén está abierto, cualquier cosa que
se ejecute con tu usuario puede leerlo.

## Copia de seguridad de la propia fleet { #backing-up-the-fleet-itself }

Después de cada render o build correctos, el directorio de la fleet se cifra
(AES-256 con PBKDF2, 600.000 iteraciones) y se copia a los nodes que figuran en
`backup.hosts`, que guardan las diez más recientes. En una máquina nueva:

```bash
kiwi-server restore --from core@lychee.home  # recupera el directorio de la fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # o una copia en un directorio, cuando quieras
```

## Copia de seguridad de los datos de las máquinas { #backing-up-the-machines-data }

Dale a un node el módulo `backup-server` (un servidor REST de restic), y a cada
máquina que deba tener copia de seguridad el módulo `backup`, apuntando a él:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Cada noche a las 03:00 (dentro de los 15 minutos siguientes), restic envía,
cifrado, lo que cada módulo pide guardar. Cada máquina solo puede llegar a su
propio repositorio, y solo añadir a él. Por eso el borrado de instantáneas
antiguas se hace desde la máquina del operador:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # en la máquina
kiwi-server prune fleet.yaml            # conserva 7 diarias, 4 semanales, 6 mensuales
```

Se probó una restauración de node a node: las copias de seguridad de papaya en
lychee.

### En la próxima versión { #coming-in-the-next-release }

!!! info "En la rama `several-servers`"
    Este trabajo está subido a las ramas `several-servers` de kiwi-modules y
    kiwi-server, pero todavía no está fusionado ni publicado. Los varios
    servidores y la restauración automática se probaron en hardware. La
    comprobación de salud de la VPN, no.

- **Varios servidores de copias de seguridad.** `backup.servers` admite una
  lista, y cada servidor recibe una copia completa propia. Si un servidor falla,
  solo falta su copia. Una restauración toma la copia más reciente de cualquier
  servidor que la tenga, y `kiwi-stack snapshots` las enumera servidor por
  servidor. El `server` único sigue funcionando.
- **Una máquina reconstruida se restaura sola.** Si una máquina se encuentra en
  las copias de seguridad pero no ha hecho ninguna de ellas (una
  reconstrucción), restaura sola todos los módulos antes de su primera copia, y
  después hace copias como antes (`backup.restore:
  auto`, el valor por defecto). Con `hold` espera a `kiwi-stack restore` o a
  `kiwi-stack backup --new`.
- **Borrado con temporizador.** `kiwi-server prune fleet.yaml --every week` (o
  `day`) instala un temporizador de usuario de systemd en tu ordenador, el único
  sitio que guarda las claves que pueden borrar. Una ejecución perdida se hace en
  el siguiente inicio de sesión. `kiwi-server status` muestra cada copia de
  seguridad y avisa cuando un node de copias de seguridad lleva tres semanas sin
  limpiarse.
- **Una salida comercial atascada vuelve a empezar.** gluetun recibe una
  comprobación de salud. Tras cinco minutos sin estar sano, el contenedor se
  mata, y su siguiente arranque elige otro servidor.

## Discos cifrados y desbloqueo { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) se instala con una clave de un solo uso que
  escribes en el primer arranque (`secrets/luks/<host>.once`). El primer `apply`
  la sustituye por `secrets/luks/<host>.key`, y un master recibe además una clave
  de volumen nueva. Perder ese archivo de clave bloquea el disco, así que mantén
  una copia de seguridad de la fleet.
- **CoreOS / uCore** cifran al instalar mediante Ignition (con unos 4 GiB de RAM
  en el primer arranque).
- **Los anillos Tang** permiten que las máquinas cifradas se desbloqueen al
  arrancar sin que haya nadie presente. Un node ejecuta el módulo `tang` (cada
  anillo es un servidor Tang con sus propias claves, `infra` en el puerto 7500
  por defecto), y el bloque `unlock:` de un host vincula su disco a anillos con
  un umbral.
- **SSH en el initramfs** (`unlock.ssh: true`: dropbear en Debian, dracut-sshd en
  CoreOS) usa su propia clave restringida, `secrets/unlock_ed25519`, que solo
  puede ejecutar el desbloqueo.
- `kiwi-server unlock fleet.yaml <host>` reenvía un anillo a una máquina que
  espera en el arranque, y `--manual` entrega la propia clave. Un anillo
  `operator` se sirve desde tu propia máquina mientras hace falta.
  `vpn-server.unlock_relay` llega a máquinas detrás de NAT.

## MTU del túnel { #tunnel-mtu }

WireGuard añade sus propias cabeceras, así que un túnel transporta paquetes más
pequeños que la línea que tiene debajo, y una ruta móvil, más pequeños todavía.
Un paquete demasiado grande para algún enlace del camino se descarta o se
fragmenta, y las conexiones se atascan. Kiwi lo gestiona en tres capas:

- **Dos ajustes.** `wg_mtu` (por defecto **1376**, un múltiplo de 16 porque
  WireGuard rellena hasta 16) es la MTU de gluetun, de las configuraciones de
  cliente de wg-easy y de `wg0`. `bridge_mtu` (por defecto **1500**) es la MTU de
  la red del stack. `validate` rechaza un `wg_mtu` cuyo paquete rellenado más 80
  bytes de cabeceras no cabe en el bridge, y cualquier valor por debajo de 1280,
  el mínimo con el que funciona IPv6.
- **El MSS se limita en ambos sentidos** a `wg_mtu - 40`, en wg-easy y en el
  cliente VPN, así TCP nunca intenta un segmento que no puede pasar.
- **TCP sondea por sí mismo.** El cliente VPN se ejecuta con
  `net.ipv4.tcp_mtu_probing=1` y `tcp_base_mss=1024`, así una conexión que da
  con una ruta que descarta en silencio los paquetes grandes encuentra un tamaño
  que funciona en lugar de quedarse colgada.

### Medir una ruta: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # un node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # un dispositivo de secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # y escribe wg_mtu en el archivo fleet
```

La prueba envía pings con «no fragmentar» a través del túnel, desde dentro del
espacio de nombres que lo contiene. Mide un node desde su propio cliente VPN
(cuyo cortafuegos descarta los pings entrantes) y un dispositivo desde el
servidor WireGuard. Empieza con un ping normal, luego prueba cada múltiplo de 16
desde 1280 hacia arriba e informa del mayor que llega **entero**. Mientras hace
ping, lee los contadores de reensamblado del kernel, así una respuesta que se
fragmentó por el camino y se volvió a unir no cuenta como que cabe.

También dice qué fijar. Para un **dispositivo**, es el `MTU =` propio del
dispositivo en su configuración WireGuard, y no afecta a nadie más. Para un
**node**, es `wg_mtu` en ese node y en su master, que `--write` pone en el
archivo fleet (cambiando solo esas líneas). Un paquete que se fragmenta solo en
su camino de salida y que el otro extremo vuelve a unir no se puede ver desde
este extremo.

Los valores por defecto se midieron en la fleet de pruebas. Para un teléfono con
datos móviles, donde las rutas suelen ser solo IPv6 detrás de 464XLAT con
encapsulado anidado, mide el propio teléfono y baja su `MTU =` si la prueba lo
indica.

## VPS de netcup { #netcup-vpses }

```bash
kiwi-server vps login fleet.yaml         # inicio de sesión device-flow; el token va a secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wipe the server and install the host's ISO
```

`vps install` pregunta antes salvo que pases `--yes`. Rechaza una ISO que lleve
secretos del rol, un `disk:` incorrecto y el cifrado de disco de CoreOS con menos
de 3500 MiB de RAM.
