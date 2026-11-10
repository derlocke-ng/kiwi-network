# Maszyny: instalacja, apply, aktualizacje

## Targety { #targets }

| Target | Co zostaje zainstalowane | Nośnik instalacyjny |
|---|---|---|
| `coreos` | Fedora CoreOS, strumień stable | standardowy obraz live ISO, dostosowany konfiguracją Ignition hosta (Butane `fcos` 1.6.0); instalacja nie potrzebuje sieci |
| `ucore` | Fedora CoreOS, który sam przechodzi (rebase) na obraz `ghcr.io/ublue-os/ucore*` (`ucore-minimal`, `ucore`, `ucore-hci`, z `-nvidia` / `-zfs`), jak we własnym przykładzie autorebase uCore | jak dla CoreOS, plus jednostki autorebase |
| `debian` | Debian stable (trixie), amd64 | standardowy netinst z preseedem w initrd, więc odpowiada od pierwszego pytania, i pliki hosta pod `/kiwi-server`; zachowany rozruch BIOS i UEFI |

Użytkownik administracyjny wszędzie dostaje sudo bez hasła. SSH przyjmuje
tylko klucze, chyba że ustawisz `ssh_password_auth: true`.

## Nośnik instalacyjny { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Obraz ISO instaluje się na `disk:` **bez pytania**, a potem **wyłącza
  maszynę** (`install.on_done: poweroff` albo `reboot`). Oznacz swoje
  pendrive'y.
- Domyślnie nośnik zawiera **tylko system bazowy**: nazwę hosta, sieć,
  użytkownika administracyjnego i klucze, politykę aktualizacji. Nie ma na nim
  żadnych sekretów stacka. Rola przychodzi później z `apply`.
- `--offline` umieszcza całą rolę i jej sekrety na obrazie ISO, dla maszyny,
  do której SSH nie dociera. Kto ma ten obraz, ma te sekrety.
- Instalator live pokazuje dyski (`lsblk`) i ma powłokę z hasłem konsoli i
  kluczami floty.

## Apply { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # po nazwie, adresie lub adresie w sieci mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # za pierwszym razem, po adresie
```

`apply` renderuje hosta ponownie i wysyła jego skrypt roli przez SSH do
`/var/lib/kiwi-server/role.sh`. Uruchamia skrypt jako root, potem wiąże dysk z
jego pierścieniami Tang, a na masterze zapisuje stan WireGuard razem z
sekretami floty. Na zaszyfrowanej maszynie z Debianem pierwsze apply zastępuje
jednorazowy klucz instalacyjny. SSH używa własnego klucza floty i sprawdza
klucze hostów względem `secrets/known_hosts`. `apply` i `status` znajdują
maszynę po nazwie, adresie statycznym, publicznym adresie mastera lub adresie
w sieci mesh, ale tylko po adresach, których klucz hosta jest zapisany.

Dla roli modułowej skrypt przekazuje stack do `kiwi-stack`:

1. Instaluje lub włącza podmana 4.4+ (na Debianie z `netavark`,
   `aardvark-dns` i `catatonit`) albo dockera, oraz użytkownika usług.
2. Ładuje moduły jądra i ustawia sysctl. Z Pi-hole aardvark-dns przenosi się
   na port 5533, a host rozwiązuje nazwy przez Pi-hole stacka. Ufa też sieci
   mesh w firewalld.
3. Odrzuca stack wyrenderowany z innym seedem. Rozpakowuje stack do
   `docker_dir`, instaluje quadlety w `/etc/containers/systemd` i jednostki
   hosta oraz usuwa to, co zainstalował moduł, którego już nie ma.
4. Otwiera porty stacka w firewalld lub ufw, jeśli któryś z nich jest aktywny.
5. Pobiera każdy obraz, potem uruchamia `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Uruchamia `kiwi-stack verify`: każdy kontener musi działać, inaczej apply
   kończy się błędem i mówi, który krok zawiódł.

Ponowne zastosowanie tego samego renderu niczego nie zmienia, a nowy render
zastępuje to, co się zmieniło. Ponowne apply restartuje jednak każdy kontener
stacka.

## Pierwszy rozruch { #first-boot }

`kiwi-role.service` uruchamia `/var/lib/kiwi-server/role.sh` raz, gdy sieć już
działa (czekając na DNS do 120 sekund). `role.done` jest zapisywany dopiero
wtedy, gdy działa każdy kontener. Błąd zostawia
`/var/lib/kiwi-server/role.failed` (krok i polecenie) i jest ponawiany przy
następnym rozruchu. Log to `/var/log/kiwi-server-role.log`. Na uCore rola
czeka, aż obraz będzie podpisany.
`sudo bash /var/lib/kiwi-server/role.sh --force` uruchamia ją ponownie.

## Aktualizacje { #updates }

Aktualizacje instalują się na bieżąco. **Restart** do nich następuje tylko w
twoim oknie (`updates.days`, `time`, `length_minutes`, czas lokalny):

| Target | Instaluje aktualizacje | Restartuje |
|---|---|---|
| `coreos` | Zincati, na bieżąco | tylko w oknie (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` je przygotowuje | `kiwi-staged-reboot.timer` w oknie |
| `debian` | unattended-upgrades, codziennie | `kiwi-reboot-if-required.timer` w oknie, gdy restart jest wymagany |

`updates.days: []` oznacza dowolny dzień, a `updates.enabled: false` wyłącza
to wszystko. Zaszyfrowana maszyna, do której pierścień Tang trzeba
przekazywać, nie restartuje się sama.

Kontenery mają własny harmonogram: cotygodniowe `kiwi-stack update`
(niedziela 00:00) uruchamia `podman auto-update`, dopóki ustawione jest
`auto_update: registry`. Codzienny restart klienta VPN o 07:00 daje świeży
adres wyjściowy.

## Na maszynie: `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # kontenery, jednostki hosta, weryfikacja
sudo kiwi-stack verify          # czy każdy kontener działa?
sudo kiwi-stack logs [service]  # z journala
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # klient VPN i każdy kontener w jego przestrzeni nazw
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # z modułem backup
sudo kiwi-stack apply DIR       # paczka stacka, bez skryptu roli
```

Stack leży w `docker_dir` (domyślnie `/home/user/docker`), a jego ustawienia w
`/etc/kiwi-server/stack.env`. Jednostki to `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` i `kiwi-stack-update.timer`, plus te, które
doda moduł.

## Co daje render { #what-a-render-produces }

`output/<host>/` zawiera:

| Plik | Co |
|---|---|
| `<host>.role.sh` | rolę jako jeden skrypt: ustawienia, stack (osadzony), polecenie i bibliotekę kiwi-stack oraz ciało roli. Uprawnienia 0600 |
| `<host>.stack/` | paczkę stacka, do przejrzenia: `docker-compose.yml`, `quadlets/`, konfiguracje modułów, jednostki hosta i `stack.sh`. `kiwi-stack apply` może ją zainstalować ręcznie |
| `<host>.bu`, `<host>.ign` | CoreOS i uCore: Butane i Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: preseed i pliki, które kopiuje |
| `<host>.iso` | nienadzorowany instalator |
