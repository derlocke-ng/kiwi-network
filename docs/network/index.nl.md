# Hoe het netwerk werkt

Een Kiwi Network is een **WireGuard-mesh met één hub**, de *kiwi-master*. Elke
andere machine (nodes thuis of op kantoor, laptops, telefoons, routers) belt uit
naar de master en ontmoet de anderen in de mesh. Het geheel wordt beschreven in
één fleet-bestand en gebouwd door [kiwi-server](../server/index.md).

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

De rol `master` draait vijf modules. Pi-hole, Tor en nginx leven binnen de
netwerknamespace van de WireGuard-server en komen samen met hem terug.

- **vpn-server** (wg-easy) is het toegangspunt voor elke client en node, en geeft
  hun WireGuard-configuraties uit. kiwi-server kan ze voor je aanmaken
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) maakt verbinding met een commerciële VPN-provider:
  Mullvad in de preset, in het algemeen elke provider die gluetun ondersteunt. De
  standaardroute van de WireGuard-server wijst ernaar, dus verkeer uit de mesh
  vertrekt via de provider, niet via het eigen adres van de master. Dat is de
  **double hop**. Een master zonder vpn-client gaat rechtstreeks naar buiten.
- **dns** (Pi-hole 6) antwoordt op het mesh-adres van de master, `10.8.0.1`. Zie
  [DNS, namen en certificaten](dns.md).
- **tor** biedt SOCKS5 aan op `10.8.0.1:9050` voor mesh-clients, met ingangs- en
  exit-nodes vastgezet op een set landen (standaard `de,ch,at,nl,fr`,
  `StrictNodes`).
- **reverse-proxy** (nginx) serveert de beheerpagina's, `wg.<master>` en
  `pihole.<master>`, aan beheergroepen in de mesh.

Een master kan ook een **nostr-relay** en een **hub** dragen voor
[mensen op je netwerk](../people/hubs.md#on-a-kiwi-network), plus Portainer en
back-ups.

### Wat er vanaf het internet bereikbaar is { #what-is-reachable-from-the-internet }

Standaard publiceert de master **één poort**: WireGuard, UDP 51820. De
beheerpagina's antwoorden alleen de mesh. Twee instellingen voegen meer toe:

- `reverse-proxy.public: true` publiceert 80 en 443, met Let's Encrypt-certificaten
  voor namen buiten het domein van de fleet. Al het andere antwoordt nog steeds
  alleen de mesh, en beheerpagina's antwoorden van buiten met 403. Dit is voor
  een publieke hub of relay.
- `vpn-server.unlock_relay` opent de TCP-poorten van
  [Tang-ringen](../server/operations.md#encrypted-disks-and-unlocking) voor
  machines achter NAT.

SSH blijft zoals het besturingssysteem het heeft (standaard alleen sleutels).
kiwi-server gebruikt het voor `apply` en `status`.

## Clientgroepen { #client-groups }

De clients van wg-easy worden op adres ingedeeld in **groepen**. Elke groep
bepaalt wat haar leden kunnen bereiken:

| Groep | Subnet | Bereikt | Ziet andere clients | Beheerpagina's |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | de nodes | nee | nee |
| `pentest` | `10.8.2.0/24` | niets in de mesh | nee | nee |
| `devices` | `10.8.3.0/24` | alles | ja | ja |
| `routers` | `10.8.4.0/24` | alles | ja | nee |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # een QR-code voor de WireGuard-app
kiwi-server enroll fleet.yaml anna  --group guests --split # alleen de mesh gaat door de tunnel
```

Elke groep mag via de exit het internet op, tenzij je `internet: false` instelt.
Clients buiten elke groep (`10.8.0.x`) zijn de gewone mesh: ze bereiken alles, en
zien de beheerpagina's zolang `admin_from_mesh` aanstaat. Groepen zijn een
instelling van de module vpn-server (`groups`), dus je kunt ze wijzigen of eigen
groepen toevoegen (`reach` accepteert `all`, `nodes`, hostnamen, adressen of
subnetten). Het oude enkele `isolated_subnet` bestaat nog, maar staat standaard
uit.

## Nodes { #nodes }

De vpn-client van een node praat niet met een commerciële VPN. Hij gebruikt de
WireGuard-configuratie die de master voor hem heeft uitgegeven (`kiwi-server enroll`
schrijft `secrets/<hostname>.conf`, en de node pakt die zelf op). Een node heeft
geen open poort op het internet nodig: hij belt uit naar de master, dus hij werkt
achter de NAT van een thuisrouter.

De rol `node` heeft drie presets:

| Preset | Wat de machine wordt |
|---|---|
| `gateway` (standaard) | Een LAN-gateway. LAN-clients die hem als standaardgateway gebruiken, vertrekken via de VPN en kunnen de mesh bereiken. Pi-hole bedient het LAN (optioneel als DHCP-server). Transmission en JDownloader draaien *binnen* de netwerknamespace van de VPN-client, dus ze hebben helemaal geen route als de tunnel niet actief is. Met nginx, Portainer en SFTP. |
| `cloud` | Nextcloud (uit de containers van het AIO-project, zonder de AIO-mastercontainer) met Collabora, plus Vaultwarden, achter nginx, plus Portainer |
| `minimal` | Alleen de VPN-client en nginx, voor modules naar eigen keuze |

Nodes kunnen ook back-ups, een back-upserver, Tang en (om uit te proberen)
OpenCloud, Immich en Paperless-ngx draaien. Zie de [modulelijst](../server/modules.md).

Diensten op een node zijn bereikbaar op het LAN en op het **mesh-adres** van de
node (bijv. `10.8.0.25`). Mesh-verkeer naar dat adres op 80 en 443 wordt
doorgestuurd naar de reverse proxy.

## Namen { #names }

Machines krijgen hun naam uit de boomgaard: **masters naar
fruitgerechten** (`crumble`, `sorbet`, `compote`, `chutney`, `strudel`,
`cobbler`, `trifle`, `cider`) en **nodes naar vruchten** (`papaya`, `lychee`,
`guava`, `quince`, `damson`), zodat het soort machine in elke logregel te lezen
is. Het is een conventie, en elke naam werkt. Diensten zitten onder hun host:
`cloud.papaya.home`, `vault.papaya.home`, `wg.sorbet.home`. Zie
[DNS, namen en certificaten](dns.md).

## Wegen naar buiten { #ways-out }

Een master is een WireGuard-server met een exit, en de exit heeft drie modi:

| Modus | Hoe de mesh het internet bereikt | Status |
|---|---|---|
| **provider** | via een commerciële VPN (gluetun): de double hop, en de preset van de master | gebouwd |
| **direct** | rechtstreeks via de eigen uplink van de master. Som de modules van de master op zonder `vpn-client` | gebouwd |
| **master** | via *de master van een ander netwerk*, als client in een van diens groepen die het internet mag bereiken en verder niets: multi-hop | ontworpen; het vereist aanmelden tussen netwerken, en dat is federatie |

Elke master biedt de mesh ook de SOCKS5 van Tor aan, wat zijn exit ook is.

## Eén mesh per netwerk { #one-mesh-per-network }

Elk netwerk heeft een eigen mesh. De standaard is `10.8.0.0/16`: masters en nodes
in `10.8.0.0/24`, daarna guests `.1`, pentest `.2`, devices `.3` en routers `.4`.
Een tweede netwerk neemt een ander bereik, bijvoorbeeld `10.9.0.0/16`, zodat een
apparaat dat in beide zit ze uit elkaar kan houden. Op dit moment is het bereik
verspreid over meerdere instellingen (`mesh_subnet`, `server_ip`, `wg_subnet`,
`wg_default_address` en `groups` van de vpn-server, en `socks_policy_accept` van
Tor), en het fleet-bestand stelt ze allemaal in.

## Adressering { #addressing }

| Wat | Standaard |
|---|---|
| De hele mesh (gerouteerd op elke host) | standaard `10.8.0.0/16` (`mesh_subnet`) |
| wg-easy-clients | `10.8.0.0/24`; de server is `10.8.0.1` |
| Clientgroepen | `10.8.1.0/24` … `10.8.4.0/24` |
| Stacknetwerk | `172.64.0.0/24` op een master, `172.128.0.0/24` op een node |
| WireGuard-MTU | `1376` (`wg_mtu`), gemeten met [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU van de stackbridge | `1500` (`bridge_mtu`) |

Elke stackhost routeert de mesh via zijn VPN-client (op de master via de
WireGuard-server), zodat de host en zijn containers elke node bereiken.

## Actueel blijven { #keeping-it-fresh }

Elke machine krijgt twee timers uit haar stack-instellingen: een **dagelijkse
VPN-herstart** (`07:00`, voor een vers exit-adres) en een **wekelijkse update**
(zondag 00:00, die `podman auto-update` draait zolang `auto_update: registry` is
ingesteld). Het besturingssysteem werkt zichzelf bij en herstart alleen in
[je venster](../server/machines.md#updates).

## Een heel LAN in de mesh { #a-whole-lan-in-the-mesh }

Een router kan zich als WireGuard-client in de groep `routers` bij de mesh
voegen, of het mesh-subnet met een statische route naar een gateway-node sturen.
Dan bereikt elk apparaat op dat LAN elke node zonder WireGuard te draaien. Zie
[Routers](routers.md).
