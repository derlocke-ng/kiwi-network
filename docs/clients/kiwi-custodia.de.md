# kiwi-custodia

Distro-Container, deren jedes Byte über einen Ausgang von
[kiwi-proxy](kiwi-proxy.md) hinausgeht. *Wie distrobox, mit dem Netzwerk in
Gewahrsam.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Aktuelles Release: **v0.2.3**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md), Benutzerbereich.
- Eine CLI (`kiwi-custodia`) und eine GTK4-App (**Kiwi Custodia**)

Eine **Box** ist eine Linux-Distribution in einem rootless Podman-Container, mit
einem eigenen Home-Verzeichnis, verbunden mit dem versiegelten Gateway eines
Ausgangs. Installiere darin alles mit ihrem Paketmanager, starte ihre Desktop-Apps
auf deinem Desktop und leg sie ins App-Raster. Die Box hat keine Route außer dem
Ausgang: nicht für `dnf`, nicht für einen Spiele-Client, nicht für ein statisches
Binary, das nie von `$ALL_PROXY` gehört hat. Fällt der Ausgang weg, hat die Box
überhaupt keine Route.

Damit ist eine Box pro Kundennetz eine saubere Art zu arbeiten: die Werkzeuge,
Schlüssel und Shell-History von Kunde A in einer Box, die von Kunde B in einer
anderen, und jede erreicht nur ihren eigenen Kunden.

## Installation { #install }

```bash
kiwi install kiwi-custodia   # brings kiwi-proxy along; or ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

Es braucht rootless Podman mit `catatonit`, kiwi-proxy, eine Wayland-Sitzung,
Python 3.12+ mit pydantic, GTK4 + libadwaita für die App und ein `/dev/net/tun`, das
rootless Container benutzen können. Distro-Images werden geladen, wenn eine Box zum
ersten Mal startet. Führe `kiwi-custodia setup` nach einem Update erneut aus.

## Benutzung { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # an exit, defined once, in kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # a box on it; the first start installs a baseline
kiwi-custodia enter work                                   # a shell in it: sudo dnf install …
kiwi-custodia run work -- firefox                          # one command in it
kiwi-custodia check work                                   # what the world sees from inside
kiwi-custodia apps work                                    # the desktop apps it has
kiwi-custodia export work firefox                          # "Firefox (work)" in the app grid
kiwi-custodia stop work
kiwi-custodia reset work                                   # back to the base image; the home stays
kiwi-custodia-gui
```

Distributionen: `fedora` (der Standard), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine` oder `custom` mit `--image`.

## Wie eine Box aufgebaut ist { #how-a-box-is-built }

Drei Container teilen sich einen Netzwerk-Namespace: das **Gateway** von
kiwi-proxy, ein **Tunnel-Sidecar** (tun2socks auf einem TUN-Gerät, das zur
Standardroute wird) und die **Box** selbst. Der gesamte Verkehr verlässt sie über
das TUN in den SOCKS5 des Ausgangs, sodass auch Programme erfasst sind, die
Proxy-Einstellungen ignorieren.

- Die Box läuft als dein Benutzer, mit derselben UID und `sudo` ohne Passwort. Ihr
  Home-Verzeichnis ist `~/.local/share/kiwi-custodia/boxes/<id>/home`, eines pro
  Box statt deines echten Home-Verzeichnisses: Zwei Boxen sind zwei Identitäten.
- Änderungen in einer Box werden beim Stoppen in einem Snapshot pro Box behalten,
  und `reset` kehrt zum Basis-Image zurück.
- Wayland, X11 (über Xwayland), PipeWire, der Session-Bus und `/dev/dri` werden
  hineingereicht, sodass Desktop-Apps und Spiele funktionieren.
- DNS läuft über den Resolver des Gateways (mit Werbeblocker) oder, bei einem
  Ausgang mit Remote-DNS, über den Upstream.

## Was sie nicht ist { #what-it-is-not }

Eine Box ist **Netzwerk-Gewahrsam, keine Sandbox gegenüber deinem Desktop**. Wie
distrobox bekommt sie dein Display und deinen Session-Bus, sodass ein Programm in
der Box Fenster anzeigen, die Zwischenablage lesen und die Portale benutzen kann.
Was sie nicht kann, ist, das Netzwerk anders als über ihren Ausgang zu erreichen.
UDP hat keinen Weg nach draußen (kein QUIC, keine WebRTC-Medien), und IPv6 hat keine
Route.

Boxen, die sich keinen Ausgang teilen dürfen, nehmen verschiedene Ausgänge.
