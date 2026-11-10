# Plik fleet

`fleet.yaml` opisuje każdą maszynę, którą buduje kiwi-server. Ma dwa klucze:
`defaults`, który dotyczy każdego hosta, i `hosts`, z jednym wpisem na
maszynę. Wszystko, co ustawia host, nadpisuje wartości domyślne.
`kiwi-server init` zapisuje punkt wyjścia z komentarzami, a pełna dokumentacja
referencyjna to
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Host ma **target** (co zostaje zainstalowane) i **rolę** (czym się staje):

- `target`: `coreos`, `ucore` (domyślnie) lub `debian`. Zobacz [Maszyny](machines.md).
- `role`: `bare` (domyślnie), `master` lub `node`. Zobacz [Role](roles.md).

## Przykład { #example }

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya staje się papaya.home; usługi to cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # CZYSZCZONY przez ISO bez pytania
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # master, VPS z Debianem
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # adres, z którym łączą się klienci i każdy node

  lychee:                                # node gateway
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # strona LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # node cloud na uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # dla pierwszego konta; potem wyłącz
```

Nie ma w nim haseł usług. Każde pominięte hasło jest generowane z
`secrets/seed`, a `kiwi-server secrets show fleet.yaml papaya` je wypisuje.
Konfiguracje WireGuard node'ów też nie są w nim wymienione:
`kiwi-server enroll` zapisuje `secrets/<hostname>.conf`, który każdy node sam
znajduje, a adres node'a w sieci mesh jest odczytywany z tego pliku.

## Wartości domyślne { #defaults }

| Klucz | Domyślnie |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | brak; wymagany dla `build`, musi zaczynać się od `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; podaj `password_hash` dla konsoli |
| `network` | `dhcp: true`; statycznie z `address` (CIDR), `gateway`, `dns` albo `iprange`, który rozdaje adresy w kolejności z pliku |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (albo `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | pierścienie Tang, z którymi wiązany jest dysk (zobacz [Eksploatacja](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | dokąd trafia kopia zapasowa katalogu floty (`hosts: []`, `keep: 10`) |
| `vps` | `server:` id, nazwa lub pseudonim serwera netcup |

## Jak łączą się ustawienia { #how-settings-combine }

- Hosty nadpisują wartości domyślne **klucz po kluczu**. Listy
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` i listy
  `coreos.*` zamiast tego *dodają* się do wartości domyślnych.
- Rola modułowa trzyma swoje ustawienia w bloku nazwanym jak rola (`master:`,
  `node:`): najpierw **ustawienia stacka**, potem **po jednym bloku na
  moduł**.
- `modules:` w tym bloku **zastępuje** listę modułów presetu. Wymagane moduły
  są dodawane same.
- **Ustawienia plikowe** (certyfikaty, konfiguracje) to ścieżki względem pliku
  fleet. Ich zawartość jest osadzana w skrypcie roli hosta.
- Ustawienie podane bez wartości oznacza wartość domyślną. Klucz z literówką
  to błąd z podpowiedzią.

## Ustawienia stacka { #stack-settings }

| Ustawienie | Domyślnie | Uwagi |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` lub `minimal` |
| `runtime` | `podman` | quadlety podmana; `docker` uruchamia docker compose |
| `auto_update` | `registry` | cotygodniowe `podman auto-update`; `off`: obrazy zmieniają się przy apply |
| `docker_dir` | `/home/user/docker` | stack i jego dane |
| `service_user` | użytkownik administracyjny | jest właścicielem katalogów z danymi |
| `vpn_ip` | z konfiguracji WireGuard | adres maszyny w sieci mesh |
| `master_ip` | z floty | adres mastera w sieci mesh |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | zmierz przez `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | z trasy domyślnej | interfejs LAN |
| `daily_vpn_restart` | `07:00` | puste: nigdy |
| `weekly_update` | `Sun *-*-* 00:00` | puste: nigdy |

`kiwi-server roles -v` i `kiwi-server modules -v` wypisują każde ustawienie z
jego wartością domyślną.

## Sprawdzanie napisanego pliku { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # błędy i ostrzeżenia
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server sprawdza też domenę: `.local` jest odrzucana, a `.lan` i publiczne
domeny najwyższego poziomu dają ostrzeżenie (zobacz
[DNS](../network/dns.md#names-servicehostnamehome)).

## Przejęcie maszyny v1 { #taking-over-a-v1-machine }

Maszynę, na której działał jeden ze starych stacków v1, można przejąć bez
utraty danych. Domyślnym środowiskiem uruchomieniowym jest teraz podman, a
skrypt roli nie zatrzymuje kontenerów dockera. Ustaw więc `runtime: docker`
albo najpierw zatrzymaj stary stack. Potem ustaw `docker_subnet` na to, czego
używał stary stack, i zmień nazwy katalogów z danymi na nazwy modułów
(`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`, …). Kontenery
zachowują swoje adresy, a wg-easy zachowuje swoich peerów.
