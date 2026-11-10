# Role

Rola to to, czym staje się maszyna. Każda rola działa na wszystkich trzech
targetach.

| Rola | Czym staje się maszyna | Moduły |
|---|---|---|
| `bare` | systemem bazowym: użytkownik administracyjny, SSH, automatyczne aktualizacje | brak |
| `master` | **kiwi-master**: punkt wejścia WireGuard z podwójnym skokiem, Pi-hole, Tor i strony administracyjne | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | **kiwi-node**, który trasuje LAN przez VPN, z Pi-hole, przekaźnikiem DHCP, stacją pobierania i SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | **kiwi-node** z Nextcloud i Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | **kiwi-node** do wypełnienia wybranymi przez ciebie modułami | `vpn-client`, `reverse-proxy` |

`node-gw` i `node-cloud` nadal działają jako nazwy presetów `gateway` i
`cloud`.

Role modułowe renderują **stack**: domyślnie quadlety podmana (docker compose
z `runtime: docker`), które `kiwi-stack` uruchamia i utrzymuje w działaniu.
Zobacz [Moduły](modules.md).

## `master` { #master }

Preset zmienia te wartości domyślne modułów:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` i `reverse-proxy`: `network_mode: vpn-server`

Dzięki temu Pi-hole, Tor i nginx działają w przestrzeni nazw sieciowych
serwera WireGuard i odpowiadają pod adresem mastera w sieci mesh. Kontenery
nazywają się `km-…` i są w sieci `knet-master` (`172.64.0.0/24`).

Master może dodać do swoich `modules:` moduły `nostr-relay` i `hub`
([hub dla ludzi](../people/hubs.md)), `portainer` i `backup`. Przekaźnik i hub
działają tylko na masterach.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

Preset wybiera listę modułów. `modules:` ją zastępuje, a wymagane moduły
dochodzą same. Kontenery nazywają się `kn-…` i są w sieci `knet-node`
(`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee uruchamia moduł backup-server
```

Preset gateway włącza własną stronę WWW Pi-hole (`expose_web_ui: true`) pod
`127.0.0.1:8080`. Reverse proxy i tak serwuje ją przez TLS pod
`pihole.<hostname>`.

## Pisanie roli { #writing-a-role }

Rola to katalog `roles/<name>/` z plikami `role.yaml` i `apply.sh`. Rola
modułowa wymienia swoje moduły i dołącza wspólne ustawienia stacka, a jej
`apply.sh` to jedno wywołanie:

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

Rola bez modułów wykonuje własną pracę w `ks_role_apply()`, korzystając z
biblioteki w `roles/common/lib.sh` (która pochodzi z kiwi-stack). Ustawienia w
`role.yaml` stają się zmiennymi `KS_ROLE_<KEY>`. Skrypt działa jako root z
`set -euo pipefail`. Testy renderują każdą rolę w drzewie i sprawdzają ją
shellcheckiem.
