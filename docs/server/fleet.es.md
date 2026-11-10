# El archivo fleet

`fleet.yaml` describe cada máquina que construye kiwi-server. Tiene dos claves:
`defaults`, que se aplica a todos los hosts, y `hosts`, con una entrada por
máquina. Todo lo que fija un host sustituye a los valores por defecto.
`kiwi-server init` escribe un punto de partida comentado, y la referencia
completa es
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Un host tiene un **target** (lo que se instala) y un **rol** (en lo que se
convierte):

- `target`: `coreos`, `ucore` (por defecto) o `debian`. Consulta [Máquinas](machines.md).
- `role`: `bare` (por defecto), `master` o `node`. Consulta [Roles](roles.md).

## Ejemplo { #example }

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya pasa a ser papaya.home; los servicios son cloud.papaya.home …
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
        wg_host: vpn.example.org     # a lo que se conectan clientes y nodes

  lychee:                                # un node gateway
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # el lado de la LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # un node cloud en uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # para la primera cuenta; desactívalo después
```

No contiene contraseñas de servicios. Cada contraseña que omites se genera a
partir de `secrets/seed`, y `kiwi-server secrets show fleet.yaml papaya` las
imprime. Tampoco se nombran las configuraciones WireGuard de los nodes:
`kiwi-server enroll` escribe `secrets/<hostname>.conf`, que cada node encuentra
por sí solo, y de ahí se lee la dirección de malla del node.

## Valores por defecto { #defaults }

| Clave | Por defecto |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | ninguno; obligatorio para `build`, debe empezar por `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; da un `password_hash` para la consola |
| `network` | `dhcp: true`; estática con `address` (CIDR), `gateway`, `dns`, o un `iprange` que reparte direcciones en el orden del archivo |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (o `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | anillos Tang a los que vincular el disco (consulta [Operaciones](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | a dónde se copia el directorio de la fleet (`hosts: []`, `keep: 10`) |
| `vps` | `server:` un id, nombre o apodo de servidor de netcup |

## Cómo se combinan los ajustes { #how-settings-combine }

- Los hosts sustituyen a los valores por defecto **clave por clave**. Las listas
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` y las listas
  `coreos.*`, en cambio, se *suman* a los valores por defecto.
- Un rol de módulos guarda sus ajustes en un bloque con el nombre del rol
  (`master:`, `node:`): primero los **ajustes del stack**, luego **un bloque por
  módulo**.
- `modules:` en ese bloque **sustituye** la lista de módulos del preset. Los
  módulos obligatorios se añaden solos.
- Los **ajustes de archivo** (certificados, configuraciones) son rutas relativas
  al archivo fleet. Su contenido se incrusta en el script de rol del host.
- Un ajuste dado sin valor significa el valor por defecto. Una clave mal escrita
  es un error con una sugerencia.

## Ajustes del stack { #stack-settings }

| Ajuste | Por defecto | Notas |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` o `minimal` |
| `runtime` | `podman` | quadlets de podman; `docker` ejecuta docker compose |
| `auto_update` | `registry` | `podman auto-update` semanal; `off`: las imágenes cambian con un apply |
| `docker_dir` | `/home/user/docker` | el stack y sus datos |
| `service_user` | el usuario administrador | es dueño de los directorios de datos |
| `vpn_ip` | de la configuración WireGuard | la dirección de malla de la máquina |
| `master_ip` | de la fleet | la dirección de malla del master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | mídela con `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | de la ruta por defecto | la interfaz de la LAN |
| `daily_vpn_restart` | `07:00` | vacío: nunca |
| `weekly_update` | `Sun *-*-* 00:00` | vacío: nunca |

`kiwi-server roles -v` y `kiwi-server modules -v` enumeran cada ajuste con su
valor por defecto.

## Comprobar lo que escribiste { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # errores y advertencias
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server también comprueba el dominio: `.local` se rechaza, y `.lan` y los
dominios de nivel superior públicos reciben una advertencia (consulta
[DNS](../network/dns.md#names-servicehostnamehome)).

## Tomar el control de una máquina v1 { #taking-over-a-v1-machine }

Una máquina que ejecutaba uno de los antiguos stacks v1 se puede tomar sin perder
datos. El runtime por defecto ahora es podman, y el script de rol no detiene los
contenedores de docker. Así que o bien fijas `runtime: docker`, o bien detienes
antes el stack antiguo. Después fija `docker_subnet` a lo que usaba el stack
antiguo y renombra los directorios de datos con los nombres de los módulos
(`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`, …). Los contenedores
conservan sus direcciones y wg-easy conserva sus peers.
