# Router: ein ganzes LAN im Mesh

Ein Gerät im Mesh löst jeden Namen der Fleet auf und erreicht jeden Node. Ein LAN
hinter einem Router kann dasselbe, ohne dass auf jedem Gerät WireGuard läuft, auf
eine von zwei Arten:

- **Der Router ist ein Mesh-Client.** Er betreibt WireGuard mit einer Konfiguration,
  die das wg-easy des Masters ausgestellt hat
  (`kiwi-server enroll fleet.yaml router --group routers`), und routet das
  Mesh-Subnetz (`10.8.0.0/16`) in den Tunnel.
  Das ist der *Split*-Tunnel: Nur Mesh-Verkehr geht hindurch. Der *Full*-Tunnel
  schickt alles, sodass das ganze LAN das Internet über den Ausgang des Masters
  erreicht.
- **Eine statische Route zu einem Gateway-Node.** Der Router hat keinen Tunnel. Er
  schickt das Mesh-Subnetz an einen Node im LAN, auf dem das Modul `gateway` läuft,
  und der leitet es über seinen VPN-Client weiter.

So oder so ersetzt eine DNS-Regel die Überschreibungen pro Host: Die Domain der
Fleet (`*.home`) wird an das Pi-hole des Masters weitergeleitet, das jeden Host- und
Dienstnamen kennt. Sonst ändert sich am DNS des Routers nichts.

Was das LAN nicht kann, ist, ein Gerät *hinter einem anderen Router* über dessen
LAN-Adresse zu erreichen. Das Mesh transportiert nur Mesh-Adressen, mit Absicht.

## OpenWrt { #openwrt }

kiwi-server schreibt die ganze Konfiguration als `uci`-Skript:

```bash
# der Router als Mesh-Client, mit der Konfiguration, die das wg-easy des Masters ausgestellt hat
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: nur das Mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: alles

# kein Tunnel auf dem Router: eine statische Route zum Gateway-Node lychee
# (lychee braucht in der Fleet eine statische LAN-Adresse: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Kopiere die Ausgabe auf den Router und führe sie aus:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Das Skript installiert das WireGuard-Paket, falls es fehlt. Es legt eine
Schnittstelle `kiwi` an (den Namen änderst du mit `--name`), mit dem `wg_mtu` der
Fleet als MTU und einem Peer für den Master und `route_allowed_ips`, eine
Firewall-Zone, in die das LAN weiterleiten darf (mit Masquerading und MSS-Clamping),
und die dnsmasq-Weiterleitung für die Domain der Fleet (`server=/home/10.8.0.1`).
Mit `--full` schickt dnsmasq jede Anfrage an das Pi-hole des Masters. Jeder
Abschnitt hat einen Namen, sodass ein erneuter Lauf des Skripts ersetzt, was es
vorher geschrieben hat.

## FritzBox { #fritzbox }

Fritz!OS hat einen WireGuard-Client und statische Routen, aber keine
DNS-Weiterleitung pro Domain, also wandert die DNS-Regel auf einen Node:

1. **Tunnel:** Internet → Freigaben → VPN (WireGuard) → Verbindung hinzufügen →
   mit einem anderen WireGuard-Dienst verbinden → die Konfiguration importieren,
   die der Master ausgestellt hat. Ihre `AllowedIPs` entscheiden über Split oder
   Full.
2. **Oder eine statische Route:** Heimnetz → Netzwerk → Netzwerkeinstellungen →
   IPv4-Routen. Ziel `10.8.0.0`, Subnetzmaske `255.255.0.0`, Gateway die
   LAN-Adresse des Gateway-Nodes.
3. **DNS:** Lass das LAN auf ein Pi-hole zeigen. Setz entweder den Gateway-Node als
   lokalen DNS-Server, oder lass das Pi-hole des Nodes den DHCP-Server des LANs sein
   (Einstellungen `dns.dhcp_*` plus das Modul dhcp-relay). Das Pi-hole des Nodes
   kennt die Namen der Fleet und leitet den Rest an den Master weiter.

Der Tunnel und statische Routen können nebeneinander bestehen. Für das Mesh gewinnt
der Tunnel.

## Jeder andere Router { #any-other-router }

Drei Fakten reichen. Gib dem Router entweder eine WireGuard-Client-Konfiguration,
oder füge eine statische Route für `10.8.0.0/16` zur LAN-Adresse des Gateway-Nodes
hinzu. Dann lass das DNS des LANs auf ein Pi-hole zeigen, das die Fleet kennt, also
auf jeden Node, auf dem das Modul `dns` läuft. Router mit dnsmasq darunter (DD-WRT,
Tomato, der Forwarder von pfSense) nehmen auch die einzeilige Weiterleitung
`server=/home/10.8.0.1`.
