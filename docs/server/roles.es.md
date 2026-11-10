# Roles

Un rol es aquello en lo que se convierte una máquina. Cada rol funciona en los
tres targets.

| Rol | En qué se convierte la máquina | Módulos |
|---|---|---|
| `bare` | el sistema base: usuario administrador, SSH, actualizaciones automáticas | ninguno |
| `master` | el **kiwi-master**: punto de entrada WireGuard con el doble salto, Pi-hole, Tor y las páginas de administración | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | un **kiwi-node** que enruta una LAN a través de la VPN, con Pi-hole, relay DHCP, una estación de descargas y SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | un **kiwi-node** con Nextcloud y Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | un **kiwi-node** para llenar con los módulos que elijas | `vpn-client`, `reverse-proxy` |

`node-gw` y `node-cloud` siguen funcionando como nombres de los presets
`gateway` y `cloud`.

Los roles de módulos renderizan un **stack**: quadlets de podman por defecto
(docker compose con `runtime: docker`), que `kiwi-stack` arranca y mantiene en
marcha. Consulta [Módulos](modules.md).

## `master` { #master }

El preset cambia estos valores por defecto de los módulos:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` y `reverse-proxy`: `network_mode: vpn-server`

Así, Pi-hole, Tor y nginx viven en el espacio de nombres de red del servidor
WireGuard y responden en la dirección de malla del master. Los contenedores se
llaman `km-…` en la red `knet-master` (`172.64.0.0/24`).

Un master puede añadir `nostr-relay` y `hub` (un [hub para personas](../people/hubs.md)),
`portainer` y `backup` a sus `modules:`. El relay y el hub solo funcionan en
masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

El preset elige la lista de módulos. `modules:` la sustituye, y los módulos
obligatorios entran solos. Los contenedores se llaman `kn-…` en la red
`knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee ejecuta el módulo backup-server
```

El preset gateway activa la página web propia de Pi-hole (`expose_web_ui: true`)
en `127.0.0.1:8080`. El proxy inverso la sirve por TLS en `pihole.<hostname>` en
cualquier caso.

## Escribir un rol { #writing-a-role }

Un rol es un directorio `roles/<name>/` con un `role.yaml` y un `apply.sh`. Un
rol de módulos enumera sus módulos e incluye los ajustes de stack compartidos, y
su `apply.sh` es una sola llamada:

```yaml
name: node-media
title: kiwi-node (media)
targets: [coreos, ucore, debian]
node_type: node
modules: [vpn-client, reverse-proxy, downloader, portainer]
settings_include: [common/stack]
module_defaults:
  downloader: { jdownloader: false }
```

```bash
ks_role_apply() { ks_stack_apply; }
```

Un rol sin módulos hace su propio trabajo en `ks_role_apply()`, usando la
biblioteca de `roles/common/lib.sh` (que viene de kiwi-stack). Los ajustes de
`role.yaml` pasan a ser `KS_ROLE_<KEY>`. El script se ejecuta como root con
`set -euo pipefail`. Las pruebas renderizan y pasan shellcheck a cada rol del
árbol.
