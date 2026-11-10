# Maszyny: instalacja, konfiguracja, aktualizacje

Ta strona prowadzi maszynę od wpisu w pliku fleet do działającego systemu,
który sam się aktualizuje. kiwi-server buduje obraz instalacyjny, który
instaluje system operacyjny bez nikogo przy klawiaturze. Potem poleceniem
`apply` konfiguruje maszynę przez SSH zgodnie z jej rolą. Od tej chwili
maszyna sama instaluje aktualizacje i uruchamia się ponownie tylko w godzinach,
na które pozwolisz.

## Systemy docelowe { #targets }

System docelowy to system operacyjny, który kiwi-server instaluje na maszynie.

| System docelowy | Co zostaje zainstalowane | Nośnik instalacyjny |
|---|---|---|
| `coreos` | Fedora CoreOS, strumień stable | Standardowy obraz live ISO uzupełniony o konfigurację Ignition hosta (Butane `fcos` 1.6.0). Instalacja nie wymaga połączenia z siecią |
| `ucore` | Fedora CoreOS, który następnie sam przechodzi (rebase) na obraz `ghcr.io/ublue-os/ucore*`. Do wyboru są obrazy `ucore-minimal`, `ucore` i `ucore-hci`, także w wariantach `-nvidia` / `-zfs`. Rebase działa tak jak w przykładzie autorebase z projektu uCore | Taki sam jak dla CoreOS, a do tego jednostki autorebase |
| `debian` | Debian stable (trixie), amd64 | Standardowy obraz netinst z plikiem preseed (odpowiedziami dla instalatora) w initrd, dzięki czemu instalator zna odpowiedzi od pierwszego pytania. Pliki hosta są na obrazie w `/kiwi-server`. Obraz nadal startuje zarówno w trybie BIOS, jak i UEFI |

Na każdym systemie docelowym użytkownik administracyjny może używać sudo bez
hasła. SSH przyjmuje wyłącznie klucze, chyba że ustawisz
`ssh_password_auth: true`.

## Nośnik instalacyjny { #install-media }

Pierwsze polecenie buduje obraz instalacyjny (ISO) dla jednego hosta. Drugie
kopiuje go na pendrive.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- ISO instaluje system na dysku wskazanym w `disk:` **bez pytania**, a więc
  kasuje ten dysk. Po zakończeniu instalacji **wyłącza maszynę**
  (`install.on_done: poweroff`, albo `reboot`, jeśli wolisz ponowne
  uruchomienie). Opisuj swoje pendrive’y.
- Domyślnie nośnik instalacyjny zawiera **tylko system bazowy**: nazwę hosta,
  ustawienia sieci, użytkownika administracyjnego z kluczami SSH i zasady
  aktualizacji. Nie ma na nim żadnych sekretów stacku. Rolę maszyna dostaje
  później, gdy uruchomisz `apply`.
- Z opcją `--offline` na ISO trafia cała rola razem z sekretami. To wariant
  dla maszyny, która nie jest dostępna przez SSH. Każdy, kto ma taki obraz ISO,
  ma też te sekrety.
- Instalator live wyświetla dyski maszyny (`lsblk`) i ma powłokę, która
  przyjmuje hasło konsoli i klucze SSH z pliku fleet.

## Konfiguracja przez `apply` { #apply }

`apply` konfiguruje maszynę przez SSH zgodnie z jej rolą.

```bash
kiwi-server apply fleet.yaml papaya                         # po nazwie, adresie albo adresie w sieci mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # za pierwszym razem, po adresie
```

Najpierw `apply` ponownie generuje konfigurację hosta, czyli tworzy jego pliki
od nowa na podstawie pliku fleet. Potem kopiuje przez SSH skrypt roli hosta do
`/var/lib/kiwi-server/role.sh`. Skrypt roli konfiguruje maszynę do jej roli,
a `apply` uruchamia go jako root. Następnie `apply` przypisuje dysk do
pierścieni Tang, czyli serwerów, dzięki którym zaszyfrowana maszyna może
odblokować dysk przy starcie. Na masterze zapisuje też stan WireGuard razem
z sekretami całej sieci. Na zaszyfrowanej maszynie z Debianem pierwsze `apply`
zastępuje jednorazowy klucz użyty przy instalacji.

Połączenie SSH korzysta z własnego klucza twojej sieci i sprawdza klucz hosta
maszyny w `secrets/known_hosts`. `apply` i `status` mogą połączyć się
z maszyną po jej nazwie, stałym adresie, publicznym adresie mastera albo po
adresie w sieci mesh, czyli adresie maszyny w prywatnej sieci WireGuard.
Używają tylko takiego adresu, dla którego klucz hosta jest już zapisany.

W roli zbudowanej z modułów skrypt roli przekazuje stack do `kiwi-stack`.
Stack to wszystkie kontenery, które maszyna uruchamia dla swoich modułów.
`kiwi-stack` wykonuje wtedy kolejno te kroki:

1. Instaluje albo włącza podman 4.4+ lub docker i dba o to, żeby istniał
   użytkownik usług. Na Debianie razem z podmanem instalowane są `netavark`,
   `aardvark-dns` i `catatonit`.
2. Ładuje moduły jądra i ustawia parametry sysctl. Jeśli w stacku jest
   Pi-hole, aardvark-dns podmana zostaje przeniesiony na port 5533, a sam host
   rozwiązuje nazwy przez Pi-hole’a ze stacku. Dodaje też sieć mesh do sieci
   zaufanych w firewalld.
3. Odrzuca stack wygenerowany z innym seedem. Seed to sekret, z którego
   generowane są hasła całej sieci. W przeciwnym razie rozpakowuje stack do
   `docker_dir`. Instaluje quadlets, czyli jednostki systemd dla kontenerów,
   w `/etc/containers/systemd`, oraz jednostki hosta. Usuwa też wszystko, co
   zainstalował moduł, którego nie ma już w stacku.
4. Otwiera porty stacku w firewalld albo ufw, jeśli któraś z tych zapór jest
   aktywna.
5. Pobiera wszystkie obrazy kontenerów, a potem uruchamia `kiwi-stack.service`,
   który uruchamia `kiwi-stack.target`.
6. Uruchamia `kiwi-stack verify`, który sprawdza, czy działa każdy kontener.
   Jeśli któryś nie działa, `apply` kończy się błędem i zgłasza krok, który się
   nie powiódł.

Jeśli ponownie zastosujesz tę samą wygenerowaną konfigurację, na maszynie nic
się nie zmieni. Nowa konfiguracja zastępuje to, co się zmieniło. Pamiętaj
jednak, że każde `apply` restartuje wszystkie kontenery stacku, nawet jeśli nic
się nie zmieniło.

## Pierwsze uruchomienie { #first-boot }

Przy pierwszym uruchomieniu `kiwi-role.service` jednorazowo wykonuje skrypt
roli `/var/lib/kiwi-server/role.sh`. Startuje, gdy sieć już działa, i czeka do
120 sekund na DNS. Plik `role.done` oznacza, że rola została ukończona,
i powstaje dopiero wtedy, gdy działa każdy kontener. Jeśli skrypt zakończy się
błędem, zostawia plik `/var/lib/kiwi-server/role.failed` z nazwą kroku
i polecenia, które się nie powiodły, a przy następnym uruchomieniu maszyny
skrypt wykonuje się ponownie. Log jest w `/var/log/kiwi-server-role.log`. Na
uCore skrypt roli czeka, aż maszyna będzie działać na podpisanym obrazie uCore.
Żeby ręcznie uruchomić skrypt jeszcze raz, użyj
`sudo bash /var/lib/kiwi-server/role.sh --force`.

## Aktualizacje { #updates }

Maszyny na bieżąco instalują aktualizacje systemu operacyjnego. **Ponowne
uruchomienie**, które je aktywuje, następuje jednak tylko w oknie serwisowym
ustawionym przez `updates.days`, `time` i `length_minutes`, według czasu
lokalnego.

| System docelowy | Instaluje aktualizacje | Uruchamia ponownie |
|---|---|---|
| `coreos` | Zincati, na bieżąco | tylko w oknie serwisowym (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` pobiera je i przygotowuje (staging) | `kiwi-staged-reboot.timer` w oknie serwisowym |
| `debian` | unattended-upgrades, codziennie | `kiwi-reboot-if-required.timer` w oknie serwisowym, jeśli aktualizacja wymaga ponownego uruchomienia |

`updates.days: []` pozwala na ponowne uruchomienie w każdy dzień,
a `updates.enabled: false` wyłącza aktualizacje i ponowne uruchomienia.
Zaszyfrowana maszyna nie uruchamia się ponownie sama, jeśli potrzebuje
pierścienia Tang, który ktoś musi jej ręcznie przekazać. W przeciwnym razie
czekałaby przy starcie, aż ktoś ją odblokuje.

Kontenery aktualizują się według własnego harmonogramu. Raz w tygodniu,
w niedzielę o 00:00, `kiwi-stack update` uruchamia `podman auto-update`, o ile
ustawione jest `auto_update: registry`. Klient VPN jest restartowany codziennie
o 07:00 i dostaje wtedy nowy adres wyjściowy. Adres wyjściowy to publiczny
adres, który widzą strony internetowe, gdy ruch wychodzi z VPN.

## Na maszynie: `kiwi-stack` { #on-the-machine-kiwi-stack }

`kiwi-stack` to polecenie, które uruchamiasz na samej maszynie, żeby obejrzeć
stack i nim sterować.

```bash
sudo kiwi-stack status          # kontenery, jednostki hosta, verify
sudo kiwi-stack verify          # czy działa każdy kontener?
sudo kiwi-stack logs [service]  # z dziennika systemd
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # klient VPN i każdy kontener w jego przestrzeni nazw
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # z modułem backup
sudo kiwi-stack apply DIR       # paczka stacku, bez skryptu roli
```

Pliki stacku są w `docker_dir` (domyślnie `/home/user/docker`), a jego
ustawienia w `/etc/kiwi-server/stack.env`. Jednostki systemd to
`kiwi-stack.service`, `kiwi-stack-vpn-restart.timer`
i `kiwi-stack-update.timer`, a do tego jednostki dodane przez moduły.

## Co powstaje przy generowaniu { #what-a-render-produces }

Wygenerowana konfiguracja to wszystko, co kiwi-server tworzy z pliku fleet dla
jednego hosta. Trafia do `output/<host>/`, gdzie znajdują się wtedy te pliki.

| Plik | Co to jest |
|---|---|
| `<host>.role.sh` | Rola jako jeden skrypt. Zawiera ustawienia, osadzony stack, polecenie kiwi-stack z biblioteką i właściwą treść roli. Plik ma uprawnienia 0600 |
| `<host>.stack/` | Paczka stacku do przejrzenia. Zawiera `docker-compose.yml`, `quadlets/`, pliki konfiguracyjne modułów, jednostki hosta i `stack.sh`. Możesz ją też zainstalować ręcznie poleceniem `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | Na CoreOS i uCore: konfiguracja Butane i Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Na Debianie: plik preseed i pliki, które kopiuje on na maszynę |
| `<host>.iso` | Obraz instalacyjny, który instaluje system bez nikogo przy klawiaturze |
