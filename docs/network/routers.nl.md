# Routers: een heel LAN in de mesh

Op deze pagina lees je hoe je een heel lokaal netwerk (LAN), bijvoorbeeld je
thuis- of kantoornetwerk, via de router met je Kiwi Network verbindt. Een
apparaat in de mesh, het besloten WireGuard-netwerk waarin al je machines
zitten, kan elke naam in de fleet opzoeken en bij elke node. De apparaten in
een LAN achter een router kunnen dat ook, zonder dat op elk ervan WireGuard
hoeft te draaien. Dat regel je op een van deze twee manieren:

- **De router is een client in de mesh.** Op de router draait WireGuard met een
  configuratie die is uitgegeven door wg-easy, de WireGuard-server van de master
  (`kiwi-server enroll fleet.yaml router --group routers`). De router stuurt
  verkeer voor het mesh-subnet (`10.8.0.0/16`) de tunnel in. Dit heet een
  *split*-tunnel, omdat alleen verkeer voor de mesh erdoor gaat. Bij een
  *full*-tunnel gaat al het verkeer erdoor. Het hele LAN komt dan op internet
  via de uitgang van de master, de verbinding van de master met internet.
- **De router heeft een statische route naar een gateway-node.** De router
  heeft zelf geen tunnel. Hij stuurt verkeer voor het mesh-subnet naar een node
  in het LAN waarop de module `gateway` draait, en die node stuurt het verkeer
  via zijn VPN-client verder.

In beide gevallen heb je genoeg aan één DNS-regel en hoef je geen afzonderlijke
hosts in te voeren. De regel stuurt verzoeken voor het domein van de fleet
(`*.home`) door naar de Pi-hole van de master, die elke hostnaam en elke
dienstnaam kent. Verder verandert er niets aan de DNS van de router.

Eén ding werkt niet: een apparaat in het LAN kan een apparaat *achter een
andere router* niet bereiken op het LAN-adres van dat apparaat. Over de mesh
gaat alleen verkeer voor mesh-adressen, en dat is zo bedoeld.

## OpenWrt { #openwrt }

Voor OpenWrt schrijft kiwi-server de hele configuratie als een `uci`-script:

```bash
# de router als client in de mesh, met de configuratie die wg-easy op de master heeft uitgegeven
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: alleen de mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: alles

# geen tunnel op de router: een statische route naar de gateway-node lychee
# (lychee heeft in het fleetbestand een vast LAN-adres nodig: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Kopieer de uitvoer naar de router en voer het script daar uit:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Het script installeert het WireGuard-pakket als dat ontbreekt. Het maakt een
interface aan met de naam `kiwi`. Met `--name` kies je een andere naam. De
interface krijgt de `wg_mtu` van de fleet als MTU en heeft één peer, de master.
Die peer wordt aangemaakt met `route_allowed_ips`, zodat OpenWrt de routes zelf
toevoegt. Daarnaast maakt het script een firewallzone aan waar het LAN verkeer
naartoe mag doorsturen, met masquerading en MSS-clamping. Tot slot voegt het de
dnsmasq-regel toe die het domein van de fleet doorstuurt naar de master
(`server=/home/10.8.0.1`). Met `--full` stuurt dnsmasq elk DNS-verzoek naar de
Pi-hole van de master. Elke sectie die het script schrijft, heeft een naam.
Voer je het script opnieuw uit, dan vervangt het dus wat het eerder heeft
geschreven.

## FritzBox { #fritzbox }

Fritz!OS heeft een WireGuard-client en statische routes, maar kan
DNS-verzoeken voor één enkel domein niet doorsturen. De DNS-regel moet daarom
door een node worden afgehandeld:

1. **Tunnel:** ga naar Internet → Permit Access → VPN (WireGuard) → Add
   Connection, kies voor een verbinding met een andere WireGuard-dienst
   (connect to another WireGuard service) en importeer de configuratie die de master heeft
   uitgegeven. De regel `AllowedIPs` in die configuratie bepaalt of de tunnel
   split of full is.
2. **Of een statische route:** ga naar Home Network → Network → Network
   Settings → IPv4 Routes. Vul `10.8.0.0` in als doelnetwerk,
   `255.255.0.0` als subnetmasker en het LAN-adres van de gateway-node als
   gateway.
3. **DNS:** laat het LAN een Pi-hole als DNS-server gebruiken. Stel de
   gateway-node in als lokale DNS-server, of laat de Pi-hole van de node de
   DHCP-server van het LAN zijn (de instellingen `dns.dhcp_*` samen met de
   module dhcp-relay). De Pi-hole van de node kent de namen van de fleet en
   stuurt alle andere verzoeken door naar de master.

Je kunt de tunnel en statische routes tegelijk gebruiken. Verkeer voor de mesh
gaat dan door de tunnel.

## Elke andere router { #any-other-router }

Bij elke andere router heb je aan drie dingen genoeg. Geef de router een
WireGuard-clientconfiguratie, of voeg een statische route voor `10.8.0.0/16`
toe die naar het LAN-adres van de gateway-node wijst. Laat het LAN daarna als
DNS-server een Pi-hole gebruiken die de fleet kent. Elke node waarop de module
`dns` draait, is zo’n Pi-hole. Bij routers op basis van dnsmasq (DD-WRT, Tomato, de
forwarder in pfSense) volstaat ook één regel in de configuratie:
`server=/home/10.8.0.1`.
