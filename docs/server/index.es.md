# kiwi-server

kiwi-server crea y gestiona una Kiwi Network. Describes cada máquina en un solo
`fleet.yaml`. kiwi-server genera una **ISO de instalación desatendida** para cada
host, que instala Fedora CoreOS, uCore o Debian y apaga la máquina. Después
**aplica** el rol por SSH y convierte la máquina en un `kiwi-master` o un
`kiwi-node`. A partir de ahí sigue trabajando con la fleet: da de alta clientes
WireGuard, lee el estado de salud de cada máquina, guarda los secretos, hace
copias de seguridad de la fleet y desbloquea discos cifrados.

Tiene una CLI, `kiwi-server`, y una app GTK4, **Kiwi Server**. Ambas se instalan
en `~/.local` y no necesitan root.

- Repositorio: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Última versión: **v2.42.0**. Está en el [catálogo de Kiwi](../desktop/catalogs.md).
- Construido sobre [kiwi-modules](single.md) v0.23.0 (los módulos y su
  renderizador) y [kiwi-stack](single.md) v0.5.0 (la parte de la máquina),
  incluidos en el repositorio y fijados por tag.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Instalación { #install }

```bash
kiwi install kiwi-server        # con kiwi-updater
```

O desde un checkout: `./install.sh install` y luego `kiwi-server doctor`.

Necesita Python 3.9+ con PyYAML y Jinja2, `openssl` y `ssh`. El almacén de
secretos necesita `age`. Para construir ISOs hacen falta `butane`,
`coreos-installer` y `xorriso` (más `cpio`, `gzip` y `curl` para Debian). En
Silverblue o Bluefin, constrúyelas como una sola imagen de contenedor en lugar de
añadir paquetes por capas:

```bash
kiwi-server toolchain build     # se usa automáticamente cuando faltan las herramientas
```

`qrencode` (para `enroll --qr`), `shellcheck` y `docker compose` son opcionales.

## De la nada a una red en marcha { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # un fleet.yaml comentado
$EDITOR fleet.yaml                        # hosts, roles, tu clave SSH, el disco de instalación
kiwi-server secrets init fleet.yaml       # opcional: secrets/ como un solo almacén cifrado con age
kiwi-server validate fleet.yaml

# el master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   arráncala; se instala y se apaga; vuelve a encenderla
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# cada node: primero su cliente WireGuard, luego el medio, luego el rol
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# tus propios dispositivos
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # lo que informa cada máquina
```

Por defecto, los medios no llevan **ninguno de los secretos del stack**: solo el
sistema base. El rol y su stack llegan con `apply`. Si no se puede llegar a una
máquina por SSH, `build --offline` pone en la ISO todo el rol y sus secretos.
Mantén una ISO así fuera del almacén de ISOs de un proveedor y bórrala después de
la instalación.

**¿Sin ISO?** `kiwi-server script fleet.yaml papaya` imprime el script para una
máquina que instalaste tú mismo (`--offline` para todo el rol).

En un VPS de netcup, `kiwi-server vps install fleet.yaml sorbet` borra el
servidor e instala la ISO a través de la API de netcup.

## Comandos { #commands }

| Comando | Qué hace |
|---|---|
| `init [fleet.yaml]` | escribe el archivo fleet de ejemplo (`--domain`, por defecto `home`) |
| `validate fleet.yaml [host…]` | lo comprueba, renderizando cada stack para detectar errores de módulos |
| `list` / `show fleet.yaml <host>` | los hosts y lo que se ha generado / la configuración efectiva de un host, con los secretos ocultos |
| `render fleet.yaml [host…]` | scripts de rol, stacks y configuraciones de instalación en `output/<host>/` |
| `build fleet.yaml [host…]` | renderiza y luego genera la ISO: sistema base por defecto, `--offline` para todo el rol |
| `script fleet.yaml <host>` | el script para cualquier máquina (`--offline` para todo el rol) |
| `apply fleet.yaml <host…>` | vuelve a renderizar, envía el rol por SSH y lo ejecuta (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | lo que informan las máquinas: rol, stack, problemas, discos, copias de seguridad, certificados |
| `enroll fleet.yaml <host\|name>` | crea u obtiene un cliente WireGuard en el master (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` como un solo archivo cifrado con age, abierto en memoria (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | las contraseñas generadas de un host |
| `ca fleet.yaml` | la CA de la fleet |
| `mtu fleet.yaml <node\|device\|address>` | mide la MTU real de un túnel y dice qué fijar (`--write`) |
| `openwrt fleet.yaml` | un script que une un router OpenWrt a la malla ([Routers](../network/routers.md)) |
| `backup` / `restore` / `prune` | el directorio de la fleet a los nodes y de vuelta; borrado de copias de seguridad antiguas de las máquinas ([Operaciones](operations.md)) |
| `unlock fleet.yaml <host>` | reenvía un anillo Tang a una máquina que espera en el arranque ([Operaciones](operations.md)) |
| `vps login\|list\|probe\|install` | la API del Server Control Panel de netcup |
| `roles [-v]`, `modules [-v]`, `targets` | lo que hay disponible, con cada ajuste y su valor por defecto |
| `toolchain [status\|build]`, `doctor` | las herramientas de ISO; comprobar esta máquina |

Todos los comandos aceptan `--porcelain` (JSON), `-o/--output-dir`, `--quiet` y
`-v`. `kiwi-server <command> -h` explica un comando.

## La app { #the-app }

**Kiwi Server** abre tu última fleet. La barra lateral tiene una vista general,
una fila por host y los valores por defecto. La *Overview* de un host muestra
datos en vivo de `kiwi-server status` (consultados una vez por minuto mientras la
ventana tiene el foco, solo lectura por SSH). Sus *Settings* son un formulario
construido a partir de los roles y los módulos. *Apply*, *Build* y *Render*
ejecutan la CLI y muestran su salida en directo, y *Build* enumera los discos que
va a borrar antes de empezar. *Unlock* y *Lock* abren y cierran el almacén de
secretos. La app escribe YAML simple, así que los comentarios de un archivo fleet
escrito a mano se pierden cuando guarda.

## Ten en cuenta { #mind }

!!! danger "Las ISOs borran el disco que se les indica"
    Al arrancar, sin preguntar. Etiquétalas. `disk:` es obligatorio para `build`
    precisamente por eso.

- **La salida contiene secretos**: hashes de contraseñas, claves WireGuard,
  claves TLS, claves LUKS. Los archivos se escriben con 0600 y `output/` está
  ignorado por git. Trata igual las ISOs hechas con `--offline`.
- **Las contraseñas de los servicios se generan** a partir de `secrets/seed`
  cuando las omites en el archivo fleet. `validate` avisa de las contraseñas
  escritas en él. `kiwi-server secrets show` las imprime. Una máquina rechaza un
  apply hecho con una semilla distinta.
- **Las claves de host SSH** se registran en `secrets/known_hosts` en el primer
  contacto, y una clave cambiada se rechaza (tras una reinstalación, borra la
  línea).
- **Un script de rol se ejecuta como root.** Lee `kiwi-server script fleet.yaml <host>
  --offline` antes de fiarte de un rol que no escribiste tú.
- **Un rol que falla lo dice.** La máquina guarda
  `/var/lib/kiwi-server/role.failed` (el paso y el comando), y `status` lo
  muestra.

## Estado { #status }

El proceso se probó en hardware en octubre y noviembre de 2026. Debian, uCore y
Fedora CoreOS arrancaron de principio a fin en dos VPS, un mini PC y una VM, y un
simulacro de node caído reconstruyó una máquina Debian cifrada en unos 14
minutos. Se restauraron copias de seguridad de un node en otro (de papaya a
lychee), y la MTU del túnel se midió y se ajustó en rutas reales, también
móviles. La CI renderiza cada rol, pasa shellcheck a cada script, valida cada
configuración de Butane y fija cuatro stacks de referencia byte a byte.

Aún sin probar: la federación entre redes. Todo es IPv4. La ISO de Debian es solo
amd64. Un plano de control previsto (`kiwi-server serve`) está diseñado, pero no
construido.

Sigue leyendo: [El archivo fleet](fleet.md) · [Roles](roles.md) · [Módulos](modules.md) ·
[Máquinas](machines.md) · [Operaciones](operations.md) ·
[Una máquina sin fleet](single.md)
