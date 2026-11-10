# Rollen

Een rol is wat een machine wordt. Elke rol draait op alle drie de targets.

| Rol | Wat de machine wordt | Modules |
|---|---|---|
| `bare` | het basissysteem: beheerdersgebruiker, SSH, automatische updates | geen |
| `master` | de **kiwi-master**: WireGuard-ingang met de double hop, Pi-hole, Tor en de beheerpagina's | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | een **kiwi-node** die een LAN via de VPN routeert, met Pi-hole, DHCP-relay, een downloadstation en SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | een **kiwi-node** met Nextcloud en Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | een **kiwi-node** om te vullen met modules naar keuze | `vpn-client`, `reverse-proxy` |

`node-gw` en `node-cloud` werken nog steeds als namen voor de presets `gateway`
en `cloud`.

De modulerollen renderen een **stack**: standaard podman-quadlets (docker
compose met `runtime: docker`), die `kiwi-stack` start en draaiende houdt. Zie
[Modules](modules.md).

## `master` { #master }

De preset wijzigt deze standaardwaarden van modules:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` en `reverse-proxy`: `network_mode: vpn-server`

Pi-hole, Tor en nginx leven dus in de netwerknamespace van de WireGuard-server
en antwoorden op het mesh-adres van de master. Containers heten `km-…` op het
netwerk `knet-master` (`172.64.0.0/24`).

Een master kan `nostr-relay` en `hub` (een [hub voor mensen](../people/hubs.md)),
`portainer` en `backup` aan zijn `modules:` toevoegen. De relay en de hub draaien
alleen op masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

De preset kiest de modulelijst. `modules:` vervangt die, en vereiste modules
komen er vanzelf bij. Containers heten `kn-…` op het netwerk `knet-node`
(`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee draait de module backup-server
```

De gateway-preset zet de eigen webpagina van Pi-hole aan (`expose_web_ui: true`)
op `127.0.0.1:8080`. De reverse proxy serveert haar hoe dan ook via TLS op
`pihole.<hostname>`.

## Een rol schrijven { #writing-a-role }

Een rol is een map `roles/<name>/` met een `role.yaml` en een `apply.sh`. Een
modulerol somt zijn modules op en neemt de gedeelde stack-instellingen op, en
zijn `apply.sh` is één aanroep:

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

Een rol zonder modules doet zijn eigen werk in `ks_role_apply()`, met de
bibliotheek in `roles/common/lib.sh` (die uit kiwi-stack komt). Instellingen in
`role.yaml` worden `KS_ROLE_<KEY>`. Het script draait als root met
`set -euo pipefail`. De tests renderen en shellchecken elke rol in de boom.
