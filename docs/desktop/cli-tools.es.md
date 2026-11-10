# kiwi-cli-tools-desktop

Cuatro pequeñas utilidades de línea de comandos para un escritorio Linux.

- Repositorio: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Última versión: **v1.2.1**. Está en el [catálogo de Kiwi](catalogs.md), ámbito de usuario.

```bash
kiwi install kiwi-cli-tools-desktop   # o ./install.sh install, en ~/.local/bin
```

## `torlink`: llegar a una máquina por Tor { #torlink-reach-a-machine-over-tor }

Una VPN de andar por casa: llega a cualquier servicio TCP (SSH, una interfaz web,
una base de datos) de otra máquina a través de Tor, sin puertos abiertos, sin
cuentas y sin servidor. Tor y socat se ejecutan en un único contenedor Podman sin
root, así que solo necesitas Podman.

Una dirección onion es la identidad. El lado que ofrece genera un **código de
invitación** para un par, y el otro lado lo acepta. El código lleva una clave de
autorización de cliente de Tor, así que el servicio es invisible para cualquiera
que no la tenga: trata el código como una contraseña.

```bash
# máquina A: ofrece SSH y una interfaz web a bob
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # imprime torlink1:…  (¡secreto!)

# máquina B: úsalos
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH por Tor
torlink connect alice web           # 127.0.0.1:2200 → alice's web UI
torlink ssh-config >> ~/.ssh/config # then `ssh alice-tor`; `select-server tor` lists them
```

Cada invitación es su propio servicio onion con solo los servicios que
enumeraste, así que `torlink revoke bob` retira ese acceso para siempre.
`torlink ls` muestra servicios, pares y reenvíos. Tor es solo TCP, y la primera
conexión tarda un rato. El puerto SOCKS del contenedor (19050) solo escucha en
loopback. El estado, incluidas tus claves onion, vive en
`~/.local/share/torlink`, y `torlink purge` lo borra.

## `pweb`: compartir una carpeta por HTTPS { #pweb-share-a-folder-over-https }

Sirve el **directorio actual** por HTTPS en un puerto libre aleatorio, para
pasar un archivo a otra máquina de la misma red. En la primera ejecución se crea
un certificado autofirmado que luego se reutiliza. Sirve a toda la LAN, así que
arráncalo en la carpeta que quieres compartir y detenlo con Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: elegir un host SSH { #select-server-pick-an-ssh-host }

Un menú numerado con cada alias `Host` concreto de tu `~/.ssh/config`. Elige uno
y se conecta. Etiqueta los hosts con un comentario `# tags: work prod` dentro del
bloque `Host` para filtrar:

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # las etiquetas que tienes
$ select-server -f other.conf   # otro archivo de configuración
```

## `tethering`: el arreglo del TTL { #tethering-the-ttl-fix }

Fija el TTL a 64 en el tráfico que llega por una interfaz, para que los
dispositivos que comparten la conexión a través de esta máquina parezcan tráfico
propio de la máquina ante un operador que cuenta saltos. Pide sudo, añade una
regla mangle de `iptables`, y la regla **no** sobrevive a un reinicio.

```
tethering            # elige la interfaz, fija la regla
tethering --status
tethering --off
```
