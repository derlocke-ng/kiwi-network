# kiwi-custodia

kiwi-custodia geeft je een aparte Linux-omgeving voor elk klantnetwerk waarin
je werkt. Elke omgeving is een container met een Linux-distributie naar keuze,
en al het netwerkverkeer ervan gaat via één exit van
[kiwi-proxy](kiwi-proxy.md). Een exit is een opgeslagen verbinding naar een
upstream, met een eigen naam, bijvoorbeeld de SOCKS5-proxy die naar het netwerk
van één klant leidt. Zo kun je voor tien klanten werken zonder tien
VPN-verbindingen op de host, en blijven de tools en sleutels van elke klant in
de omgeving van die klant. *Ken je distrobox, dan is dit hetzelfde idee, maar
kan de container het netwerk alleen via zijn exit bereiken.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Nieuwste release: **v0.2.3**. Staat in de [Kiwi-catalogus](../desktop/catalogs.md), scope user.
- kiwi-custodia heeft een opdrachtregeltool (`kiwi-custodia`) en een GTK4-app (**Kiwi Custodia**).

Een **box** is één Linux-distributie in een rootless Podman-container, dus een
container die zonder rootrechten als je eigen gebruiker draait. De box heeft een
eigen thuismap en is aangesloten op de gateway van een exit. De gateway is de
container die kiwi-proxy voor een exit start, en de enige route daaruit leidt
naar de upstream van de exit. In de box kun je alles installeren met de
pakketbeheerder van de distributie. De desktop-apps uit de box openen op je
eigen desktop, en je kunt ze aan het overzicht van apps toevoegen. De box heeft
geen andere route dan de exit. Dat geldt voor elk programma erin: voor `dnf`,
voor een gameclient en voor een statisch gelinkt programma dat `$ALL_PROXY`
negeert. Stopt de exit, dan heeft de box helemaal geen route meer.

Daarom is één box per klantnetwerk een goede manier van werken. De tools,
sleutels en shellgeschiedenis van klant A staan in de ene box en die van klant
B in een andere, en elke box bereikt alleen zijn eigen klant.

## Installeren { #install }

```bash
kiwi install kiwi-custodia   # neemt kiwi-proxy mee; of ./install.sh install
kiwi-custodia setup          # het tunnel-image, plus het gateway-image en de DNS-gegevens van kiwi-proxy
```

kiwi-custodia heeft rootless Podman met `catatonit` nodig, kiwi-proxy, een
Wayland-sessie en Python 3.12+ met pydantic. De app heeft GTK4 en libadwaita
nodig. Rootless containers moeten bovendien `/dev/net/tun` kunnen gebruiken. De
images van de distributies worden niet tijdens de setup gedownload, maar pas
wanneer een box die zo’n image gebruikt voor het eerst start. Voer na een update
opnieuw `kiwi-custodia setup` uit.

## Gebruiken { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # een exit, één keer vastgelegd, in kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # een box erop; de eerste start installeert een basis
kiwi-custodia enter work                                   # een shell erin: sudo dnf install …
kiwi-custodia run work -- firefox                          # één commando erin
kiwi-custodia check work                                   # wat de buitenwereld van binnenuit ziet
kiwi-custodia apps work                                    # de desktop-apps die erin zitten
kiwi-custodia export work firefox                          # "Firefox (work)" in het overzicht van apps
kiwi-custodia stop work
kiwi-custodia reset work                                   # terug naar het basisimage; de thuismap blijft
kiwi-custodia-gui
```

De beschikbare distributies zijn `fedora` (de standaard), `fedora-toolbox`,
`ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`,
`arch-toolbox`, `opensuse`, `rocky` en `alpine`. Je kunt ook `custom` kiezen en
met `--image` zelf een image opgeven.

## Hoe een box is opgebouwd { #how-a-box-is-built }

Een draaiende box bestaat uit drie containers die één netwerk-namespace delen:
ze hebben dezelfde netwerkinterfaces, routes en firewallregels. De eerste is de
**gateway** van kiwi-proxy. De tweede is een **tunnel-sidecar**, een
hulpcontainer die tun2socks draait op een TUN-apparaat. Een TUN-apparaat is een
virtuele netwerkinterface, en hier wordt het de standaardroute. De derde
container is de **box** zelf. Al het verkeer uit de box gaat het TUN-apparaat in
en van daar naar de SOCKS5-proxy van de exit. Dat loopt via de standaardroute
en niet via proxy-instellingen, dus ook programma’s die proxy-instellingen
negeren, vallen eronder.

- De box draait als jouw gebruiker, met dezelfde uid, en `sudo` werkt erin
  zonder wachtwoord. De thuismap is
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Elke box heeft een eigen
  thuismap en gebruikt niet je echte, dus twee boxen zijn twee aparte
  identiteiten.
- Stopt een box, dan worden de wijzigingen die erin zijn gemaakt bewaard in een
  snapshot die bij deze box hoort. `reset` zet de box terug naar het
  basisimage.
- Wayland, X11 (via Xwayland), PipeWire, de sessiebus en `/dev/dri` zijn in de
  box beschikbaar, zodat desktop-apps en games werken.
- DNS-verzoeken worden beantwoord door de resolver van de gateway, die ook
  reclamedomeinen blokkeert. Bij een exit met remote DNS zoekt de upstream de
  namen op.

## Wat het niet is { #what-it-is-not }

Een box **beperkt het netwerk. Het is geen sandbox die je desktop beschermt
tegen de programma’s erin.** Net als een distrobox-container krijgt de box
toegang tot je scherm en je sessiebus. Een programma in de box kan dus vensters
tonen, het klembord lezen en de desktopportalen gebruiken. Wat het niet kan, is
het netwerk op een andere manier bereiken dan via zijn exit. UDP wordt niet
doorgestuurd, dus QUIC en media via WebRTC werken niet, en voor IPv6 is er geen
route.

Boxen op dezelfde exit delen die exit. Boxen die van elkaar gescheiden moeten
blijven, hebben verschillende exits nodig.
