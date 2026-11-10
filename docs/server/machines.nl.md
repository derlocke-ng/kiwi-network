# Machines: installeren, toepassen, bijwerken

Op deze pagina volg je een machine vanaf haar vermelding in het fleetbestand
tot een werkend systeem dat zichzelf bijwerkt. kiwi-server bouwt een
installatie-image dat het besturingssysteem installeert zonder dat er iemand
achter het toetsenbord zit. Daarna richt het de machine met het commando
`apply` via SSH in voor haar rol. Vanaf dat moment installeert de machine haar
updates zelf en herstart ze alleen op de tijden die jij toestaat.

## Doelsystemen { #targets }

Het doelsysteem (`target`) is het besturingssysteem dat kiwi-server op een
machine installeert.

| Doelsysteem | Wat er wordt geïnstalleerd | Installatiemedium |
|---|---|---|
| `coreos` | Fedora CoreOS, stable-stream | De standaard live-ISO, aangevuld met de Ignition-configuratie van de host (Butane `fcos` 1.6.0). Voor de installatie is geen netwerkverbinding nodig |
| `ucore` | Fedora CoreOS, dat daarna zelf overstapt (rebase) op een image `ghcr.io/ublue-os/ucore*`. De images zijn `ucore-minimal`, `ucore` en `ucore-hci`, ook met `-nvidia` / `-zfs`. De rebase werkt zoals het autorebase-voorbeeld van uCore zelf | Hetzelfde als bij CoreOS, plus de autorebase-units |
| `debian` | Debian stable (trixie), amd64 | Het standaard netinst-image met de preseed (het bestand met de antwoorden voor het installatieprogramma) in de initrd, zodat het installatieprogramma vanaf de eerste vraag zijn antwoorden heeft. De bestanden van de host staan op het image onder `/kiwi-server`. Het image start nog steeds op met zowel BIOS als UEFI |

Op elk doelsysteem kan de beheerder sudo gebruiken zonder wachtwoord. SSH
accepteert alleen sleutels, tenzij je `ssh_password_auth: true` instelt.

## Installatiemedium { #install-media }

Het eerste commando bouwt het installatie-image (ISO) voor één host. Het tweede
zet het op een USB-stick.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- De ISO installeert **zonder te vragen** op de schijf die bij `disk:` staat, en
  wist die schijf daarbij. Is de installatie klaar, dan **zet hij de machine
  uit** (`install.on_done: poweroff`, of `reboot` om haar in plaats daarvan te
  herstarten). Zet een label op je USB-sticks.
- Standaard staat op het installatiemedium **alleen het basissysteem**: de
  hostnaam, de netwerkinstellingen, de beheerder met de SSH-sleutels en het
  updatebeleid. Er staan geen secrets van de stack op. De machine krijgt haar
  rol pas later, als je `apply` uitvoert.
- Met `--offline` komen de hele rol en de secrets op de ISO. Dat is bedoeld
  voor een machine die niet via SSH bereikbaar is. Wie die ISO heeft, heeft ook
  die secrets.
- Het live-installatieprogramma toont de schijven van de machine (`lsblk`) en
  heeft een shell, waarop je met het consolewachtwoord en de SSH-sleutels van
  de fleet kunt inloggen.

## Toepassen { #apply }

`apply` richt een machine via SSH in voor haar rol.

```bash
kiwi-server apply fleet.yaml papaya                         # op naam, adres of mesh-adres
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # de eerste keer, op adres
```

`apply` genereert eerst de bestanden van de host opnieuw uit het fleetbestand.
Daarna kopieert het via SSH het rolscript van de host naar
`/var/lib/kiwi-server/role.sh`. Het rolscript richt de machine in voor haar
rol, en `apply` voert het als root uit. Vervolgens koppelt `apply` de schijf
aan haar Tang-ringen, servers waarmee een versleutelde machine bij het
opstarten haar schijf kan ontgrendelen. Op een master bewaart het ook de
WireGuard-status samen met de secrets van de fleet. Op een versleutelde
Debian-machine vervangt de eerste `apply` de eenmalige sleutel die bij de
installatie is gebruikt.

De SSH-verbinding gebruikt de eigen sleutel van de fleet en controleert de
hostsleutel van de machine aan de hand van `secrets/known_hosts`. `apply` en
`status` kunnen een machine bereiken via haar naam, haar vaste adres, het
openbare adres van de master of haar mesh-adres, het adres van de machine in
het besloten WireGuard-netwerk. Ze gebruiken alleen een adres waarvan de
hostsleutel al bekend is.

Bij een rol die uit modules is opgebouwd, geeft het rolscript de stack door aan
`kiwi-stack`. De stack bestaat uit alle containers die de machine voor haar
modules draait. `kiwi-stack` doorloopt dan deze stappen:

1. Het installeert of activeert podman 4.4+ of docker en zorgt dat de
   servicegebruiker bestaat. Op Debian komen bij podman ook `netavark`,
   `aardvark-dns` en `catatonit`.
2. Het laadt kernelmodules en stelt sysctls in. Zit Pi-hole in de stack, dan
   wordt aardvark-dns van podman naar poort 5533 verplaatst, en zoekt de host
   zelf namen op via de Pi-hole van de stack. Ook voegt het de mesh toe aan de
   netwerken die firewalld vertrouwt.
3. Het weigert een stack die uit een andere seed is gegenereerd. De seed is
   het geheim waaruit de wachtwoorden van de fleet worden gegenereerd. Klopt
   de seed, dan pakt het de stack uit in `docker_dir`. Het installeert de
   quadlets, de systemd-units voor de containers, in `/etc/containers/systemd`,
   en installeert de host-units. Ook verwijdert het alles wat een module heeft
   geïnstalleerd die niet meer in de stack zit.
4. Het zet de poorten van de stack open in firewalld of ufw, als een van die
   twee actief is.
5. Het downloadt alle containerimages en start daarna `kiwi-stack.service`,
   die `kiwi-stack.target` start.
6. Het voert `kiwi-stack verify` uit, dat controleert of elke container draait.
   Draait er een niet, dan mislukt de `apply` en wordt de mislukte stap
   gemeld.

Pas je dezelfde gegenereerde configuratie opnieuw toe, dan verandert er niets
op de machine. Pas je een nieuwe toe, dan wordt vervangen wat er is veranderd.
Let wel: bij elke `apply` worden alle containers van de stack herstart, ook als
er niets is veranderd.

## Eerste keer opstarten { #first-boot }

Bij de eerste keer opstarten voert `kiwi-role.service` het rolscript
`/var/lib/kiwi-server/role.sh` één keer uit. Het start zodra het netwerk
actief is en wacht tot 120 seconden op DNS. Het bestand `role.done` geeft aan
dat de rol klaar is, en wordt pas geschreven als elke container draait. Mislukt
het script, dan laat het het bestand `/var/lib/kiwi-server/role.failed` achter,
met de stap en het commando die zijn mislukt, en bij de volgende keer opstarten
wordt het script opnieuw uitgevoerd. Het logbestand is
`/var/log/kiwi-server-role.log`. Op uCore wacht het rolscript tot de machine
het ondertekende uCore-image draait. Wil je het script met de hand opnieuw
uitvoeren, gebruik dan `sudo bash /var/lib/kiwi-server/role.sh --force`.

## Updates { #updates }

Machines installeren de updates van hun besturingssysteem doorlopend. De
**herstart** waarmee de updates actief worden, gebeurt alleen binnen het
onderhoudsvenster dat je met `updates.days`, `time` en `length_minutes`
instelt, in lokale tijd.

| Doelsysteem | Installeert updates | Herstart |
|---|---|---|
| `coreos` | Zincati, doorlopend | alleen in het venster (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` downloadt en klaarzet ze (staging) | `kiwi-staged-reboot.timer` in het venster |
| `debian` | unattended-upgrades, dagelijks | `kiwi-reboot-if-required.timer` in het venster, als een update een herstart vereist |

Met `updates.days: []` mag de herstart op elke dag plaatsvinden, en met
`updates.enabled: false` zet je de updates en de herstarts uit. Een
versleutelde machine herstart niet uit zichzelf als ze een Tang-ring nodig
heeft die iemand met de hand naar haar moet doorsturen. Anders zou ze bij het
opstarten blijven wachten tot iemand haar ontgrendelt.

De containers worden volgens een eigen schema bijgewerkt. Eens per week, op
zondag om 00:00, voert `kiwi-stack update` het commando `podman auto-update`
uit, mits `auto_update: registry` is ingesteld. De VPN-client wordt elke dag om
07:00 herstart en krijgt daardoor een nieuw uitgangsadres. Het uitgangsadres is
het openbare adres dat websites zien als het verkeer uit de VPN komt.

## Op de machine: `kiwi-stack` { #on-the-machine-kiwi-stack }

`kiwi-stack` is het commando dat je op de machine zelf gebruikt om de stack te
bekijken en te bedienen.

```bash
sudo kiwi-stack status          # containers, host-units, verify
sudo kiwi-stack verify          # draait elke container?
sudo kiwi-stack logs [service]  # uit het journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # de VPN-client en elke container in zijn namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # met de module backup
sudo kiwi-stack apply DIR       # een stackbundel, zonder rolscript
```

De bestanden van de stack staan in `docker_dir` (standaard
`/home/user/docker`), en de instellingen in `/etc/kiwi-server/stack.env`. De
systemd-units zijn `kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` en
`kiwi-stack-update.timer`, plus de units die een module eventueel toevoegt.

## Wat er wordt gegenereerd { #what-a-render-produces }

Voor elke host genereert kiwi-server uit het fleetbestand een set bestanden in
`output/<host>/`:

| Bestand | Wat |
|---|---|
| `<host>.role.sh` | De rol als één script. Het bevat de instellingen, de ingesloten stack, het commando en de bibliotheek van kiwi-stack, en de eigenlijke rol. Het bestand heeft modus 0600 |
| `<host>.stack/` | De stackbundel, zodat je die kunt nakijken. Hij bevat `docker-compose.yml`, `quadlets/`, de configuratiebestanden van de modules, de host-units en `stack.sh`. Je kunt hem ook met de hand installeren met `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | Op CoreOS en uCore de Butane- en Ignition-configuratie |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Op Debian het preseed-bestand en de bestanden die daarmee naar de machine worden gekopieerd |
| `<host>.iso` | Het installatie-image, dat installeert zonder dat er iemand achter het toetsenbord zit |
