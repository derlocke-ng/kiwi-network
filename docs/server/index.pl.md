# kiwi-server

kiwi-server tworzy Kiwi Network i nią zarządza. Każdą maszynę opisujesz w
jednym `fleet.yaml`. kiwi-server robi dla każdego hosta **nienadzorowany obraz
ISO instalacyjny**, który instaluje Fedora CoreOS, uCore lub Debiana i
wyłącza maszynę. Potem **stosuje** (apply) rolę przez SSH i zamienia maszynę w
`kiwi-master` albo `kiwi-node`. Następnie dalej pracuje z flotą: rejestruje
klientów WireGuard, odczytuje stan każdej maszyny, przechowuje sekrety, robi
kopię zapasową floty i odblokowuje zaszyfrowane dyski.

Ma CLI, `kiwi-server`, i aplikację GTK4, **Kiwi Server**. Obie instalują się w
`~/.local` i nie potrzebują roota.

- Repozytorium: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Najnowsze wydanie: **v2.42.0**. Jest w [katalogu Kiwi](../desktop/catalogs.md).
- Zbudowany na [kiwi-modules](single.md) v0.23.0 (moduły i ich renderer)
  i [kiwi-stack](single.md) v0.5.0 (strona maszyny), dołączonych do
  repozytorium (vendored) i przypiętych tagiem.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Instalacja { #install }

```bash
kiwi install kiwi-server        # przez kiwi-updater
```

Albo z checkoutu: `./install.sh install`, potem `kiwi-server doctor`.

Potrzebuje Pythona 3.9+ z PyYAML i Jinja2, `openssl` i `ssh`. Magazyn
sekretów potrzebuje `age`. Budowanie obrazów ISO wymaga `butane`,
`coreos-installer` i `xorriso` (plus `cpio`, `gzip` i `curl` dla Debiana). Na
Silverblue lub Bluefin zbuduj je jako jeden obraz kontenera zamiast nakładać
pakiety:

```bash
kiwi-server toolchain build     # używany automatycznie, gdy brakuje narzędzi
```

`qrencode` (dla `enroll --qr`), `shellcheck` i `docker compose` są opcjonalne.

## Od zera do działającej sieci { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # fleet.yaml z komentarzami
$EDITOR fleet.yaml                        # hosty, role, twój klucz SSH, dysk instalacyjny
kiwi-server secrets init fleet.yaml       # opcjonalnie: secrets/ jako jeden magazyn zaszyfrowany age
kiwi-server validate fleet.yaml

# master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   uruchom z niego; instaluje się i wyłącza; włącz ponownie
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# każdy node: najpierw jego klient WireGuard, potem nośnik, potem rola
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# twoje własne urządzenia
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # co raportuje każda maszyna
```

Nośniki domyślnie nie zawierają **żadnych sekretów stacka**: tylko system
bazowy. Rola i jej stack przychodzą z `apply`. Jeśli maszyna nie jest
osiągalna przez SSH, `build --offline` umieszcza całą rolę i jej sekrety na
obrazie ISO. Nie trzymaj takiego obrazu w magazynie ISO dostawcy i usuń go po
instalacji.

**W ogóle bez ISO?** `kiwi-server script fleet.yaml papaya` wypisuje skrypt dla
maszyny zainstalowanej samodzielnie (`--offline` dla całej roli).

Na VPS-ie netcup `kiwi-server vps install fleet.yaml sorbet` czyści serwer i
instaluje obraz ISO przez API netcup.

## Polecenia { #commands }

| Polecenie | Co robi |
|---|---|
| `init [fleet.yaml]` | zapisuje przykładowy plik fleet (`--domain`, domyślnie `home`) |
| `validate fleet.yaml [host…]` | sprawdza go, renderując każdy stack, żeby wyłapać błędy modułów |
| `list` / `show fleet.yaml <host>` | hosty i to, co zostało wygenerowane / efektywna konfiguracja jednego hosta, z zamaskowanymi sekretami |
| `render fleet.yaml [host…]` | skrypty ról, stacki i konfiguracje instalacji do `output/<host>/` |
| `build fleet.yaml [host…]` | renderuje, potem obraz ISO: domyślnie system bazowy, `--offline` dla całej roli |
| `script fleet.yaml <host>` | skrypt dla dowolnej maszyny (`--offline` dla całej roli) |
| `apply fleet.yaml <host…>` | renderuje ponownie, wysyła rolę przez SSH i ją uruchamia (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | co raportują maszyny: rola, stack, problemy, dyski, kopie zapasowe, certyfikaty |
| `enroll fleet.yaml <host\|name>` | tworzy lub pobiera klienta WireGuard na masterze (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` jako jeden plik zaszyfrowany age, otwierany do pamięci (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | wygenerowane hasła hosta |
| `ca fleet.yaml` | CA floty |
| `mtu fleet.yaml <node\|device\|address>` | mierzy rzeczywiste MTU tunelu i podpowiada, co ustawić (`--write`) |
| `openwrt fleet.yaml` | skrypt, który dołącza router OpenWrt do sieci mesh ([Routery](../network/routers.md)) |
| `backup` / `restore` / `prune` | katalog floty na node'y i z powrotem; usuwanie starych kopii zapasowych maszyn ([Eksploatacja](operations.md)) |
| `unlock fleet.yaml <host>` | przekazuje pierścień Tang do maszyny czekającej przy starcie ([Eksploatacja](operations.md)) |
| `vps login\|list\|probe\|install` | API Server Control Panel netcup |
| `roles [-v]`, `modules [-v]`, `targets` | co jest dostępne, z każdym ustawieniem i jego wartością domyślną |
| `toolchain [status\|build]`, `doctor` | narzędzia do ISO; sprawdzenie tej maszyny |

Każde polecenie przyjmuje `--porcelain` (JSON), `-o/--output-dir`, `--quiet` i
`-v`. `kiwi-server <command> -h` objaśnia jedno polecenie.

## Aplikacja { #the-app }

**Kiwi Server** otwiera twoją ostatnią flotę. Pasek boczny ma przegląd, jeden
wiersz na hosta i ustawienia domyślne. *Overview* hosta pokazuje bieżące dane z
`kiwi-server status` (odpytywane raz na minutę, gdy okno ma fokus, tylko do
odczytu przez SSH). Jego *Settings* to formularz zbudowany z ról i modułów.
*Apply*, *Build* i *Render* uruchamiają CLI i strumieniują jego wynik, a
*Build* przed startem wypisuje dyski, które wyczyści. *Unlock* i *Lock*
otwierają i zamykają magazyn sekretów. Aplikacja zapisuje zwykły YAML, więc
komentarze w ręcznie pisanym pliku fleet giną przy zapisie.

## Uwaga { #mind }

!!! danger "Obrazy ISO czyszczą dysk, który im wskazano"
    Przy starcie, bez pytania. Oznacz je. `disk:` jest wymagany dla `build`
    właśnie z tego powodu.

- **Wynik zawiera sekrety**: skróty haseł, klucze WireGuard, klucze TLS, klucze
  LUKS. Pliki są zapisywane z uprawnieniami 0600, a `output/` jest ignorowany
  przez gita. Tak samo traktuj obrazy ISO zrobione z `--offline`.
- **Hasła usług są generowane** z `secrets/seed`, gdy pominiesz je w pliku
  fleet. `validate` ostrzega o hasłach w nim wpisanych.
  `kiwi-server secrets show` je wypisuje. Maszyna odrzuca apply zrobione z
  innym seedem.
- **Klucze hosta SSH** są zapisywane w `secrets/known_hosts` przy pierwszym
  kontakcie, a zmieniony klucz jest odrzucany (po reinstalacji usuń tę linię).
- **Skrypt roli działa jako root.** Przeczytaj `kiwi-server script fleet.yaml <host>
  --offline`, zanim zaufasz roli, której autorem nie jesteś.
- **Nieudana rola to mówi.** Maszyna zachowuje `/var/lib/kiwi-server/role.failed`
  (krok i polecenie), a `status` to pokazuje.

## Stan { #status }

Potok został sprawdzony na sprzęcie w październiku i listopadzie 2026. Debian,
uCore i Fedora CoreOS zostały uruchomione od początku do końca na dwóch
VPS-ach, mini PC i maszynie wirtualnej, a ćwiczenie z martwym node'em
odbudowało zaszyfrowaną maszynę z Debianem w około 14 minut. Kopie zapasowe
node'ów zostały odtworzone z jednego node'a na innym (z papaya na lychee), a
MTU tunelu zostało zmierzone i dostrojone na prawdziwych ścieżkach, w tym
mobilnych. CI renderuje każdą rolę, sprawdza każdy skrypt shellcheckiem,
waliduje każdą konfigurację Butane i przypina cztery wzorcowe stacki bajt w
bajt.

Jeszcze niesprawdzone: federacja między sieciami. Wszystko działa na IPv4.
Obraz ISO Debiana jest tylko dla amd64. Planowana płaszczyzna sterowania
(`kiwi-server serve`) jest zaprojektowana, ale niezbudowana.

Czytaj dalej: [Plik fleet](fleet.md) · [Role](roles.md) · [Moduły](modules.md) ·
[Maszyny](machines.md) · [Eksploatacja](operations.md) ·
[Jedna maszyna bez floty](single.md)
