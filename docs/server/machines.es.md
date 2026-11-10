# Máquinas: instalar, aplicar, actualizar

En esta página se sigue a una máquina desde su entrada en el archivo fleet hasta
que se convierte en un sistema en marcha que se actualiza solo. kiwi-server construye una
imagen de instalación que instala el sistema operativo sin que nadie tenga que
estar delante del teclado. Después, con el comando `apply`, prepara la máquina
para su rol por SSH. A partir de ahí, la máquina instala sus actualizaciones por
su cuenta y solo se reinicia en las horas que tú permitas.

## Sistemas de destino { #targets }

El sistema de destino (`target`) es el sistema operativo que kiwi-server
instala en una máquina.

| Sistema de destino | Qué se instala | Medio de instalación |
|---|---|---|
| `coreos` | Fedora CoreOS, rama stable | La ISO live estándar, adaptada con la configuración de Ignition del host (Butane `fcos` 1.6.0). La instalación no necesita conexión de red |
| `ucore` | Fedora CoreOS, que después se pasa por sí solo (rebase) a una imagen `ghcr.io/ublue-os/ucore*`. Las imágenes son `ucore-minimal`, `ucore` y `ucore-hci`, también en sus variantes `-nvidia` / `-zfs`. El rebase funciona igual que el ejemplo de autorebase del propio uCore | La misma que para CoreOS, más las unidades de autorebase |
| `debian` | Debian stable (trixie), amd64 | La imagen netinst estándar con el preseed (el archivo con las respuestas para el instalador) dentro de su initrd, de modo que el instalador tiene sus respuestas desde la primera pregunta. Los archivos del host van en la imagen, en `/kiwi-server`. La imagen sigue arrancando tanto con BIOS como con UEFI |

En todos los sistemas de destino, el usuario administrador puede usar sudo sin
contraseña. SSH solo acepta claves, salvo que pongas `ssh_password_auth: true`.

## Medios de instalación { #install-media }

El primer comando construye la imagen de instalación (ISO) de un host. El
segundo la copia a una memoria USB.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- La ISO instala el sistema en el disco indicado en `disk:` **sin preguntar**, y
  borra todo lo que había en él.
  Cuando termina la instalación, **apaga la máquina**
  (`install.on_done: poweroff`, o `reboot` si prefieres que se reinicie).
  Etiqueta tus memorias USB.
- Por defecto, el medio de instalación contiene **solo el sistema base**: el
  nombre de host, los ajustes de red, el usuario administrador con las claves
  SSH y la política de actualizaciones. No contiene ningún secreto del stack. La
  máquina recibe su rol más tarde, cuando ejecutas `apply`.
- Con `--offline`, el rol completo y sus secretos van dentro de la ISO. Esto
  está pensado para una máquina a la que no se puede llegar por SSH. Quien
  tenga esa ISO tiene esos secretos.
- El instalador live muestra los discos de la máquina (`lsblk`) y tiene una
  shell, que acepta la contraseña de consola y las claves SSH de la fleet.

## Aplicar el rol { #apply }

`apply` prepara una máquina para su rol, por SSH.

```bash
kiwi-server apply fleet.yaml papaya                         # por nombre, dirección o dirección en la mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # la primera vez, por dirección
```

Primero, `apply` vuelve a generar la configuración del host, es decir, crea de
nuevo sus archivos a partir del archivo fleet. Después copia por SSH el script de rol del host a
`/var/lib/kiwi-server/role.sh`. El script de rol es el que prepara la máquina
para su rol, y `apply` lo ejecuta como root. A continuación, `apply` vincula el
disco a sus anillos Tang, que son servidores que permiten a una máquina cifrada
desbloquear su disco al arrancar. En un master, además, guarda el estado de
WireGuard junto con los secretos de la fleet. En una máquina Debian cifrada, el
primer `apply` sustituye la clave de un solo uso que se usó para la
instalación.

La conexión SSH usa la clave propia de la fleet y comprueba la clave de host de
la máquina con `secrets/known_hosts`. `apply` y `status` pueden llegar a una
máquina por su nombre, por su dirección estática, por la dirección pública del
master o por su dirección en la mesh, que es la que tiene la máquina dentro de
la red WireGuard privada. Solo usan una dirección cuya clave de host ya esté
registrada.

En un rol construido con módulos, el script de rol entrega el stack a
`kiwi-stack`. El stack es el conjunto de contenedores que la máquina ejecuta
para sus módulos. `kiwi-stack` sigue entonces estos pasos:

1. Instala o activa podman 4.4+ o docker, y se asegura de que exista el usuario
   de servicio. En Debian, podman se instala con `netavark`, `aardvark-dns` y
   `catatonit`.
2. Carga módulos del kernel y establece sysctls. Si el stack incluye Pi-hole,
   el aardvark-dns de podman pasa al puerto 5533, y el propio host resuelve los
   nombres a través del Pi-hole del stack. Además, añade la mesh a las redes de
   confianza de firewalld.
3. Rechaza un stack generado con un seed distinto. El seed es el secreto a
   partir del cual se generan las contraseñas de la fleet. Si el seed coincide,
   descomprime el stack en `docker_dir`. Instala los quadlets, que son las
   unidades de systemd de los contenedores, en `/etc/containers/systemd`, e
   instala las unidades del host. También elimina lo que hubiera instalado un
   módulo que ya no forma parte del stack.
4. Abre los puertos del stack en firewalld o en ufw, si alguno de los dos está
   activo.
5. Descarga todas las imágenes de contenedor y después arranca
   `kiwi-stack.service`, que a su vez arranca `kiwi-stack.target`.
6. Ejecuta `kiwi-stack verify`, que comprueba que todos los contenedores estén
   en marcha. Si alguno no lo está, el `apply` falla e indica el paso que ha
   fallado.

Si vuelves a aplicar la misma configuración generada, no cambia nada en la
máquina. Si aplicas una configuración generada nueva, se sustituye lo que haya
cambiado. Ten en cuenta que cada `apply` reinicia todos los contenedores del
stack, aunque no haya cambiado nada.

## Primer arranque { #first-boot }

En el primer arranque, `kiwi-role.service` ejecuta una vez el script de rol
`/var/lib/kiwi-server/role.sh`. Empieza cuando la red ya está activa y espera
hasta 120 segundos a que funcione el DNS. El archivo `role.done` marca el rol
como terminado, y solo se escribe cuando todos los contenedores están en
marcha. Si el script falla, deja el archivo `/var/lib/kiwi-server/role.failed`,
que indica el paso y el comando que fallaron, y el script se vuelve a ejecutar
en el siguiente arranque. El log está en `/var/log/kiwi-server-role.log`. En
uCore, el script de rol espera hasta que la máquina funciona con la imagen
firmada de uCore. Para volver a ejecutar el script a mano, usa
`sudo bash /var/lib/kiwi-server/role.sh --force`.

## Actualizaciones { #updates }

Las máquinas instalan continuamente las actualizaciones del sistema operativo.
El **reinicio** que las activa solo se produce dentro de la ventana de
mantenimiento que definas con `updates.days`, `time` y `length_minutes`, en hora
local.

| Sistema de destino | Instala las actualizaciones | Se reinicia |
|---|---|---|
| `coreos` | Zincati, de forma continua | solo dentro de la ventana (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` las descarga y las deja preparadas (staged) | `kiwi-staged-reboot.timer`, dentro de la ventana |
| `debian` | unattended-upgrades, a diario | `kiwi-reboot-if-required.timer`, dentro de la ventana, si alguna actualización exige reiniciar |

Con `updates.days: []`, el reinicio se permite cualquier día, y con
`updates.enabled: false` se desactivan las actualizaciones y los reinicios. Una
máquina cifrada no se reinicia sola si necesita un anillo Tang que alguien
tiene que reenviarle a mano, porque, si no, se quedaría esperando en el arranque
hasta que alguien la desbloqueara.

Los contenedores se actualizan con su propio calendario. Una vez por semana,
los domingos a las 00:00, `kiwi-stack update` ejecuta `podman auto-update`,
siempre que esté puesto `auto_update: registry`. El cliente de VPN se reinicia
todos los días a las 07:00, con lo que obtiene una nueva dirección de salida.
La dirección de salida es la dirección pública que ven los sitios web cuando el
tráfico sale de la VPN.

## En la máquina: `kiwi-stack` { #on-the-machine-kiwi-stack }

`kiwi-stack` es el comando que se ejecuta en la propia máquina para ver el
estado del stack y controlarlo.

```bash
sudo kiwi-stack status          # contenedores, unidades del host, verify
sudo kiwi-stack verify          # ¿están todos los contenedores en marcha?
sudo kiwi-stack logs [service]  # desde el journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # el cliente de VPN y todos los contenedores de su namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # con el módulo backup
sudo kiwi-stack apply DIR       # un paquete de stack, sin script de rol
```

Los archivos del stack están en `docker_dir` (por defecto,
`/home/user/docker`), y sus ajustes, en `/etc/kiwi-server/stack.env`. Las
unidades de systemd son `kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` y
`kiwi-stack-update.timer`, además de las que añada cada módulo.

## Qué contiene la configuración generada { #what-a-render-produces }

La configuración generada es lo que kiwi-server produce para un host a partir
del archivo fleet. Se escribe en `output/<host>/`, que contiene entonces estos
archivos.

| Archivo | Qué es |
|---|---|
| `<host>.role.sh` | El rol en un único script. Contiene los ajustes, el stack incrustado, el comando y la biblioteca de kiwi-stack, y el cuerpo del rol. El archivo tiene el modo 0600 |
| `<host>.stack/` | El paquete del stack, para que puedas revisarlo. Contiene `docker-compose.yml`, `quadlets/`, los archivos de configuración de los módulos, las unidades del host y `stack.sh`. También puedes instalarlo a mano con `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | En CoreOS y uCore, la configuración de Butane y de Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | En Debian, el archivo preseed y los archivos que este copia en la máquina |
| `<host>.iso` | La imagen de instalación, que instala sin que nadie tenga que estar delante del teclado |
