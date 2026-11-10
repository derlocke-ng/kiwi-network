# Rollen

Eine Rolle ist das, was aus einer Maschine wird. Jede Rolle läuft auf allen drei Zielen.

| Rolle | Was aus der Maschine wird | Module |
|---|---|---|
| `bare` | das Basissystem: Admin-Benutzer, SSH, automatische Updates | keine |
| `master` | der **kiwi-master**: WireGuard-Einstiegspunkt mit dem Double Hop, Pi-hole, Tor und den Admin-Seiten | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, Preset `gateway` | ein **kiwi-node**, der ein LAN durch das VPN routet, mit Pi-hole, DHCP-Relay, einer Download-Station und SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, Preset `cloud` | ein **kiwi-node** mit Nextcloud und Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, Preset `minimal` | ein **kiwi-node**, den du mit Modulen deiner Wahl füllst | `vpn-client`, `reverse-proxy` |

`node-gw` und `node-cloud` funktionieren weiterhin als Namen für die Presets
`gateway` und `cloud`.

Die Modulrollen rendern einen **Stack**: standardmäßig Podman-Quadlets (docker
compose mit `runtime: docker`), die `kiwi-stack` startet und am Laufen hält. Siehe
[Module](modules.md).

## `master` { #master }

Das Preset ändert diese Modul-Standardwerte:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` und `reverse-proxy`: `network_mode: vpn-server`

Pi-hole, Tor und nginx leben also im Netzwerk-Namespace des WireGuard-Servers und
antworten unter der Mesh-Adresse des Masters. Container heißen `km-…` und hängen am
Netzwerk `knet-master` (`172.64.0.0/24`).

Ein Master kann `nostr-relay` und `hub` (einen [Hub für Menschen](../people/hubs.md)),
`portainer` und `backup` zu seinen `modules:` hinzufügen. Das Relay und der Hub
laufen nur auf Mastern.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

Das Preset wählt die Modulliste. `modules:` ersetzt sie, und benötigte Module
kommen von selbst dazu. Container heißen `kn-…` und hängen am Netzwerk `knet-node`
(`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # auf lychee läuft das Modul backup-server
```

Das Gateway-Preset schaltet die eigene Webseite von Pi-hole ein (`expose_web_ui: true`)
unter `127.0.0.1:8080`. Der Reverse Proxy liefert sie so oder so per TLS unter
`pihole.<hostname>` aus.

## Eine Rolle schreiben { #writing-a-role }

Eine Rolle ist ein Verzeichnis `roles/<name>/` mit einer `role.yaml` und einem
`apply.sh`. Eine Modulrolle listet ihre Module auf und bindet die gemeinsamen
Stack-Einstellungen ein, und ihr `apply.sh` besteht aus einem Aufruf:

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

Eine Rolle ohne Module erledigt ihre Arbeit selbst in `ks_role_apply()` und nutzt
dazu die Bibliothek in `roles/common/lib.sh` (die aus kiwi-stack stammt).
Einstellungen in `role.yaml` werden zu `KS_ROLE_<KEY>`. Das Skript läuft als root mit
`set -euo pipefail`. Die Tests rendern jede Rolle im Baum und prüfen sie mit
shellcheck.
