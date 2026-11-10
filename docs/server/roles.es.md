# Roles

El rol determina para qué se usa una máquina en tu Kiwi Network. En el archivo
fleet asignas un rol a cada host, y kiwi-server prepara la máquina para él. Una
máquina puede ser un sistema base sin más, el master al que se conectan todos
los dispositivos y nodes, o un node en el que funcionan tus servicios. Todos los
roles funcionan en los tres sistemas de destino, es decir, en los tres sistemas
operativos que kiwi-server sabe instalar.

| Rol | En qué se convierte la máquina | Módulos |
|---|---|---|
| `bare` | Solo el sistema base, con un usuario administrador, SSH y actualizaciones automáticas | ninguno |
| `master` | El **kiwi-master**. Es el punto de entrada de WireGuard a la red y envía el tráfico de la red hacia Internet a través de una VPN comercial (el doble salto). Además ejecuta Pi-hole como DNS con bloqueo de publicidad, Tor y las páginas de administración | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | Un **kiwi-node** que envía por la VPN el tráfico de una red local (LAN). Además ejecuta Pi-hole, un relay DHCP, un gestor de descargas y SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | Un **kiwi-node** en el que funcionan Nextcloud y Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | Un **kiwi-node** con solo los dos módulos básicos, al que añades los módulos que quieras | `vpn-client`, `reverse-proxy` |

El rol `node` viene en varios presets. Un preset es una lista de módulos ya
preparada. Los nombres de rol antiguos `node-gw` y `node-cloud` siguen
funcionando y equivalen a los presets `gateway` y `cloud`.

Los roles `master` y `node` se construyen con módulos, y cada módulo es un
servicio. kiwi-server convierte los módulos de un host en un **stack**, el
conjunto de contenedores que ejecuta la máquina. Por defecto, el stack está
formado por quadlets de podman, que son unidades de systemd que ejecutan
contenedores. Con `runtime: docker`, lo ejecuta docker compose. En la máquina,
`kiwi-stack` arranca el stack y lo mantiene en marcha. Consulta
[Módulos](modules.md).

## `master` { #master }

El rol `master` cambia estos valores por defecto de los módulos:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` y `reverse-proxy`: `network_mode: vpn-server`

Con estos ajustes, Pi-hole, Tor y nginx comparten el namespace de red del
servidor WireGuard. Un namespace de red es el conjunto de interfaces de red y
direcciones que ve un contenedor. Por eso los tres servicios son accesibles en
la dirección del master en la mesh, es decir, en su dirección dentro de la red
WireGuard privada. Los contenedores de un master se llaman `km-…` y están
conectados a la red `knet-master` (`172.64.0.0/24`).

En un master también pueden funcionar `nostr-relay` y `hub` (para un
[hub para personas](../people/hubs.md)), `portainer` y `backup`. Para usarlos,
añádelos a la lista `modules:` del master. El relay y el hub solo funcionan en
masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

El preset determina qué módulos ejecuta un node. Si escribes tu propia lista
`modules:`, esta sustituye a la del preset. Si los módulos de tu lista
necesitan otros, estos se añaden automáticamente. Los contenedores de un node se llaman
`kn-…` y están conectados a la red `knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # en lychee funciona el módulo backup-server
```

El preset `gateway` también deja accesible la página web propia de Pi-hole en
`127.0.0.1:8080` dentro del node (`expose_web_ui: true`). Tanto si este ajuste
está activado como si no, el proxy inverso sirve esa página por TLS en
`pihole.<hostname>`.

## Escribir un rol { #writing-a-role }

Puedes escribir tus propios roles. Un rol es un directorio `roles/<name>/` con
un `role.yaml` y un `apply.sh`. Un rol construido con módulos enumera sus
módulos en `role.yaml` e incluye los ajustes comunes del stack. Su `apply.sh`
se reduce entonces a una sola llamada.

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

Un rol sin módulos hace todo el trabajo por sí mismo en `ks_role_apply()`. Puede
usar la biblioteca de `roles/common/lib.sh`, que procede de kiwi-stack. Los
ajustes que declara `role.yaml` llegan al script como variables con el nombre
`KS_ROLE_<KEY>`. El script se ejecuta como root con `set -euo pipefail`. Las
pruebas del proyecto generan todos los roles del árbol y les pasan shellcheck.
