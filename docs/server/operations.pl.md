# Eksploatacja

Codzienna praca z działającą flotą, w całości z maszyny operatora.

## Stan { #status }

```bash
kiwi-server status fleet.yaml            # każdy host
kiwi-server status fleet.yaml papaya        # jeden
```

Każda maszyna raportuje przez SSH (tylko do odczytu): swoją rolę, swój stack,
problemy (nieudana rola, zatrzymany kontener), swoje dyski i to, czy są
zaszyfrowane lub zablokowane, swoje kopie zapasowe i ile zostało ważności jej
certyfikatom. Node z kopiami zapasowymi raportuje też swoją pojemność.
Aplikacja Kiwi Server pokazuje to samo w *Overview* każdego hosta.

## Sekrety { #secrets }

Wszystko, co tajne, leży w `secrets/` obok pliku fleet: seed, z którego
wyprowadzane jest każde wygenerowane hasło, CA floty, konfiguracje WireGuard,
klucze LUKS i klucze hostów SSH.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ staje się jednym plikiem zaszyfrowanym age
kiwi-server secrets unlock fleet.yaml    # otwórz go do pamięci (--for 8h; 0 zostawia go otwartym)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` trzyma jeden klucz w GNOME Keyring i jeden raz pokazuje **klucz
odzyskiwania**. Gdy magazyn jest otwarty, może go odczytać wszystko, co działa
jako ty.

## Kopia zapasowa samej floty { #backing-up-the-fleet-itself }

Po każdym udanym renderze lub buildzie katalog floty jest szyfrowany (AES-256
z PBKDF2, 600 000 iteracji) i kopiowany na node'y wymienione w
`backup.hosts`, które przechowują dziesięć najnowszych kopii. Na świeżej
maszynie:

```bash
kiwi-server restore --from core@lychee.home  # katalog floty z powrotem
kiwi-server backup fleet.yaml --local /mnt/usb   # albo kopia do katalogu, w dowolnym momencie
```

## Kopie zapasowe danych maszyn { #backing-up-the-machines-data }

Daj node'owi moduł `backup-server` (serwer restic REST), a każdej maszynie,
która ma mieć kopię zapasową, moduł `backup` wskazujący na niego:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Co noc o 03:00 (w ciągu 15 minut po tej godzinie) restic wysyła, zaszyfrowane,
to, co każdy moduł każe zachować. Każda maszyna ma dostęp tylko do własnego
repozytorium i może do niego tylko dopisywać. Dlatego usuwanie starych
snapshotów odbywa się z maszyny operatora:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # na maszynie
kiwi-server prune fleet.yaml            # zachowaj 7 dziennych, 4 tygodniowe, 6 miesięcznych
```

Odtwarzanie przetestowano z node'a na node'a: kopie zapasowe papaya na lychee.

### W następnym wydaniu { #coming-in-the-next-release }

!!! info "Na gałęzi `several-servers`"
    Ta praca jest wypchnięta na gałęzie `several-servers` w kiwi-modules i
    kiwi-server, ale nie jest jeszcze scalona ani wydana. Kilka serwerów i
    automatyczne odtwarzanie przetestowano na sprzęcie. Kontroli stanu VPN nie.

- **Kilka serwerów kopii zapasowych.** `backup.servers` przyjmuje listę, a
  każdy serwer dostaje własną pełną kopię. Jeśli jeden serwer zawiedzie,
  brakuje tylko jego kopii. Odtwarzanie bierze najświeższą kopię z tego
  serwera, który ją ma, a `kiwi-stack snapshots` wypisuje je serwer po
  serwerze. Pojedyncze `server` nadal działa.
- **Odbudowana maszyna sama się odtwarza.** Jeśli maszyna znajduje siebie w
  kopiach zapasowych, ale nie zrobiła żadnej z nich (odbudowa), przed swoją
  pierwszą kopią sama odtwarza każdy moduł, a potem robi kopie jak wcześniej
  (`backup.restore:
  auto`, domyślnie). Z `hold` czeka na `kiwi-stack restore` lub
  `kiwi-stack backup --new`.
- **Przycinanie na timerze.** `kiwi-server prune fleet.yaml --every week` (lub
  `day`) instaluje timer użytkownika systemd na twoim komputerze, jedynym
  miejscu, które ma klucze uprawnione do usuwania. Pominięte uruchomienie
  nastąpi przy następnym logowaniu. `kiwi-server status` pokazuje każdą kopię
  zapasową i ostrzega, gdy node z kopiami zapasowymi nie był przycinany od
  trzech tygodni.
- **Zawieszone komercyjne wyjście startuje od nowa.** gluetun dostaje kontrolę
  stanu. Po pięciu minutach w złym stanie kontener jest zabijany, a przy
  następnym starcie wybiera inny serwer.

## Zaszyfrowane dyski i odblokowywanie { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) instaluje się z jednorazowym kluczem,
  który wpisujesz przy pierwszym rozruchu (`secrets/luks/<host>.once`).
  Pierwsze `apply` zastępuje go kluczem `secrets/luks/<host>.key`, a master
  dostaje też nowy klucz wolumenu. Utrata tego pliku klucza blokuje dysk, więc
  trzymaj kopię zapasową floty.
- **CoreOS / uCore** szyfrują przy instalacji przez Ignition (przy około 4 GiB
  RAM przy pierwszym rozruchu).
- **Pierścienie Tang** pozwalają zaszyfrowanym maszynom odblokować się przy
  starcie bez obecności człowieka. Node uruchamia moduł `tang` (każdy
  pierścień to jeden serwer Tang z własnymi kluczami, domyślnie `infra` na
  porcie 7500), a blok `unlock:` hosta wiąże jego dysk z pierścieniami z
  progiem.
- **SSH w initramfs** (`unlock.ssh: true`: dropbear na Debianie, dracut-sshd
  na CoreOS) używa własnego ograniczonego klucza, `secrets/unlock_ed25519`,
  który może tylko uruchomić odblokowanie.
- `kiwi-server unlock fleet.yaml <host>` przekazuje pierścień do maszyny
  czekającej przy starcie, a `--manual` przekazuje sam klucz. Pierścień
  `operator` jest serwowany z twojej własnej maszyny, dopóki jest potrzebny.
  `vpn-server.unlock_relay` dociera do maszyn za NAT-em.

## MTU tunelu { #tunnel-mtu }

WireGuard dodaje własne nagłówki, więc tunel przenosi mniejsze pakiety niż
łącze pod nim, a ścieżka mobilna jeszcze mniejsze. Pakiet zbyt duży dla
któregoś łącza po drodze zostaje odrzucony lub podzielony, a połączenia się
zawieszają. Kiwi radzi sobie z tym na trzech warstwach:

- **Dwa ustawienia.** `wg_mtu` (domyślnie **1376**, wielokrotność 16, bo
  WireGuard dopełnia do 16) to MTU gluetuna, konfiguracji klientów wg-easy i
  `wg0`. `bridge_mtu` (domyślnie **1500**) to MTU sieci stacka. `validate`
  odrzuca `wg_mtu`, którego dopełniony pakiet plus 80 bajtów nagłówków nie
  mieści się w mostku, oraz wszystko poniżej 1280, minimum, z którym działa
  IPv6.
- **MSS jest przycinane w obie strony** do `wg_mtu - 40`, w wg-easy i w
  kliencie VPN, więc TCP nigdy nie próbuje segmentu, który nie może przejść.
- **TCP samo sonduje.** Klient VPN działa z `net.ipv4.tcp_mtu_probing=1` i
  `tcp_base_mss=1024`, więc połączenie, które trafi na ścieżkę po cichu
  odrzucającą duże pakiety, znajduje działający rozmiar, zamiast się
  zawiesić.

### Pomiar ścieżki: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # urządzenie z secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # i zapisz wg_mtu w pliku fleet
```

Sonda wysyła przez tunel pingi z flagą don't-fragment, z wnętrza przestrzeni
nazw, która go trzyma. Node mierzy z jego własnego klienta VPN (którego
zapora odrzuca przychodzące pingi), a urządzenie z serwera WireGuard. Zaczyna
od zwykłego pinga, potem próbuje każdej wielokrotności 16 od 1280 w górę i
podaje największą, która dociera **w całości**. Podczas pingowania odczytuje
liczniki ponownego składania pakietów w jądrze, więc odpowiedź podzielona po
drodze i złożona z powrotem nie liczy się jako pasująca.

Podaje też, co ustawić. Dla **urządzenia** jest to jego własne `MTU =` w jego
konfiguracji WireGuard i nikogo innego to nie dotyczy. Dla **node'a** jest to
`wg_mtu` na tym nodzie i na jego masterze, które `--write` wpisuje do pliku
fleet (zmieniając tylko te linie). Pakietu, który jest dzielony tylko w drodze
na zewnątrz i składany z powrotem przez drugą stronę, nie widać z tej strony.

Wartości domyślne zmierzono na testowej flocie. Dla telefonu na danych
mobilnych, gdzie ścieżki są często tylko IPv6 za 464XLAT z zagnieżdżoną
enkapsulacją, zmierz sam telefon i obniż jego własne `MTU =`, jeśli sonda tak
wskaże.

## VPS-y netcup { #netcup-vpses }

```bash
kiwi-server vps login fleet.yaml         # logowanie device flow; token trafia do secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wipe the server and install the host's ISO
```

`vps install` najpierw pyta, chyba że podasz `--yes`. Odrzuca obraz ISO, który
zawiera sekrety roli, błędny `disk:` oraz szyfrowanie dysku CoreOS przy mniej
niż 3500 MiB RAM.
