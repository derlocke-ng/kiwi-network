# kiwi-custodia

kiwi-custodia gibt dir für jedes Kundennetz, in dem du arbeitest, eine eigene
Linux-Umgebung. Jede Umgebung ist ein Container mit einer Linux-Distribution
deiner Wahl, und ihr gesamter Netzwerkverkehr läuft über einen Exit von
[kiwi-proxy](kiwi-proxy.md). Ein Exit ist eine Verbindung zu einem Upstream,
die einen Namen hat, zum Beispiel der SOCKS5-Proxy, der ins Netz eines Kunden
führt. So kannst du für zehn Kunden arbeiten, ohne dass zehn VPN-Verbindungen
auf dem Host laufen, und die Werkzeuge und Schlüssel jedes Kunden bleiben in seiner
Umgebung. *Wenn du distrobox kennst: Das ist dieselbe Idee, nur dass der
Container das Netzwerk ausschließlich über seinen Exit erreicht.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Aktuelles Release: **v0.2.3**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md), Scope user.
- Es gibt ein Kommandozeilenwerkzeug (`kiwi-custodia`) und eine GTK4-App (**Kiwi Custodia**).

Eine **Box** ist eine Linux-Distribution in einem Rootless-Container von
Podman, also in einem Container, der unter deinem eigenen Benutzer ohne
Root-Rechte läuft. Die Box hat ein eigenes Home-Verzeichnis und hängt am
Gateway eines Exits. Das Gateway ist der Container, den kiwi-proxy für einen
Exit startet, und seine einzige Route nach draußen führt zum Upstream des
Exits. In der Box kannst du mit dem Paketmanager der Distribution beliebige
Software installieren. Ihre Desktop-Apps öffnen sich auf deinem Desktop, und du
kannst sie in die Anwendungsübersicht aufnehmen. Eine andere Route als den Exit
hat die Box nicht. Das gilt für jedes Programm darin: für `dnf`, für einen
Spiele-Client und für ein statisch gelinktes Programm, das `$ALL_PROXY`
ignoriert. Fällt der Exit aus, hat die Box überhaupt keine Route mehr.

Deshalb ist eine Box pro Kundennetz eine gute Arbeitsweise. Die Werkzeuge,
Schlüssel und die Shell-History von Kunde A liegen in einer Box, die von
Kunde B in einer anderen, und jede Box erreicht nur ihren eigenen Kunden.

## Installation { #install }

```bash
kiwi install kiwi-custodia   # bringt kiwi-proxy mit; oder ./install.sh install
kiwi-custodia setup          # das Tunnel-Image sowie Gateway-Image und DNS-Daten von kiwi-proxy
```

kiwi-custodia braucht rootless Podman mit `catatonit`, kiwi-proxy, eine
Wayland-Sitzung und Python 3.12+ mit pydantic. Die App braucht GTK4 und
libadwaita. Außerdem müssen Rootless-Container `/dev/net/tun` benutzen dürfen.
Die Images der Distributionen werden beim Setup nicht heruntergeladen. Ein
Image wird erst geladen, wenn eine Box, die es verwendet, zum ersten Mal
startet. Führe nach einem Update `kiwi-custodia setup` erneut aus.

## Bedienung { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # ein Exit, einmal in kiwi-proxy angelegt
kiwi-custodia new work --exit client-a --distro fedora     # eine Box daran; der erste Start installiert eine Grundausstattung
kiwi-custodia enter work                                   # eine Shell darin: sudo dnf install …
kiwi-custodia run work -- firefox                          # ein einzelner Befehl darin
kiwi-custodia check work                                   # was die Welt von innen aus sieht
kiwi-custodia apps work                                    # die Desktop-Apps, die sie hat
kiwi-custodia export work firefox                          # "Firefox (work)" in der Anwendungsübersicht
kiwi-custodia stop work
kiwi-custodia reset work                                   # zurück zum Basis-Image; das Home bleibt
kiwi-custodia-gui
```

Zur Auswahl stehen die Distributionen `fedora` (voreingestellt),
`fedora-toolbox`, `ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`,
`kali`, `arch`, `arch-toolbox`, `opensuse`, `rocky` und `alpine`. Du kannst
auch `custom` wählen und mit `--image` selbst ein Image angeben.

## So ist eine Box aufgebaut { #how-a-box-is-built }

Eine laufende Box besteht aus drei Containern, die sich einen
Netzwerk-Namespace teilen, also dieselben Netzwerkschnittstellen, Routen und
Firewall-Regeln. Der erste ist das **Gateway** von kiwi-proxy. Der zweite ist
ein **Tunnel-Sidecar**, ein Hilfscontainer, in dem tun2socks auf einem
TUN-Gerät läuft. Ein TUN-Gerät ist eine virtuelle Netzwerkschnittstelle, und
hier wird sie zur Standardroute. Der dritte Container ist die **Box** selbst.
Der gesamte Verkehr der Box geht in das TUN-Gerät und von dort zum
SOCKS5-Proxy des Exits. Das geschieht über die Standardroute und nicht über
Proxy-Einstellungen. Deshalb sind auch Programme erfasst, die
Proxy-Einstellungen ignorieren.

- Die Box läuft unter deinem Benutzer, mit derselben UID, und `sudo`
  funktioniert darin ohne Passwort. Ihr Home-Verzeichnis ist
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Jede Box hat ihr eigenes
  Home und benutzt nicht dein echtes. Zwei Boxen sind also zwei getrennte
  Identitäten.
- Wird eine Box gestoppt, werden die Änderungen darin in einem Snapshot
  gespeichert, der zu dieser Box gehört. `reset` setzt die Box auf das
  Basis-Image zurück.
- Wayland, X11 (über Xwayland), PipeWire, der Session-Bus und `/dev/dri` stehen
  in der Box zur Verfügung, damit Desktop-Apps und Spiele funktionieren.
- DNS-Anfragen beantwortet der Resolver des Gateways, der auch Werbedomains
  blockiert. Bei einem Exit mit Remote-DNS löst stattdessen der Upstream die
  Namen auf.

## Was es nicht ist { #what-it-is-not }

Eine Box **schränkt das Netzwerk ein. Sie ist keine Sandbox, die deinen
Desktop vor den Programmen darin schützt.** Wie ein distrobox-Container bekommt
die Box Zugriff auf deinen Bildschirm und deinen Session-Bus. Ein Programm in
der Box kann deshalb Fenster anzeigen, die Zwischenablage lesen und die
Desktop-Portale benutzen. Was es nicht kann: das Netzwerk auf einem anderen Weg
erreichen als über seinen Exit. UDP wird nicht weitergeleitet, deshalb
funktionieren QUIC und WebRTC-Medien nicht, und für IPv6 gibt es keine Route.

Boxen am selben Exit teilen ihn sich. Boxen, die voneinander getrennt bleiben
müssen, brauchen verschiedene Exits.
