# Plik fleet

W pliku fleet, `fleet.yaml`, opisujesz każdą maszynę swojej Kiwi Network. Dla
każdej z nich podajesz, jaki system operacyjny dostanie, do czego będzie
służyć i jak mają być skonfigurowane jej usługi. kiwi-server buduje każdą
maszynę według tego opisu, więc zapisujesz swoje wymagania raz i nie musisz
niczego konfigurować ręcznie na żadnej maszynie.

Plik ma dwa klucze. `defaults` zawiera ustawienia wspólne dla wszystkich
hostów, a `hosts` ma po jednym wpisie na każdą maszynę. Ustawienie we wpisie
hosta ma pierwszeństwo przed tym samym ustawieniem w `defaults`. Polecenie
`kiwi-server init` zapisuje plik z komentarzami, od którego możesz zacząć,
a pełną dokumentację wszystkich ustawień znajdziesz w
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Każdy host ma **system docelowy** (`target`), czyli system operacyjny, który
zostanie zainstalowany, i **rolę** (`role`), czyli zadanie, jakie maszyna
będzie potem wykonywać.

- `target` to `coreos`, `ucore` (domyślnie) albo `debian`. Zobacz [Maszyny](machines.md).
- `role` to `bare` (domyślnie), `master` albo `node`. Zobacz [Role](roles.md).

## Przykład { #example }

Ten plik fleet opisuje trzy maszyny. Pierwsza to master, czyli maszyna,
z którą łączą się wszystkie pozostałe. Działa na VPS-ie z Debianem, czyli na
wynajętym serwerze wirtualnym. Druga to node `gateway`, który kieruje ruch sieci
lokalnej przez VPN. Trzecia to node `cloud` z Nextcloud i Vaultwarden.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya to papaya.home; usługi to cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # ISO CZYŚCI go bez pytania
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
        wg_host: vpn.example.org     # adres, z którym łączą się klienci i node'y

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

W przykładzie nie ma haseł usług. Każde hasło, którego nie podasz, kiwi-server
generuje z seeda zapisanego w `secrets/seed`, a polecenie
`kiwi-server secrets show fleet.yaml papaya` wypisuje hasła tego hosta.

W przykładzie nie wskazano też plików konfiguracyjnych WireGuard node’ów.
`kiwi-server enroll` zapisuje konfigurację node’a w `secrets/<hostname>.conf`,
a klient VPN node’a znajduje ją tam bez żadnego wpisu w pliku fleet. Z tego
samego pliku odczytywany jest adres node’a w sieci mesh. Sieć mesh to prywatna
sieć WireGuard, która łączy wszystkie twoje maszyny, a adres w sieci mesh to
adres maszyny w tej sieci.

## Wartości domyślne { #defaults }

Jeśli klucza nie ustawia ani twój blok `defaults`, ani żaden host, kiwi-server
używa wbudowanej wartości z tej tabeli.

| Klucz | Wartość domyślna |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Brak wartości domyślnej. `build` jej wymaga, a wartość musi zaczynać się od `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Ustaw `password_hash`, jeśli chcesz logować się na konsoli |
| `network` | `dhcp: true`. Dla stałego adresu ustaw `address` (w notacji CIDR), `gateway` i `dns`. Możesz też ustawić `iprange`, z którego hosty dostają adresy w kolejności, w jakiej występują w pliku |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (albo `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Pierścienie Tang, do których przypisany jest dysk. Pierścień to serwer Tang, dzięki któremu zaszyfrowana maszyna może odblokować dysk przy starcie (zobacz [Eksploatacja](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | Hosty, na których przechowywana jest kopia zapasowa katalogu z plikiem fleet, i liczba przechowywanych kopii (`hosts: []`, `keep: 10`) |
| `vps` | `server:` identyfikator, nazwa albo pseudonim (nickname) serwera w netcup |

## Jak łączą się ustawienia { #how-settings-combine }

- Host nadpisuje wartości domyślne **klucz po kluczu**, więc wystarczy, że
  poda tylko te klucze, które się różnią. Wyjątkiem są listy
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` i listy
  `coreos.*`. Wpisy hosta w tych listach są *dopisywane* do wartości
  domyślnych, zamiast je zastępować.
- Role zbudowane z modułów, `master` i `node`, trzymają swoje ustawienia
  w bloku nazwanym tak jak rola (`master:` albo `node:`). W tym bloku są
  najpierw **ustawienia stacku**, a potem **po jednym bloku na każdy moduł**.
  Stack to wszystkie kontenery, które maszyna uruchamia dla swoich modułów,
  a ustawienia stacku dotyczą ich wszystkich.
- Lista `modules:` w tym bloku **zastępuje** listę modułów presetu. Preset to
  gotowa lista modułów. Moduły, których wymagają moduły z listy, są dodawane
  automatycznie.
- **Ustawienia wskazujące pliki**, na przykład certyfikaty i pliki konfiguracyjne,
  podaje się jako ścieżki względem pliku fleet. kiwi-server kopiuje zawartość
  tych plików do skryptu roli hosta, czyli skryptu, który konfiguruje maszynę
  do jej roli.
- Ustawienie zapisane bez wartości dostaje wartość domyślną. Jeśli zrobisz
  literówkę w nazwie klucza, kiwi-server zgłosi błąd i podpowie klucz, o który
  prawdopodobnie chodziło.

## Ustawienia stacku { #stack-settings }

Ustawienia stacku dotyczą całego stacku maszyny. Wpisujesz je bezpośrednio
w bloku roli.

| Ustawienie | Wartość domyślna | Uwagi |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` albo `minimal` |
| `runtime` | `podman` | `podman` uruchamia kontenery jako podman quadlets, czyli jednostki systemd dla kontenerów. `docker` używa docker compose |
| `auto_update` | `registry` | `registry` uruchamia `podman auto-update` raz w tygodniu. Przy `off` obrazy kontenerów zmieniają się tylko wtedy, gdy ponownie zastosujesz konfigurację hosta |
| `docker_dir` | `/home/user/docker` | katalog ze stackiem i jego danymi |
| `service_user` | użytkownik administracyjny | użytkownik, do którego należą katalogi z danymi |
| `vpn_ip` | z konfiguracji WireGuard | adres maszyny w sieci mesh |
| `master_ip` | z pliku fleet | adres mastera w sieci mesh |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | możesz je zmierzyć poleceniem `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | z trasy domyślnej | interfejs sieciowy po stronie LAN |
| `daily_vpn_restart` | `07:00` | pusta wartość wyłącza codzienny restart |
| `weekly_update` | `Sun *-*-* 00:00` | pusta wartość wyłącza cotygodniową aktualizację |

`kiwi-server roles -v` i `kiwi-server modules -v` wypisują każde ustawienie
z jego wartością domyślną.

## Sprawdzanie pliku { #checking-what-you-wrote }

kiwi-server może sprawdzić plik fleet i pokazać, jak rozumie konfigurację
jednego hosta.

```bash
kiwi-server validate fleet.yaml          # błędy i ostrzeżenia
kiwi-server show fleet.yaml papaya          # faktyczna konfiguracja jednego hosta, sekrety zamaskowane
```

kiwi-server sprawdza też domenę. Odrzuca `.local`, a przy `.lan`
i publicznych domenach najwyższego poziomu wyświetla ostrzeżenie (zobacz
[DNS](../network/dns.md#names-servicehostnamehome)).

## Przejęcie maszyny z v1 { #taking-over-a-v1-machine }

Maszynę, na której działał jeden ze starych stacków v1, możesz włączyć do
pliku fleet bez utraty danych. Domyślnym środowiskiem uruchomieniowym jest teraz
podman, a skrypt roli nie zatrzymuje działających jeszcze kontenerów dockera.
Ustaw więc `runtime: docker` albo najpierw zatrzymaj stary stack. Następnie
ustaw w `docker_subnet` podsieć, której używał stary stack, i zmień nazwy
katalogów z danymi na nowe nazwy modułów (`kmvpn-server` → `km-vpn-server`,
`knvault` → `kn-vault`, …). Kontenery zachowają wtedy swoje adresy, a wg-easy
swoich peerów.
