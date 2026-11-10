# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop es un paquete de cuatro pequeñas herramientas de línea
de comandos para un escritorio Linux. `torlink` te da acceso por Tor a un
servicio de otra máquina, `pweb` comparte una carpeta por HTTPS,
`select-server` te deja elegir un host SSH en un menú y `tethering` ajusta el
TTL del tráfico de los dispositivos que comparten tu conexión.

- Repositorio: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Última versión: **v1.2.1**. Está en el [catálogo de Kiwi](catalogs.md), en el ámbito de usuario.

```bash
kiwi install kiwi-cli-tools-desktop   # o ./install.sh install, en ~/.local/bin
```

## `torlink`: acceder a una máquina por Tor { #torlink-reach-a-machine-over-tor }

Con `torlink` puedes acceder por la red Tor a cualquier servicio TCP de otra
máquina, como SSH, una interfaz web o una base de datos. Es un sustituto
sencillo de una VPN: ninguna de las dos máquinas necesita un puerto abierto, no
hace falta ninguna cuenta y no hay que mantener ningún servidor. Tor y socat
funcionan juntos en un único contenedor de Podman rootless, así que solo
necesitas Podman.

Una máquina que ofrece servicios se identifica por su dirección onion, que es
una dirección dentro de la red Tor. En esa máquina creas un **código de
invitación** para un peer, es decir, para la otra parte que debe tener acceso.
El peer acepta el código en la otra máquina. El código contiene una clave de
autorización de cliente de Tor, y sin ella nadie puede ver siquiera que el
servicio existe. Así que trata el código como una contraseña.

```bash
# máquina A: ofrecer SSH y una interfaz web a "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # muestra torlink1:…  (¡secreto!)

# máquina B: usarlos
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH por Tor
torlink connect alice web           # 127.0.0.1:2200 → la interfaz web de alice
torlink ssh-config >> ~/.ssh/config # después `ssh alice-tor`; `select-server tor` los muestra
```

Cada invitación es un servicio onion independiente que solo contiene los
servicios que indicaste en ella. Por eso `torlink revoke bob` retira ese acceso
para siempre. `torlink ls` muestra tus servicios, tus peers y tus redirecciones,
es decir, los puertos locales que llevan a los servicios de un peer. Tor solo
transporta TCP, y la primera conexión tarda un rato. El puerto SOCKS del
contenedor (19050) solo escucha en la interfaz de loopback. El estado de
`torlink`, incluidas tus claves onion, se guarda en `~/.local/share/torlink`, y
`torlink purge` lo borra.

## `pweb`: compartir una carpeta por HTTPS { #pweb-share-a-folder-over-https }

`pweb` sirve el **directorio actual** por HTTPS en un puerto libre elegido al
azar. Úsalo para pasar un archivo a otra máquina de la misma red. La primera
vez que se ejecuta crea un certificado autofirmado, y después lo reutiliza.
Mientras `pweb` está en marcha, cualquier máquina de la red local puede acceder
a la carpeta. Arráncalo en la carpeta que de verdad quieres compartir y
detenlo con Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: elegir un host SSH { #select-server-pick-an-ssh-host }

`select-server` muestra un menú numerado con todos los alias `Host` concretos
de tu `~/.ssh/config`, es decir, todos los que no son un patrón con comodines.
Eliges uno y se conecta a ese host. Para filtrar el menú, etiqueta tus hosts:
añade un comentario como `# tags: work prod` dentro del bloque `Host` y pasa
una etiqueta en la línea de comandos:

```
$ select-server work            # solo los hosts con la etiqueta "work"
$ select-server --tags          # las etiquetas que tienes
$ select-server -f other.conf   # otro archivo de configuración
```

## `tethering`: ajustar el TTL para los dispositivos conectados { #tethering-the-ttl-fix }

`tethering` sirve para cuando otros dispositivos usan la conexión a Internet de
esta máquina, lo que se conoce como tethering o compartir conexión. Algunas
operadoras cuentan los saltos de red del tráfico y así distinguen los
dispositivos conectados de la propia máquina. `tethering` pone el TTL a 64 en
todo el tráfico que llega por una interfaz. Para la operadora, el tráfico de
los dispositivos conectados parece entonces tráfico de la propia máquina. La
herramienta pide sudo y añade una regla `iptables` de tipo mangle. La regla
**no** sobrevive a un reinicio.

```
tethering            # elegir la interfaz, aplicar la regla
tethering --status
tethering --off
```
