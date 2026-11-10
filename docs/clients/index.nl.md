# Werken met veel klantnetwerken

Tien klanten op afstand betekent vaak tien VPN's of SOCKS-eindpunten, één om het
netwerk van elke klant te bereiken. Ze allemaal op de host draaien is een
rommeltje: tien tunnels tegelijk, routes die met elkaar vechten, en het ene
netwerk dat in het volgende lekt. De Kiwi-desktopapps geven ieder in plaats
daarvan een **verzegelde exit**: een container waarvan de enige route die ene
upstream is. Je tools sluiten aan op de exit die ze nodig hebben, en verder
verandert er niets op de host.

| App | Wat het doet |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | De motor. Een **exit** is één upstream met een naam: een SOCKS5 die je hebt gekregen, of een die een providermodule maakt. Als je hem opstart, ontstaat er een **gateway**, een netwerknamespace waarvan de enige route die upstream is. Apps op de host kunnen hem als lokale SOCKS5-poort gebruiken |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distroboxen op een exit**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky of Alpine in een rootless container met een eigen homemap. *Alles* in de box vertrekt via de exit: pakketbeheerders, games, statische binary's die nooit van een proxy hebben gehoord |
| [**kiwi-fox**](kiwi-fox.md) | **Browserprofielen op een exit**: Camoufox, Firefox of Tor Browser, elk profiel met eigen opslag |
| [**Providermodules**](providers.md) | Exits via Tor, een VPN (gluetun), 9proxy of Mysterium. Tor en Mysterium zijn de snelle weg naar meer exit-IP's, handig om te testen |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Hoe het schoon blijft { #how-it-stays-clean }

- **Fail-closed.** De firewall van een gateway laat alles vallen behalve die ene
  upstream. Als de gateway uitvalt, verliest alles wat erop aangesloten was zijn
  route. De killswitch is het ontbreken van een route, geen software die iets
  moet opmerken.
- **Er draait niets wat niet gebruikt wordt.** Een gateway die een box of browser
  heeft opgestart, verdwijnt wanneer de laatste vertrekt. Alleen exits die je met
  `kiwi-proxy up` start, blijven draaien.
- **Gescheiden blijft gescheiden.** Wat op dezelfde exit zit, deelt die (één IP,
  één namespace). Klanten die elkaar niet mogen tegenkomen, krijgen verschillende
  exits, en elke box heeft een eigen homemap, dus SSH-sleutels en browserprofielen
  lopen niet door elkaar.
- **Geen root, geen hostroutes.** Alles draait in rootless Podman, en het eigen
  netwerk van de host blijft onaangeroerd.
- **Ook DNS gaat via de exit.** Standaard worden namen via DoH door de exit
  opgezocht, met lijsten voor advertentieblokkering. Voor de **interne
  hostnamen** van een klant geef je de namen in plaats daarvan door aan de kant
  van de klant met `--dns remote` (ook de modus voor Tor en `.onion`-namen).

## Beperkingen { #limits }

Deze komen uit de repository's:

- **Alleen TCP, alleen IPv4.** UDP kan nergens heen (geen QUIC, geen
  WebRTC-media), en IPv6 krijgt geen route.
- **Eén VPN-configuratie per machine.** De VPN-providermodule bevat één
  gluetun-configuratie (één `vpn.json`, één eigen WireGuard-configuratie), en de
  exits ervan verschillen alleen in serverland. Voor de eigen VPN's van meerdere
  klanten naast elkaar is vandaag een SOCKS5-eindpunt per klant de weg.
- **Een box is netwerkbewaring, geen sandbox.** Hij deelt je beeldscherm,
  sessiebus en klembord, net als distrobox. Wat hij niet kan, is het netwerk
  bereiken anders dan via zijn exit.
- **Mysterium:** één identiteit heeft één verbinding tegelijk.

## Aan de slag { #get-started }

```bash
kiwi install kiwi-custodia            # neemt kiwi-proxy mee
kiwi-custodia setup                   # images en DNS-gegevens

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # een shell waarvan de enige weg naar buiten de SOCKS5 van klant A is
```
