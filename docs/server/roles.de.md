# Rollen

Die Rolle legt fest, wofür eine Maschine in deinem Kiwi Network da ist. Du gibst
jedem Host in der Fleet-Datei eine Rolle, und kiwi-server richtet die Maschine
dafür ein. Eine Maschine kann ein schlichtes Grundsystem sein, der Master, mit
dem sich alle Geräte und Nodes verbinden, oder ein Node, auf dem deine Dienste
laufen. Jede Rolle funktioniert auf allen drei Zielsystemen, also auf allen
Betriebssystemen, die kiwi-server installieren kann.

| Rolle | Was aus der Maschine wird | Module |
|---|---|---|
| `bare` | Nur das Grundsystem, mit Admin-Benutzer, SSH und automatischen Updates | keine |
| `master` | Der **kiwi-master**. Er ist der WireGuard-Zugang zum Netzwerk und leitet den Internetverkehr des Netzwerks über ein kommerzielles VPN weiter (der Double Hop). Außerdem laufen auf ihm Pi-hole als DNS mit Werbeblocker, Tor und die Admin-Seiten | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, Preset `gateway` | Ein **kiwi-node**, der den Verkehr eines lokalen Netzes (LAN) durch das VPN leitet. Außerdem laufen darauf Pi-hole, ein DHCP-Relay, eine Download-Station und SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, Preset `cloud` | Ein **kiwi-node** mit Nextcloud und Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, Preset `minimal` | Ein **kiwi-node** mit nur den beiden Grundmodulen, zu denen du die Module hinzufügst, die du haben möchtest | `vpn-client`, `reverse-proxy` |

Die Rolle `node` gibt es in mehreren Presets. Ein Preset ist eine fertige Liste
von Modulen. Die älteren Rollennamen `node-gw` und `node-cloud` funktionieren
weiterhin und stehen für die Presets `gateway` und `cloud`.

Die Rollen `master` und `node` bestehen aus Modulen, und ein Modul ist ein
einzelner Dienst. Aus den Modulen eines Hosts macht kiwi-server einen **Stack**,
also alle Container, die die Maschine betreibt. Standardmäßig besteht der Stack
aus podman-Quadlets, das sind systemd-Units, die Container starten. Mit
`runtime: docker` übernimmt docker compose den Betrieb. Auf der Maschine startet
`kiwi-stack` den Stack und hält ihn am Laufen. Siehe [Module](modules.md).

## `master` { #master }

Die Rolle `master` ändert diese Standardwerte der Module:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` und `reverse-proxy`: `network_mode: vpn-server`

Mit diesen Einstellungen teilen sich Pi-hole, Tor und nginx den
Netzwerk-Namespace des WireGuard-Servers. Ein Netzwerk-Namespace ist der Satz
von Netzwerkschnittstellen und Adressen, den ein Container sieht. Die drei
Dienste sind deshalb unter der Mesh-Adresse des Masters erreichbar, also unter
seiner Adresse im privaten WireGuard-Netzwerk. Die Container auf einem Master
heißen `km-…` und hängen am Netzwerk `knet-master` (`172.64.0.0/24`).

Auf einem Master können außerdem `nostr-relay` und `hub` laufen (für einen [Hub
für Menschen](../people/hubs.md)), dazu `portainer` und `backup`. Dafür nimmst
du sie in die `modules:`-Liste des Masters auf. Relay und Hub laufen nur auf
Mastern.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

Welche Module ein Node betreibt, legt das Preset fest. Schreibst du eine eigene
`modules:`-Liste, ersetzt sie die Liste des Presets, und Module, die von den
aufgeführten vorausgesetzt werden, kommen automatisch dazu. Die Container auf
einem Node heißen `kn-…` und hängen am Netzwerk `knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # auf lychee läuft das Modul backup-server
```

Das Preset `gateway` macht außerdem die eigene Weboberfläche von Pi-hole auf dem
Node unter `127.0.0.1:8080` erreichbar (`expose_web_ui: true`). Unabhängig von
dieser Einstellung liefert der Reverse-Proxy die Seite per TLS unter
`pihole.<hostname>` aus.

## Eine eigene Rolle schreiben { #writing-a-role }

Du kannst auch eine eigene Rolle schreiben. Eine Rolle ist ein Verzeichnis
`roles/<name>/` mit einer `role.yaml` und einer `apply.sh`. Eine Rolle, die aus
Modulen besteht, führt ihre Module in `role.yaml` auf und bindet die gemeinsamen
Stack-Einstellungen ein. Ihre `apply.sh` besteht dann aus einem einzigen Aufruf.

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

Eine Rolle ohne Module erledigt ihre Arbeit selbst in `ks_role_apply()`. Sie
kann dafür die Bibliothek in `roles/common/lib.sh` nutzen, die aus kiwi-stack
stammt. Die Einstellungen, die `role.yaml` deklariert, stehen dem Skript als
Variablen namens `KS_ROLE_<KEY>` zur Verfügung. Das Skript läuft als root mit
`set -euo pipefail`. Die Tests des Projekts erzeugen jede Rolle, die im
Repository liegt, und prüfen sie mit shellcheck.
