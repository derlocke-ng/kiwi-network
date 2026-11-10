# Router: ein ganzes LAN im Mesh

Diese Seite zeigt, wie du ein ganzes lokales Netz (LAN), zum Beispiel dein Heim-
oder Büronetz, über seinen Router an dein Kiwi Network anbindest. Ein Gerät im
Mesh, also im privaten WireGuard-Netzwerk deiner Maschinen, kann jeden Namen der
Fleet auflösen und jeden Node erreichen. Die Geräte in einem LAN hinter einem
Router können das auch, ohne dass auf jedem von ihnen WireGuard laufen muss.
Dafür gibt es zwei Wege:

- **Der Router ist ein Client im Mesh.** Auf dem Router läuft WireGuard mit
  einer Konfiguration, die wg-easy, der WireGuard-Server des Masters,
  ausgestellt hat (`kiwi-server enroll fleet.yaml router --group routers`). Den
  Verkehr für das Mesh-Subnetz (`10.8.0.0/16`) schickt der Router in den Tunnel.
  Das nennt sich *Split*-Tunnel, weil nur der Verkehr für das Mesh durch den
  Tunnel läuft. Bei einem *Full*-Tunnel geht der gesamte Verkehr hindurch, und
  das ganze LAN gelangt über den Ausgang des Masters ins Internet, also über
  dessen Internetverbindung.
- **Der Router hat eine statische Route zu einem Gateway-Node.** Auf dem Router
  läuft kein Tunnel. Er schickt den Verkehr für das Mesh-Subnetz an einen Node
  im LAN, auf dem das Modul `gateway` läuft, und dieser Node leitet ihn über
  seinen VPN-Client weiter.

In beiden Fällen genügt eine einzige DNS-Regel, Einträge für einzelne Hosts
brauchst du nicht. Die Regel leitet Anfragen für die Fleet-Domain (`*.home`) an
das Pi-hole des Masters weiter, das jeden Host- und jeden Dienstnamen kennt.
Sonst ändert sich am DNS des Routers nichts.

Eines geht nicht: Ein Gerät im LAN kann ein Gerät *hinter einem anderen Router*
nicht über dessen LAN-Adresse erreichen. Das Mesh transportiert nur Verkehr für
Mesh-Adressen, und das ist so gewollt.

## OpenWrt { #openwrt }

Für OpenWrt schreibt kiwi-server die komplette Konfiguration als `uci`-Skript:

```bash
# der Router als Client im Mesh, mit der Konfiguration, die wg-easy auf dem Master ausgestellt hat
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: nur das Mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: alles

# kein Tunnel auf dem Router: eine statische Route zum Gateway-Node lychee
# (lychee braucht in der Fleet eine statische LAN-Adresse: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Kopiere die Ausgabe auf den Router und führe sie dort aus:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Das Skript installiert das WireGuard-Paket, falls es fehlt. Es legt eine
Schnittstelle namens `kiwi` an, den Namen kannst du mit `--name` ändern. Die
Schnittstelle übernimmt `wg_mtu` aus der Fleet als MTU und hat genau einen Peer,
den Master. Der Peer wird mit `route_allowed_ips` angelegt, sodass OpenWrt die
Routen selbst einträgt. Außerdem legt das Skript eine Firewall-Zone an, in die
das LAN weiterleiten darf, mit Masquerading und MSS-Clamping. Zum Schluss
ergänzt es die dnsmasq-Regel, die die Fleet-Domain an den Master weiterleitet
(`server=/home/10.8.0.1`). Mit `--full` schickt dnsmasq jede DNS-Anfrage an das
Pi-hole des Masters. Jeder Abschnitt, den das Skript schreibt, hat einen Namen.
Führst du das Skript noch einmal aus, ersetzt es deshalb, was es beim letzten
Mal geschrieben hat.

## FritzBox { #fritzbox }

Fritz!OS bringt einen WireGuard-Client und statische Routen mit, kann aber
DNS-Anfragen nicht für eine einzelne Domain weiterleiten. Die DNS-Regel muss
deshalb ein Node übernehmen:

1. **Tunnel:** Öffne Internet → Freigaben → VPN (WireGuard) → Verbindung
   hinzufügen, wähle die Verbindung zu einem anderen WireGuard-Dienst und
   importiere die Konfiguration, die der Master ausgestellt hat. Die Zeile
   `AllowedIPs` dieser Konfiguration entscheidet, ob der Tunnel split oder full
   ist.
2. **Oder eine statische Route:** Öffne Heimnetz → Netzwerk →
   Netzwerkeinstellungen → IPv4-Routen. Trage `10.8.0.0` als Ziel ein,
   `255.255.0.0` als Subnetzmaske und die LAN-Adresse des Gateway-Nodes als
   Gateway.
3. **DNS:** Sorge dafür, dass das LAN ein Pi-hole als DNS-Server nutzt. Trage
   dazu entweder den Gateway-Node als lokalen DNS-Server ein, oder mach das
   Pi-hole des Nodes zum DHCP-Server des LAN (mit den Einstellungen `dns.dhcp_*`
   und dem Modul dhcp-relay). Das Pi-hole des Nodes kennt die Namen der Fleet
   und leitet alle anderen Anfragen an den Master weiter.

Tunnel und statische Route kannst du gleichzeitig nutzen. Der Verkehr für das
Mesh läuft dann durch den Tunnel.

## Andere Router { #any-other-router }

Bei jedem anderen Router reichen drei Dinge. Gib dem Router entweder eine
WireGuard-Client-Konfiguration, oder richte eine statische Route für
`10.8.0.0/16` ein, die auf die LAN-Adresse des Gateway-Nodes zeigt. Sorge dann
dafür, dass das LAN als DNS-Server ein Pi-hole nutzt, das die Fleet kennt. Jeder
Node, auf dem das Modul `dns` läuft, hat so ein Pi-hole. Router, die auf dnsmasq
aufbauen (DD-WRT, Tomato, der Forwarder in pfSense), verstehen außerdem die
einzeilige Weiterleitungsregel `server=/home/10.8.0.1`.
