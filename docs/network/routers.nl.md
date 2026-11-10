# Routers: een heel LAN in de mesh

Een apparaat in de mesh kan elke fleet-naam opzoeken en elke node bereiken. Een
LAN achter een router kan hetzelfde zonder dat elk apparaat WireGuard draait, op
een van twee manieren:

- **De router is een mesh-client.** Hij draait WireGuard met een configuratie
  die wg-easy op de master heeft uitgegeven (`kiwi-server enroll fleet.yaml router --group routers`)
  en routeert het mesh-subnet (`10.8.0.0/16`) de tunnel in.
  Dat is de *split*-tunnel: alleen mesh-verkeer gaat erdoorheen. De *full*-tunnel
  stuurt alles, zodat het hele LAN het internet bereikt via de exit van de
  master.
- **Een statische route naar een gateway-node.** De router heeft geen tunnel. Hij
  stuurt het mesh-subnet naar een node op het LAN die de module `gateway` draait,
  en die stuurt het door via zijn VPN-client.

Hoe dan ook vervangt één DNS-regel de overrides per host: het domein van de fleet
(`*.home`) wordt doorgestuurd naar de Pi-hole van de master, die elke host- en
dienstnaam kent. Verder verandert er niets aan de DNS van de router.

Wat het LAN niet kan, is een apparaat *achter een andere router* bereiken via
zijn LAN-adres. De mesh vervoert alleen mesh-adressen, en dat is zo bedoeld.

## OpenWrt { #openwrt }

kiwi-server schrijft de hele configuratie als een `uci`-script:

```bash
# de router als mesh-client, met de configuratie die wg-easy op de master heeft uitgegeven
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: alleen de mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: alles

# geen tunnel op de router: een statische route naar de gateway-node lychee
# (lychee heeft een statisch LAN-adres nodig in de fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Kopieer de uitvoer naar de router en voer die uit:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Het script installeert het WireGuard-pakket als dat ontbreekt. Het maakt een
interface `kiwi` aan (wijzig de naam met `--name`), met de `wg_mtu` van de fleet
als MTU en één peer voor de master
en `route_allowed_ips`, een firewallzone waarin het LAN mag doorsturen (met
masquerading en MSS-clamping), en de dnsmasq-doorverwijzing voor het domein van
de fleet (`server=/home/10.8.0.1`). Met `--full` stuurt dnsmasq elke opzoeking
naar de Pi-hole van de master. Elke sectie heeft een naam, dus als je het script
opnieuw draait, vervangt het wat het eerder schreef.

## FritzBox { #fritzbox }

Fritz!OS heeft een WireGuard-client en statische routes, maar geen DNS-doorverwijzing
per domein, dus de DNS-regel verhuist naar een node:

1. **Tunnel:** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   verbinden met een andere WireGuard-dienst → importeer de configuratie die de
   master heeft uitgegeven. De `AllowedIPs` daarin bepalen split of full.
2. **Of een statische route:** Home Network → Network → Network Settings → IPv4
   Routes. Bestemming `10.8.0.0`, subnetmasker `255.255.0.0`, gateway het
   LAN-adres van de gateway-node.
3. **DNS:** laat het LAN naar een Pi-hole wijzen. Stel de gateway-node in als
   lokale DNS-server, of laat de Pi-hole van de node de DHCP-server van het LAN
   zijn (instellingen `dns.dhcp_*` plus de module dhcp-relay). De Pi-hole van de
   node kent de namen van de fleet en stuurt de rest door naar de master.

De tunnel en statische routes kunnen naast elkaar bestaan. Voor de mesh wint de
tunnel.

## Elke andere router { #any-other-router }

Drie feiten zijn genoeg. Geef de router een WireGuard-clientconfiguratie, of voeg
een statische route voor `10.8.0.0/16` toe naar het LAN-adres van de gateway-node.
Laat daarna de DNS van het LAN wijzen naar een Pi-hole die de fleet kent, en dat
is elke node die de module `dns` draait. Routers met dnsmasq eronder (DD-WRT,
Tomato, de forwarder van pfSense) accepteren ook de doorverwijzing van één regel
`server=/home/10.8.0.1`.
