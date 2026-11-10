# Rollen

De rol bepaalt waarvoor een machine in je Kiwi Network wordt gebruikt. Je geeft
elke host in het fleetbestand een rol, en kiwi-server richt de machine daarvoor
in. Een machine kan een kaal basissysteem zijn, de master waarmee elk apparaat
en elke node verbinding maakt, of een node waarop je diensten draaien. Elke rol
werkt op alle drie de doelsystemen, de besturingssystemen die kiwi-server kan
installeren.

| Rol | Wat de machine wordt | Modules |
|---|---|---|
| `bare` | Alleen het basissysteem, met een beheerder, SSH en automatische updates | geen |
| `master` | De **kiwi-master**. Hier komen alle WireGuard-verbindingen van het netwerk binnen, en het internetverkeer van het netwerk gaat van hier door een commerciële VPN verder (de double hop). Daarnaast draaien er Pi-hole voor DNS dat reclame blokkeert, Tor en de beheerpagina’s | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | Een **kiwi-node** die het verkeer van een lokaal netwerk (LAN) door de VPN stuurt. Er draaien ook Pi-hole, een DHCP-relay, een downloadstation en SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | Een **kiwi-node** waarop Nextcloud en Vaultwarden draaien | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | Een **kiwi-node** met alleen de twee basismodules, waaraan je zelf de modules toevoegt die je wilt | `vpn-client`, `reverse-proxy` |

De rol `node` is er in presets. Een preset is een kant-en-klare lijst met
modules. De oudere rolnamen `node-gw` en `node-cloud` werken nog en staan voor
de presets `gateway` en `cloud`.

De rollen `master` en `node` zijn opgebouwd uit modules, en een module is één
dienst. kiwi-server maakt van de modules van een host een **stack**: alle
containers die de machine draait. Standaard bestaat de stack uit
podman-quadlets, systemd-units die containers draaien. Met `runtime: docker`
wordt hij door docker compose gedraaid. Op de machine start `kiwi-stack` de
stack en houdt hem in de lucht. Zie [Modules](modules.md).

## `master` { #master }

De rol `master` wijzigt deze standaardwaarden van modules:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` en `reverse-proxy`: `network_mode: vpn-server`

Met deze instellingen delen Pi-hole, Tor en nginx de netwerk-namespace van de
WireGuard-server. Een netwerk-namespace is de set netwerkinterfaces en adressen
die een container ziet. De drie diensten zijn daardoor bereikbaar op het
mesh-adres van de master, zijn adres in het besloten WireGuard-netwerk. De
containers op een master heten `km-…` en hangen aan het netwerk `knet-master`
(`172.64.0.0/24`).

Op een master kunnen ook `nostr-relay` en `hub` draaien (voor een
[hub voor mensen](../people/hubs.md)), en `portainer` en `backup`. Wil je ze
gebruiken, zet ze dan in de lijst `modules:` van de master. De relay en de hub
draaien alleen op masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

De preset bepaalt welke modules een node draait. Schrijf je een eigen lijst
`modules:`, dan vervangt die de lijst van de preset, en modules die de
opgesomde modules nodig hebben, worden automatisch toegevoegd. De containers op
een node heten `kn-…` en hangen aan het netwerk `knet-node`
(`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # op lychee draait de module backup-server
```

De preset `gateway` maakt ook de eigen webpagina van Pi-hole beschikbaar op
`127.0.0.1:8080` op de node (`expose_web_ui: true`). Of deze instelling nu aan
of uit staat, de reverse proxy levert de pagina altijd via TLS op
`pihole.<hostname>`.

## Een rol schrijven { #writing-a-role }

Je kunt ook zelf een rol schrijven. Een rol is een map `roles/<name>/` met een
`role.yaml` en een `apply.sh`. Een rol die uit modules is opgebouwd, somt haar
modules op in `role.yaml` en neemt de gedeelde stack-instellingen over. Haar
`apply.sh` bestaat dan uit één aanroep.

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

Een rol zonder modules doet haar werk zelf in `ks_role_apply()`. Ze kan daarbij
de bibliotheek in `roles/common/lib.sh` gebruiken, die uit kiwi-stack komt. De
instellingen die `role.yaml` declareert, zijn in het script beschikbaar als
variabelen met de naam `KS_ROLE_<KEY>`. Het script draait als root met
`set -euo pipefail`. De tests van het project genereren elke rol in de
repository en halen haar door shellcheck.
