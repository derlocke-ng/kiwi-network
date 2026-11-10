# Máquinas: instalar, aplicar, actualizar

## Targets { #targets }

| Target | Qué se instala | Medio de instalación |
|---|---|---|
| `coreos` | Fedora CoreOS, flujo stable | la ISO live estándar, personalizada con el Ignition del host (Butane `fcos` 1.6.0); la instalación no necesita red |
| `ucore` | Fedora CoreOS que se rebasa sola a una imagen `ghcr.io/ublue-os/ucore*` (`ucore-minimal`, `ucore`, `ucore-hci`, con `-nvidia` / `-zfs`), como el propio ejemplo de autorebase de uCore | como para CoreOS, más las unidades de autorebase |
| `debian` | Debian stable (trixie), amd64 | la netinst estándar con el preseed en su initrd, para que responda desde la primera pregunta, y los archivos del host en `/kiwi-server`; se conservan el arranque BIOS y UEFI |

El usuario administrador tiene sudo sin contraseña en todas partes. SSH solo
acepta claves salvo que fijes `ssh_password_auth: true`.

## Medios de instalación { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Una ISO instala en `disk:` **sin preguntar** y luego **apaga la máquina**
  (`install.on_done: poweroff`, o `reboot`). Etiqueta tus memorias USB.
- Por defecto, los medios llevan **solo el sistema base**: nombre de host, red,
  usuario administrador y claves, política de actualizaciones. No llevan ninguno
  de los secretos del stack. El rol llega después con `apply`.
- `--offline` pone en la ISO todo el rol y sus secretos, para una máquina a la
  que SSH no llega. Quien tenga esa ISO tiene esos secretos.
- El instalador live muestra los discos (`lsblk`) y tiene una shell con la
  contraseña de consola y las claves de la fleet.

## Aplicar { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # por nombre, dirección o dirección de malla
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # la primera vez, por dirección
```

`apply` vuelve a renderizar el host y envía su script de rol por SSH a
`/var/lib/kiwi-server/role.sh`. Ejecuta el script como root, luego vincula el
disco a sus anillos Tang y, en un master, guarda el estado de WireGuard con los
secretos de la fleet. En una máquina Debian cifrada, el primer apply sustituye la
clave de instalación de un solo uso. SSH usa la clave propia de la fleet y
comprueba las claves de host contra `secrets/known_hosts`. `apply` y `status`
encuentran una máquina por su nombre, su dirección estática, la dirección pública
del master o su dirección de malla, pero solo direcciones cuya clave de host está
registrada.

En un rol de módulos, el script entrega el stack a `kiwi-stack`:

1. Instala o activa podman 4.4+ (en Debian con `netavark`, `aardvark-dns` y
   `catatonit`) o docker, y el usuario de servicio.
2. Carga módulos del kernel y fija sysctls. Con Pi-hole, aardvark-dns pasa al
   puerto 5533 y el host resuelve a través del Pi-hole del stack. Además confía
   en la malla en firewalld.
3. Rechaza un stack renderizado con otra semilla. Desempaqueta el stack en
   `docker_dir`, instala los quadlets en `/etc/containers/systemd` y las unidades
   del host, y quita lo que había instalado un módulo que ya no está.
4. Abre los puertos del stack en firewalld o ufw, si uno de ellos está activo.
5. Descarga todas las imágenes y luego arranca `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Ejecuta `kiwi-stack verify`: todos los contenedores deben estar en marcha, o
   el apply falla y dice qué paso falló.

Aplicar de nuevo el mismo render no cambia nada, y un render nuevo sustituye lo
que cambió. Eso sí, un nuevo apply reinicia todos los contenedores del stack.

## Primer arranque { #first-boot }

`kiwi-role.service` ejecuta `/var/lib/kiwi-server/role.sh` una vez, cuando la red
está activa (esperando hasta 120 segundos al DNS). `role.done` solo se escribe
cuando todos los contenedores están en marcha. Un fallo deja
`/var/lib/kiwi-server/role.failed` (el paso y el comando) y se reintenta en el
siguiente arranque. El log es `/var/log/kiwi-server-role.log`. En uCore, el rol
espera hasta que la imagen esté firmada.
`sudo bash /var/lib/kiwi-server/role.sh --force` lo vuelve a ejecutar.

## Actualizaciones { #updates }

Las actualizaciones se instalan de forma continua. El **reinicio** para
aplicarlas solo ocurre dentro de tu ventana (`updates.days`, `time`,
`length_minutes`, hora local):

| Target | Instala actualizaciones | Reinicia |
|---|---|---|
| `coreos` | Zincati, de forma continua | solo en la ventana (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` las prepara | `kiwi-staged-reboot.timer` en la ventana |
| `debian` | unattended-upgrades, a diario | `kiwi-reboot-if-required.timer` en la ventana, cuando hace falta uno |

`updates.days: []` significa cualquier día, y `updates.enabled: false` lo
desactiva todo. Una máquina cifrada cuyo anillo Tang hay que reenviarle no se
reinicia sola.

Los contenedores tienen su propio calendario: un `kiwi-stack update` semanal
(domingo a las 00:00) ejecuta `podman auto-update` mientras
`auto_update: registry` esté puesto. Un reinicio diario del cliente VPN a las
07:00 da una dirección de salida nueva.

## En la máquina: `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # contenedores, unidades del host, verify
sudo kiwi-stack verify          # ¿todos los contenedores en marcha?
sudo kiwi-stack logs [service]  # desde el journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # el cliente VPN y todos los contenedores de su espacio de nombres
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # con el módulo backup
sudo kiwi-stack apply DIR       # un paquete de stack, sin script de rol
```

El stack vive en `docker_dir` (por defecto `/home/user/docker`), y sus ajustes en
`/etc/kiwi-server/stack.env`. Las unidades son `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` y `kiwi-stack-update.timer`, más las que añada un
módulo.

## Qué produce un render { #what-a-render-produces }

`output/<host>/` contiene:

| Archivo | Qué |
|---|---|
| `<host>.role.sh` | el rol como un solo script: ajustes, el stack (incrustado), el comando y la biblioteca de kiwi-stack, y el cuerpo del rol. Modo 0600 |
| `<host>.stack/` | el paquete del stack, para revisarlo: `docker-compose.yml`, `quadlets/`, configuraciones de los módulos, unidades del host y `stack.sh`. `kiwi-stack apply` puede instalarlo a mano |
| `<host>.bu`, `<host>.ign` | CoreOS y uCore: Butane e Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: el preseed y los archivos que copia |
| `<host>.iso` | el instalador desatendido |
