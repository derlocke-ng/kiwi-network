# So funktioniert das Netzwerk

Ein Kiwi Network ist ein **WireGuard-Mesh mit einem Hub**, dem *kiwi-master*. Jede
andere Maschine (Nodes zu Hause oder im Büro, Laptops, Telefone, Router) wählt sich
beim Master ein und trifft die anderen im Mesh. All das wird in einer einzigen
Fleet-Datei beschrieben und von [kiwi-server](../server/index.md) gebaut.

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

Die Rolle `master` betreibt fünf Module. Pi-hole, Tor und nginx leben im
Netzwerk-Namespace des WireGuard-Servers und kommen mit ihm zurück.

- **vpn-server** (wg-easy) ist der Einstiegspunkt für jeden Client und jeden Node
  und stellt deren WireGuard-Konfigurationen aus. kiwi-server kann sie für dich
  anlegen (`kiwi-server enroll`).
- **vpn-client** (gluetun) verbindet sich mit einem kommerziellen VPN-Anbieter: im
  Preset Mullvad, allgemein jeder Anbieter, den gluetun unterstützt. Die
  Standardroute des WireGuard-Servers zeigt darauf, sodass Verkehr aus dem Mesh über
  den Anbieter hinausgeht, nicht über die eigene Adresse des Masters. Das ist der
  **Double Hop**. Ein Master ohne vpn-client geht direkt hinaus.
- **dns** (Pi-hole 6) antwortet unter der Mesh-Adresse des Masters, `10.8.0.1`.
  Siehe [DNS, Namen & Zertifikate](dns.md).
- **tor** bietet Mesh-Clients SOCKS5 unter `10.8.0.1:9050`, mit Eingangs- und
  Ausgangs-Nodes, die auf eine Auswahl von Ländern festgelegt sind (Standard
  `de,ch,at,nl,fr`, `StrictNodes`).
- **reverse-proxy** (nginx) liefert die Admin-Seiten `wg.<master>` und
  `pihole.<master>` an Admin-Gruppen im Mesh aus.

Ein Master kann außerdem ein **nostr-Relay** und einen **Hub** für die
[Menschen in deinem Netzwerk](../people/hubs.md#on-a-kiwi-network) mitbringen,
dazu Portainer und Backups.

### Was aus dem Internet erreichbar ist { #what-is-reachable-from-the-internet }

Standardmäßig veröffentlicht der Master **einen Port**: WireGuard, UDP 51820. Die
Admin-Seiten antworten nur dem Mesh. Zwei Einstellungen fügen mehr hinzu:

- `reverse-proxy.public: true` veröffentlicht 80 und 443, mit Zertifikaten von Let's
  Encrypt für Namen außerhalb der Domain der Fleet. Alles andere antwortet weiterhin
  nur dem Mesh, und Admin-Seiten antworten von außen mit 403. Das ist für einen
  öffentlichen Hub oder ein öffentliches Relay gedacht.
- `vpn-server.unlock_relay` öffnet die TCP-Ports von
  [Tang-Ringen](../server/operations.md#encrypted-disks-and-unlocking) für Maschinen
  hinter NAT.

SSH bleibt so, wie das Betriebssystem es eingerichtet hat (standardmäßig nur
Schlüssel). kiwi-server benutzt es für `apply` und `status`.

## Client-Gruppen { #client-groups }

Die Clients von wg-easy werden nach Adresse in **Gruppen** sortiert. Jede Gruppe
entscheidet, was ihre Mitglieder erreichen können:

| Gruppe | Subnetz | Erreicht | Sieht andere Clients | Admin-Seiten |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | die Nodes | nein | nein |
| `pentest` | `10.8.2.0/24` | nichts im Mesh | nein | nein |
| `devices` | `10.8.3.0/24` | alles | ja | ja |
| `routers` | `10.8.4.0/24` | alles | ja | nein |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # ein QR-Code für die WireGuard-App
kiwi-server enroll fleet.yaml anna  --group guests --split # nur das Mesh geht durch den Tunnel
```

Jede Gruppe darf über den Ausgang ins Internet, außer du setzt `internet: false`.
Clients außerhalb jeder Gruppe (`10.8.0.x`) sind das einfache Mesh: Sie erreichen
alles und sehen die Admin-Seiten, solange `admin_from_mesh` eingeschaltet ist.
Gruppen sind eine Einstellung des Moduls vpn-server (`groups`), du kannst sie also
ändern oder eigene hinzufügen (`reach` nimmt `all`, `nodes`, Hostnamen, Adressen
oder Subnetze). Das alte einzelne `isolated_subnet` gibt es noch, aber es ist
standardmäßig aus.

## Nodes { #nodes }

Der vpn-client eines Nodes spricht nicht mit einem kommerziellen VPN. Er benutzt die
WireGuard-Konfiguration, die der Master für ihn ausgestellt hat (`kiwi-server enroll`
schreibt `secrets/<hostname>.conf`, und der Node holt sie sich von selbst). Ein Node
braucht keinen offenen Port im Internet: Er wählt sich beim Master ein und
funktioniert deshalb hinter dem NAT eines Heimrouters.

Die Rolle `node` hat drei Presets:

| Preset | Was aus der Maschine wird |
|---|---|
| `gateway` (Standard) | Ein LAN-Gateway. LAN-Clients, die es als Standard-Gateway benutzen, gehen über das VPN hinaus und können das Mesh erreichen. Pi-hole bedient das LAN (optional als dessen DHCP-Server). Transmission und JDownloader laufen *im* Netzwerk-Namespace des VPN-Clients, sodass sie überhaupt keine Route haben, wenn der Tunnel unten ist. Mit nginx, Portainer und SFTP. |
| `cloud` | Nextcloud (aus den Containern des AIO-Projekts, ohne den AIO-Master-Container) mit Collabora, dazu Vaultwarden, hinter nginx, dazu Portainer |
| `minimal` | Nur der VPN-Client und nginx, für Module deiner Wahl |

Nodes können außerdem Backups, einen Backup-Server, Tang und (zum Ausprobieren)
OpenCloud, Immich und Paperless-ngx betreiben. Siehe die
[Modulliste](../server/modules.md).

Dienste auf einem Node sind in seinem LAN und unter seiner **Mesh-Adresse**
erreichbar (z. B. `10.8.0.25`). Mesh-Verkehr an diese Adresse auf 80 und 443 wird an
den Reverse Proxy weitergeleitet.

## Namen { #names }

Maschinen werden nach dem Obstgarten benannt: **Master nach Obstgerichten**
(`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`, `cider`)
und **Nodes nach Früchten** (`papaya`, `lychee`, `guava`, `quince`, `damson`), sodass
die Art einer Maschine in jeder Logzeile lesbar ist. Das ist eine Konvention, und
jeder Name funktioniert. Dienste liegen unter ihrem Host: `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. Siehe [DNS, Namen & Zertifikate](dns.md).

## Wege hinaus { #ways-out }

Ein Master ist ein WireGuard-Server mit einem Ausgang, und der Ausgang hat drei Modi:

| Modus | Wie das Mesh das Internet erreicht | Status |
|---|---|---|
| **provider** | über ein kommerzielles VPN (gluetun): der Double Hop, und das Preset des Masters | gebaut |
| **direct** | direkt über die eigene Anbindung des Masters. Liste die Module des Masters ohne `vpn-client` auf | gebaut |
| **master** | über *den Master eines anderen Netzwerks*, als Client in einer seiner Gruppen, der das Internet erreichen darf und sonst nichts: Multi-Hop | entworfen; es braucht Aufnahme über Netzwerke hinweg, also Föderation |

Jeder Master bietet dem Mesh außerdem den SOCKS5 von Tor an, unabhängig von seinem
Ausgang.

## Ein Mesh pro Netzwerk { #one-mesh-per-network }

Jedes Netzwerk hat sein eigenes Mesh. Der Standard ist `10.8.0.0/16`: Master und
Nodes in `10.8.0.0/24`, dann Gäste `.1`, Pentest `.2`, Geräte `.3` und Router `.4`.
Ein zweites Netzwerk nimmt einen anderen Bereich, zum Beispiel `10.9.0.0/16`, damit
ein Gerät, das in beiden ist, sie auseinanderhalten kann. Heute ist der Bereich über
mehrere Einstellungen verteilt (`mesh_subnet`, `server_ip`, `wg_subnet`,
`wg_default_address` und `groups` des vpn-server und `socks_policy_accept` von Tor),
und die Fleet-Datei setzt sie alle.

## Adressierung { #addressing }

| Was | Standard |
|---|---|
| Das ganze Mesh (auf jedem Host geroutet) | standardmäßig `10.8.0.0/16` (`mesh_subnet`) |
| wg-easy-Clients | `10.8.0.0/24`; der Server ist `10.8.0.1` |
| Client-Gruppen | `10.8.1.0/24` … `10.8.4.0/24` |
| Stack-Netzwerk | `172.64.0.0/24` auf einem Master, `172.128.0.0/24` auf einem Node |
| WireGuard-MTU | `1376` (`wg_mtu`), gemessen mit [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU der Stack-Bridge | `1500` (`bridge_mtu`) |

Jeder Stack-Host routet das Mesh über seinen VPN-Client (auf dem Master über den
WireGuard-Server), sodass der Host und seine Container jeden Node erreichen.

## Frisch halten { #keeping-it-fresh }

Jede Maschine bekommt aus ihren Stack-Einstellungen zwei Timer: einen **täglichen
VPN-Neustart** (`07:00`, für eine frische Ausgangsadresse) und ein **wöchentliches
Update** (Sonntag 00:00, das `podman auto-update` ausführt, solange
`auto_update: registry` gesetzt ist). Das Betriebssystem aktualisiert sich selbst und
startet nur in [deinem Zeitfenster](../server/machines.md#updates) neu.

## Ein ganzes LAN im Mesh { #a-whole-lan-in-the-mesh }

Ein Router kann dem Mesh als WireGuard-Client in der Gruppe `routers` beitreten oder
das Mesh-Subnetz mit einer statischen Route an einen Gateway-Node schicken. Dann
erreicht jedes Gerät in diesem LAN jeden Node, ohne WireGuard zu betreiben. Siehe
[Router](routers.md).
