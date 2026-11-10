# Machines: installeren, toepassen, bijwerken

## Targets { #targets }

| Target | Wat er geïnstalleerd wordt | Installatiemedium |
|---|---|---|
| `coreos` | Fedora CoreOS, stable-stream | de standaard live-ISO, aangepast met de Ignition van de host (Butane `fcos` 1.6.0); voor de installatie is geen netwerk nodig |
| `ucore` | Fedora CoreOS dat zichzelf rebaset op een `ghcr.io/ublue-os/ucore*`-image (`ucore-minimal`, `ucore`, `ucore-hci`, met `-nvidia` / `-zfs`), zoals het eigen autorebase-voorbeeld van uCore | zoals bij CoreOS, plus de autorebase-units |
| `debian` | Debian stable (trixie), amd64 | de standaard netinst met de preseed in de initrd, zodat hij vanaf de eerste vraag zelf antwoordt, en de bestanden van de host onder `/kiwi-server`; BIOS- en UEFI-boot blijven behouden |

De beheerdersgebruiker krijgt overal sudo zonder wachtwoord. SSH accepteert
alleen sleutels, tenzij je `ssh_password_auth: true` instelt.

## Installatiemedia { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Een ISO installeert op `disk:` **zonder te vragen** en **schakelt de machine
  daarna uit** (`install.on_done: poweroff`, of `reboot`). Label je sticks.
- Standaard bevatten de media **alleen het basissysteem**: hostnaam, netwerk,
  beheerdersgebruiker en sleutels, updatebeleid. Geen enkel geheim van de stack
  staat erop. De rol komt later met `apply`.
- `--offline` zet de hele rol en haar geheimen op de ISO, voor een machine die
  SSH niet kan bereiken. Wie die ISO heeft, heeft die geheimen.
- De live-installer toont de schijven (`lsblk`) en heeft een shell met het
  consolewachtwoord en de sleutels van de fleet.

## Toepassen { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # op naam, adres of mesh-adres
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # de eerste keer, op adres
```

`apply` rendert de host opnieuw en stuurt zijn rolscript via SSH naar
`/var/lib/kiwi-server/role.sh`. Het voert het script uit als root, bindt daarna
de schijf aan haar Tang-ringen en slaat op een master de WireGuard-status op bij
de geheimen van de fleet. Op een versleutelde Debian-machine vervangt de eerste
apply de eenmalige installatiesleutel. SSH gebruikt de eigen sleutel van de
fleet en controleert hostsleutels tegen `secrets/known_hosts`. `apply` en
`status` vinden een machine op haar naam, statische adres, het publieke adres
van de master of haar mesh-adres, maar alleen adressen waarvan de hostsleutel
bekend is.

Bij een modulerol geeft het script de stack door aan `kiwi-stack`:

1. Het installeert of activeert podman 4.4+ (op Debian met `netavark`,
   `aardvark-dns` en `catatonit`) of docker, en de servicegebruiker.
2. Het laadt kernelmodules en stelt sysctls in. Met Pi-hole verhuist aardvark-dns
   naar poort 5533 en zoekt de host op via de Pi-hole van de stack. Ook vertrouwt
   het de mesh in firewalld.
3. Het weigert een stack die uit een andere seed is gerenderd. Het pakt de stack
   uit in `docker_dir`, installeert de quadlets in `/etc/containers/systemd` en
   de host-units, en verwijdert wat een vertrokken module had geïnstalleerd.
4. Het opent de poorten van de stack in firewalld of ufw, als een van beide
   actief is.
5. Het haalt elke image binnen en start daarna `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Het draait `kiwi-stack verify`: elke container moet draaien, anders faalt de
   apply en zegt hij welke stap mislukte.

Dezelfde render opnieuw toepassen verandert niets, en een nieuwe render vervangt
wat er veranderd is. Een nieuwe apply herstart wel elke container van de stack.

## Eerste start { #first-boot }

`kiwi-role.service` voert `/var/lib/kiwi-server/role.sh` één keer uit, nadat het
netwerk op is (met tot 120 seconden wachten op DNS). `role.done` wordt pas
geschreven als elke container draait. Een fout laat
`/var/lib/kiwi-server/role.failed` achter (de stap en het commando) en wordt bij
de volgende start opnieuw geprobeerd. Het log is
`/var/log/kiwi-server-role.log`. Op uCore wacht de rol tot de image ondertekend
is. `sudo bash /var/lib/kiwi-server/role.sh --force` voert haar opnieuw uit.

## Updates { #updates }

Updates worden doorlopend geïnstalleerd. De **herstart** naar die updates gebeurt
alleen binnen je venster (`updates.days`, `time`, `length_minutes`, lokale tijd):

| Target | Installeert updates | Herstart |
|---|---|---|
| `coreos` | Zincati, doorlopend | alleen in het venster (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` zet ze klaar | `kiwi-staged-reboot.timer` in het venster |
| `debian` | unattended-upgrades, dagelijks | `kiwi-reboot-if-required.timer` in het venster, als er een nodig is |

`updates.days: []` betekent elke dag, en `updates.enabled: false` zet alles uit.
Een versleutelde machine waarnaar de Tang-ring doorgestuurd moet worden, herstart
niet uit zichzelf.

De containers hebben een eigen schema: een wekelijkse `kiwi-stack update`
(zondag 00:00) draait `podman auto-update` zolang `auto_update: registry` is
ingesteld. Een dagelijkse herstart van de VPN-client om 07:00 geeft een vers
exit-adres.

## Op de machine: `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # containers, host-units, verify
sudo kiwi-stack verify          # draait elke container?
sudo kiwi-stack logs [service]  # uit de journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # de VPN-client en elke container in zijn namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # met de backup-module
sudo kiwi-stack apply DIR       # een stackbundel, zonder rolscript
```

De stack staat in `docker_dir` (standaard `/home/user/docker`), en de
instellingen ervan in `/etc/kiwi-server/stack.env`. De units zijn
`kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` en
`kiwi-stack-update.timer`, plus wat een module toevoegt.

## Wat een render oplevert { #what-a-render-produces }

`output/<host>/` bevat:

| Bestand | Wat |
|---|---|
| `<host>.role.sh` | de rol als één script: instellingen, de stack (ingebed), het kiwi-stack-commando en de bibliotheek, en de inhoud van de rol. Modus 0600 |
| `<host>.stack/` | de stackbundel, om na te kijken: `docker-compose.yml`, `quadlets/`, moduleconfiguraties, host-units en `stack.sh`. `kiwi-stack apply` kan hem met de hand installeren |
| `<host>.bu`, `<host>.ign` | CoreOS en uCore: Butane en Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: de preseed en de bestanden die hij erin kopieert |
| `<host>.iso` | de installer die zonder tussenkomst installeert |
