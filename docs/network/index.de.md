# So funktioniert das Netzwerk

Ein Kiwi Network verbindet deine eigenen Maschinen zu einem privaten Netzwerk,
egal wo sie stehen: Server zu Hause oder im Büro, Laptops, Handys und ganze
Heimnetze hinter einem Router. Die Maschinen erreichen einander so, als hingen
sie am selben lokalen Netz, und nur eine von ihnen muss aus dem Internet
erreichbar sein. Diese Seite erklärt, wie das Netzwerk aufgebaut ist und welche
Aufgabe jeder Teil darin hat.

Das private Netzwerk ist ein **WireGuard-Mesh**. WireGuard ist die VPN-Software,
die die Verbindungen verschlüsselt. *Mesh* nennen diese Seiten das private
Netzwerk, in dem alle deine Maschinen hängen. In seiner Mitte steht eine
Maschine, der *kiwi-master*. Alle anderen – Nodes zu Hause oder im Büro,
Laptops, Handys, Router – bauen die Verbindung zum Master selbst auf und
erreichen danach über das Mesh auch einander. Beschrieben ist das ganze Netzwerk
in einer einzigen Datei, der Fleet-Datei (`fleet.yaml`), und
[kiwi-server](../server/index.md) baut es daraus auf.

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

## Der Master { #the-master }

Der Master ist die Maschine, mit der sich alle anderen verbinden. Seine Rolle
`master` besteht aus den fünf Modulen, die unten aufgeführt sind. Pi-hole, Tor
und nginx teilen sich dabei den Netzwerk-Namespace des WireGuard-Servers. Ein
Netzwerk-Namespace ist der eigene Satz von Netzwerkschnittstellen, Adressen und
Routen, den ein Container hat. Die drei Dienste haben also kein eigenes
Netzwerk, sondern nutzen das des WireGuard-Servers. Deshalb werden sie auch
zusammen mit ihm neu gestartet.

- **vpn-server** (wg-easy) ist der WireGuard-Server. Jeder Client und jeder Node
  verbindet sich mit ihm, und er stellt ihre WireGuard-Konfigurationen aus.
  kiwi-server kann diese Konfigurationen für dich anlegen
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) verbindet den Master mit einem kommerziellen
  VPN-Anbieter. Im Preset ist das Mullvad, es funktioniert aber jeder Anbieter,
  den gluetun unterstützt. Die Standardroute des WireGuard-Servers zeigt auf
  diesen VPN-Client. Verkehr aus dem Mesh ins Internet wird deshalb über den
  Anbieter geschickt, und Websites sehen dessen Adresse, nicht die des Masters.
  Diese Verbindung ist der *Ausgang* des Masters: der Weg, auf dem der Verkehr
  aus dem Mesh ins Internet gelangt. Weil der Verkehr dabei nacheinander durch
  zwei VPNs läuft, erst durch deins, dann durch das des Anbieters, heißt dieser
  Aufbau **Double Hop**. Ein Master ohne vpn-client schickt den Verkehr direkt
  ins Internet, mit seiner eigenen Adresse als Absender.
- **dns** (Pi-hole 6) ist der DNS-Server für das Mesh. Er antwortet unter der
  Mesh-Adresse des Masters, `10.8.0.1`. Mehr dazu unter [DNS, Namen &
  Zertifikate](dns.md).
- **tor** stellt den Clients im Mesh unter `10.8.0.1:9050` einen SOCKS5-Proxy
  bereit. Als Eingangs- und Exit-Knoten kommen nur Tor-Knoten aus bestimmten
  Ländern in Frage (Standard: `de,ch,at,nl,fr`, durchgesetzt mit `StrictNodes`).
- **reverse-proxy** (nginx) liefert die Admin-Seiten `wg.<master>` und
  `pihole.<master>` aus, also die Weboberflächen von wg-easy und Pi-hole.
  Erreichbar sind sie nur im Mesh, und auch dort nur für Clients, die
  Admin-Seiten sehen dürfen (siehe „Client-Gruppen“ weiter unten).

Auf einem Master können außerdem ein **nostr-Relay** und ein **Hub** für die
[Menschen in deinem Netzwerk](../people/hubs.md#on-a-kiwi-network) laufen. Ein
Hub ist die Seite einer Community, die im Browser läuft, und ein nostr-Relay ist
die Art von Server, über die sich Hubs synchronisieren. Auch Portainer und
Backups lassen sich auf einem Master ergänzen.

### Was aus dem Internet erreichbar ist { #what-is-reachable-from-the-internet }

Standardmäßig ist auf dem Master genau **ein Port** zum Internet hin offen:
WireGuard auf UDP 51820. Die Admin-Seiten lassen sich nur aus dem Mesh öffnen.
Zwei Einstellungen öffnen weitere Ports:

- `reverse-proxy.public: true` öffnet die Ports 80 und 443 und holt
  Let's-Encrypt-Zertifikate für Namen außerhalb der Fleet-Domain. Alles andere
  bleibt weiterhin nur aus dem Mesh erreichbar, und die Admin-Seiten beantworten
  Anfragen von außen mit dem Fehler 403. Gedacht ist die Einstellung für einen
  öffentlichen Hub oder ein öffentliches Relay.
- `vpn-server.unlock_relay` öffnet die TCP-Ports von
  [Tang-Ringen](../server/operations.md#encrypted-disks-and-unlocking) für
  Maschinen hinter NAT. Tang ist ein Server, mit dessen Hilfe eine Maschine ihre
  verschlüsselte Festplatte beim Start selbst entsperren kann. Ein Ring ist ein
  Tang-Server mit eigenen Schlüsseln.

SSH lässt kiwi-server so, wie das Betriebssystem es einrichtet. Standardmäßig
heißt das: Anmeldung nur mit Schlüsseln. kiwi-server selbst nutzt SSH für
`apply` und `status`.

## Client-Gruppen { #client-groups }

Die Clients des WireGuard-Servers (wg-easy) werden anhand ihrer Adresse in
**Gruppen** eingeteilt. Die Gruppe legt fest, was ihre Mitglieder erreichen
dürfen:

| Gruppe | Subnetz | Erreicht | Sieht andere Clients | Admin-Seiten |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | die Nodes | nein | nein |
| `pentest` | `10.8.2.0/24` | nichts im Mesh | nein | nein |
| `devices` | `10.8.3.0/24` | alles | ja | ja |
| `routers` | `10.8.4.0/24` | alles | ja | nein |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # ein QR-Code für die WireGuard-App
kiwi-server enroll fleet.yaml anna  --group guests --split # nur das Mesh läuft durch den Tunnel
```

Die Mitglieder aller Gruppen erreichen über den Ausgang des Masters außerdem das
Internet, es sei denn, du setzt für die Gruppe `internet: false`. Ein Client,
dessen Adresse zu keiner Gruppe gehört (`10.8.0.x`), ist ein gewöhnliches
Mitglied des Mesh. Er erreicht alles und kann die Admin-Seiten öffnen, solange
`admin_from_mesh` eingeschaltet ist.

Die Gruppen sind eine Einstellung des Moduls vpn-server (`groups`). Du kannst
sie also ändern oder eigene hinzufügen. Die Einstellung `reach` einer Gruppe
nimmt `all`, `nodes`, Hostnamen, Adressen oder Subnetze an. Die ältere
Einstellung `isolated_subnet`, mit der sich eine einzelne isolierte Gruppe
festlegen ließ, gibt es noch, sie ist aber standardmäßig ausgeschaltet.

## Nodes { #nodes }

Ein Node ist eine Maschine zu Hause oder im Büro, auf der deine Dienste laufen.
Auch er hat ein vpn-client-Modul. Auf einem Node verbindet es sich aber nicht
mit einem kommerziellen VPN-Anbieter, sondern mit dem Master, und zwar mit der
WireGuard-Konfiguration, die der Master für diesen Node ausgestellt hat.
`kiwi-server enroll` schreibt diese Konfiguration nach
`secrets/<hostname>.conf`, und der Node verwendet sie, ohne dass du noch etwas
einstellen musst. Einen offenen Port zum Internet braucht ein Node nicht, denn
er baut die Verbindung zum Master selbst auf. Deshalb funktioniert er auch
hinter dem NAT eines Heimrouters.

Für die Rolle `node` gibt es drei Presets:

| Preset | Was aus der Maschine wird |
|---|---|
| `gateway` (Standard) | Ein Gateway für das lokale Netz (LAN). Geräte im LAN, die diese Maschine als Standard-Gateway eingetragen haben, gelangen über das VPN ins Internet und erreichen außerdem das Mesh. Pi-hole ist der DNS-Server des LAN und auf Wunsch auch sein DHCP-Server. Die Download-Programme Transmission und JDownloader laufen *im* Netzwerk-Namespace des VPN-Clients und haben deshalb überhaupt keine Route, solange der Tunnel nicht steht. Zum Preset gehören außerdem nginx, Portainer und SFTP. |
| `cloud` | Deine eigene Cloud: Nextcloud mit Collabora für Dateien, Kalender und Dokumente sowie Vaultwarden für Passwörter. Die Dienste liegen hinter nginx, Portainer ist ebenfalls dabei. Nextcloud wird aus den Containern des AIO-Projekts aufgebaut, aber ohne dessen Master-Container. |
| `minimal` | Nur der VPN-Client und nginx. Die Module, die du haben möchtest, fügst du selbst hinzu. |

Nodes können außerdem Backups, einen Backup-Server und Tang übernehmen.
OpenCloud, Immich und Paperless-ngx sind zum Ausprobieren dabei. Alle Module
stehen in der [Modulliste](../server/modules.md).

Die Dienste eines Nodes erreichst du aus seinem LAN und unter seiner
**Mesh-Adresse** (zum Beispiel `10.8.0.25`). Verkehr aus dem Mesh, der an diese
Adresse auf Port 80 oder 443 geht, wird an den Reverse-Proxy des Nodes
weitergeleitet.

## Namen { #names }

Für die Namen der Maschinen gilt eine Konvention: **Master heißen nach
Obstgerichten** (`crumble`, `sorbet`, `compote`, `chutney`, `strudel`,
`cobbler`, `trifle`, `cider`), **Nodes nach Früchten** (`papaya`, `lychee`,
`guava`, `quince`, `damson`). So erkennst du in jeder Logzeile, zu welcher Art
von Maschine ein Name gehört. Es ist nur eine Konvention, jeder andere Name
funktioniert genauso. Ein Dienst bekommt einen Namen unterhalb des Namens der
Maschine, auf der er läuft: `cloud.papaya.home`, `vault.papaya.home`,
`wg.sorbet.home`. Mehr dazu unter [DNS, Namen & Zertifikate](dns.md).

## Wie das Mesh ins Internet gelangt { #ways-out }

Ein Master ist ein WireGuard-Server mit einem Ausgang, also dem Weg, auf dem der
Verkehr aus dem Mesh ins Internet gelangt. Für diesen Ausgang gibt es drei
Arten:

| Ausgangsart | Wie das Mesh ins Internet gelangt | Status |
|---|---|---|
| **provider** | Über einen kommerziellen VPN-Anbieter (gluetun). Das ist der Double Hop, und so richtet ihn das Master-Preset ein. | umgesetzt |
| **direct** | Direkt über den Internetanschluss des Masters. Dafür führst du die Module des Masters ohne `vpn-client` auf. | umgesetzt |
| **master** | Über den *Master eines anderen Netzwerks*. Dein Master ist dort ein Client in einer Gruppe, die ins Internet darf und sonst nichts erreicht. Das nennt sich Multi-Hop. | entworfen; setzt voraus, dass Geräte über Netzwerkgrenzen hinweg aufgenommen werden können, also Föderation |

Unabhängig von der Ausgangsart stellt jeder Master dem Mesh außerdem den
SOCKS5-Proxy von Tor bereit.

## Ein Mesh pro Netzwerk { #one-mesh-per-network }

Jedes Netzwerk hat sein eigenes Mesh mit einem eigenen Adressbereich. Der
Standard ist `10.8.0.0/16`. Master und Nodes liegen in `10.8.0.0/24`, danach
folgen die Gruppen: guests in `.1`, pentest in `.2`, devices in `.3` und routers
in `.4`. Ein zweites Netzwerk bekommt einen anderen Bereich, zum Beispiel
`10.9.0.0/16`, damit ein Gerät, das zu beiden Netzwerken gehört, sie
auseinanderhalten kann. Bisher lässt sich der Bereich nicht an einer einzigen
Stelle festlegen, sondern steckt in mehreren Einstellungen: `mesh_subnet`, beim
vpn-server `server_ip`, `wg_subnet`, `wg_default_address` und `groups` sowie bei
Tor `socks_policy_accept`. Die Fleet-Datei setzt sie alle.

## Adressen { #addressing }

| Was | Standard |
|---|---|
| Das gesamte Mesh (auf jedem Host geroutet) | `10.8.0.0/16`, sofern `mesh_subnet` nichts anderes festlegt |
| Clients von wg-easy | `10.8.0.0/24`; der Server hat `10.8.0.1` |
| Client-Gruppen | `10.8.1.0/24` … `10.8.4.0/24` |
| Stack-Netzwerk | `172.64.0.0/24` auf einem Master, `172.128.0.0/24` auf einem Node |
| WireGuard-MTU | `1376` (`wg_mtu`), gemessen mit [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU der Stack-Bridge | `1500` (`bridge_mtu`) |

Der Stack einer Maschine besteht aus den Containern, in denen ihre Module
laufen. Jede Maschine mit einem Stack routet den Adressbereich des Mesh über
ihren VPN-Client, der Master über den WireGuard-Server. So erreichen die
Maschine und ihre Container jeden Node.

## Automatische Neustarts und Updates { #keeping-it-fresh }

Jede Maschine bekommt zwei Timer, die du in den Einstellungen ihres Stacks
konfigurierst. Der erste startet **jeden Tag** um `07:00` das VPN neu, wodurch
die Maschine eine neue Ausgangsadresse erhält. Der zweite ist ein
**wöchentliches Update** am Sonntag um 00:00 Uhr: Er führt `podman auto-update`
aus, sofern `auto_update: registry` gesetzt ist. Auch das Betriebssystem
aktualisiert sich selbst. Neu gestartet wird die Maschine dafür nur in dem
[Wartungsfenster, das du festgelegt hast](../server/machines.md#updates).

## Ein ganzes LAN im Mesh { #a-whole-lan-in-the-mesh }

Ein Router kann als WireGuard-Client der Gruppe `routers` am Mesh teilnehmen.
Alternativ schickt er den Verkehr für das Mesh-Subnetz über eine statische Route
an einen Gateway-Node. In beiden Fällen erreicht jedes Gerät im LAN dieses
Routers jeden Node, ohne dass darauf WireGuard laufen muss. Wie das geht, steht
unter [Router](routers.md).
