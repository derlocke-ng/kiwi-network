# Zo werkt het netwerk

Een Kiwi Network verbindt je eigen machines in één besloten netwerk, waar ze
ook staan: servers thuis of op kantoor, laptops, telefoons en complete
thuisnetwerken achter een router. De machines bereiken elkaar alsof ze in
hetzelfde lokale netwerk hangen, en maar één ervan hoeft bereikbaar te zijn
vanaf internet. Op deze pagina lees je hoe dat netwerk is opgebouwd en waar elk
onderdeel voor dient.

Het besloten netwerk is een **WireGuard-mesh**. WireGuard is de VPN-software
die de verbindingen versleutelt, en *de mesh* is in deze documentatie de naam
voor het besloten netwerk waarin al je machines zitten. In het midden van de
mesh staat één machine, de *kiwi-master*. Alle andere machines (nodes thuis of
op kantoor, laptops, telefoons, routers) zetten zelf de verbinding met de master
op en kunnen daarna via de mesh bij elkaar. Het hele netwerk staat beschreven in
één bestand, het fleetbestand, en [kiwi-server](../server/index.md) bouwt het
netwerk aan de hand van dat bestand op.

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## De master { #the-master }

De master is de machine waarmee alle andere verbinding maken. Bij de rol
`master` horen de vijf modules hieronder. Pi-hole, Tor en nginx delen de
netwerk-namespace van de WireGuard-server. Een netwerk-namespace is de eigen set
netwerkinterfaces, adressen en routes van een container. Deze drie diensten
hebben dus geen eigen netwerk, maar gebruiken dat van de WireGuard-server.
Daarom worden ze samen met de WireGuard-server herstart.

- **vpn-server** (wg-easy) is de WireGuard-server. Elke client en elke node
  maakt er verbinding mee, en de server geeft hun WireGuard-configuraties uit.
  Die configuraties kan kiwi-server voor je aanmaken (`kiwi-server enroll`).
- **vpn-client** (gluetun) verbindt de master met een commerciële VPN-provider.
  De preset gebruikt Mullvad, maar elke provider die gluetun ondersteunt, werkt.
  De standaardroute van de WireGuard-server wijst naar deze VPN-client. Verkeer
  uit de mesh naar internet gaat daardoor via de provider, en websites zien het
  adres van de provider en niet dat van de master zelf. Deze verbinding is de
  *uitgang* van de master: de weg waarlangs verkeer uit de mesh op internet
  komt. Het verkeer gaat achter elkaar door twee VPN’s, eerst die van jou en dan
  die van de provider, en daarom heet deze opzet de **double hop**. Een master
  zonder vpn-client stuurt het verkeer rechtstreeks naar internet, vanaf zijn
  eigen adres.
- **dns** (Pi-hole 6) is de DNS-server van de mesh. Je bereikt hem op het
  mesh-adres van de master, `10.8.0.1`. Zie
  [DNS, namen en certificaten](dns.md).
- **tor** biedt de clients in de mesh een SOCKS5-proxy aan op `10.8.0.1:9050`.
  Tor kiest zijn entrynodes en Tor-exitnodes alleen uit een vaste reeks landen (standaard `de,ch,at,nl,fr`, afgedwongen met `StrictNodes`).
- **reverse-proxy** (nginx) levert de beheerpagina’s `wg.<master>` en
  `pihole.<master>`, de webinterfaces van wg-easy en Pi-hole. Ze zijn alleen
  binnen de mesh te openen, en alleen door clients die beheerpagina’s mogen
  zien (zie “Clientgroepen” hieronder).

Op een master kunnen ook een **nostr-relay** en een **hub** draaien voor de
[mensen in je netwerk](../people/hubs.md#on-a-kiwi-network). Een hub is een
communitysite die in de browser draait, en een nostr-relay is het soort server
waarover hubs hun gegevens synchroniseren. Ook Portainer en back-ups kun je aan
een master toevoegen.

### Wat bereikbaar is vanaf internet { #what-is-reachable-from-the-internet }

Standaard staat er op de master precies **één poort** open naar internet:
WireGuard op UDP 51820. De beheerpagina’s kun je alleen vanuit de mesh openen.
Met twee instellingen zet je meer poorten open:

- `reverse-proxy.public: true` zet de poorten 80 en 443 open en vraagt Let’s
  Encrypt-certificaten aan voor namen buiten het domein van de fleet. Al het
  andere blijft alleen vanuit de mesh bereikbaar, en op verzoeken van buiten
  antwoorden de beheerpagina’s met foutcode 403. Deze instelling is bedoeld voor
  een openbare hub of relay.
- `vpn-server.unlock_relay` zet de TCP-poorten van
  [Tang-ringen](../server/operations.md#encrypted-disks-and-unlocking) open voor
  machines achter NAT. Tang is een server waarmee een machine met een
  versleutelde schijf die schijf bij het opstarten kan ontgrendelen, en een
  ring is één Tang-server met eigen sleutels.

Aan SSH verandert kiwi-server niets. Het blijft zoals het besturingssysteem het
instelt, en dat betekent standaard dat je alleen met sleutels kunt inloggen.
Zelf gebruikt kiwi-server SSH voor `apply` en `status`.

## Clientgroepen { #client-groups }

De clients van de WireGuard-server (wg-easy) zijn op basis van hun adres
ingedeeld in **groepen**. De groep bepaalt waar de leden bij mogen:

| Groep | Subnet | Kan bij | Ziet andere clients | Beheerpagina’s |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | de nodes | nee | nee |
| `pentest` | `10.8.2.0/24` | niets in de mesh | nee | nee |
| `devices` | `10.8.3.0/24` | alles | ja | ja |
| `routers` | `10.8.4.0/24` | alles | ja | nee |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # een QR-code voor de WireGuard-app
kiwi-server enroll fleet.yaml anna  --group guests --split # alleen verkeer voor de mesh gaat door de tunnel
```

De leden van elke groep kunnen ook via de uitgang van de master op internet,
tenzij je voor de groep `internet: false` instelt. Een client met een adres
buiten alle groepen (`10.8.0.x`) is een gewoon lid van de mesh. Zo’n client kan
overal bij en kan de beheerpagina’s openen zolang `admin_from_mesh` aanstaat.

De groepen zijn een instelling van de module vpn-server (`groups`). Je kunt ze
dus aanpassen of er eigen groepen aan toevoegen. Bij `reach` geef je voor een
groep `all`, `nodes`, hostnamen, adressen of subnetten op. De oudere instelling
`isolated_subnet`, waarmee je één afgezonderde groep vastlegde, bestaat nog
maar staat standaard uit.

## Nodes { #nodes }

Een node is een machine thuis of op kantoor waarop je diensten draaien. Ook een
node heeft de module vpn-client, maar hier maakt die geen verbinding met een
commerciële VPN-provider. De module verbindt de node met de master, met de
WireGuard-configuratie die de master voor de node heeft uitgegeven.
`kiwi-server enroll` schrijft die configuratie naar `secrets/<hostname>.conf`,
en de node gebruikt ze zonder dat je verder iets hoeft in te stellen. Een node
heeft geen open poort naar internet nodig, want hij zet zelf de verbinding met
de master op. Daardoor werkt een node ook achter de NAT van een thuisrouter.

De rol `node` heeft drie presets:

| Preset | Wat de machine wordt |
|---|---|
| `gateway` (standaard) | Een gateway voor het lokale netwerk (LAN). Apparaten in het LAN die deze machine als standaardgateway gebruiken, komen via de VPN op internet en kunnen bij de mesh. Pi-hole is de DNS-server van het LAN en kan desgewenst ook de DHCP-server zijn. De downloadprogramma’s Transmission en JDownloader draaien *in* de netwerk-namespace van de VPN-client. Ligt de tunnel plat, dan hebben ze dus helemaal geen route. Bij de preset horen ook nginx, Portainer en SFTP. |
| `cloud` | Je eigen cloud: Nextcloud met Collabora voor bestanden, agenda’s en documenten, en Vaultwarden voor wachtwoorden. Deze diensten staan achter nginx, en ook Portainer hoort erbij. Nextcloud is opgebouwd uit de containers van het AIO-project, maar zonder de AIO-mastercontainer. |
| `minimal` | Alleen de VPN-client en nginx. De modules die je wilt hebben, voeg je zelf toe. |

Op een node kunnen ook back-ups, een back-upserver en Tang draaien. OpenCloud,
Immich en Paperless-ngx worden meegeleverd om uit te proberen. Zie de
[lijst met modules](../server/modules.md).

De diensten op een node bereik je vanuit het LAN van de node en op het
**mesh-adres** van de node (bijvoorbeeld `10.8.0.25`). Verkeer uit de mesh naar
dat adres op poort 80 en 443 wordt doorgestuurd naar de reverse proxy van de
node.

## Namen { #names }

Voor de namen van machines geldt een afspraak. **Masters zijn vernoemd naar
fruitgerechten** (`crumble`, `sorbet`, `compote`, `chutney`, `strudel`,
`cobbler`, `trifle`, `cider`) en **nodes naar fruitsoorten** (`papaya`, `lychee`,
`guava`, `quince`, `damson`). Zo zie je aan elke logregel om wat voor machine
het gaat. Meer dan een afspraak is het niet: elke naam werkt. Een dienst krijgt
een naam onder de naam van de machine waarop hij draait: `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. Zie
[DNS, namen en certificaten](dns.md).

## Zo komt de mesh op internet { #ways-out }

Een master is een WireGuard-server met een uitgang: de weg waarlangs verkeer
uit de mesh op internet komt. Die uitgang kent drie modi:

| Modus | Hoe de mesh op internet komt | Status |
|---|---|---|
| **provider** | Via een commerciële VPN-provider (gluetun). Dit is de double hop, en zo richt de preset voor de master het in. | gebouwd |
| **direct** | Rechtstreeks via de eigen internetverbinding van de master. Voor deze modus som je de modules van de master op zonder `vpn-client`. | gebouwd |
| **master** | Via *de master van een ander netwerk*. Jouw master is daar een client, in een groep die wel op internet mag maar verder nergens bij kan. Dit heet multi-hop. | ontworpen; hiervoor moeten apparaten over netwerkgrenzen heen kunnen worden toegevoegd, en dat is federatie |

Welke uitgangsmodus een master ook heeft, hij biedt de mesh altijd ook de
SOCKS5-proxy van Tor aan.

## Eén mesh per netwerk { #one-mesh-per-network }

Elk netwerk heeft een eigen mesh met een eigen adresbereik. Standaard is dat
`10.8.0.0/16`. Masters en nodes zitten in `10.8.0.0/24`, en daarna komen de
groepen: guests in `.1`, pentest in `.2`, devices in `.3` en routers in `.4`.
Een tweede netwerk gebruikt een ander bereik, bijvoorbeeld `10.9.0.0/16`, zodat
een apparaat dat bij beide netwerken hoort ze uit elkaar kan houden. Het bereik is
op dit moment geen losse instelling, maar zit verspreid over meerdere
instellingen (`mesh_subnet`, bij de vpn-server `server_ip`, `wg_subnet`,
`wg_default_address` en `groups`, en bij Tor `socks_policy_accept`). In het
fleetbestand worden ze allemaal ingesteld.

## Adressering { #addressing }

| Wat | Standaard |
|---|---|
| De hele mesh (op elke host gerouteerd) | standaard `10.8.0.0/16` (`mesh_subnet`) |
| Clients van wg-easy | `10.8.0.0/24`; de server is `10.8.0.1` |
| Clientgroepen | `10.8.1.0/24` … `10.8.4.0/24` |
| Netwerk van de stack | `172.64.0.0/24` op een master, `172.128.0.0/24` op een node |
| MTU van WireGuard | `1376` (`wg_mtu`), gemeten met [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU van de bridge van de stack | `1500` (`bridge_mtu`) |

De stack van een machine bestaat uit alle containers van de modules die erop
draaien. Elke machine met een stack routeert het adresbereik van de mesh via de
VPN-client, of op de master via de WireGuard-server. De machine en de
containers erop kunnen daardoor bij elke node.

## Automatisch herstarten en updaten { #keeping-it-fresh }

Elke machine krijgt twee timers, die je in de stack-instellingen van de machine
configureert. De eerste **herstart elke dag de VPN**, om `07:00`, zodat de
machine een nieuw uitgangsadres krijgt. De tweede voert **elke week een update**
uit, op zondag om 00:00. Dan draait `podman auto-update`, mits
`auto_update: registry` is ingesteld. Ook het besturingssysteem werkt zichzelf
bij, en het herstart alleen in
[het onderhoudsvenster dat je hebt ingesteld](../server/machines.md#updates).

## Een heel LAN in de mesh { #a-whole-lan-in-the-mesh }

Een router kan als WireGuard-client in de groep `routers` aan de mesh meedoen.
Het kan ook anders: de router stuurt verkeer voor het mesh-subnet met een
statische route naar een gateway-node. In beide gevallen kan elk apparaat in het
LAN van die router bij elke node, zonder zelf WireGuard te draaien. Zie
[Routers](routers.md).
