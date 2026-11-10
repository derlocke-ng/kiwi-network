# Beheer

Deze pagina gaat over het werk dat begint zodra de machines zijn geïnstalleerd
en draaien: nagaan hoe het met ze gaat, de secrets veilig bewaren, back-ups
maken van de fleet en van de gegevens op de machines, versleutelde schijven
ontgrendelen, de tunnel-MTU afstellen en installeren op een server van netcup.
Dat doe je allemaal met kiwi-server vanaf je eigen computer, de
*beheercomputer*, waar het fleetbestand en de secrets staan.

## Status { #status }

`kiwi-server status` laat zien hoe het met de machines van de fleet gaat, met
allemaal of met de machine die je noemt:

```bash
kiwi-server status fleet.yaml            # alle hosts
kiwi-server status fleet.yaml papaya        # één host
```

kiwi-server maakt via SSH verbinding met elke machine en leest daar alleen
gegevens uit. Elke
machine meldt haar rol en haar stack (de containers en diensten die erop
draaien), eventuele problemen zoals een mislukte rol of een gestopte container,
haar schijven en of die versleuteld of vergrendeld zijn, haar back-ups, en hoe
lang haar certificaten nog geldig zijn. Een back-upnode meldt ook hoeveel
ruimte hij heeft. De app Kiwi Server toont dezelfde gegevens op het tabblad
*Overview* van elke host.

## Secrets { #secrets }

Alles wat geheim is, staat in `secrets/`, de map naast het fleetbestand. Daarin
staan de seed waaruit elk gegenereerd wachtwoord wordt afgeleid, de eigen
certificaatautoriteit (CA) van de fleet, de WireGuard-configuraties, de
LUKS-sleutels van de versleutelde schijven en de SSH-hostsleutels. kiwi-server
kan deze map versleuteld bewaren en alleen openen zolang je ermee werkt:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ wordt één met age versleuteld bestand
kiwi-server secrets unlock fleet.yaml    # in het geheugen openen (--for 8h; 0 houdt het open)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # de gegenereerde wachtwoorden van een host
```

`secrets init` maakt de versleutelde opslag aan. Het zet een sleutel in de
GNOME-sleutelbos en toont je een **herstelsleutel**. Die herstelsleutel krijg
je maar één keer te zien. Zolang de opslag open is, kan elk programma dat onder
jouw gebruikersaccount draait de inhoud lezen.

## Een back-up van de fleet zelf { #backing-up-the-fleet-itself }

In de fleetmap staan het fleetbestand en `secrets/`, en kiwi-server maakt
daar zelf een back-up van. Na elke geslaagde `render` of `build` (de twee
stappen die de configuratie en de installatie-ISO’s van de hosts genereren)
versleutelt het de fleetmap (AES-256 met PBKDF2, 600.000 iteraties) en kopieert
het die naar de nodes die in `backup.hosts` staan. Elk van die nodes bewaart de
tien nieuwste kopieën. Op een nieuwe computer haal je de fleetmap terug van een
van die nodes. Je kunt ook op elk moment een kopie naar een map naar keuze
schrijven:

```bash
kiwi-server restore --from core@lychee.home  # de fleetmap terughalen
kiwi-server backup fleet.yaml --local /mnt/usb   # of op elk moment een kopie naar een map
```

## Een back-up van de gegevens op de machines { #backing-up-the-machines-data }

Van de gegevens op de machines wordt een back-up gemaakt met het
back-upprogramma restic. Eén node bewaart de back-ups. Geef die node de module
`backup-server`, die een restic REST-server draait. Elke machine waarvan een
back-up moet worden gemaakt, krijgt de module `backup`, met een instelling die
naar die server wijst:

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

Elke nacht om 03:00, of tot 15 minuten later, stuurt restic de gegevens die
elke module bewaard wil hebben versleuteld naar de back-upserver. Een machine
kan op de server alleen bij haar eigen repository, en kan daar alleen back-ups
toevoegen, niet verwijderen. Daarom wordt het commando dat oude snapshots
opruimt op de beheercomputer uitgevoerd. Een snapshot is bij restic de
opgeslagen stand van één back-up. Het eerste commando hieronder is voor de
machine zelf, het tweede voor je eigen computer:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # op de machine
kiwi-server prune fleet.yaml            # bewaart 7 dagelijkse, 4 wekelijkse, 6 maandelijkse
```

Het terugzetten is getest tussen twee nodes: de back-ups van papaya zijn op
lychee teruggezet.

### In de volgende release { #coming-in-the-next-release }

!!! info "Op de branch `several-servers`"
    Dit werk staat op de branches `several-servers` van kiwi-modules en
    kiwi-server, maar is nog niet gemerged of uitgebracht. Meerdere
    back-upservers en het automatisch terugzetten zijn op hardware getest. De
    healthcheck voor de VPN niet.

- **Meerdere back-upservers.** `backup.servers` neemt een lijst met servers, en
  elke server krijgt een eigen volledige kopie. Valt er een server uit, dan
  heeft dat alleen gevolgen voor de kopie op die server. Bij het terugzetten wordt de nieuwste kopie
  genomen, van welke server die ook komt, en `kiwi-stack snapshots` toont de
  snapshots per server. De enkele instelling `server` werkt nog steeds.
- **Een opnieuw opgebouwde machine zet haar gegevens zelf terug.** Een machine
  die opnieuw is opgebouwd, vindt op de server back-ups van zichzelf terwijl ze
  er zelf nog geen heeft gemaakt. In dat geval zet ze elke module zelf terug
  voordat ze haar eerste back-up maakt, en daarna gaan de back-ups gewoon
  verder. Dat is de standaard, `backup.restore: auto`. Met `hold` wacht de
  machine tot je `kiwi-stack restore` of `kiwi-stack backup --new` uitvoert.
- **Oude snapshots opruimen met een timer.**
  `kiwi-server prune fleet.yaml --every week` (of `day`) installeert op je
  eigen computer een systemd-timer voor je eigen gebruiker. Alleen daar staan
  de sleutels die iets mogen verwijderen. Wordt een geplande keer gemist, dan
  wordt die bij de volgende keer inloggen ingehaald. `kiwi-server status` toont elke
  back-upkopie en waarschuwt als er op een back-upnode drie weken lang geen
  oude snapshots zijn opgeruimd.
- **Een vastgelopen verbinding met de commerciële VPN-provider herstelt
  zichzelf.** gluetun, de container van de VPN-client, krijgt een healthcheck:
  een controle die regelmatig nagaat of de verbinding nog werkt. Is de
  verbinding vijf minuten lang niet in orde, dan wordt de container geforceerd
  gestopt, en bij de volgende start kiest hij een andere server.

## Versleutelde schijven en ontgrendelen { #encrypted-disks-and-unlocking }

Een versleutelde schijf moet bij elke keer opstarten worden ontgrendeld. In dit
deel lees je hoe elk doelsysteem (het besturingssysteem waarmee een machine
wordt geïnstalleerd) de schijf versleutelt, en hoe de schijf met of zonder
iemand erbij kan worden ontgrendeld.

- **Debian** (`debian.encrypt: true`) wordt geïnstalleerd met een eenmalige
  sleutel, die je bij de eerste keer opstarten intypt. Je vindt hem in
  `secrets/luks/<host>.once`. De eerste `apply` vervangt hem door
  `secrets/luks/<host>.key`, en een master krijgt op dat moment ook een nieuwe
  volumesleutel. Raak je dat sleutelbestand kwijt, dan blijft de schijf op
  slot. Zorg dus dat er een back-up van de fleet is.
- **CoreOS / uCore** versleutelen de schijf als onderdeel van de installatie,
  via Ignition, het programma dat een CoreOS-machine bij de eerste keer
  opstarten configureert. De machine heeft daarvoor bij de eerste keer
  opstarten ongeveer 4 GiB RAM nodig.
- **Tang-ringen** zorgen dat versleutelde machines hun schijf bij het opstarten
  kunnen ontgrendelen zonder dat er iemand bij is. Tang is een kleine server
  waaraan een machine via het netwerk hulp vraagt bij het ontgrendelen van haar
  schijf. Een node draait de module `tang`, en elke ring is één Tang-server met
  eigen sleutels. Standaard is er één ring, `infra`, op poort 7500. Met het blok
  `unlock:` koppel je de schijf van een host aan een of meer ringen en stel je
  een drempel in: het aantal ringen dat moet antwoorden.
- **SSH in de initramfs** (`unlock.ssh: true`) laat je inloggen op een machine
  die wacht tot haar schijf wordt ontgrendeld. De initramfs is het kleine
  systeem dat draait voordat de schijf open is. De SSH-server daarin is
  dropbear op Debian en dracut-sshd op CoreOS. Hij accepteert een eigen,
  beperkte sleutel, `secrets/unlock_ed25519`, waarmee je alleen het
  ontgrendelen kunt uitvoeren.
- `kiwi-server unlock fleet.yaml <host>` stuurt een ring door naar een machine
  die bij het opstarten wacht. Zo kan de machine een ring gebruiken die ze zelf
  niet kan bereiken. Met `--manual` geeft het de sleutel zelf door. Een ring
  met de naam `operator` wordt vanaf je eigen computer aangeboden zolang hij
  nodig is. Met `vpn-server.unlock_relay` maak je een ring via de master
  bereikbaar voor machines achter NAT.

## Tunnel-MTU { #tunnel-mtu }

De MTU is het grootste pakket dat een netwerkverbinding in één stuk kan
doorgeven. WireGuard voegt aan elk pakket zijn eigen headers toe. Door een tunnel
passen daarom kleinere pakketten dan door de verbinding eronder, en door een
mobiele verbinding nog kleinere. Is een pakket te groot voor een van de
verbindingen onderweg, dan wordt het weggegooid of opgesplitst, en blijven
verbindingen hangen. Kiwi pakt dit op drie manieren aan:

- **Twee instellingen.** `wg_mtu` is de MTU van gluetun (de VPN-client), van de
  clientconfiguraties die wg-easy (de WireGuard-server) uitgeeft, en van de
  WireGuard-interface `wg0`. De standaardwaarde is **1376**. Dat is een
  veelvoud van 16, omdat WireGuard elk pakket aanvult tot het volgende veelvoud
  van 16 bytes. `bridge_mtu` is de MTU van het netwerk van de stack, dat de
  containers op een machine met elkaar verbindt. De standaardwaarde is
  **1500**. `validate` weigert een `wg_mtu` waarbij het aangevulde pakket plus
  80 bytes aan headers niet in de bridge past. Het weigert ook alles onder
  1280, de kleinste MTU waarmee IPv6 werkt.
- **De MSS wordt in beide richtingen begrensd.** De MSS is de grootste
  hoeveelheid gegevens die TCP in één pakket stopt. wg-easy en de VPN-client
  beperken die allebei tot `wg_mtu - 40`, zodat TCP nooit een segment probeert
  dat er niet door past.
- **TCP vindt zelf een grootte die werkt.** De VPN-client draait met
  `net.ipv4.tcp_mtu_probing=1` en `tcp_base_mss=1024`. Loopt een verbinding
  over een pad dat grote pakketten zonder melding weggooit, dan probeert TCP
  steeds kleinere pakketten tot er een grootte werkt, in plaats van te blijven
  hangen.

### Een pad meten: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Wil je weten wat er over het pad naar een node of een apparaat echt doorkomt,
meet het dan:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # een node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # een apparaat uit secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # en wg_mtu in het fleetbestand zetten
```

De meting stuurt pings door de tunnel met de vlag don’t-fragment, zodat ze
onderweg niet kunnen worden opgesplitst. Ze worden verstuurd vanuit de
netwerk-namespace waarin de tunnel zit. Een netwerk-namespace is een aparte
netwerkomgeving op een machine, zoals een container die heeft. Een node wordt
gemeten vanuit zijn eigen VPN-client, omdat de firewall van de client
binnenkomende pings weggooit. Een apparaat wordt gemeten vanaf de
WireGuard-server. De meting begint met een gewone ping, probeert daarna elk
veelvoud van 16 vanaf 1280 en meldt het grootste pakket dat **heel**
aankomt. Tijdens het pingen leest ze de tellers van de kernel voor het weer
samenvoegen van pakketten. Zo telt een antwoord dat onderweg is opgesplitst en
weer samengevoegd niet mee als passend.

De meting vertelt je ook wat je moet instellen. Bij een **apparaat** is dat de
regel `MTU =` in de eigen WireGuard-configuratie van het apparaat, en verder
merkt niemand er iets van. Bij een **node** is het `wg_mtu` op die node en op
zijn master. Met `--write` zet de meting de waarde in het fleetbestand en past
ze alleen die regels aan. Eén ding is vanaf deze kant niet te zien: een pakket
dat alleen op de heenweg wordt opgesplitst en aan de andere kant weer wordt
samengevoegd.

De standaardwaarden zijn gemeten op de testfleet. Een telefoon op mobiele data
heeft een eigen meting nodig, want mobiele paden zijn vaak alleen IPv6, achter
464XLAT en met geneste encapsulatie. Meet de telefoon zelf, en verlaag zijn
eigen `MTU =` als de meting dat aangeeft.

## VPS’en van netcup { #netcup-vpses }

netcup is een hostingprovider, en op dit moment de enige waar kiwi-server zelf
een gehuurde server (een VPS) kan installeren. Dat gaat via de API van het
Server Control Panel van netcup. Andere hostingproviders zijn
[gepland](roadmap.md#more-hosters-and-network-boot), als plug-ins.

```bash
kiwi-server vps login fleet.yaml         # inloggen via device flow; het token komt in secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # de server wissen en de ISO van de host installeren
```

`vps install` wist de server en vraagt daarom eerst om bevestiging, tenzij je
`--yes` meegeeft. Het weigert te installeren in drie gevallen: als er secrets
van de rol op de ISO staan, als `disk:` de verkeerde schijf noemt, en als een
CoreOS-schijf moet worden versleuteld op een server met minder dan 3500 MiB
RAM.
