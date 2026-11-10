# kiwi-killswitch

kiwi-killswitch is een **VPN-killswitch** voor GNOME op Fedora Silverblue en
Bluefin. Een killswitch zorgt ervoor dat je computer geen verkeer buiten de VPN
om verstuurt, bijvoorbeeld als de VPN-verbinding wegvalt of als je naar een
ander netwerk overstapt. Deze killswitch is **fail-closed**: de firewall
blokkeert alles wat niet uitdrukkelijk is toegestaan. Als er iets misgaat, wordt
het verkeer dus tegengehouden en niet doorgelaten.

De firewall wordt alleen beheerd door een daemon met rootrechten. Die bedien je
met een schakelaar in het snelmenu van GNOME (Quick Settings), met een GTK4-app
of met een opdrachtregeltool (CLI). Alle drie sturen hun verzoeken via de
D-Bus-systeembus naar de daemon, en geen van de drie vraagt ooit om een
wachtwoord.

De killswitch beschermt **één** VPN-verbinding tegelijk, WireGuard of OpenVPN.
Hij maakt zelf geen verbinding met je VPN. Je verbindingen start je in
Instellingen van GNOME, en de killswitch stelt zijn firewallregels in voor de
verbinding die echt actief is, zodat er geen verkeer buiten die verbinding om
de computer uit kan.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Nieuwste release: **v0.2.3**. Staat in de [Kiwi-catalogus](catalogs.md) en
  heeft twee scopes, user + system. Het ene deel wordt in je thuismap
  geïnstalleerd, het andere is van root.
- Werkt met GNOME Shell 45 tot en met 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Een GNOME-extensie is een proces zonder rootrechten. Ze kan de firewall niet
aanpassen, en dat mag ook niet. Daarom doet de daemon al het blokkeren, en
stuurt de gebruikersinterface alleen verzoeken naar de daemon.

## Wat hij doet { #what-it-does }

- **Hij is fail-closed.** De firewall gebruikt `policy drop` voor uitgaand,
  inkomend en doorgestuurd verkeer, voor IPv4 en IPv6. Elk pakket wordt dus
  weggegooid, tenzij een regel het toestaat. Een nieuwe set regels vervangt de
  oude in één atomaire stap. Verkeer kan alleen via de beschermde tunnel naar
  buiten. Valt de VPN weg, herstart je de computer of stap je over van wifi op
  tethering, dan blijft alles geblokkeerd tot er weer een toegestane route is.
- **Nieuwe netwerkinterfaces worden geblokkeerd.** Sluit je USB-tethering aan of
  zet je wifi aan terwijl de killswitch op scherp staat, dus is ingeschakeld,
  dan is de nieuwe interface standaard geblokkeerd. Ze wordt niet toegelaten
  alleen omdat geen enkele regel haar noemt.
- **Er zijn drie filterniveaus.** *Standard* filtert uitgaand en inkomend
  verkeer. *Strict* is de standaardinstelling en filtert daarnaast
  **doorgestuurd** verkeer. Dat is nodig omdat containers, VM’s en Waydroid hun
  verkeer via de host sturen, en doorgestuurde pakketten komen nooit langs de
  output-hook. *Paranoid* voegt op elke netwerkkaart (NIC) een
  **netdev-egress**-keten toe. Dat is de enige laag die verkeer van raw sockets
  ziet.
- **DNS-verzoeken kunnen niet om de tunnel heen.** Je kiest welke DNS-resolver
  wordt gebruikt zolang de killswitch op scherp staat. Je kunt DNS-verzoeken
  door de VPN sturen, de resolver gebruiken van het netwerk waarop je zit, of
  een resolver die je zelf kiest. De eigen resolver van het netwerk wordt alleen
  gebruikt in het netwerk van een vertrouwde kiwi-node. De killswitch past je
  keuze toe via de instellingen per verbinding van systemd-resolved. Als tweede
  beveiliging gooit een nftables-regel elk ander DNS-verzoek weg.
- **Heeft de VPN-server een hostnaam, dan vertrouwt de daemon gewone DNS niet.**
  Hij zoekt de hostnaam van de VPN-server zelf op. Daarvoor gebruikt hij
  DNS-over-HTTPS, maakt hij verbinding met een vastgezet IP-adres en
  controleert hij het certificaat. Elk antwoord bewaart hij in een cache.
- **Eerst kies je een verbinding, dan pas je toe.** Wijzigingen worden eerst
  klaargezet: ze worden verzameld en gaan pas in als je ze toepast. Daardoor kun
  je van “thuis-LAN + kiwi-node” overstappen op “tethering + VPN” *terwijl je al
  via tethering werkt*. Apply voert dan alle wijzigingen in één atomaire
  transactie door, en de killswitch staat op geen enkel moment daartussen uit.
- **Vertrouwde kiwi-nodes.** Misschien heeft je netwerk een gateway die je
  verkeer al door een tunnel stuurt. In een Kiwi-netwerk is dat een
  [gateway-node](../server/roles.md#node). In zijn eigen netwerk kan zo’n
  gateway de plaats van de VPN innemen. De killswitch herkent hem aan zijn
  IP-adres **en** zijn MAC-adres. Dit moet je zelf aanzetten. De killswitch
  besluit nooit uit zichzelf dat een gateway te vertrouwen is.
- **Er kan maar één VPN verbinding maken.** Alleen de server van de gekozen
  verbinding is bereikbaar. Elke andere tunnel die je start, krijgt geen
  verbinding, en de gebruikersinterface laat zien welke het is.
- **De regels blijven staan.** Ze zijn er nog na een herstart, na uit- en
  weer inloggen en na een herstart van NetworkManager. Een aparte unit laadt
  blokkeerregels *voordat het netwerk opkomt*.

## Installeren { #install }

kiwi-killswitch heeft `nftables`, `NetworkManager` en `python3-gobject` nodig,
en voor WireGuard ook `wireguard-tools`. Die zijn allemaal aanwezig op
Silverblue en Bluefin. Er wordt niets naar de onveranderlijke `/usr`
geschreven. Je gebruiker moet in de groep `wheel` zitten.

```bash
kiwi install kiwi-killswitch   # beide delen; richt zo nodig de system-scope van kiwi in
```

Je kunt hem ook vanuit een kloon van de repository installeren. Voer eerst
`sudo ./install.sh install` uit: dat installeert de daemon, de CLI, het
D-Bus-beleid en de systemd-units. Voer daarna `./install.sh install` uit voor de
GNOME-extensie en de app met instellingen. Log uit en weer in, zodat GNOME de
extensie laadt. Bij het verwijderen wordt de killswitch eerst uitgeschakeld,
zodat je na het verwijderen niet met een geblokkeerd netwerk blijft zitten.

## Gebruiken { #use }

Open in het snelmenu van GNOME **Quick Settings → Kill Switch** om de
killswitch aan en uit te zetten en te kiezen welke VPN wordt beschermd. Voor de
rest open je **Kiwi Kill Switch** in het overzicht van apps. De CLI kent deze
commando’s:

```bash
kiwi-killswitch status                   # wat er nu wordt afgedwongen
kiwi-killswitch list                     # VPN-verbindingen die NetworkManager kent
kiwi-killswitch vpn <name>               # klaarzetten welke wordt beschermd
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # één atomaire transactie
kiwi-killswitch arm                      # of: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # wat klaarstaat; revert gooit het weg
```

!!! warning "Inschakelen via SSH"
    Schakel je de killswitch in, dan wordt een SSH-sessie vanuit een subnet dat
    niet in `mgmt_subnets` staat afgebroken. Zo hoort een killswitch zich te
    gedragen. Werk je via SSH, stel dan eerst deze waarden in:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Herstel.** De CLI heeft geen netwerk nodig, dus een tekstconsole (TTY) is
altijd genoeg om `kiwi-killswitch disarm` uit te voeren. Is de daemon zelf weg,
verwijder dan zijn firewalltabellen met `sudo nft delete table inet kiwi_ks` en
`sudo nft delete table netdev kiwi_ks_egress`.

**Virtuele machines.** Een VM in bridge-modus stuurt haar verkeer nooit via de
host, dus de killswitch heeft er geen invloed op. Vermijd in dat geval
`paranoid`, want dat niveau filtert op de fysieke netwerkkaart. Een VM achter
NAT stuurt haar verkeer wel via de host. Met `strict` gaat dat verkeer via de
tunnel naar buiten en wordt het geblokkeerd als de tunnel niet actief is. Zet
het subnet van de VM in `mgmt_subnets`, zodat haar DHCP- en DNS-verzoeken de
host bereiken. De tabel laat zien wat elke instelling toestaat:

| Instelling | Uitgaand | Inkomend | Blijft buiten de tunnel |
|---|---|---|---|
| `allow_lan` | ja (auto) | nee | nee |
| `bypass_subnets` | ja | nee | nee |
| `mgmt_subnets` | ja | ja | ja |

**Controleren of het werkt.** Zet de killswitch aan en haal daarna de VPN neer
met `nmcli connection down …`. Nu moet `curl --max-time 5 ifconfig.me` een
**time-out** geven. Je echte IP-adres mag niet verschijnen. Beoordeel het
resultaat niet door de publieke IP-adressen te vergelijken die je ziet. Of het
verkeer echt door de tunnel gaat, bewijs je met `wg show <iface> transfer` of
`ip route get 1.1.1.1`.

## Andere firewalls en bekende grenzen { #coexistence-and-known-limits }

- **firewalld kan aan blijven.** De ketens van firewalld draaien op prioriteit
  10, die van de killswitch op −10.
- Gebruik hem **niet** samen met een andere killswitch die een eigen tabel heeft
  die uitgaand verkeer weggooit.
- Laat `nftables.service` met rust als je die niet gebruikt. Wordt deze service
  gestopt, dan verwijdert ze alle nftables-tabellen. De daemon laadt zijn regels
  binnen enkele seconden opnieuw, maar gedurende die seconden ontbreken ze, en
  er is geen reden om dat te veroorzaken.
- Een VPN waarvan de server als **hostnaam** is opgegeven, kan geen nieuwe
  verbinding maken zolang de killswitch op scherp staat, tenzij DNS op *een
  resolver die ik kies* staat. NetworkManager en OpenVPN zoeken de naam namelijk
  op via de resolver van het systeem, en die is geblokkeerd zolang er geen
  tunnel actief is. Verbindingen waarvan de server als IP-adres is opgegeven,
  hebben hier geen last van.
- **Een resolver die je zelf kiest, is buiten de tunnel bereikbaar** zolang de
  tunnel niet actief is. Zet er DNS-over-TLS voor aan.
- **Een vertrouwde node die zonder MAC-adres is opgeslagen**, wordt alleen aan
  zijn gateway-adres herkend.
- **Bediening zonder wachtwoord** werkt via het D-Bus-beleid voor de groep
  `wheel`. Dat betekent ook dat elk programma dat als jouw gebruiker draait, de
  killswitch kan uitzetten zonder het je te vragen.
- De killswitch houdt lekken tegen op netwerkniveau. Hij is geen Tails of
  Whonix. Tegen browser-fingerprinting, WebRTC of een app die via de tunnel
  gegevens naar de maker stuurt, doet hij niets.
- Het is een persoonlijk programma en het is niet onafhankelijk gecontroleerd.
  `tests/run.sh` test de echte daemon met echte nftables. Elke testgroep draait
  in een eigen namespace, en de tests hebben geen root nodig.
- De release-tags zijn nog niet ondertekend. Met kiwi-updater 2.4 vraagt het
  root-deel daarom om je wachtwoord als het wordt bijgewerkt.

kiwi-killswitch is gebaseerd op drie eerdere tools van dezelfde maker. De
volgorde bij het opstarten komt uit `gnome-vpn-killswitch`, het herkennen van
de gateway uit `kiwi-vpn-monitor`, en de opbouw van de daemon uit
`nova-killswitch`.
