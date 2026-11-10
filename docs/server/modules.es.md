# Módulos

Un módulo es un servicio de una máquina de una Kiwi Network. Un [rol](roles.md)
elige un conjunto de módulos, y el renderizador los convierte en un **stack**
para un host. El renderizador es
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), que kiwi-server
incluye en su repositorio. El stack es un archivo compose, **quadlets de podman**
(una unidad systemd por contenedor), las configuraciones y unidades del host, y
`stack.sh`, el manifiesto que los nombra a todos. [kiwi-stack](single.md) lo
pone en la máquina. Todas las plantillas se resuelven en la máquina que
renderiza. El target solo necesita podman 4.4 o posterior (o docker con el plugin
compose, con `runtime: docker`).

```bash
kiwi-server modules -v      # cada módulo y cada ajuste con su valor por defecto
```

## La red { #the-network }

| Módulo | Qué es | Funciona en | Requiere | En el host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: el punto de entrada de todos los clientes y nodes; su ruta por defecto es el cliente VPN (el doble salto) | master | nada | `51820/udp`; la interfaz en `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: el túnel del que cuelga cada máquina: hacia el master en un node, hacia una VPN comercial en el master | ambos | nada | nada |
| `dns` | **Pi-hole 6**: bloquea anuncios para la malla o la LAN, sirve los nombres de la fleet y, opcionalmente, los proxies SOCKS5 de Mullvad por nombre | ambos | nada | `53` en un node |
| `tor` | un proxy **Tor SOCKS5** para los clientes de la malla, fijado a países | ambos | nada | `127.0.0.1:9050` en un node; la dirección de malla `:9050` en un master |
| `reverse-proxy` | **nginx** con TLS: un bloque server por servicio; las páginas de administración solo responden a la malla; nombres públicos opcionales con Let's Encrypt | ambos | nada | `80`, `443` en un node, o en un master público |
| `gateway` | enrutamiento por políticas en el host: los clientes de la LAN que usan esta máquina como puerta de enlace salen por la VPN | node | vpn-client | una unidad del host |
| `dhcp-relay` | retransmite el DHCP de la LAN a Pi-hole, para que Pi-hole pueda ser el servidor DHCP de la LAN | node | dns | `67/udp` |

## Servicios { #services }

| Módulo | Qué es | Funciona en | Requiere |
|---|---|---|---|
| `cloud` | **Nextcloud** con los contenedores del proyecto AIO, *sin* el contenedor maestro de AIO (sin socket de docker, funciona con podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, la búsqueda de texto completo y Whiteboard son interruptores | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, el gestor de contraseñas compatible con Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** y **JDownloader** dentro del espacio de nombres de red del cliente VPN: sin túnel, no hay tráfico | node | vpn-client |
| `sftp` | un servidor SFTP en su propio puerto (`2224`), para recoger las descargas | node | nada |
| `portainer` | **Portainer CE**, una interfaz web para los contenedores (`127.0.0.1:9443`, y `portainer.<host>`) | ambos | nada |
| `opencloud` | **OpenCloud**: archivos y compartición en un solo binario de Go (para probar) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**: fotos y vídeos (para probar) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: documentos escaneados con OCR y búsqueda de texto completo (para probar) | node | vpn-client, reverse-proxy |

Los tres últimos no están en ningún preset; añádelos a `modules:`.

## Personas { #people }

| Módulo | Qué es | Funciona en | Requiere |
|---|---|---|---|
| `nostr-relay` | **strfry**, el relay en el que un hub guarda sus eventos (en `relay.<host>`). Desde Internet, los miembros pueden publicar tras demostrar su clave (NIP-42): claves `approved` de la lista firmada de los administradores, o cualquiera `registered` con una cuenta. La malla siempre puede publicar | master | reverse-proxy |
| `hub` | un **hub de kiwi-framework** como contenedor (Armory por defecto, en `hub.<host>`), privado, semipúblico o público | master | reverse-proxy |

Consulta [Tu propio hub](../people/hubs.md).

## Copias de seguridad y discos { #backups-and-disks }

| Módulo | Qué es | Funciona en | Requiere |
|---|---|---|---|
| `backup` | los datos de esta máquina con **restic**, cifrados, hacia un node backup-server: cada noche a las `03:00` (dentro de los 15 minutos siguientes) y con `kiwi-stack backup`. Cada módulo dice qué parte de él se guarda. Próxima versión: varios servidores y una máquina reconstruida que se restaura sola ([detalles](operations.md#coming-in-the-next-release)) | ambos | nada |
| `backup-server` | un **servidor REST de restic**; cada máquina solo llega a su propio repositorio, solo de anexado | node | vpn-client, reverse-proxy |
| `tang` | servidores **Tang** para que las máquinas cifradas se desbloqueen al arrancar; un anillo es un servidor con sus propias claves (por defecto `infra` en `7500`) | node | nada |

Consulta [Operaciones](operations.md).

## Ajustes importantes { #important-settings }

| Módulo | Ajuste | Por defecto | Notas |
|---|---|---|---|
| vpn-server | `wg_host` | (obligatorio) | el nombre o la IP a la que se conectan los clientes |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | consulta [grupos de clientes](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | puertos Tang para máquinas detrás de NAT |
| vpn-client | `vpn_provider` | `custom` | `custom`: la configuración WireGuard que emitió el master (un node); o un proveedor de gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | dónde está una salida comercial |
| | `dot_providers` | `quad9` | el DNS-over-TLS de gluetun |
| | `extra_dnat_rules` | `[]` | p. ej., SSH desde la malla al host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | solo mientras el master no es accesible |
| | `dhcp_enabled` | `false` | con `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` en un master | [los proxies de Mullvad por nombre](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | nodos de entrada y de salida, `StrictNodes` |
| reverse-proxy | `public` | `false` | solo el master: 80/443 con Let's Encrypt para nombres fuera del dominio de la fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | apúntalo a un disco grande |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | actívalo para la primera cuenta y luego desactívalo |
| downloader | `download_dir` | (obligatorio) | |
| nostr-relay | `members` | `approved` | o `registered` |
| | `write_pubkeys` | `[]` | los administradores: siempre pueden publicar, y solo cuentan sus listas de miembros y de bloqueos |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | cualquier hub de kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | un hub semipúblico |
| backup | `server` | (obligatorio) | `https://…` de un node backup-server que incluya esta máquina |
| tang | `rings` | `{ infra: "7500" }` | nombre y puerto |

Las contraseñas y claves que omites se generan a partir de la semilla de la
fleet.

## Nombres { #names }

Cada módulo anuncia sus nombres al proxy inverso y al DNS de la fleet, bajo el
nombre del host:

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

- Con podman, cada servicio es un quadlet en `/etc/containers/systemd`, arrancado
  a través de `kiwi-stack.target`, con su log en el journal. Un contenedor que
  vive en el espacio de nombres de red de otro queda ligado a él y vuelve con él.
- Los secretos van a archivos `kiwi/env/<service>.env` que solo puede leer root,
  nunca a las unidades.
- Las direcciones fijas siguen el plan de v1, así que una máquina migrada las
  conserva: vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`,
  cloud `.6`, vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer
  `.250`, sftp `.251`. Los demás módulos cuentan desde `.100`. Los contenedores
  sin dirección fija usan el tercer cuarto de la red (`.128/26`).
- Fedora CoreOS y uCore funcionan con SELinux activado, así que los bind mounts
  llevan la etiqueta `:z`. Los montajes del socket de contenedores y de
  `/lib/modules` nunca se etiquetan.

## Escribir un módulo { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` declara los metadatos del módulo y sus tipos de node, sus
dependencias, los puertos del host que abre, sus plantillas y adónde va su
salida, el almacenamiento, qué parte de él se copia, la integración con el host
(sysctls, módulos del kernel), los bloques server de nginx que anuncia, las URL
que se imprimen cuando el rol ha terminado, sus reglas de validación y sus
`settings`. El esquema de ajustes valida el archivo fleet y construye el
formulario de la app. Las plantillas son Jinja2 y ven el contexto del host: el
nombre y el tipo del host, la dirección de cada módulo, la malla, los nombres de
la fleet, cada módulo activado y los ajustes de cada módulo.

Con podman, el archivo compose se traduce a quadlets. Solo se traduce un conjunto
conocido de claves de compose, y cualquier otra cosa es un error al renderizar.

Los módulos se desarrollan y se publican en
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). La referencia
completa del formato es
[docs/modules.md de kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
