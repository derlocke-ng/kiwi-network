# kiwi-custodia

Distro-containers waarvan elke byte via een [kiwi-proxy](kiwi-proxy.md)-exit
vertrekt. *Zie het als distrobox, met het netwerk in bewaring.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Nieuwste release: **v0.2.3**. Het staat in de [Kiwi-catalogus](../desktop/catalogs.md), gebruikersscope.
- Een CLI (`kiwi-custodia`) en een GTK4-app (**Kiwi Custodia**)

Een **box** is één Linux-distributie in een rootless Podman-container, met een
eigen homemap, gekoppeld aan de verzegelde gateway van een exit. Installeer er
wat je wilt in met de pakketbeheerder, draai de desktopapps ervan op je desktop,
en zet ze in het app-overzicht. De box heeft geen andere route dan de exit:
niet voor `dnf`, niet voor een gameclient, niet voor een statische binary die
nooit van `$ALL_PROXY` heeft gehoord. Als de exit wegvalt, heeft de box
helemaal geen route.

Dat maakt een box per klantnetwerk tot een schone manier van werken: de tools,
sleutels en shellgeschiedenis van klant A in één box, die van klant B in een
andere, en elk bereikt alleen de eigen klant.

## Installeren { #install }

```bash
kiwi install kiwi-custodia   # neemt kiwi-proxy mee; of ./install.sh install
kiwi-custodia setup          # de tunnel-image, plus de gateway-image en DNS-gegevens van kiwi-proxy
```

Het vereist rootless Podman met `catatonit`, kiwi-proxy, een Wayland-sessie,
Python 3.12+ met pydantic, GTK4 + libadwaita voor de app, en `/dev/net/tun`
bruikbaar voor rootless containers. Distro-images worden binnengehaald wanneer
een box voor het eerst start. Voer `kiwi-custodia setup` opnieuw uit na een
update.

## Gebruik { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # een exit, één keer gedefinieerd, in kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # een box erop; de eerste start installeert een basis
kiwi-custodia enter work                                   # een shell erin: sudo dnf install …
kiwi-custodia run work -- firefox                          # één commando erin
kiwi-custodia check work                                   # wat de wereld van binnenuit ziet
kiwi-custodia apps work                                    # de desktopapps die erin zitten
kiwi-custodia export work firefox                          # "Firefox (work)" in het app-overzicht
kiwi-custodia stop work
kiwi-custodia reset work                                   # terug naar de basisimage; de homemap blijft
kiwi-custodia-gui
```

Distributies: `fedora` (de standaard), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine`, of `custom` met `--image`.

## Hoe een box is opgebouwd { #how-a-box-is-built }

Drie containers delen één netwerknamespace: de **gateway** van kiwi-proxy, een
**tunnel-sidecar** (tun2socks op een TUN-apparaat dat de standaardroute wordt),
en de **box** zelf. Al het verkeer vertrekt via de TUN naar de SOCKS5 van de
exit, dus programma's die proxy-instellingen negeren vallen er ook onder.

- De box draait als jouw gebruiker, met dezelfde uid en `sudo` zonder wachtwoord.
  De homemap is `~/.local/share/kiwi-custodia/boxes/<id>/home`, één per box in
  plaats van je echte homemap: twee boxen zijn twee identiteiten.
- Wijzigingen binnen een box worden bij het stoppen bewaard in een snapshot per
  box, en `reset` keert terug naar de basisimage.
- Wayland, X11 (via Xwayland), PipeWire, de sessiebus en `/dev/dri` worden
  doorgegeven, dus desktopapps en games werken.
- DNS gaat via de resolver van de gateway (met advertentieblokkering), of via de
  upstream bij een exit met remote DNS.

## Wat het niet is { #what-it-is-not }

Een box is **netwerkbewaring, geen sandbox tegenover je desktop**. Net als
distrobox krijgt hij je beeldscherm en sessiebus, dus een programma in de box kan
vensters tonen, het klembord lezen en de portals gebruiken. Wat het niet kan, is
het netwerk bereiken anders dan via zijn exit. UDP kan nergens heen (geen
QUIC, geen WebRTC-media), en IPv6 heeft geen route.

Boxen die geen exit mogen delen, nemen verschillende exits.
