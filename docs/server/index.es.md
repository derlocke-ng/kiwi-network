# kiwi-server

kiwi-server es la herramienta con la que se crea y se administra una Kiwi
Network. Describes todas las máquinas en un único archivo, `fleet.yaml`, y
kiwi-server las prepara a partir de él, así que no tienes que instalar y
configurar cada una a mano.

Para cada host, kiwi-server genera una **ISO de instalación desatendida**: una
imagen que instala Fedora CoreOS, uCore o Debian sin hacer ninguna pregunta y
después apaga la máquina. A continuación, kiwi-server **aplica** por SSH el rol
de la máquina, lo que la convierte en un `kiwi-master` o en un `kiwi-node`. A
partir de ahí sigue ocupándose de la fleet: da de alta clientes de WireGuard,
consulta el estado de cada máquina, guarda los secretos (contraseñas y claves),
hace copia de seguridad de la fleet y desbloquea los discos cifrados.

kiwi-server se distribuye como herramienta de línea de comandos (CLI),
`kiwi-server`, y como app GTK4, **Kiwi Server**. Las dos se instalan en
`~/.local` y no necesitan permisos de root.

- Repositorio: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Última versión: **v2.42.0**. Está disponible en el [catálogo de Kiwi](../desktop/catalogs.md).
- kiwi-server se apoya en [kiwi-modules](single.md) v0.23.0, que contiene los
  módulos y el programa que genera la configuración a partir de ellos, y en
  [kiwi-stack](single.md) v0.5.0, que es la parte que se ejecuta en cada
  máquina. Los dos van incluidos en kiwi-server en forma de copia (vendored) y
  están fijados por tag.

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

También puedes instalarlo desde un clon del repositorio: ejecuta
`./install.sh install` y después `kiwi-server doctor`.

kiwi-server necesita Python 3.9+ con PyYAML y Jinja2, además de los programas
`openssl` y `ssh`. El almacén de secretos necesita `age`. Para construir las ISO
hacen falta `butane`, `coreos-installer` y `xorriso`, y para Debian también
`cpio`, `gzip` y `curl`. En Silverblue o Bluefin no añadas estos paquetes al
sistema como capas. Es mejor construir las herramientas para las ISO como una
sola imagen de contenedor:

```bash
kiwi-server toolchain build     # se usa automáticamente cuando faltan las herramientas
```

`qrencode` (para `enroll --qr`), `shellcheck` y `docker compose` son opcionales.

## De cero a una red en marcha { #from-nothing-to-a-running-network }

Con los comandos siguientes pasas de un directorio vacío a una red en marcha,
con un master, un node y tus propios dispositivos:

```bash
kiwi-server init                          # un fleet.yaml comentado
$EDITOR fleet.yaml                        # hosts, roles, tu clave SSH, el disco de instalación
kiwi-server secrets init fleet.yaml       # opcional: secrets/ como un único almacén cifrado con age
kiwi-server validate fleet.yaml

# el master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   arranca la máquina desde la ISO; se instala y se apaga; vuelve a encenderla
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# cada node: primero su cliente de WireGuard, después la ISO y por último el rol
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# tus propios dispositivos
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # lo que comunica cada máquina
```

Por defecto, una ISO de instalación **no contiene ningún secreto del stack**,
que es el conjunto de contenedores y configuración de una máquina. La ISO solo
lleva el sistema base, y el rol y su stack se envían después a la máquina con
`apply`. Si a una máquina no se puede llegar por SSH, `build --offline` mete en
la ISO el rol completo con sus secretos. No subas una ISO así al almacén de ISO
de un proveedor de hosting, y bórrala después de la instalación.

**Si no quieres usar ninguna ISO,** `kiwi-server script fleet.yaml papaya`
imprime el script para una máquina que hayas instalado tú. Con `--offline`, el
script contiene el rol completo.

En un VPS de netcup, `kiwi-server vps install fleet.yaml sorbet` borra el
servidor e instala la ISO mediante la API de netcup, sin que nadie tenga que
sentarse delante de una consola. Por ahora, netcup es el único proveedor de
hosting con el que funciona. Hay otros
[previstos](roadmap.md#more-hosters-and-network-boot).

## Comandos { #commands }

| Comando | Qué hace |
|---|---|
| `init [fleet.yaml]` | Escribe el archivo fleet de ejemplo. `--domain` establece el dominio, que por defecto es `home`. |
| `validate fleet.yaml [host…]` | Comprueba el archivo fleet. Genera todos los stacks, para detectar también los errores de los módulos. |
| `list` / `show fleet.yaml <host>` | El primero enumera los hosts y lo que se ha generado para cada uno. El segundo muestra la configuración efectiva de un host, con los secretos ocultos. |
| `render fleet.yaml [host…]` | Escribe los scripts de rol, los stacks y las configuraciones de instalación en `output/<host>/`. |
| `build fleet.yaml [host…]` | Genera la configuración y después construye la ISO. Por defecto, la ISO solo contiene el sistema base; con `--offline` contiene el rol completo. |
| `script fleet.yaml <host>` | Imprime el script para cualquier máquina. Con `--offline`, el script contiene el rol completo. |
| `apply fleet.yaml <host…>` | Vuelve a generar la configuración, envía el rol a la máquina por SSH y lo ejecuta allí (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Muestra lo que comunican las máquinas: rol, stack, problemas, discos, copias de seguridad y certificados. |
| `enroll fleet.yaml <host\|name>` | Crea un cliente de WireGuard en el master, o recupera uno que ya existe (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Gestionan `secrets/` como un único archivo cifrado con age, que se abre en memoria cuando lo desbloqueas (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Muestra las contraseñas generadas de un host. |
| `ca fleet.yaml` | Muestra la CA de la fleet. |
| `mtu fleet.yaml <node\|device\|address>` | Mide la MTU real de un túnel y te dice qué valor poner (`--write`). |
| `openwrt fleet.yaml` | Escribe un script que conecta un router OpenWrt a la mesh, la red WireGuard privada que comparten todas las máquinas ([Routers](../network/routers.md)). |
| `backup` / `restore` / `prune` | Hacen copia de seguridad del directorio de la fleet en los nodes, la restauran desde allí y eliminan las copias de seguridad antiguas de las máquinas ([Administración](operations.md)). |
| `unlock fleet.yaml <host>` | Reenvía un anillo Tang a una máquina que está esperando, durante el arranque, a que se desbloquee su disco cifrado ([Administración](operations.md)). |
| `vps login\|list\|probe\|install` | Trabajan con la API del Server Control Panel de netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Muestran lo que hay disponible, con cada ajuste y su valor por defecto. |
| `toolchain [status\|build]`, `doctor` | Gestionan las herramientas para las ISO y comprueban este ordenador. |

Todos los comandos aceptan `--porcelain` (salida en JSON), `-o/--output-dir`,
`--quiet` y `-v`. `kiwi-server <command> -h` explica un comando concreto.

## La app { #the-app }

La app **Kiwi Server** abre la fleet con la que trabajaste la última vez. En la
barra lateral hay una vista general, una fila por cada host y los valores por
defecto. La vista *Overview* de un host muestra información actual, obtenida
con `kiwi-server status`. La app la consulta una vez por minuto mientras la
ventana tiene el foco, por SSH y solo en modo lectura. *Settings* contiene los
ajustes del host: un formulario que se construye a partir de los roles y los
módulos. *Apply*, *Build* y *Render* ejecutan la herramienta de línea de
comandos y muestran su salida a medida que se produce. Antes de empezar,
*Build* enumera los discos que va a borrar. *Unlock* y *Lock* abren y cierran
el almacén de secretos. La app escribe YAML sin más, de modo que los
comentarios de un archivo fleet escrito a mano se pierden cuando la app lo
guarda.

## Cosas que conviene tener presentes { #mind }

!!! danger "Las ISO borran el disco que se les ha indicado"
    Una ISO de instalación borra el disco para el que se construyó en cuanto
    una máquina arranca desde ella, sin preguntar. Etiqueta tus ISO.
    Precisamente por eso `build` exige el ajuste `disk:`.

- **La salida contiene secretos.** Son hashes de contraseñas, claves de
  WireGuard, claves TLS y claves LUKS. Los archivos se escriben con el modo
  0600, y git ignora `output/`. Trata con el mismo cuidado las ISO hechas con
  `--offline`.
- **Las contraseñas de los servicios se generan** a partir de `secrets/seed` si
  no las pones en el archivo fleet. `validate` te avisa de las contraseñas que
  están escritas en el archivo fleet, y `kiwi-server secrets show` muestra las
  generadas. Una máquina rechaza un `apply` hecho con un seed distinto.
- **Las claves de host SSH** se guardan en `secrets/known_hosts` la primera vez
  que kiwi-server se conecta a una máquina. Si más adelante la clave de una
  máquina cambia, la conexión se rechaza. Después de reinstalar una máquina,
  borra su línea de ese archivo.
- **Un script de rol se ejecuta como root.** Antes de fiarte de un rol que no
  has escrito tú, lee la salida de `kiwi-server script fleet.yaml <host>
  --offline`.
- **Si un rol falla, queda constancia.** La máquina conserva el archivo
  `/var/lib/kiwi-server/role.failed`, que indica el paso y el comando que
  fallaron, y `status` lo muestra.

## Estado { #status }

Todo el proceso, desde el archivo fleet hasta una máquina en marcha, se probó en
hardware real en octubre y noviembre de 2026. Debian, uCore y Fedora CoreOS lo
recorrieron entero en dos VPS, un mini PC y una máquina virtual. En un
ejercicio que simulaba la pérdida de un node, una máquina Debian cifrada se
reconstruyó en unos 14 minutos. Las copias de seguridad de un node se
restauraron en otro (de papaya a lychee). La MTU del túnel se midió y se ajustó
en conexiones reales, también móviles. Las pruebas automáticas (CI) generan
todos los roles, pasan shellcheck a todos los scripts y validan todas las
configuraciones de Butane. Además, comparan byte a byte cuatro stacks de
referencia, los llamados golden stacks, con su salida guardada.

La federación entre redes aún no se ha probado. Todo usa IPv4. La ISO de Debian
solo existe para amd64. Hay un plano de control (`kiwi-server serve`) previsto
y diseñado, pero aún no está implementado.

Sigue leyendo: [El archivo fleet](fleet.md) · [Roles](roles.md) · [Módulos](modules.md) ·
[Máquinas](machines.md) · [Administración](operations.md) ·
[Una sola máquina, sin fleet](single.md)
