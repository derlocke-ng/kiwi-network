# kiwi-server

kiwi-server to narzędzie, które tworzy Kiwi Network i nią zarządza. Każdą
maszynę opisujesz w jednym pliku, `fleet.yaml`, a kiwi-server na jego podstawie
konfiguruje maszyny, więc nie musisz instalować i ustawiać każdej z nich
ręcznie.

Dla każdego hosta kiwi-server tworzy **instalacyjny obraz ISO do instalacji
bezobsługowej**. Taki obraz bez zadawania pytań instaluje system Fedora
CoreOS, uCore albo Debian, a potem wyłącza maszynę. Następnie kiwi-server przez SSH
**stosuje** rolę maszyny, dzięki czemu staje się ona `kiwi-master` albo
`kiwi-node`. Potem nadal zajmuje się twoimi maszynami: dodaje klientów WireGuard,
odczytuje stan każdej maszyny, przechowuje sekrety (hasła i klucze), robi kopię
zapasową pliku fleet i sekretów oraz odblokowuje zaszyfrowane dyski.

kiwi-server jest dostępny jako narzędzie wiersza poleceń (CLI), `kiwi-server`,
i jako aplikacja GTK4, **Kiwi Server**. Oba instalują się w `~/.local` i nie
potrzebują uprawnień roota.

- Repozytorium: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Najnowsze wydanie: **v2.42.0**. Znajdziesz je w [katalogu aplikacji Kiwi](../desktop/catalogs.md).
- kiwi-server opiera się na [kiwi-modules](single.md) v0.23.0, które zawiera
  moduły i program generujący z nich konfigurację, oraz na
  [kiwi-stack](single.md) v0.5.0, czyli części działającej na każdej maszynie.
  Kopie obu są dołączone do kiwi-server (vendoring), a ich wersje są
  przypięte do tagów.

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

Możesz też zainstalować narzędzie z kopii repozytorium: uruchom
`./install.sh install`, a potem `kiwi-server doctor`.

kiwi-server wymaga Pythona 3.9+ z PyYAML i Jinja2 oraz programów `openssl`
i `ssh`. Zaszyfrowany magazyn sekretów potrzebuje `age`. Do budowania obrazów
ISO potrzebne są `butane`, `coreos-installer` i `xorriso`, a dla Debiana
dodatkowo `cpio`, `gzip` i `curl`. Na Silverblue i Bluefin nie nakładaj tych
pakietów na system (layering). Zamiast tego zbuduj narzędzia do ISO jako jeden
obraz kontenera:

```bash
kiwi-server toolchain build     # używany automatycznie, gdy brakuje narzędzi
```

`qrencode` (dla `enroll --qr`), `shellcheck` i `docker compose` są opcjonalne.

## Od zera do działającej sieci { #from-nothing-to-a-running-network }

Poniższe polecenia prowadzą od pustego folderu do działającej sieci
z masterem, jednym node’em i twoimi urządzeniami:

```bash
kiwi-server init                          # plik fleet.yaml z komentarzami
$EDITOR fleet.yaml                        # hosty, role, twój klucz SSH, dysk do instalacji
kiwi-server secrets init fleet.yaml       # opcjonalnie: secrets/ jako jeden magazyn zaszyfrowany age
kiwi-server validate fleet.yaml

# master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   uruchom z niego maszynę; zainstaluje się i wyłączy; włącz ją ponownie
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# każdy node: najpierw jego klient WireGuard, potem nośnik, potem rola
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# twoje urządzenia
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # co zgłasza każda maszyna
```

Domyślnie instalacyjny obraz ISO **nie zawiera żadnych sekretów stacku**.
Jest na nim tylko system bazowy, a rolę i jej stack (wszystkie kontenery
i konfigurację maszyny) wysyła później na maszynę polecenie `apply`. Jeśli
maszyna nie jest dostępna przez SSH, `build --offline` umieszcza na ISO całą
rolę razem z sekretami. Takiego obrazu nie wgrywaj do magazynu ISO dostawcy
hostingu i usuń go po instalacji.

**Jeśli w ogóle nie chcesz używać ISO,** polecenie
`kiwi-server script fleet.yaml papaya` wypisze skrypt dla maszyny, którą
zainstalujesz samodzielnie. Z opcją `--offline` skrypt zawiera całą rolę.

Na VPS-ie w netcup polecenie `kiwi-server vps install fleet.yaml sorbet`
czyści serwer i instaluje ISO przez API netcup, więc nikt nie musi siedzieć
przy konsoli. Na razie netcup to jedyny obsługiwany dostawca hostingu. Kolejni
są [planowani](roadmap.md#more-hosters-and-network-boot).

## Polecenia { #commands }

| Polecenie | Co robi |
|---|---|
| `init [fleet.yaml]` | Zapisuje przykładowy plik fleet. `--domain` ustawia domenę, domyślnie `home`. |
| `validate fleet.yaml [host…]` | Sprawdza plik fleet. Generuje przy tym każdy stack, więc wychodzą na jaw także błędy w modułach. |
| `list` / `show fleet.yaml <host>` | Pierwsze polecenie wypisuje hosty i to, co już dla nich wygenerowano. Drugie pokazuje faktyczną konfigurację jednego hosta, z zamaskowanymi sekretami. |
| `render fleet.yaml [host…]` | Zapisuje skrypty ról, stacki i konfiguracje instalacji w `output/<host>/`. |
| `build fleet.yaml [host…]` | Generuje konfigurację, a potem buduje ISO. Domyślnie ISO zawiera tylko system bazowy, a z `--offline` całą rolę. |
| `script fleet.yaml <host>` | Wypisuje skrypt dla dowolnej maszyny. Z `--offline` skrypt zawiera całą rolę. |
| `apply fleet.yaml <host…>` | Ponownie generuje konfigurację, wysyła rolę na maszynę przez SSH i tam ją uruchamia (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Pokazuje, co zgłaszają maszyny: rolę, stack, problemy, dyski, kopie zapasowe i certyfikaty. |
| `enroll fleet.yaml <host\|name>` | Tworzy klienta WireGuard na masterze albo pobiera istniejącego (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Zarządza `secrets/` jako jednym plikiem zaszyfrowanym age, który po odblokowaniu jest otwierany w pamięci (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Pokazuje wygenerowane hasła hosta. |
| `ca fleet.yaml` | Pokazuje urząd certyfikacji (CA) sieci. |
| `mtu fleet.yaml <node\|device\|address>` | Mierzy rzeczywiste MTU tunelu i podpowiada, jaką wartość ustawić (`--write`). |
| `openwrt fleet.yaml` | Zapisuje skrypt, który dołącza router z OpenWrt do sieci mesh ([Routery](../network/routers.md)). |
| `backup` / `restore` / `prune` | Robi kopię zapasową katalogu z plikiem fleet na node’ach, przywraca go stamtąd i usuwa stare kopie zapasowe maszyn ([Eksploatacja](operations.md)). |
| `unlock fleet.yaml <host>` | Przekazuje pierścień Tang do maszyny, która przy starcie czeka na odblokowanie zaszyfrowanego dysku ([Eksploatacja](operations.md)). |
| `vps login\|list\|probe\|install` | Obsługuje API Server Control Panel firmy netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Pokazuje, co jest dostępne, z każdym ustawieniem i jego wartością domyślną. |
| `toolchain [status\|build]`, `doctor` | Zarządza narzędziami do ISO i sprawdza ten komputer. |

Każde polecenie przyjmuje `--porcelain` (wynik w JSON), `-o/--output-dir`,
`--quiet` i `-v`. `kiwi-server <command> -h` opisuje pojedyncze polecenie.

## Aplikacja { #the-app }

Aplikacja **Kiwi Server** otwiera ostatnio używany plik fleet.
Na pasku bocznym ma przegląd, jeden wiersz na każdy host i wartości domyślne.
Widok *Overview* hosta pokazuje bieżące dane z `kiwi-server status`. Gdy okno
jest aktywne, aplikacja pobiera je raz na minutę przez SSH, wyłącznie do
odczytu. *Settings* hosta to formularz zbudowany na podstawie ról i modułów.
*Apply*, *Build* i *Render* uruchamiają narzędzie wiersza poleceń i na bieżąco
pokazują jego wynik. Zanim *Build* zacznie, wypisuje dyski, które wyczyści.
*Unlock* i *Lock* otwierają i zamykają magazyn sekretów. Aplikacja zapisuje
zwykły YAML, więc gdy zapisze plik fleet napisany ręcznie, komentarze w nim
przepadną.

## O czym pamiętać { #mind }

!!! danger "Obrazy ISO czyszczą wskazany dysk"
    Instalacyjny obraz ISO czyści dysk, dla którego został zbudowany, gdy
    tylko maszyna z niego wystartuje, i o nic nie pyta. Oznaczaj swoje obrazy
    ISO. Właśnie dlatego `build` wymaga ustawienia `disk:`.

- **Pliki wynikowe zawierają sekrety.** Są to skróty haseł, klucze WireGuard, klucze TLS
  i klucze LUKS. Pliki są zapisywane z uprawnieniami 0600, a git ignoruje
  `output/`. Z obrazami ISO zbudowanymi z `--offline` obchodź się tak samo
  ostrożnie.
- **Hasła usług są generowane** z `secrets/seed`, jeśli nie wpiszesz ich do
  pliku fleet. `validate` ostrzega przed hasłami wpisanymi w plik fleet,
  a `kiwi-server secrets show` wypisuje wygenerowane. Maszyna odrzuca `apply`
  przygotowane z innym seedem.
- **Klucze hosta SSH** są zapisywane w `secrets/known_hosts`, gdy kiwi-server
  po raz pierwszy łączy się z maszyną. Jeśli klucz maszyny później się zmieni,
  połączenie zostanie odrzucone. Po ponownej instalacji maszyny usuń jej
  wiersz z tego pliku.
- **Skrypt roli działa jako root.** Zanim zaufasz roli, której nie jesteś
  autorem, przeczytaj wynik `kiwi-server script fleet.yaml <host>
  --offline`.
- **Nieudana rola jest zgłaszana.** Na maszynie zostaje plik
  `/var/lib/kiwi-server/role.failed` z nazwą kroku i polecenia, które się nie
  powiodły, a `status` go pokazuje.

## Stan { #status }

Cały proces, od pliku fleet do działającej maszyny, został przetestowany na
prawdziwym sprzęcie w październiku i listopadzie 2026. Debian, uCore i Fedora
CoreOS przeszły go w całości na dwóch VPS-ach, mini PC i maszynie wirtualnej.
W ćwiczeniu, które symulowało awarię node’a, zaszyfrowaną maszynę z Debianem
odbudowano w około 14 minut. Kopie zapasowe node’a przywrócono z jednego
node’a na drugi (z papaya na lychee). MTU tunelu zmierzono i dostrojono na
prawdziwych łączach, także komórkowych. Testy automatyczne (CI) generują
konfigurację każdej roli, sprawdzają każdy skrypt programem shellcheck
i walidują każdą konfigurację Butane. Porównują też bajt po bajcie cztery
wzorcowe stacki (golden stacks) z ich zapisanym wynikiem.

Federacji między sieciami jeszcze nie przetestowano. Wszystko działa na IPv4.
Obraz ISO Debiana istnieje tylko dla amd64. Warstwa sterowania (control plane,
`kiwi-server serve`) jest planowana i zaprojektowana, ale jeszcze
niezrealizowana.

Czytaj dalej: [Plik fleet](fleet.md) · [Role](roles.md) · [Moduły](modules.md) ·
[Maszyny](machines.md) · [Eksploatacja](operations.md) ·
[Jedna maszyna bez pliku fleet](single.md)
