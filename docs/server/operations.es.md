# Administración

Esta página trata del trabajo que viene después, cuando las máquinas ya están
instaladas y en marcha: comprobar su estado, guardar los secretos a buen
recaudo, hacer copia de seguridad de la fleet y de los datos de las máquinas,
desbloquear los discos cifrados, ajustar la MTU del túnel e instalar en un
servidor de netcup. Todo esto lo haces con kiwi-server desde tu propio
ordenador, el *equipo de administración*, donde están el archivo fleet y los
secretos.

## Estado { #status }

`kiwi-server status` muestra cómo están las máquinas de la fleet, todas o solo
la que indiques:

```bash
kiwi-server status fleet.yaml            # todos los hosts
kiwi-server status fleet.yaml papaya        # uno
```

kiwi-server se conecta a cada máquina por SSH y se limita a leer. Cada máquina
comunica su rol y su stack (el conjunto de contenedores y servicios que
ejecuta), los problemas que tenga, como un rol que ha fallado o un contenedor
detenido, sus discos y si están cifrados o bloqueados, sus copias de seguridad y
cuánto tiempo les queda de validez a sus certificados. Un node de copias de
seguridad informa además de su capacidad. La app Kiwi Server muestra la misma
información en la vista *Overview* de cada host.

## Secretos { #secrets }

Todo lo secreto se guarda en `secrets/`, el directorio que está junto al
archivo fleet. Contiene el seed del que se derivan todas las contraseñas
generadas, la autoridad de certificación (CA) propia de la fleet, las
configuraciones de WireGuard, las claves LUKS de los discos cifrados y las
claves de host SSH. kiwi-server puede mantener este directorio cifrado y
abrirlo solo mientras trabajas con él:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ pasa a ser un único archivo cifrado con age
kiwi-server secrets unlock fleet.yaml    # lo abre en memoria (--for 8h; 0 lo deja abierto)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # las contraseñas generadas de un host
```

`secrets init` crea el almacén cifrado. Guarda una clave en el llavero de GNOME
(GNOME Keyring) y te muestra una **clave de recuperación**. La clave de
recuperación solo se muestra una vez. Mientras el almacén está abierto,
cualquier programa que se ejecute con tu cuenta de usuario puede leerlo.

## Copia de seguridad de la propia fleet { #backing-up-the-fleet-itself }

El directorio de la fleet contiene el archivo fleet y `secrets/`, y kiwi-server
hace copia de seguridad de él por su cuenta. Después de cada generación o
construcción que sale bien (los dos pasos que crean la configuración de los
hosts y sus ISO de instalación), cifra el directorio de la fleet (AES-256 con
PBKDF2, 600 000 iteraciones) y lo copia a los nodes que figuran en
`backup.hosts`. Cada uno de esos nodes conserva las diez copias más recientes.
En un ordenador nuevo, recuperas el directorio de la fleet desde uno de esos
nodes. Además, puedes escribir una copia en el directorio que quieras cuando
quieras:

```bash
kiwi-server restore --from core@lychee.home  # recupera el directorio de la fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # o una copia en un directorio, en cualquier momento
```

## Copia de seguridad de los datos de las máquinas { #backing-up-the-machines-data }

Los datos de las máquinas se copian con restic, un programa de copias de
seguridad. Las copias las guarda un node. Ponle a ese node el módulo
`backup-server`, que ejecuta un servidor REST de restic. Cada máquina de la que
haya que hacer copia de seguridad recibe el módulo `backup`, con un ajuste que
apunta a ese servidor:

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

Cada noche a las 03:00, o hasta 15 minutos después, restic envía cifrados al
servidor de copias de seguridad los datos que cada módulo quiere conservar.
Cada máquina solo puede llegar a su propio repositorio en el servidor, y solo
puede añadir datos a él: no puede borrar nada. Por eso, el comando que elimina
los snapshots antiguos se ejecuta en tu propio ordenador. Un snapshot es lo que
restic llama al estado guardado en cada copia de seguridad. El primer comando
de abajo es para la propia máquina; el segundo, para tu ordenador:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # en la máquina
kiwi-server prune fleet.yaml            # conserva 7 diarios, 4 semanales y 6 mensuales
```

La restauración se ha probado entre dos nodes, restaurando en lychee las copias
de seguridad de papaya.

### En la próxima versión { #coming-in-the-next-release }

!!! info "En la rama `several-servers`"
    Este trabajo está subido a las ramas `several-servers` de kiwi-modules y de
    kiwi-server, pero todavía no se ha fusionado ni publicado. El uso de
    varios servidores de copias de seguridad y la restauración automática se
    han probado en hardware real. La comprobación de estado de la VPN, no.

- **Varios servidores de copias de seguridad.** `backup.servers` admite una
  lista de servidores, y cada uno recibe una copia completa propia. Si un
  servidor falla, solo se ve afectada su copia. Una restauración toma la copia
  más reciente del servidor que la tenga, y `kiwi-stack snapshots` muestra los
  snapshots servidor por servidor. El ajuste `server`, para un solo servidor,
  sigue funcionando.
- **Una máquina reconstruida se restaura sola.** Una máquina que se ha
  reconstruido encuentra en el servidor copias de seguridad de sí misma, aunque
  no ha hecho ninguna. En ese caso restaura por su cuenta todos los módulos
  antes de hacer su primera copia, y después sigue haciendo copias como antes.
  Es el comportamiento por defecto, `backup.restore: auto`. Con `hold`, la
  máquina espera hasta que ejecutes `kiwi-stack restore` o
  `kiwi-stack backup --new`.
- **Eliminar los snapshots antiguos con un temporizador.**
  `kiwi-server prune fleet.yaml --every week` (o `day`) instala un temporizador
  (timer) de usuario de systemd en tu ordenador, que es el único sitio donde
  están las claves con permiso para borrar. Si se salta una ejecución, se
  hace en el siguiente inicio de sesión. `kiwi-server status` muestra cada
  copia de seguridad y avisa cuando en un node de copias de seguridad llevan
  tres semanas sin eliminarse los snapshots antiguos.
- **Una conexión atascada con el proveedor de VPN comercial se recupera sola.**
  gluetun, el contenedor del cliente de VPN, recibe una comprobación de estado
  (health check), que revisa cada cierto tiempo si la conexión sigue
  funcionando. Cuando lleva cinco minutos fallando, se detiene el contenedor a la
  fuerza, y al volver a arrancar elige otro servidor.

## Discos cifrados y desbloqueo { #encrypted-disks-and-unlocking }

Un disco cifrado hay que desbloquearlo cada vez que la máquina arranca. En esta
sección se explica cómo cifra el disco cada sistema de destino (el sistema
operativo con el que se instala la máquina) y cómo se puede desbloquear, con
alguien delante o sin nadie.

- **Debian** (`debian.encrypt: true`) se instala con una clave de un solo uso,
  que escribes en el primer arranque. La encontrarás en
  `secrets/luks/<host>.once`. El primer `apply` la sustituye por
  `secrets/luks/<host>.key`, y en ese momento un master recibe además una nueva
  clave de volumen. Si pierdes ese archivo de clave, el disco se queda
  bloqueado, así que mantén al día la copia de seguridad de la fleet.
- **CoreOS / uCore** cifran el disco durante la instalación, mediante Ignition,
  la herramienta que configura una máquina CoreOS en su primer arranque. Para
  ello, la máquina necesita unos 4 GiB de RAM en el primer arranque.
- **Los anillos Tang** permiten a las máquinas cifradas desbloquear el disco al
  arrancar sin que nadie tenga que estar presente. Tang es un pequeño servidor
  al que una máquina pide ayuda por la red para desbloquear su disco. Un node
  ejecuta el módulo `tang`, y cada anillo es un servidor Tang con sus propias
  claves. Por defecto hay un anillo, `infra`, en el puerto 7500. El bloque
  `unlock:` de un host vincula su disco a uno o varios anillos y fija un umbral,
  es decir, el número de anillos que tienen que responder.
- **SSH en el initramfs** (`unlock.ssh: true`) te permite entrar en una máquina
  que está esperando a que se desbloquee su disco. El initramfs es el pequeño
  sistema que se ejecuta antes de que el disco esté abierto. Su servidor SSH es
  dropbear en Debian y dracut-sshd en CoreOS. Acepta una clave propia y
  restringida, `secrets/unlock_ed25519`, que solo sirve para desbloquear.
- `kiwi-server unlock fleet.yaml <host>` reenvía un anillo a una máquina que
  está esperando en el arranque, de modo que la máquina puede usar un anillo al
  que no llega por sí misma. Con `--manual`, entrega directamente la clave. Un
  anillo llamado `operator` se sirve desde tu propio ordenador mientras hace
  falta. `vpn-server.unlock_relay` hace que las máquinas detrás de NAT puedan
  llegar a un anillo a través del master.

## MTU del túnel { #tunnel-mtu }

La MTU es el tamaño máximo de paquete que un enlace de red transporta de una
sola pieza. WireGuard añade sus propias cabeceras a cada paquete, así que por
un túnel caben paquetes más pequeños que por la conexión sobre la que va, y por
una conexión móvil, más pequeños todavía. Un paquete demasiado grande para
alguno de los enlaces de su camino se descarta o se fragmenta, y las conexiones
se quedan colgadas. Kiwi lo resuelve de tres maneras:

- **Dos ajustes.** `wg_mtu` es la MTU de gluetun (el cliente de VPN), de las
  configuraciones de cliente que emite wg-easy (el servidor WireGuard) y de la
  interfaz WireGuard `wg0`. Su valor por defecto es **1376**, un múltiplo de 16,
  porque WireGuard rellena cada paquete hasta el siguiente múltiplo de 16
  bytes. `bridge_mtu` es la MTU de la red del stack, que conecta los
  contenedores de una máquina. Su valor por defecto es **1500**. `validate`
  rechaza un `wg_mtu` si el paquete rellenado, más 80 bytes de cabeceras, no
  cabe en el bridge. También rechaza cualquier valor por debajo de 1280, la MTU
  mínima con la que funciona IPv6.
- **El MSS se limita en los dos sentidos.** El MSS es la cantidad máxima de
  datos que TCP mete en un paquete. Tanto wg-easy como el cliente de VPN lo
  limitan a `wg_mtu - 40`, de modo que TCP nunca intenta enviar un segmento que
  no pueda pasar.
- **TCP encuentra por sí mismo un tamaño que funciona.** El cliente de VPN
  funciona con `net.ipv4.tcp_mtu_probing=1` y `tcp_base_mss=1024`. Cuando una
  conexión pasa por un camino que descarta sin avisar los paquetes grandes, TCP
  prueba con paquetes más pequeños hasta dar con un tamaño que funcione, en
  lugar de quedarse colgado.

### Medir un camino: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Para saber qué tamaño admite de verdad el camino hasta un node o un
dispositivo, mídelo:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # un node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # un dispositivo de secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # y además escribe wg_mtu en el archivo fleet
```

La medición envía pings por el túnel con el indicador de no fragmentar
(don't fragment) activado, para que no se puedan partir por el camino. Los
envía desde dentro del namespace de red en el que está el túnel. Un namespace
de red es un entorno de red separado dentro de una máquina, como el que tiene
un contenedor. Un node se mide desde su propio cliente de VPN, porque el
cortafuegos del cliente descarta los pings entrantes. Un dispositivo se mide
desde el servidor WireGuard. La medición empieza con un ping normal, luego
prueba todos los múltiplos de 16 a partir de 1280 hacia arriba e indica el
tamaño más grande que llega **entero**. Mientras hace los pings, lee los
contadores de reensamblado del kernel. Así, una respuesta que se ha partido por
el camino y se ha vuelto a juntar no cuenta como un tamaño que cabe.

La medición te dice también qué valor poner. Para un **dispositivo**, es la
línea `MTU =` de su propia configuración de WireGuard, y no afecta a nadie más.
Para un **node**, es `wg_mtu` en ese node y en su master. Con `--write`, la
medición escribe el valor en el archivo fleet y solo cambia esas líneas. Hay una
cosa que no se puede ver desde este extremo: un paquete que solo se parte a la
ida y que el otro extremo vuelve a juntar.

Los valores por defecto se midieron en la fleet de pruebas. Un teléfono con
datos móviles necesita su propia medición, porque los caminos móviles suelen
ser solo IPv6, detrás de 464XLAT y con encapsulados anidados. Mide el propio
teléfono y baja su `MTU =` si la medición lo indica.

## VPS de netcup { #netcup-vpses }

netcup es un proveedor de hosting, y hoy es el único en el que kiwi-server
puede instalar por su cuenta un servidor alquilado (un VPS). Lo hace mediante
la API del Server Control Panel de netcup. Hay otros proveedores de hosting
[previstos](roadmap.md#more-hosters-and-network-boot) en forma de plugins.

```bash
kiwi-server vps login fleet.yaml         # inicio de sesión por device flow; el token va a secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # borra el servidor e instala la ISO del host
```

`vps install` borra el servidor, así que antes pregunta, salvo que añadas
`--yes`. Se niega a instalar en tres casos: cuando la ISO lleva secretos del
rol, cuando `disk:` indica un disco equivocado y cuando hay que cifrar un disco
de CoreOS en un servidor con menos de 3500 MiB de RAM.
