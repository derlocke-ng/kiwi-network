# kiwi-killswitch

Een **fail-closed VPN-killswitch** voor GNOME op Fedora Silverblue en Bluefin.
Eén root-daemon beheert de firewall. Een schakelaar in GNOME Snelle instellingen,
een GTK4-app en een CLI sturen hem aan via de D-Bus-systeembus, zonder ooit om
een wachtwoord te vragen.

Hij beschermt **één** VPN-verbinding tegelijk, WireGuard of OpenVPN. Hij maakt
niet zelf verbinding met je VPN: je zet verbindingen op in de GNOME-instellingen,
en de killswitch bouwt een lekdichte firewall rond wat er echt actief is.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Nieuwste release: **v0.2.3**. Het staat in de [Kiwi-catalogus](catalogs.md), scopes user + system.
- GNOME Shell 45 tot en met 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Een GNOME-extensie is een proces zonder rechten. Ze kan en mag de firewall niet
aanraken, dus de handhaving zit in de daemon en de interface vraagt alleen.

## Wat het doet { #what-it-does }

- **Fail-closed.** `policy drop` op output, input en forward, IPv4 en IPv6,
  atomisch omgewisseld. Verkeer vertrekt alleen via de beschermde tunnel. Als de
  VPN wegvalt, je herstart, of je van wifi naar tethering overstapt, blijft alles
  geblokkeerd tot er weer een toegestaan pad is.
- **Nieuwe interfaces kunnen niet lekken.** Sluit USB-tethering aan of zet wifi
  aan terwijl hij ingeschakeld is, en de nieuwe interface is standaard
  geblokkeerd, niet toegestaan door weglating.
- **Drie niveaus van handhaving.** *Standard* filtert output en input. *Strict*
  (de standaard) filtert ook **doorgestuurd** verkeer, want containers, VM's en
  Waydroid routeren via de host en doorgestuurde pakketten passeren de output-hook
  nooit. *Paranoid* voegt een **netdev-egress**-keten toe op elke netwerkkaart,
  de enige laag die verkeer van raw sockets ziet.
- **DNS kan niet afdwalen.** Kies via de VPN, die van het netwerk zelf (alleen
  vertrouwde kiwi-nodes), of een resolver die je kiest. Het wordt toegepast via de
  instellingen per link van systemd-resolved, met een nftables-vangnet dat elke
  andere opzoeking laat vallen.
- **Endpoints met een hostnaam worden vastgepind, niet aan DNS toevertrouwd.** De
  daemon zoekt de hostnaam van een VPN-server zelf op, via DNS-over-HTTPS naar een
  vastgepind IP met een geverifieerd certificaat, en slaat elk antwoord op.
- **Kies een verbinding, dan Toepassen.** Wijzigingen worden klaargezet, dus je
  kunt van "thuis-LAN + kiwi-node" overstappen naar "tethering + VPN" *terwijl je
  al op tethering zit*, en het dan toepassen als één atomische transactie zonder
  uitgeschakeld moment ertussen.
- **Vertrouwde kiwi-nodes.** Een gateway die al voor je tunnelt (een
  [gateway-node](../server/roles.md#node)), herkend aan IP **en** MAC, kan op zijn
  eigen netwerk de plaats van de VPN innemen. Dat is opt-in en wordt nooit
  afgeleid.
- **Eén VPN, afgedwongen.** Alleen de server van de gekozen verbinding is
  bereikbaar. Elke andere tunnel die je start, kan geen verbinding maken, en de
  interface noemt hem.
- **Overleeft alles.** Herstarts, uit- en inloggen, herstarts van
  NetworkManager: de regels blijven. Een aparte unit installeert een harde
  blokkade *voordat het netwerk opkomt*.

## Installeren { #install }

Het vereist `nftables`, `NetworkManager`, `python3-gobject` en, voor WireGuard,
`wireguard-tools`, allemaal aanwezig op Silverblue en Bluefin. Er wordt niets
naar de onveranderlijke `/usr` geschreven. Je gebruiker moet in `wheel` zitten.

```bash
kiwi install kiwi-killswitch   # beide helften; richt zo nodig de systeemscope van kiwi in
```

Of vanuit een clone: `sudo ./install.sh install` (de daemon, CLI, buspolicy en
systemd-units), daarna `./install.sh install` (de GNOME-extensie en de
instellingenapp). Log uit en weer in zodat GNOME de extensie laadt. Bij
deïnstalleren wordt eerst uitgeschakeld, zodat je niet buitengesloten kunt
raken.

## Gebruik { #use }

Open **Snelle instellingen → Kill Switch** om in en uit te schakelen en te kiezen
welke VPN beschermd wordt, of **Kiwi Kill Switch** in het app-overzicht voor al
het andere.

```bash
kiwi-killswitch status                   # wat er op dit moment wordt afgedwongen
kiwi-killswitch list                     # VPN-verbindingen die NetworkManager kent
kiwi-killswitch vpn <name>               # klaarzetten welke beschermd wordt
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # één atomische transactie
kiwi-killswitch arm                      # of: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # wat er klaarstaat; revert gooit het weg
```

!!! warning "Inschakelen via SSH"
    Inschakelen verbreekt een sessie vanuit een subnet dat niet in `mgmt_subnets`
    staat. Dat is correct gedrag voor een killswitch. Stel het eerst in:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Herstel.** De CLI heeft geen netwerk nodig, dus een TTY is altijd genoeg:
`kiwi-killswitch disarm`. Als de daemon zelf weg is:
`sudo nft delete table inet kiwi_ks` en `sudo nft delete table netdev kiwi_ks_egress`.

**Virtuele machines.** Een VM met bridge routeert nooit via de host, dus de
killswitch laat hem met rust (vermijd `paranoid`, dat op de fysieke kaart
filtert). Een VM achter NAT routeert via de host. `strict` stuurt hem door de
tunnel naar buiten en blokkeert hem als de tunnel niet actief is. Voeg zijn subnet
toe aan `mgmt_subnets` zodat zijn DHCP en DNS de host bereiken:

| Instelling | Uitgaand | Inkomend | Buiten de tunnel vastgezet |
|---|---|---|---|
| `allow_lan` | ja (auto) | nee | nee |
| `bypass_subnets` | ja | nee | nee |
| `mgmt_subnets` | ja | ja | ja |

**Controleren.** Schakel hem in en haal dan de VPN neer
(`nmcli connection down …`). `curl --max-time 5 ifconfig.me` moet een **time-out**
geven, niet je echte IP tonen. Beoordeel het niet door exit-IP's te vergelijken:
bewijs het gebruik van de tunnel met `wg show <iface> transfer` of
`ip route get 1.1.1.1`.

## Naast andere software en bekende beperkingen { #coexistence-and-known-limits }

- **firewalld kan aan blijven.** De ketens daarvan draaien op prioriteit 10 en
  de onze op −10.
- Draai hem **niet** naast een andere killswitch die een output-drop-tabel
  beheert.
- Laat `nftables.service` met rust als je die niet gebruikt. Hem stoppen leegt
  elke tabel. De daemon zet zijn regels binnen enkele seconden terug, maar er is
  geen reden om dat venster te openen.
- Een VPN met een **hostnaam** als endpoint kan niet opnieuw verbinden terwijl de
  killswitch ingeschakeld is, tenzij DNS op *a resolver I choose* staat.
  NetworkManager en OpenVPN zoeken de naam op via de systeemresolver, en die is
  geblokkeerd zolang er geen tunnel actief is. Verbindingen met een letterlijk IP
  hebben er geen last van.
- **Een resolver die je kiest, is buiten de tunnel bereikbaar** zolang de tunnel
  niet actief is. Zet er DNS-over-TLS voor aan.
- **Een vertrouwde node die zonder MAC is opgeslagen**, wordt alleen op zijn
  gateway-adres herkend.
- **Bediening zonder wachtwoord** is de D-Bus-buspolicy voor de groep `wheel`.
  Dat betekent ook dat elk programma dat als jou draait de schakelaar zonder te
  vragen kan uitzetten.
- Hij stopt lekken op netwerkniveau. Hij is geen Tails of Whonix en doet niets
  tegen browser-fingerprinting, WebRTC, of een app die via de tunnel naar huis
  belt.
- Het is een persoonlijke tool en is niet onafhankelijk geaudit. `tests/run.sh`
  test de echte daemon met echte nftables, elke testgroep in een eigen namespace,
  zonder root.
- De release-tags zijn nog niet ondertekend, dus met kiwi-updater 2.4 vraagt de
  root-helft om je wachtwoord bij een update.

Hij stamt af van `gnome-vpn-killswitch` (opstartvolgorde), `kiwi-vpn-monitor`
(gateway-detectie) en `nova-killswitch` (de daemon-architectuur) van de auteur.
