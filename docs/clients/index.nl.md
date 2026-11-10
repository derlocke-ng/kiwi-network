# Werken in veel klantnetwerken

Werk je op afstand voor veel klanten, dan heb je meestal voor het netwerk van
elke klant een aparte VPN- of SOCKS-verbinding nodig. Tien klanten betekenen dan
tien verbindingen. Als ze allemaal op de host draaien, gaat dat mis: er staan
tien tunnels tegelijk open, hun routes zitten elkaar in de weg, en verkeer voor
het netwerk van de ene klant kan in dat van een andere terechtkomen.

Met de desktop-apps van Kiwi werk je in het netwerk van elke klant afgeschermd
van de rest. De host raakt niet vol met tunnels en routes, en er draaien geen
tien VPN-verbindingen tegelijk. Elke verbinding krijgt een eigen container, en
de enige route uit die container leidt naar die ene klant. Zo’n verbinding heet
een **exit**. Je programma’s draaien in een container of een browserprofiel dat
de exit gebruikt die ze nodig hebben, en verder verandert er niets op de host.

| App | Wat het doet |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | De basis waarop de andere apps bouwen. Een **exit** is een opgeslagen verbinding naar een upstream, met een eigen naam. De upstream is de proxy waar je verkeer naartoe wordt gestuurd: een SOCKS5-proxy die je van de klant hebt gekregen, of een die een providermodule aanmaakt. Start je een exit, dan maakt kiwi-proxy er een **gateway** voor aan. Een gateway is een netwerk-namespace (een eigen set netwerkinterfaces, adressen en routes, met een eigen firewall) waarvan de enige route naar die upstream leidt. Programma’s op de host kunnen een exit gebruiken via een lokale SOCKS5-poort |
| [**kiwi-custodia**](kiwi-custodia.md) | **Linux-distributies in boxen die een exit gebruiken.** Een box is een rootless container (een container die zonder rootrechten draait) met Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky of Alpine en een eigen thuismap. *Al* het netwerkverkeer van de box gaat via de exit. Dat geldt ook voor pakketbeheerders, games en statisch gelinkte programma’s die proxy-instellingen negeren |
| [**kiwi-fox**](kiwi-fox.md) | **Browserprofielen die een exit gebruiken.** Elk profiel draait Camoufox, Firefox of Tor Browser en heeft een eigen opslag |
| [**Providermodules**](providers.md) | Modules die exits aanmaken via Tor, een VPN (met gluetun), 9proxy of Mysterium. Met Tor en Mysterium kom je snel aan extra IP-adressen, wat handig is om te testen |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Hoe de exits gescheiden blijven { #how-it-stays-clean }

- **Een gateway is fail-closed.** Bij een storing valt de verbinding weg, en er
  gaat nooit een andere weg open. De firewall in een gateway gooit alles weg wat
  niet naar de ene upstream van de gateway gaat. Valt de gateway uit, dan heeft
  alles wat eraan hangt geen verbinding meer. Geen enkel programma hoeft de
  storing op te merken en erop te reageren, want zonder gateway is er gewoon
  geen route.
- **Alleen wat je gebruikt, draait.** Start een box of een browser een gateway,
  dan wordt die gateway weer opgeruimd zodra de laatste box of browser die hem
  gebruikt, is gestopt. Alleen exits die je zelf met `kiwi-proxy up` start,
  blijven draaien.
- **Klanten blijven gescheiden.** Boxen en browsers op dezelfde exit delen die
  exit, dus ze hebben hetzelfde IP-adres en dezelfde netwerk-namespace. Klanten
  die elkaar niet mogen zien, krijgen verschillende exits. Elke box heeft
  bovendien een eigen thuismap, dus de SSH-sleutels en browserprofielen van de
  ene klant zijn niet beschikbaar in de box van een andere klant.
- **Geen rootrechten en geen routes op de host.** Alles draait in rootless
  Podman, dat containers als je eigen gebruiker draait. Aan het netwerk van de
  host zelf verandert niets.
- **Ook DNS-verzoeken gaan via de exit.** Standaard worden namen opgezocht met
  DNS over HTTPS (DoH) via de exit, en lijsten met reclamedomeinen worden
  geblokkeerd. Wil je de **interne hostnamen** van een klant opzoeken, gebruik
  dan `--dns remote`. De namen worden dan doorgegeven aan de kant van de klant
  en daar opgezocht. Tor en `.onion`-namen hebben deze modus ook nodig.

## Grenzen { #limits }

Deze grenzen staan in de repository’s zelf:

- **Alleen TCP en alleen IPv4.** UDP wordt niet doorgestuurd, dus QUIC en media
  via WebRTC werken niet. Voor IPv6 is er geen route.
- **Eén VPN-configuratie per machine.** De providermodule voor VPN heeft één
  gluetun-configuratie, met één `vpn.json` en één eigen WireGuard-configuratie.
  De exits ervan verschillen alleen in het land van de server. Heb je de eigen
  VPN’s van meerdere klanten tegelijk nodig, dan doe je dat op dit moment
  met een SOCKS5-eindpunt per klant.
- **Een box beperkt het netwerk, maar is geen sandbox.** Net als een
  distrobox-container deelt hij je scherm, je sessiebus en je klembord. Wat hij
  niet kan, is het netwerk op een andere manier bereiken dan via zijn exit.
- **Mysterium:** één identiteit kan maar één verbinding tegelijk hebben.

## Aan de slag { #get-started }

De volgende commando’s installeren de apps, slaan de SOCKS5-proxy van één klant
op als exit, en openen een shell in een Fedora-box die deze exit gebruikt:

```bash
kiwi install kiwi-custodia            # neemt kiwi-proxy mee
kiwi-custodia setup                   # images en DNS-gegevens

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # een shell die alleen via de SOCKS5 van klant A naar buiten kan
```
