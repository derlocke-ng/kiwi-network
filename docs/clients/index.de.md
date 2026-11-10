# Mit vielen Kundennetzen arbeiten

Zehn Kunden aus der Ferne betreuen heißt oft zehn VPNs oder SOCKS-Endpunkte, einen
für das Netz jedes Kunden. Sie alle auf dem Host zu betreiben, ist ein Durcheinander:
zehn Tunnel gleichzeitig, Routen, die sich in die Quere kommen, und ein Netz, das
ins nächste leckt. Die Kiwi-Desktop-Apps geben stattdessen jedem einen
**versiegelten Ausgang**: einen Container, dessen einzige Route dieser eine
Upstream ist. Deine Werkzeuge treten dem Ausgang bei, den sie brauchen, und sonst
ändert sich auf dem Host nichts.

| App | Was sie tut |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Der Motor. Ein **Ausgang** ist ein Upstream mit Namen: ein SOCKS5, das du bekommen hast, oder eines, das ein Provider-Modul erzeugt. Wird er hochgefahren, entsteht ein **Gateway**, ein Netzwerk-Namespace, dessen einzige Route dieser Upstream ist. Host-Apps können ihn als lokalen SOCKS5-Port nutzen |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distro-Boxen an einem Ausgang**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky oder Alpine in einem rootless Container mit eigenem Home-Verzeichnis. *Alles* in der Box geht über den Ausgang hinaus: Paketmanager, Spiele, statische Binaries, die nie von einem Proxy gehört haben |
| [**kiwi-fox**](kiwi-fox.md) | **Browserprofile an einem Ausgang**: Camoufox, Firefox oder Tor Browser, jedes Profil mit eigenem Speicher |
| [**Provider-Module**](providers.md) | Ausgänge aus Tor, einem VPN (gluetun), 9proxy oder Mysterium. Tor und Mysterium sind der schnelle Weg zu mehr Ausgangs-IPs, praktisch zum Testen |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Wie es sauber bleibt { #how-it-stays-clean }

- **Fail-closed.** Die Firewall eines Gateways verwirft alles außer seinem einen
  Upstream. Stirbt das Gateway, verliert alles, was ihm beigetreten ist, seine
  Route. Der Kill Switch ist das Fehlen einer Route, keine Software, die etwas
  bemerken muss.
- **Nichts läuft, was nicht benutzt wird.** Ein Gateway, das eine Box oder ein
  Browser hochgefahren hat, verschwindet, wenn der Letzte geht. Nur Ausgänge, die
  du mit `kiwi-proxy up` startest, bleiben oben.
- **Was getrennt ist, bleibt getrennt.** Was am selben Ausgang hängt, teilt ihn
  (eine IP, ein Namespace). Kunden, die sich nicht begegnen dürfen, bekommen
  verschiedene Ausgänge, und jede Box hat ihr eigenes Home-Verzeichnis, sodass sich
  SSH-Schlüssel und Browserprofile nicht kreuzen.
- **Kein Root, keine Host-Routen.** Alles läuft in rootless Podman, und das eigene
  Netzwerk des Hosts bleibt unberührt.
- **Auch DNS geht über den Ausgang.** Standardmäßig werden Namen per DoH über den
  Ausgang aufgelöst, mit Werbeblocklisten. Für die **internen Hostnamen** eines
  Kunden gibst du die Namen stattdessen mit `--dns remote` an die Seite des Kunden
  weiter (auch der Modus für Tor und `.onion`-Namen).

## Grenzen { #limits }

Diese stammen aus den Repositories:

- **Nur TCP, nur IPv4.** UDP kommt nirgendwo hinaus (kein QUIC, keine
  WebRTC-Medien), und IPv6 bekommt keine Route.
- **Eine VPN-Konfiguration pro Maschine.** Das VPN-Provider-Modul hält eine
  gluetun-Konfiguration (eine `vpn.json`, eine eigene WireGuard-Konfiguration), und
  seine Ausgänge unterscheiden sich nur im Serverland. Für die eigenen VPNs mehrerer
  Kunden nebeneinander ist heute ein SOCKS5-Endpunkt pro Kunde der Weg.
- **Eine Box ist Netzwerk-Gewahrsam, keine Sandbox.** Sie teilt dein Display, den
  Session-Bus und die Zwischenablage, wie distrobox. Was sie nicht kann, ist, das
  Netzwerk anders als über ihren Ausgang zu erreichen.
- **Mysterium:** Eine Identität hält immer nur eine Verbindung gleichzeitig.

## Loslegen { #get-started }

```bash
kiwi install kiwi-custodia            # brings kiwi-proxy along
kiwi-custodia setup                   # images and DNS data

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
