# Módulos

Un módulo es un servicio que puede ejecutar una máquina de tu Kiwi Network, por
ejemplo el servidor VPN, el servidor DNS con bloqueo de publicidad, Nextcloud o
la copia de seguridad de cada noche. Con los módulos decides qué hace cada
máquina. Cada [rol](roles.md) trae consigo un conjunto de módulos, y en el
archivo fleet puedes cambiar ese conjunto.

Un generador convierte los módulos de un host en un **stack**, es decir, en
todo lo que la máquina necesita para ejecutar esos servicios. El generador es
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), y kiwi-server
incluye una copia. Un stack consta de un archivo compose, los **quadlets de
podman** (una unidad de systemd por contenedor), los archivos de configuración,
las unidades de systemd para el host y `stack.sh`, un manifiesto que los
enumera todos. [kiwi-stack](single.md) instala el stack en la máquina. Todas
las plantillas se rellenan en el ordenador donde se genera el stack. La máquina
que lo ejecuta solo necesita podman 4.4 o posterior, o docker con el plugin de
compose si pones `runtime: docker`.

Este comando muestra todos los módulos con sus ajustes.

```bash
kiwi-server modules -v      # todos los módulos y todos los ajustes con su valor por defecto
```

## La red { #the-network }

Estos módulos construyen la mesh, la red WireGuard privada que comparten todas
tus máquinas, y controlan cómo sale su tráfico a Internet.

| Módulo | Qué es | Funciona en | Necesita | En el host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, el servidor WireGuard al que se conectan todos los clientes y nodes. Su ruta por defecto es el cliente de VPN, así que el tráfico hacia Internet continúa por la VPN comercial del master (el doble salto) | master | nada | `51820/udp`, y la interfaz web en `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, el túnel VPN por el que pasa el tráfico de una máquina. En un node, el túnel lleva al master; en el master, a una VPN comercial | ambos | nada | nada |
| `dns` | **Pi-hole 6**, un servidor DNS que bloquea la publicidad para la mesh o para la LAN. Responde por los nombres de la fleet y puede dar también nombres a los proxies SOCKS5 de Mullvad | ambos | nada | `53` en un node |
| `tor` | Un proxy **SOCKS5 de Tor** para los clientes de la mesh. Solo usa nodos de Tor de los países que indiques | ambos | nada | `127.0.0.1:9050` en un node, y la dirección en la mesh `:9050` en un master |
| `reverse-proxy` | **nginx** con TLS. Tiene un bloque server por servicio, de modo que cada servicio es accesible con su propio nombre. Las páginas de administración solo se pueden abrir desde la mesh. Los nombres públicos con certificados de Let's Encrypt son opcionales | ambos | nada | `80`, `443` en un node, o en un master con `public` activado |
| `gateway` | Enrutamiento por políticas en el host. El tráfico a Internet de los dispositivos de la LAN que usan esta máquina como puerta de enlace se envía por la VPN | node | vpn-client | una unidad de systemd en el host |
| `dhcp-relay` | Pasa a Pi-hole las peticiones DHCP de la LAN, para que Pi-hole pueda ser el servidor DHCP de la LAN | node | dns | `67/udp` |

## Servicios { #services }

| Módulo | Qué es | Funciona en | Necesita |
|---|---|---|---|
| `cloud` | **Nextcloud**, montado con los contenedores del proyecto AIO, pero *sin* el contenedor maestro de AIO. Por eso no necesita el socket de docker y funciona con podman. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, la búsqueda de texto completo y Whiteboard se pueden activar o desactivar uno por uno | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, un gestor de contraseñas compatible con Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** y **JDownloader**. Los dos funcionan en el namespace de red del cliente de VPN, es decir, usan su conexión de red y no tienen ninguna propia. Mientras el túnel está caído, no transfieren nada | node | vpn-client |
| `sftp` | Un servidor SFTP en su propio puerto (`2224`), desde el que puedes recoger las descargas | node | nada |
| `portainer` | **Portainer CE**, una interfaz web para los contenedores. Es accesible en `127.0.0.1:9443` y en `portainer.<host>` | ambos | nada |
| `opencloud` | **OpenCloud**, para archivos y para compartir archivos, en un único binario de Go (para probar) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, para fotos y vídeos (para probar) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, para documentos escaneados, con OCR y búsqueda de texto completo (para probar) | node | vpn-client, reverse-proxy |

Los tres últimos módulos no forman parte de ningún preset. Para usar uno de
ellos, añádelo a `modules:`.

## Personas { #people }

Un hub es el sitio propio de una comunidad, en el navegador. Estos dos módulos
ejecutan un hub y el relay en el que el hub guarda sus eventos.

| Módulo | Qué es | Funciona en | Necesita |
|---|---|---|---|
| `nostr-relay` | **strfry**, el relay en el que un hub guarda sus eventos. Es accesible en `relay.<host>`. Quien se conecta desde Internet solo puede publicar si es miembro y ha demostrado que la clave es suya (NIP-42). Con `approved`, los miembros son las claves de una lista que firman los administradores. Con `registered`, es miembro cualquiera que tenga una cuenta. Las conexiones desde la mesh siempre pueden publicar | master | reverse-proxy |
| `hub` | Un **hub de kiwi-framework** que funciona como contenedor. Por defecto es Armory, y es accesible en `hub.<host>`. Un hub puede ser privado, semipúblico o público | master | reverse-proxy |

Consulta [Tener tu propio hub](../people/hubs.md).

## Copias de seguridad y discos { #backups-and-disks }

| Módulo | Qué es | Funciona en | Necesita |
|---|---|---|---|
| `backup` | Hace copia de seguridad cifrada de los datos de esta máquina con **restic**, en un node que ejecuta el módulo backup-server. La copia se hace cada noche a las `03:00` (o hasta 15 minutos después) y siempre que ejecutas `kiwi-stack backup`. Cada módulo define cuáles de sus datos entran en la copia. Para la próxima versión están previstas las copias en varios servidores y que una máquina reconstruida restaure sus propios datos ([detalles](operations.md#coming-in-the-next-release)) | ambos | nada |
| `backup-server` | Un **servidor REST de restic** que guarda las copias de seguridad. Cada máquina solo puede llegar a su propio repositorio, y solo puede añadir datos a él (solo añadir, append-only) | node | vpn-client, reverse-proxy |
| `tang` | Servidores **Tang**, que permiten a las máquinas con el disco cifrado desbloquearlo al arrancar sin que nadie tenga que estar presente. Un anillo es un servidor Tang con sus propias claves. Por defecto hay un anillo llamado `infra` en el puerto `7500` | node | nada |

Consulta [Administración](operations.md).

## Ajustes importantes { #important-settings }

| Módulo | Ajuste | Valor por defecto | Notas |
|---|---|---|---|
| vpn-server | `wg_host` | (obligatorio) | el nombre o la dirección IP a la que se conectan los clientes |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | consulta los [grupos de clientes](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | redirección de puertos en el master por la que las máquinas detrás de NAT llegan a su anillo Tang |
| vpn-client | `vpn_provider` | `custom` | `custom` usa la configuración de WireGuard que emitió el master, que es lo que necesita un node. Si no, indica un proveedor de gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | los países y ciudades de los servidores de la VPN comercial que se usan |
| | `dot_providers` | `quad9` | el proveedor de DNS-over-TLS que usa gluetun |
| | `extra_dnat_rules` | `[]` | reglas de reenvío adicionales, por ejemplo para entrar por SSH al host desde la mesh |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | solo se usa mientras no se puede llegar al master |
| | `dhcp_enabled` | `false` | se usa junto con `dhcp_start`, `dhcp_end` y `dhcp_router` |
| | `mullvad_socks` | `true` en un master | [los proxies de Mullvad por su nombre](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | los países de los nodos de entrada y de salida de Tor, impuestos con `StrictNodes` |
| reverse-proxy | `public` | `false` | solo en el master. Abre 80/443 y usa Let's Encrypt para los nombres de fuera del dominio de la fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | ponlo en un directorio de un disco grande |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | actívalo para crear la primera cuenta y luego vuelve a desactivarlo |
| downloader | `download_dir` | (obligatorio) | |
| nostr-relay | `members` | `approved` | o `registered` |
| | `write_pubkeys` | `[]` | las claves de los administradores. Los administradores siempre pueden publicar, y solo valen sus listas de miembros y de expulsados |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | la imagen de cualquier hub hecho con kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | defínelos para un hub semipúblico |
| backup | `server` | (obligatorio) | la dirección `https://…` de un node con backup-server que tenga esta máquina en su lista |
| tang | `rings` | `{ infra: "7500" }` | el nombre y el puerto de cada anillo |

Si no indicas una contraseña o una clave, se genera a partir del seed de la
fleet.

## Nombres { #names }

Cada módulo registra los nombres de sus servicios en el proxy inverso y en el
DNS de la fleet. Cada nombre se compone del nombre del servicio y del nombre del
host.

| Servicio | Nombre |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (cualquier host con `dns` y el proxy inverso) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relay / hub | `relay.<host>` / `hub.<host>` |
| servidor de copias de seguridad | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Contenedores { #containers }

- Con podman, cada servicio es un quadlet en `/etc/containers/systemd`. Los
  quadlets se arrancan a través de `kiwi-stack.target`, y sus logs van al
  journal de systemd. Un contenedor que comparte el namespace de red de otro
  está ligado a él, así que se reinicia junto con él.
- Los secretos se escriben en archivos `kiwi/env/<service>.env` que solo root
  puede leer. Nunca se escriben en las unidades.
- Los contenedores tienen direcciones fijas que siguen el plan de direcciones
  de v1, de modo que una máquina migrada desde v1 conserva sus direcciones. Son
  estas: vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud
  `.6`, vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`
  y sftp `.251`. Los demás módulos reciben direcciones correlativas a partir de
  `.100`. Los contenedores sin dirección fija reciben una del tercer cuarto de
  la red (`.128/26`).
- Fedora CoreOS y uCore funcionan con SELinux activado, así que los bind mounts
  llevan la etiqueta `:z`. Los montajes del socket de contenedores y de
  `/lib/modules` nunca se etiquetan.

## Escribir un módulo { #writing-a-module }

Un módulo es un directorio con los siguientes archivos.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` describe el módulo. Declara sus metadatos y los tipos de node en
los que funciona, sus dependencias y los puertos que abre en el host. Indica las
plantillas del módulo y dónde se escribe su resultado, su almacenamiento y
cuáles de sus datos entran en la copia de seguridad. Declara también la
integración con el host (sysctls y módulos del kernel), los bloques server de
nginx que registra el módulo, las URL que se muestran cuando el rol termina, las
reglas de validación y los `settings` del módulo.

El esquema de ajustes sirve para dos cosas: valida el archivo fleet, y la app de
kiwi-server construye a partir de él su formulario de ajustes. Las plantillas se
escriben en Jinja2 y pueden usar el contexto del host. Ese contexto contiene el
nombre y el tipo del host, la dirección de cada módulo, la mesh, los nombres de
la fleet, los módulos activados y los ajustes de cada módulo.

Con podman, el archivo compose se traduce a quadlets. La traducción admite un
conjunto fijo de claves de compose, y cualquier otra clave produce un error al
generar el stack.

Los módulos se desarrollan y se publican en
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). La referencia
completa del formato está en
[docs/modules.md de kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
