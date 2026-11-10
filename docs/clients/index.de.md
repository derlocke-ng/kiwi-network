# Arbeiten in vielen Kundennetzen

Wer aus der Ferne für viele Kunden arbeitet, braucht meist für jedes
Kundennetz eine eigene VPN- oder SOCKS-Verbindung. Zehn Kunden bedeuten dann zehn
Verbindungen. Laufen alle auf dem Host, gibt es Ärger: Zehn Tunnel stehen
gleichzeitig, ihre Routen kommen sich gegenseitig in die Quere, und Verkehr,
der für das Netz des einen Kunden bestimmt ist, kann im Netz eines anderen
landen.

Mit den Desktop-Apps von Kiwi arbeitest du in jedem Kundennetz sauber getrennt.
Der Host bleibt frei von Tunneln und Routen, und es laufen nicht zehn
VPN-Verbindungen auf einmal. Jede Verbindung kommt in einen eigenen Container,
und der einzige Weg aus diesem Container hinaus führt zu genau diesem einen
Kunden. So eine Verbindung heißt **Exit**. Deine Programme laufen in einem
Container oder einem Browser-Profil, das den Exit nutzt, den es braucht. Am
Host selbst ändert sich nichts.

| App | Was sie macht |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Die Grundlage, auf der die anderen Apps aufbauen. Ein **Exit** ist eine Verbindung zu einem Upstream, die du unter einem Namen speicherst. Der Upstream ist der Proxy, an den dein Verkehr geschickt wird: entweder ein SOCKS5-Proxy, den du bekommen hast, oder einer, den ein Provider-Modul anlegt. Wenn du einen Exit startest, legt kiwi-proxy dafür ein **Gateway** an. Ein Gateway ist ein Netzwerk-Namespace (ein eigener Netzwerk-Stack mit eigenen Routen und eigener Firewall), dessen einzige Route zu diesem Upstream führt. Programme auf dem Host können einen Exit über einen lokalen SOCKS5-Port nutzen |
| [**kiwi-custodia**](kiwi-custodia.md) | **Linux-Distributionen in Boxen, die einen Exit nutzen.** Eine Box ist ein Rootless-Container (einer, der ohne Root-Rechte läuft) mit Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky oder Alpine und einem eigenen Home-Verzeichnis. *Der gesamte* Netzwerkverkehr der Box läuft über den Exit. Dazu gehören auch Paketmanager, Spiele und statisch gelinkte Programme, die Proxy-Einstellungen ignorieren |
| [**kiwi-fox**](kiwi-fox.md) | **Browser-Profile, die einen Exit nutzen.** In jedem Profil läuft Camoufox, Firefox oder Tor Browser, und jedes hat seinen eigenen Speicher |
| [**Provider-Module**](providers.md) | Module, die Exits über Tor, ein VPN (mit gluetun), 9proxy oder Mysterium anlegen. Mit Tor und Mysterium kommst du schnell an weitere IP-Adressen, was zum Testen praktisch ist |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## So bleiben die Exits getrennt { #how-it-stays-clean }

- **Ein Gateway ist fail-closed.** Ein Ausfall kappt die Verbindung und öffnet
  nie einen anderen Weg. Die Firewall im Gateway verwirft alles, was nicht an
  den einen Upstream des Gateways geht. Fällt das Gateway aus, hat alles, was
  daran hängt, keine Verbindung mehr. Kein Programm muss den Ausfall bemerken
  und darauf reagieren, denn ohne Gateway gibt es schlicht keine Route.
- **Es läuft nur, was du benutzt.** Startet eine Box oder ein Browser ein
  Gateway, wird es wieder entfernt, sobald die letzte Box oder der letzte
  Browser daran beendet ist. Weiter laufen nur Exits, die du selbst mit
  `kiwi-proxy up` gestartet hast.
- **Kunden bleiben getrennt.** Boxen und Browser am selben Exit teilen ihn sich,
  haben also dieselbe IP-Adresse und denselben Netzwerk-Namespace. Kunden, die
  sich nicht gegenseitig sehen dürfen, bekommen verschiedene Exits. Außerdem
  hat jede Box ihr eigenes Home-Verzeichnis. Die SSH-Schlüssel und
  Browser-Profile des einen Kunden sind in der Box eines anderen also nicht
  vorhanden.
- **Keine Root-Rechte und keine Routen auf dem Host.** Alles läuft in rootless
  Podman, das Container unter deinem eigenen Benutzer ausführt. Am Netzwerk des
  Hosts wird nichts verändert.
- **Auch DNS-Anfragen laufen über den Exit.** Standardmäßig werden Namen per
  DNS over HTTPS (DoH) über den Exit aufgelöst, und Domains aus Werbelisten
  werden blockiert. Um die **internen Hostnamen** eines Kunden aufzulösen,
  verwendest du stattdessen `--dns remote`. Die Namen werden dann an die Seite
  des Kunden weitergereicht und dort aufgelöst. Auch Tor und `.onion`-Namen
  brauchen diesen Modus.

## Grenzen { #limits }

Diese Grenzen nennen die Repositories selbst:

- **Nur TCP und nur IPv4.** UDP wird nicht weitergeleitet, deshalb
  funktionieren QUIC und WebRTC-Medien nicht. Für IPv6 gibt es keine Route.
- **Eine VPN-Konfiguration pro Rechner.** Das VPN-Provider-Modul hat eine
  einzige gluetun-Konfiguration, mit einer `vpn.json` und einer eigenen
  WireGuard-Konfiguration. Seine Exits unterscheiden sich nur im Land des
  Servers. Brauchst du die VPNs mehrerer Kunden gleichzeitig, geht das heute
  über einen SOCKS5-Endpunkt pro Kunde.
- **Eine Box schränkt das Netzwerk ein, ist aber keine Sandbox.** Wie ein
  distrobox-Container teilt sie sich deinen Bildschirm, deinen Session-Bus und
  deine Zwischenablage. Was sie nicht kann: das Netzwerk auf einem anderen Weg
  erreichen als über ihren Exit.
- **Mysterium:** Eine Identität kann immer nur eine Verbindung gleichzeitig
  haben.

## Loslegen { #get-started }

Die folgenden Befehle installieren die Apps, speichern den SOCKS5-Proxy eines
Kunden als Exit und öffnen eine Shell in einer Fedora-Box, die diesen Exit
nutzt:

```bash
kiwi install kiwi-custodia            # bringt kiwi-proxy mit
kiwi-custodia setup                   # Images und DNS-Daten

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # eine Shell, deren einziger Weg nach draußen der SOCKS5-Proxy von Kunde A ist
```
