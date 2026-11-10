# Role

Rola określa, do czego służy maszyna w twojej Kiwi Network. W pliku fleet
przypisujesz rolę każdemu hostowi, a kiwi-server konfiguruje maszynę zgodnie
z nią. Maszyna może być samym systemem bazowym, masterem, z którym łączą się
wszystkie urządzenia i node’y, albo node’em, na którym działają twoje usługi.
Każda rola działa na wszystkich trzech systemach docelowych, czyli systemach
operacyjnych, które kiwi-server potrafi zainstalować.

| Rola | Czym staje się maszyna | Moduły |
|---|---|---|
| `bare` | Tylko systemem bazowym z użytkownikiem administracyjnym, SSH i automatycznymi aktualizacjami | brak |
| `master` | **kiwi-master**. Łączą się z nim wszyscy uczestnicy sieci WireGuard, a ruch z sieci do internetu przekazuje on dalej przez komercyjny VPN (podwójny przeskok, double hop). Działają na nim też Pi-hole jako DNS blokujący reklamy, Tor i strony administracyjne | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | **kiwi-node**, który kieruje ruch sieci lokalnej (LAN) przez VPN. Działają na nim też Pi-hole, przekazywanie zapytań DHCP (DHCP relay), stacja pobierania plików i SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | **kiwi-node** z Nextcloud i Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | **kiwi-node** z dwoma podstawowymi modułami, do których dodajesz potrzebne ci moduły | `vpn-client`, `reverse-proxy` |

Rola `node` ma kilka presetów. Preset to gotowa lista modułów.
Starsze nazwy ról `node-gw` i `node-cloud` nadal działają i oznaczają presety
`gateway` i `cloud`.

Role `master` i `node` są zbudowane z modułów, a moduł to jedna usługa.
kiwi-server zamienia moduły hosta w **stack**, czyli wszystkie kontenery, które
uruchamia maszyna. Domyślnie stack składa się z podman quadlets, czyli
jednostek systemd uruchamiających kontenery. Z `runtime: docker` uruchamia go
docker compose. Na maszynie `kiwi-stack` uruchamia stack i pilnuje, żeby
działał. Zobacz [Moduły](modules.md).

## `master` { #master }

Rola `master` zmienia te wartości domyślne modułów:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` i `reverse-proxy`: `network_mode: vpn-server`

Dzięki tym ustawieniom Pi-hole, Tor i nginx współdzielą sieciową przestrzeń
nazw (network namespace) serwera WireGuard, czyli zestaw interfejsów i adresów
sieciowych, który widzi kontener. Te trzy usługi są więc dostępne pod adresem
mastera w sieci mesh, czyli w prywatnej sieci WireGuard. Kontenery na masterze
mają nazwy `km-…` i są podłączone do sieci `knet-master` (`172.64.0.0/24`).

Na masterze mogą też działać `nostr-relay` i `hub` (do prowadzenia
[huba społeczności](../people/hubs.md)), `portainer` oraz `backup`. Żeby ich
używać, dodaj je do listy `modules:` mastera. Przekaźnik i hub działają
wyłącznie na masterach.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

To preset decyduje, jakie moduły uruchamia node. Jeśli napiszesz własną listę
`modules:`, zastąpi ona listę presetu, a moduły wymagane przez moduły z listy
zostaną dodane automatycznie. Kontenery na nodzie mają nazwy `kn-…` i są
podłączone do sieci `knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # na lychee działa moduł backup-server
```

Preset `gateway` udostępnia też własną stronę WWW Pi-hole’a pod
`127.0.0.1:8080` na nodzie (`expose_web_ui: true`). Niezależnie od tego
ustawienia reverse proxy udostępnia tę stronę przez TLS pod
`pihole.<hostname>`.

## Własna rola { #writing-a-role }

Możesz napisać własną rolę. Rola to katalog `roles/<name>/` z plikami
`role.yaml` i `apply.sh`. Rola zbudowana z modułów wypisuje je w `role.yaml`
i dołącza wspólne ustawienia stacku. Jej `apply.sh` składa się wtedy z jednego
wywołania.

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

Rola bez modułów wykonuje całą pracę sama w `ks_role_apply()`. Może przy tym
korzystać z biblioteki `roles/common/lib.sh`, która pochodzi z kiwi-stack.
Ustawienia zadeklarowane w `role.yaml` są dostępne w skrypcie jako zmienne
`KS_ROLE_<KEY>`. Skrypt działa jako root z `set -euo pipefail`. Testy projektu
generują konfigurację każdej roli w repozytorium i sprawdzają ją programem
shellcheck.
