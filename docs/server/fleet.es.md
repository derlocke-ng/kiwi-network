# El archivo fleet

En el archivo fleet, `fleet.yaml`, describes todas las máquinas de tu Kiwi
Network. Para cada una indica qué sistema operativo recibe, para qué se usa y
cómo se configuran sus servicios. kiwi-server construye todas las máquinas a
partir de esta descripción: escribes una sola vez lo que quieres y no tienes que
configurar ninguna máquina a mano.

El archivo tiene dos claves. `defaults` contiene los ajustes que valen para
todos los hosts, y `hosts` tiene una entrada por máquina. Un ajuste en la
entrada de un host tiene prioridad sobre el mismo ajuste en `defaults`.
`kiwi-server init` escribe un archivo comentado del que puedes partir, y la
referencia completa está en
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Cada host tiene un **sistema de destino** (`target`), que es el sistema
operativo que se instala, y un **rol** (`role`), que es la tarea que la máquina
cumple después.

- `target` es `coreos`, `ucore` (el valor por defecto) o `debian`. Consulta [Máquinas](machines.md).
- `role` es `bare` (el valor por defecto), `master` o `node`. Consulta [Roles](roles.md).

## Ejemplo { #example }

Este archivo fleet describe tres máquinas. La primera es el master, la máquina a
la que se conectan todas las demás, en un VPS con Debian (un servidor virtual
alquilado). La segunda es un node `gateway`, que envía por la VPN el tráfico de
una red local. La tercera es un node `cloud`, en el que funcionan Nextcloud y
Vaultwarden.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya pasa a ser papaya.home; los servicios, cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # la ISO lo BORRA sin preguntar
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # el master, un VPS con Debian
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # la dirección a la que se conectan los clientes y los nodes

  lychee:                                # un node gateway
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # el lado de la LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # un node cloud con uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # para la primera cuenta; desactívalo después
```

El ejemplo no contiene ninguna contraseña de servicio. kiwi-server genera todas
las contraseñas que no pongas a partir del seed que hay en `secrets/seed`, y
`kiwi-server secrets show fleet.yaml papaya` muestra las contraseñas de ese
host.

Tampoco aparecen en el ejemplo los archivos de configuración de WireGuard de los
nodes. `kiwi-server enroll` guarda la configuración de un node en
`secrets/<hostname>.conf`, y el cliente de VPN del node la encuentra ahí sin que
haga falta ninguna entrada en el archivo fleet. De ese mismo archivo se lee la
dirección del node en la mesh. La mesh es la red WireGuard privada que comparten
todas tus máquinas, y la dirección en la mesh es la que tiene cada máquina
dentro de ella.

## Valores por defecto { #defaults }

Si ni tu bloque `defaults` ni un host definen una clave, kiwi-server usa el
valor incorporado que aparece en esta tabla.

| Clave | Valor por defecto |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Sin valor por defecto. `build` lo necesita, y tiene que empezar por `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Define un `password_hash` si quieres poder entrar desde la consola |
| `network` | `dhcp: true`. Para una dirección estática, define `address` (en notación CIDR), `gateway` y `dns`. O bien define un `iprange`, del que los hosts reciben sus direcciones en el orden en que aparecen en el archivo |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (o `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Los anillos Tang a los que está vinculado el disco. Un anillo es un servidor Tang, que permite a una máquina cifrada desbloquear su disco al arrancar (consulta [Administración](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | Los hosts en los que se guarda la copia de seguridad del directorio de la fleet, y cuántas copias se conservan (`hosts: []`, `keep: 10`) |
| `vps` | `server:` el id, el nombre o el apodo de un servidor de netcup |

## Cómo se combinan los ajustes { #how-settings-combine }

- Un host sustituye los valores por defecto **clave por clave**, así que solo
  tiene que nombrar las claves que cambian. Las listas `admin.ssh_keys`,
  `debian.packages`, `debian.kernel_arguments` y las listas `coreos.*` son la
  excepción: las entradas que pone un host en ellas se *añaden* a las de
  `defaults` en lugar de sustituirlas.
- Los roles que se construyen con módulos, `master` y `node`, guardan sus
  ajustes en un bloque con el nombre del rol (`master:` o `node:`). En ese
  bloque van primero los **ajustes del stack** y después **un bloque por
  módulo**. El stack es el conjunto de contenedores que una máquina ejecuta para
  sus módulos, y los ajustes del stack se aplican a todos ellos.
- Una lista `modules:` dentro de ese bloque **sustituye** la lista de módulos
  del preset. Un preset es una lista de módulos ya preparada. Los módulos que
  necesitan los de la lista se añaden automáticamente.
- Los **ajustes de archivo**, como los certificados y los archivos de
  configuración, se indican como rutas relativas al archivo fleet. kiwi-server
  copia el contenido de esos archivos en el script de rol del host, que es el
  script que prepara la máquina para su rol.
- Un ajuste que escribas sin valor recibe su valor por defecto. Si te equivocas
  al escribir una clave, kiwi-server da un error y te sugiere la clave que
  probablemente querías poner.

## Ajustes del stack { #stack-settings }

Los ajustes del stack se aplican a todo el stack de una máquina. Se escriben
directamente en el bloque del rol.

| Ajuste | Valor por defecto | Notas |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` o `minimal` |
| `runtime` | `podman` | Con `podman`, los contenedores funcionan como quadlets de podman, que son unidades de systemd para contenedores. Con `docker` se usa docker compose |
| `auto_update` | `registry` | `registry` ejecuta `podman auto-update` una vez por semana. Con `off`, las imágenes de los contenedores solo cambian cuando vuelves a aplicar el host |
| `docker_dir` | `/home/user/docker` | el directorio que contiene el stack y sus datos |
| `service_user` | el usuario administrador | el usuario propietario de los directorios de datos |
| `vpn_ip` | de la configuración de WireGuard | la dirección de la máquina en la mesh |
| `master_ip` | de la fleet | la dirección del master en la mesh |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | puedes medirlas con `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` en el master, `172.128.0.0/24` en un node | |
| `pub_iface` | según la ruta por defecto | la interfaz de red del lado de la LAN |
| `daily_vpn_restart` | `07:00` | con un valor vacío se desactiva el reinicio diario |
| `weekly_update` | `Sun *-*-* 00:00` | con un valor vacío se desactiva la actualización semanal |

`kiwi-server roles -v` y `kiwi-server modules -v` enumeran todos los ajustes con
su valor por defecto.

## Comprobar lo que has escrito { #checking-what-you-wrote }

kiwi-server puede revisar el archivo fleet por ti y mostrarte cómo interpreta
un host.

```bash
kiwi-server validate fleet.yaml          # errores y avisos
kiwi-server show fleet.yaml papaya          # la configuración efectiva de un host, con los secretos ocultos
```

kiwi-server también comprueba el dominio. Rechaza `.local` y avisa si usas
`.lan` o un dominio de nivel superior público (consulta
[DNS](../network/dns.md#names-servicehostnamehome)).

## Incorporar una máquina v1 { #taking-over-a-v1-machine }

Una máquina que funcionaba con uno de los antiguos stacks v1 puede pasar a la
fleet sin perder sus datos. El entorno de ejecución por defecto es ahora podman,
y el script de rol no detiene los contenedores de docker que sigan en marcha.
Así que pon `runtime: docker` o detén primero el stack antiguo. Después, pon en
`docker_subnet` la subred que usaba el stack antiguo y cambia el nombre de los
directorios de datos por los nuevos nombres de módulo (`kmvpn-server` →
`km-vpn-server`, `knvault` → `kn-vault`, …). Así, los contenedores conservan sus
direcciones y wg-easy conserva sus peers.
