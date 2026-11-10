# Eksploatacja

Ta strona opisuje pracę, która zaczyna się, gdy maszyny są już zainstalowane
i działają: sprawdzanie ich stanu, bezpieczne przechowywanie sekretów, kopie
zapasowe pliku fleet i danych na maszynach, odblokowywanie zaszyfrowanych
dysków, dostrajanie MTU tunelu i instalację na serwerze w netcup. Wszystko to
robisz narzędziem kiwi-server z twojego własnego komputera (*komputera
administratora*), na którym znajdują się plik fleet i sekrety.

## Stan { #status }

`kiwi-server status` pokazuje, w jakim stanie są twoje maszyny: wszystkie
albo ta, którą podasz:

```bash
kiwi-server status fleet.yaml            # każdy host
kiwi-server status fleet.yaml papaya        # jeden
```

kiwi-server łączy się z każdą maszyną przez SSH i tylko odczytuje dane. Każda
maszyna zgłasza swoją rolę i swój stack (wszystkie kontenery i usługi, które
uruchamia), ewentualne problemy, takie jak nieudana rola albo zatrzymany
kontener, swoje dyski i to, czy są zaszyfrowane lub zablokowane, swoje kopie
zapasowe oraz to, jak długo jeszcze ważne są jej certyfikaty. Node z serwerem
kopii zapasowych zgłasza też swoją pojemność. Aplikacja Kiwi Server pokazuje te
same informacje w widoku *Overview* każdego hosta.

## Sekrety { #secrets }

Wszystko, co tajne, jest przechowywane w `secrets/`, katalogu obok pliku
fleet. Jest tam seed, z którego wyprowadzane są wszystkie generowane hasła,
własny urząd certyfikacji (CA) twojej sieci, konfiguracje WireGuard, klucze
LUKS zaszyfrowanych dysków i klucze hosta SSH. kiwi-server może trzymać ten
katalog zaszyfrowany i otwierać go tylko na czas pracy:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ staje się jednym plikiem zaszyfrowanym age
kiwi-server secrets unlock fleet.yaml    # otwórz go w pamięci (--for 8h; 0 zostawia otwarty)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # wygenerowane hasła hosta
```

`secrets init` tworzy zaszyfrowany magazyn. Zapisuje jeden klucz w GNOME
Keyring i pokazuje ci **klucz odzyskiwania**. Klucz odzyskiwania jest
wyświetlany tylko raz. Dopóki magazyn jest otwarty, może go odczytać każdy
program działający na twoim koncie użytkownika.

## Kopia zapasowa pliku fleet i sekretów { #backing-up-the-fleet-itself }

Katalog z plikiem fleet zawiera ten plik oraz `secrets/`, a kiwi-server sam
robi jego kopię zapasową. Po każdym udanym `render` albo `build` (dwóch krokach, które
generują konfigurację hostów i ich instalacyjne obrazy ISO) szyfruje ten
katalog (AES-256 z PBKDF2, 600 000 iteracji) i kopiuje go na node’y wymienione
w `backup.hosts`. Każdy z tych node’ów przechowuje dziesięć najnowszych kopii.
Na nowym komputerze przywracasz ten katalog z jednego z tych node’ów.
W dowolnej chwili możesz też zapisać kopię w wybranym katalogu:

```bash
kiwi-server restore --from core@lychee.home  # przywróć katalog z plikiem fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # albo zapisz kopię w katalogu, w dowolnej chwili
```

## Kopie zapasowe danych na maszynach { #backing-up-the-machines-data }

Kopie zapasowe danych na maszynach robi restic, program do kopii zapasowych.
Kopie przechowuje jeden node. Dodaj temu node’owi moduł `backup-server`, który
uruchamia serwer REST restic. Każda maszyna, której dane mają być
zabezpieczane, dostaje moduł `backup` z ustawieniem wskazującym ten serwer:

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

Co noc o 03:00 lub do 15 minut później restic wysyła na serwer kopii
zapasowych, w postaci zaszyfrowanej, te dane, które każdy moduł chce
zachować. Maszyna ma dostęp tylko do własnego repozytorium na serwerze i może
tylko do niego dopisywać. Nie może tam niczego usunąć. Dlatego polecenie, które
usuwa stare snapshoty, uruchamia się na komputerze administratora. Snapshot to
w restic zapisany stan z jednego przebiegu kopii zapasowej. Pierwsze polecenie
poniżej uruchamiasz na samej maszynie, drugie na swoim komputerze:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # na maszynie
kiwi-server prune fleet.yaml            # zostawia 7 dziennych, 4 tygodniowe, 6 miesięcznych
```

Przywracanie przetestowano między dwoma node’ami: kopie zapasowe z papaya
przywrócono na lychee.

### W następnym wydaniu { #coming-in-the-next-release }

!!! info "Na gałęzi `several-servers`"
    Te zmiany są już wypchnięte na gałęzie `several-servers` repozytoriów
    kiwi-modules i kiwi-server, ale nie zostały jeszcze scalone ani wydane.
    Kilka serwerów kopii zapasowych i automatyczne przywracanie przetestowano
    na sprzęcie. Kontroli stanu VPN jeszcze nie.

- **Kilka serwerów kopii zapasowych.** `backup.servers` przyjmuje listę
  serwerów, a każdy serwer dostaje własną, pełną kopię. Gdy jeden serwer
  ulegnie awarii, dotyczy to tylko jego kopii. Przy przywracaniu brana jest
  najnowsza kopia, niezależnie od tego, który serwer ją ma, a `kiwi-stack snapshots` wypisuje
  snapshoty osobno dla każdego serwera. Pojedyncze ustawienie `server` nadal
  działa.
- **Odbudowana maszyna sama przywraca swoje dane.** Po odbudowie maszyna
  znajduje na serwerze kopie zapasowe samej siebie, choć sama nie zrobiła
  jeszcze żadnej. W takiej sytuacji, zanim zrobi pierwszą kopię, przywraca
  dane wszystkich modułów, a potem robi kopie tak jak wcześniej. To zachowanie
  domyślne (`backup.restore: auto`). Przy `hold` maszyna czeka, aż uruchomisz
  `kiwi-stack restore` albo `kiwi-stack backup --new`.
- **Usuwanie starych snapshotów według harmonogramu.**
  `kiwi-server prune fleet.yaml --every week` (albo `day`) instaluje na twoim
  komputerze timer użytkownika systemd. Twój komputer to jedyne miejsce, gdzie
  są klucze uprawnione do usuwania. Pominięte uruchomienie zostanie nadrobione
  przy następnym logowaniu. `kiwi-server status` pokazuje
  każdą kopię zapasową i ostrzega, gdy na nodzie z kopiami od trzech tygodni
  nie usuwano starych snapshotów.
- **Zawieszone połączenie z komercyjnym dostawcą VPN samo wraca do
  działania.** gluetun, kontener klienta VPN, dostaje kontrolę stanu (health
  check), która co jakiś czas sprawdza, czy połączenie nadal działa. Jeśli przez
  pięć minut wypada źle, kontener zostaje zatrzymany siłą (kill), a przy następnym
  starcie wybiera inny serwer.

## Zaszyfrowane dyski i ich odblokowywanie { #encrypted-disks-and-unlocking }

Zaszyfrowany dysk trzeba odblokować przy każdym uruchomieniu maszyny. W tej
sekcji opisano, jak każdy system docelowy (system operacyjny instalowany na
maszynie) szyfruje dysk i jak można go odblokować z udziałem człowieka albo
bez niego.

- **Debian** (`debian.encrypt: true`) jest instalowany z jednorazowym
  kluczem, który wpisujesz przy pierwszym uruchomieniu. Znajdziesz go
  w `secrets/luks/<host>.once`. Pierwsze `apply` zastępuje go kluczem
  `secrets/luks/<host>.key`, a master dostaje wtedy dodatkowo nowy klucz
  woluminu. Jeśli stracisz ten plik z kluczem, dysk pozostanie zablokowany,
  więc pilnuj kopii zapasowej pliku fleet
  i sekretów.
- **CoreOS / uCore** szyfrują dysk w ramach instalacji przez Ignition,
  narzędzie, które konfiguruje maszynę z CoreOS przy pierwszym uruchomieniu.
  Maszyna potrzebuje do tego przy pierwszym uruchomieniu około 4 GiB RAM.
- **Pierścienie Tang** pozwalają zaszyfrowanym maszynom odblokować dyski przy
  starcie bez udziału człowieka. Tang to mały serwer, którego maszyna przez
  sieć prosi o pomoc w odblokowaniu dysku. Na nodzie działa moduł `tang`,
  a każdy pierścień to jeden serwer Tang z własnymi kluczami. Domyślnie jest
  jeden pierścień, `infra`, na porcie 7500. Blok `unlock:` hosta przypisuje
  jego dysk do jednego lub kilku pierścieni i ustala próg, czyli liczbę
  pierścieni, które muszą odpowiedzieć.
- **SSH w initramfs** (`unlock.ssh: true`) pozwala połączyć się z maszyną,
  która czeka na odblokowanie dysku. Initramfs to mały system, który działa,
  zanim dysk zostanie otwarty. Serwerem SSH jest w nim dropbear na Debianie
  i dracut-sshd na CoreOS. Przyjmuje on własny klucz z ograniczonymi
  uprawnieniami, `secrets/unlock_ed25519`, który pozwala tylko na odblokowanie.
- `kiwi-server unlock fleet.yaml <host>` przekazuje pierścień do maszyny, która
  czeka przy starcie, dzięki czemu może ona skorzystać z pierścienia, z którym
  sama się nie połączy. Z opcją `--manual` przekazuje sam klucz. Pierścień
  o nazwie `operator` jest udostępniany z twojego komputera na czas, gdy jest
  potrzebny. `vpn-server.unlock_relay` udostępnia pierścień przez mastera
  maszynom za NAT-em.

## MTU tunelu { #tunnel-mtu }

MTU to największy pakiet, jaki łącze sieciowe przenosi w całości. WireGuard
dodaje do każdego pakietu własne nagłówki, więc tunel przenosi mniejsze
pakiety niż łącze pod nim, a łącze komórkowe jeszcze mniejsze. Pakiet zbyt
duży dla któregoś z łączy po drodze zostaje odrzucony albo podzielony,
a połączenia się zawieszają. Kiwi radzi sobie z tym na trzy sposoby:

- **Dwa ustawienia.** `wg_mtu` to MTU gluetun (klienta VPN), konfiguracji
  klientów wystawianych przez wg-easy (serwer WireGuard) i interfejsu
  WireGuard `wg0`.
  Domyślnie wynosi **1376**. To wielokrotność 16, bo WireGuard dopełnia każdy
  pakiet do najbliższej wielokrotności 16 bajtów. `bridge_mtu` to MTU sieci
  stacku, która łączy kontenery na maszynie. Domyślnie wynosi **1500**.
  `validate` odrzuca `wg_mtu`, przy którym dopełniony pakiet razem z 80 bajtami
  nagłówków nie mieści się w moście. Odrzuca też wszystko poniżej 1280, bo to
  najmniejsze MTU, przy którym działa IPv6.
- **MSS jest ograniczany w obu kierunkach.** MSS to największa porcja danych,
  jaką TCP umieszcza w jednym pakiecie. Zarówno wg-easy, jak i klient VPN
  ograniczają go do `wg_mtu - 40`, więc TCP nigdy nie próbuje wysłać segmentu,
  który nie przejdzie.
- **TCP sam znajduje działający rozmiar.** Klient VPN działa
  z `net.ipv4.tcp_mtu_probing=1` i `tcp_base_mss=1024`. Gdy połączenie biegnie
  trasą, która po cichu odrzuca duże pakiety, TCP próbuje coraz mniejszych, aż
  znajdzie rozmiar, który działa, zamiast się zawiesić.

### Pomiar trasy: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Żeby sprawdzić, co naprawdę przenosi trasa do node’a albo urządzenia, zmierz
ją:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # urządzenie z secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # i zapisz wg_mtu w pliku fleet
```

Pomiar wysyła przez tunel pingi z ustawioną flagą „nie fragmentuj” (don’t
fragment), więc po drodze nie mogą zostać podzielone. Wysyła je z wnętrza
sieciowej przestrzeni nazw (network namespace), w której jest tunel.
Sieciowa przestrzeń nazw to osobne środowisko sieciowe na maszynie, takie jak
to, które ma kontener. Node jest mierzony z jego własnego klienta VPN, bo
zapora sieciowa klienta odrzuca przychodzące pingi. Urządzenie jest mierzone
z serwera WireGuard. Pomiar zaczyna się od zwykłego pingu, potem sprawdza
każdą wielokrotność 16 od 1280 w górę i podaje największy rozmiar, który
dociera **w całości**. W trakcie pingowania odczytuje liczniki składania
pakietów w jądrze. Dzięki temu odpowiedź, która po drodze została podzielona
i z powrotem złożona, nie liczy się jako pasująca.

Pomiar podpowiada też, co ustawić. Dla **urządzenia** jest to linia `MTU =`
we własnej konfiguracji WireGuard tego urządzenia i nikogo innego to nie
dotyczy. Dla **node’a** jest to `wg_mtu` na tym nodzie i na jego masterze.
Z opcją `--write` pomiar wpisuje wartość do pliku fleet i zmienia tylko te
linie. Jednej rzeczy pomiar ze swojej strony nie zobaczy: pakietu podzielonego
tylko w drodze tam i złożonego z powrotem przez drugą stronę.

Wartości domyślne zmierzono na sieci testowej. Telefon w sieci komórkowej
wymaga własnego pomiaru, bo trasy komórkowe często działają wyłącznie po IPv6
za 464XLAT, z zagnieżdżoną enkapsulacją. Zmierz sam telefon i obniż jego
własne `MTU =`, jeśli tak wyjdzie z pomiaru.

## VPS-y w netcup { #netcup-vpses }

netcup to dostawca hostingu i na razie jedyny, u którego kiwi-server potrafi
sam zainstalować wynajęty serwer (VPS). Robi to przez API Server Control
Panel firmy netcup. Inni dostawcy hostingu są
[planowani](roadmap.md#more-hosters-and-network-boot) jako wtyczki.

```bash
kiwi-server vps login fleet.yaml         # logowanie device flow; token trafia do secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wyczyść serwer i zainstaluj ISO hosta
```

`vps install` czyści serwer, dlatego najpierw pyta o potwierdzenie, chyba że
podasz `--yes`. Odmawia instalacji w trzech przypadkach: gdy ISO zawiera
sekrety roli, gdy `disk:` wskazuje niewłaściwy dysk i gdy dysk z CoreOS ma być
zaszyfrowany na serwerze z mniej niż 3500 MiB RAM.
