# kiwi-server

kiwi-server is het programma waarmee je een Kiwi Network opbouwt en beheert. Je
beschrijft al je machines in één bestand, `fleet.yaml`, en kiwi-server richt de
machines aan de hand daarvan in. Je hoeft dus niet elke machine met de hand te
installeren en te configureren.

Voor elke host maakt kiwi-server een **installatie-ISO voor een automatische
installatie**: een image dat Fedora CoreOS, uCore of Debian op de machine zet
zonder iets te vragen, en de machine daarna uitzet. Vervolgens wordt via SSH de
rol van de machine **toegepast**, en daarmee wordt de machine een `kiwi-master`
of een `kiwi-node`. Ook daarna blijft kiwi-server het werk
voor je machines doen: het voegt WireGuard-clients toe, leest uit hoe het met
elke machine gaat, bewaart de secrets, maakt een back-up van het fleetbestand
en ontgrendelt versleutelde schijven.

kiwi-server is er als opdrachtregelprogramma (CLI), `kiwi-server`, en als
GTK4-app, **Kiwi Server**. Beide worden in `~/.local` geïnstalleerd en hebben
geen rootrechten nodig.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Nieuwste release: **v2.42.0**. Je vindt hem in de [Kiwi-catalogus](../desktop/catalogs.md).
- kiwi-server is gebouwd op [kiwi-modules](single.md) v0.23.0, met de modules en
  het programma dat er configuratie uit genereert, en op
  [kiwi-stack](single.md) v0.5.0, het deel dat op elke machine draait. Van
  beide zit een kopie in kiwi-server (vendored), vastgezet op een tag.

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

## Installeren { #install }

```bash
kiwi install kiwi-server        # met kiwi-updater
```

Je kunt het ook installeren vanuit een kloon van de repository: voer
`./install.sh install` uit en daarna `kiwi-server doctor`.

kiwi-server heeft Python 3.9+ met PyYAML en Jinja2 nodig, en de programma’s
`openssl` en `ssh`. Voor de opslag van de secrets is `age` nodig. Om ISO’s te
bouwen heb je `butane`, `coreos-installer` en `xorriso` nodig, en voor Debian
ook `cpio`, `gzip` en `curl`. Installeer deze pakketten op Silverblue of
Bluefin niet als extra laag in het systeem (layering), maar bouw de ISO-tools als één
containerimage:

```bash
kiwi-server toolchain build     # wordt automatisch gebruikt als de tools ontbreken
```

`qrencode` (voor `enroll --qr`), `shellcheck` en `docker compose` zijn
optioneel.

## Van niets naar een werkend netwerk { #from-nothing-to-a-running-network }

Met de commando’s hieronder kom je van een lege map tot een werkend netwerk met
een master, een node en je eigen apparaten:

```bash
kiwi-server init                          # een fleet.yaml met uitleg in commentaar
$EDITOR fleet.yaml                        # hosts, rollen, je SSH-sleutel, de installatieschijf
kiwi-server secrets init fleet.yaml       # optioneel: secrets/ als één met age versleutelde opslag
kiwi-server validate fleet.yaml

# de master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   opstarten; hij installeert en zet zichzelf uit; daarna weer aanzetten
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# elke node: eerst de WireGuard-client, dan het installatiemedium, dan de rol
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# je eigen apparaten
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # wat elke machine meldt
```

Standaard staan er op een installatie-ISO **geen secrets van de stack**. Er
staat alleen het basissysteem op. De rol en de stack worden pas daarna met
`apply` naar de machine gestuurd. Kun je een machine niet via SSH bereiken, dan
zet `build --offline` de hele rol met de secrets op de ISO. Upload zo’n ISO
niet naar de ISO-opslag van een hostingprovider, en verwijder hem na de
installatie.

**Wil je helemaal geen ISO gebruiken,** dan geeft
`kiwi-server script fleet.yaml papaya` het script voor een machine die je zelf
hebt geïnstalleerd. Met `--offline` bevat het script de hele rol.

Op een VPS van netcup wist `kiwi-server vps install fleet.yaml sorbet` de
server en installeert het de ISO via de API van netcup, zodat niemand achter
een console hoeft te zitten. netcup is tot nu toe de enige hostingprovider die
wordt ondersteund. Andere zijn [gepland](roadmap.md#more-hosters-and-network-boot).

## Commando’s { #commands }

| Commando | Wat het doet |
|---|---|
| `init [fleet.yaml]` | Schrijft het voorbeeldfleetbestand. `--domain` stelt het domein in. Standaard is dat `home`. |
| `validate fleet.yaml [host…]` | Controleert het fleetbestand. Het genereert daarbij elke stack, zodat ook fouten in modules aan het licht komen. |
| `list` / `show fleet.yaml <host>` | Het eerste toont de hosts en wat er voor ze is gegenereerd. Het tweede toont de configuratie die voor één host echt geldt, met de secrets afgeschermd. |
| `render fleet.yaml [host…]` | Schrijft de rolscripts, stacks en installatieconfiguraties naar `output/<host>/`. |
| `build fleet.yaml [host…]` | Genereert de configuratie en bouwt daarna de ISO. Standaard bevat de ISO alleen het basissysteem, met `--offline` de hele rol. |
| `script fleet.yaml <host>` | Geeft het script voor elke willekeurige machine. Met `--offline` bevat het script de hele rol. |
| `apply fleet.yaml <host…>` | Genereert de configuratie opnieuw, stuurt de rol via SSH naar de machine en voert hem daar uit (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Toont wat de machines melden: rol, stack, problemen, schijven, back-ups en certificaten. |
| `enroll fleet.yaml <host\|name>` | Maakt een WireGuard-client aan op de master, of haalt er een op die al bestaat (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Beheert `secrets/` als één met age versleuteld bestand, dat bij het ontgrendelen in het geheugen wordt geopend (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Toont de gegenereerde wachtwoorden van een host. |
| `ca fleet.yaml` | Toont de CA van de fleet. |
| `mtu fleet.yaml <node\|device\|address>` | Meet de echte MTU van een tunnel en vertelt je welke waarde je moet instellen (`--write`). |
| `openwrt fleet.yaml` | Schrijft een script dat een OpenWrt-router aan de mesh toevoegt ([Routers](../network/routers.md)). |
| `backup` / `restore` / `prune` | Maakt een back-up van de fleetmap op nodes, haalt hem daar terug en verwijdert oude back-ups van machines ([Beheer](operations.md)). |
| `unlock fleet.yaml <host>` | Stuurt een Tang-ring door naar een machine die bij het opstarten wacht tot haar versleutelde schijf wordt ontgrendeld ([Beheer](operations.md)). |
| `vps login\|list\|probe\|install` | Werkt met de API van het Server Control Panel van netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Toont wat er beschikbaar is, met elke instelling en de standaardwaarde. |
| `toolchain [status\|build]`, `doctor` | Beheert de ISO-tools en controleert deze computer. |

Elk commando kent `--porcelain` (uitvoer als JSON), `-o/--output-dir`,
`--quiet` en `-v`. `kiwi-server <command> -h` legt één commando uit.

## De app { #the-app }

De app **Kiwi Server** opent de fleet waaraan je het laatst hebt gewerkt. In de
zijbalk staan een overzicht, een regel per host en de standaardinstellingen.
Het tabblad *Overview* van een host toont actuele gegevens uit
`kiwi-server status`. De app haalt die eens per minuut op, via SSH en alleen
lezend, zolang het venster actief is. *Settings* is per host een formulier dat
uit de rollen en modules wordt opgebouwd. *Apply*, *Build* en *Render* starten
het opdrachtregelprogramma en tonen de uitvoer terwijl die binnenkomt. Voordat
*Build* begint, toont het de schijven die worden gewist. Met *Unlock* en *Lock*
open en sluit je de opslag van de secrets. De app schrijft gewone YAML. Heb je
een fleetbestand met de hand geschreven, dan raak je de commentaarregels kwijt
zodra de app het opslaat.

## Waar je op moet letten { #mind }

!!! danger "De ISO’s wissen de schijf die je ze opgeeft"
    Een installatie-ISO wist zonder te vragen de schijf waarvoor hij is
    gebouwd, zodra een machine ervan opstart. Zet een label op je ISO’s.
    Precies daarom vereist `build` de instelling `disk:`.

- **De uitvoer bevat secrets.** Het gaat om wachtwoordhashes, WireGuard-sleutels,
  TLS-sleutels en LUKS-sleutels. De bestanden worden met modus 0600 geschreven,
  en git negeert `output/`. Ga net zo zorgvuldig om met ISO’s die met
  `--offline` zijn gemaakt.
- **Wachtwoorden voor diensten worden gegenereerd** uit `secrets/seed` als je ze
  niet in het fleetbestand zet. `validate` waarschuwt je voor wachtwoorden die
  in het fleetbestand staan, en `kiwi-server secrets show` toont de gegenereerde
  wachtwoorden. Een machine weigert een `apply` die met een andere seed is
  gemaakt.
- **SSH-hostsleutels** worden in `secrets/known_hosts` vastgelegd zodra
  kiwi-server voor het eerst met een machine verbinding maakt. Verandert de
  sleutel van een machine later, dan wordt de verbinding geweigerd. Verwijder
  na een herinstallatie de regel van die machine uit dit bestand.
- **Een rolscript draait als root.** Lees eerst de uitvoer van `kiwi-server script fleet.yaml <host>
  --offline` voordat je een rol vertrouwt die je niet zelf hebt geschreven.
- **Een mislukte rol wordt gemeld.** De machine bewaart het bestand
  `/var/lib/kiwi-server/role.failed`, met de stap en het commando die zijn
  mislukt, en `status` toont het.

## Status { #status }

Het hele traject, van het fleetbestand tot een werkende machine, is in oktober
en november 2026 getest op echte hardware. Debian, uCore en Fedora CoreOS zijn
het hele traject doorlopen op twee VPS’en, een mini-pc en een VM. In een
oefening waarin het uitvallen van een node werd nagespeeld, werd een versleutelde
Debian-machine in ongeveer 14 minuten opnieuw opgebouwd. Back-ups van nodes zijn
van de ene node op een andere teruggezet (papaya naar lychee). De tunnel-MTU is
op echte verbindingen gemeten en afgesteld, ook op mobiele. De geautomatiseerde
tests (CI) genereren elke rol, halen elk script door shellcheck en valideren
elke Butane-configuratie. Ook vergelijken ze vier referentiestacks, de golden
stacks, byte voor byte met hun opgeslagen uitvoer.

Federatie tussen netwerken is nog niet getest. Alles draait op IPv4. De
Debian-ISO is er alleen voor amd64. Een control plane (`kiwi-server serve`) is
gepland en ontworpen, maar nog niet gebouwd.

Lees verder: [Het fleetbestand](fleet.md) · [Rollen](roles.md) · [Modules](modules.md) ·
[Machines](machines.md) · [Beheer](operations.md) ·
[Eén machine zonder fleet](single.md)
