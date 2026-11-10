# Provider-Module

In [kiwi-proxy](kiwi-proxy.md) ist ein Exit eine Verbindung zu einem Upstream,
die einen Namen hat und über die deine Boxen und Browser ihren Verkehr
schicken. Meist ist das eine Verbindung, die du bekommen hast, etwa der
SOCKS5-Proxy, der ins Netz eines Kunden führt. Ein Provider-Modul ist für den
anderen Fall da: Es legt den Exit selbst an, über Tor, ein VPN-Abo, 9proxy oder
Mysterium. Vor allem Tor und Mysterium sind dafür gedacht, dir für Tests
zusätzliche IP-Adressen zu verschaffen.

Jedes Modul liegt in einem eigenen Repository. kiwi-updater installiert es in
das Modulverzeichnis von kiwi-proxy, und ab dann verwaltet kiwi-proxy es.
kiwi-proxy baut das Container-Image des Moduls, startet das Modul, wenn ein
Exit es braucht, und stoppt es, sobald kein Gateway es mehr nutzt. Ein Gateway
ist der Container, den kiwi-proxy für einen Exit betreibt, solange der Exit
läuft.

| Modul | Repository | Release | Exit | Voraussetzung |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | das Tor-Netzwerk, mit einem eigenen Circuit pro Exit und frei wählbarem Land des Exit-Knotens | nichts (es ist kostenlos) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | ein WireGuard- oder OpenVPN-Tunnel über [gluetun](https://github.com/qdm12/gluetun) | ein VPN-Abo |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | ein Exit über einen privaten Internetanschluss (Residential) von [9proxy](https://9proxy.com/) | ein Konto bei 9proxy und der proprietäre Client von 9proxy, der nicht mitgeliefert wird |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | das dVPN von [Mysterium](https://mysterium.network/) (ein dezentrales VPN), mit einer Liste von Knoten, aus der du nach Land und IP-Typ auswählst | eine registrierte Consumer-Identität mit MYST-Guthaben |

Alle vier Module stehen unter GPL-3.0-or-later und sind im
[Kiwi-Katalog](../desktop/catalogs.md). Jedes gibt `DEPENDS=kiwi-proxy` an,
deshalb installiert kiwi-updater zuerst kiwi-proxy. Tor und Mysterium sind der
schnelle Weg zu weiteren IP-Adressen nach außen, zum Beispiel zum Testen.

## Installieren und benutzen { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # sein Image bauen (kiwi-proxy setup baut alle)
kiwi-proxy module list
kiwi-proxy module countries tor                  # in welchen Ländern Tor-Exit-Knoten zur Wahl stehen
kiwi-proxy add tor-de --module tor --country de  # ein Exit daraus
kiwi-custodia new test --exit tor-de             # eine Box daran, oder:
kiwi-fox new test --exit tor-de                  # ein Browser-Profil daran
```

Bei einem Tor-Exit wird das Land mit der Tor-Option `StrictNodes` erzwungen.
Ein Circuit, der in diesem Land keinen Exit-Knoten findet, schlägt fehl und
kommt nie in einem anderen Land heraus. Exits des Tor-Moduls reichen die
SOCKS-Zugangsdaten weiter, die Tor Browser für jede Website mitschickt. Das ist
ihre Voreinstellung (`--socks-auth passthrough`).

## So hängt ein Provider am Gateway { #how-it-is-wired }

**Jeder Provider bietet SOCKS5 an und sonst nichts.** Ein Provider-Container
braucht eine eigene Verbindung ins Internet. Im Netzwerk-Namespace eines
Gateways kann er deshalb nicht laufen, denn dort wird alles verworfen, was
nicht an ein einziges Ziel geht. Stattdessen sind Provider und Gateway über ein
Bridge-Netzwerk von rootless Podman verbunden, `kf-providers`, in dem jedes
Modul eine feste Adresse hat:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** bietet SOCKS5 selbst an. kiwi-proxy schickt für jeden Exit eigene
  Zugangsdaten, und die Tor-Option `IsolateSOCKSAuth` gibt dann jedem Exit
  einen eigenen Circuit, also einen eigenen Pfad durch das Tor-Netzwerk.
- **VPN und Mysterium** verwenden einen Tunnel, und ein Tunnel bietet kein
  SOCKS5. Deshalb teilt sich ein kleiner Adapter, microsocks, den
  Netzwerk-Namespace des Tunnels. Er bietet SOCKS5 an und schickt den Verkehr
  durch den Tunnel.
- **9proxy** führt den Client von 9proxy aus, der einen SOCKS5-Port öffnet,
  über den der Verkehr an einem privaten Internetanschluss herauskommt.

Ein Provider-Container bedient alle Exits, die dasselbe Modul und dieselbe
Lease verwenden. Als Lease bezeichnet ein Modul jeden der Exits, die es zur
Auswahl anbietet, zum Beispiel ein Land für den VPN-Server oder einen
Mysterium-Knoten.
Verliert ein Tunnel seine Sitzung, ist er fail-closed: Es kommt kein Verkehr
mehr hinaus, und der Tunnel wird neu gestartet.

## Konfiguration { #configuration }

Der Zustand jedes Moduls liegt in
`~/.local/share/kiwi-proxy/modules-state/<module>/`, außerhalb jedes
Repositorys:

- **vpn**: Die Datei `vpn.json` enthält die Einstellungen für gluetun, etwa
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` und `WIREGUARD_ADDRESSES`. Jeder Schlüssel
  in Großbuchstaben wird unverändert an gluetun weitergegeben. Die Datei kann
  außerdem eine Liste `leases` enthalten. Ein optionales Verzeichnis `gluetun/`
  nimmt weitere Dateien auf, zum Beispiel eine `wireguard.conf` für den
  Provider `custom` von gluetun. Pro Rechner gibt es eine solche
  Konfiguration, und die Exits darauf unterscheiden sich im Land des Servers.
- **9proxy**: Die Konfigurationsdatei ist `config/account.conf`. Der
  proprietäre Client ist nicht dabei. Bevor du
  `kiwi-proxy module setup 9proxy` ausführst, legst du den Client in das
  Verzeichnis `module/containers/vendor/` des Plugins und ergänzt im
  `Containerfile` des Plugins `COPY vendor/ /opt/9proxy/`. Ohne den Client wird
  das Image zwar trotzdem gebaut, aber der Provider startet nicht und öffnet
  keinen Port.
- **mysterium**: Führe `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase` aus oder benutze *Configure…* in der App Kiwi Proxy. Die
  Passphrase wird als Podman-Secret gespeichert. Eine Identität kann immer nur
  eine Verbindung gleichzeitig haben.

## Status { #status }

Tor braucht kein Konto. Das Mysterium-Modul wurde am 7. November 2026
vollständig durchgetestet. Laut ihren READMEs sind die Module für VPN und
9proxy fertig und mit Unit-Tests versehen, wurden aber noch nicht vollständig
mit einem echten Abo oder Konto durchgespielt.
