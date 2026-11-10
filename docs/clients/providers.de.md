# Provider-Module

Ein Provider-Modul gibt [kiwi-proxy](kiwi-proxy.md) einen Ausgang, den es selbst
erzeugt, statt eines SOCKS5, das du bekommen hast. Jedes liegt in einem eigenen
Repository, wird über kiwi-updater in das Modulverzeichnis von kiwi-proxy
installiert und von kiwi-proxy verwaltet: Es baut das Image des Moduls, fährt es
hoch, wenn ein Ausgang es braucht, und fährt es herunter, wenn kein Gateway es mehr
nutzt.

| Modul | Repository | Release | Ausgang | Braucht |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | das Tor-Netzwerk, ein Circuit pro Ausgang, beliebiges Ausgangsland | nichts (kostenlos) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | ein WireGuard- oder OpenVPN-Tunnel über [gluetun](https://github.com/qdm12/gluetun) | ein VPN-Abo |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | ein Residential-Ausgang von [9proxy](https://9proxy.com/) | ein 9proxy-Konto und dessen proprietärer Client (wird nicht weiterverteilt) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | das dVPN von [Mysterium](https://mysterium.network/), mit einer Auswahl unter Nodes nach Land und IP-Typ | eine registrierte Consumer-Identität mit MYST-Guthaben |

Alle vier stehen unter GPL-3.0-or-later, sind im [Kiwi-Katalog](../desktop/catalogs.md)
und deklarieren `DEPENDS=kiwi-proxy`, sodass kiwi zuerst kiwi-proxy installiert. Tor
und Mysterium sind der schnelle Weg zu mehr Ausgangs-IPs, zum Beispiel zum Testen.

## Installation und Benutzung { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # sein Image bauen (kiwi-proxy setup erledigt alle)
kiwi-proxy module list
kiwi-proxy module countries tor                  # wo Tor austreten kann
kiwi-proxy add tor-de --module tor --country de  # ein Ausgang daraus
kiwi-custodia new test --exit tor-de             # eine Box daran, oder:
kiwi-fox new test --exit tor-de                  # ein Browserprofil daran
```

Bei Tor wird das Land mit `StrictNodes` festgehalten, sodass der Circuit eher
scheitert, als woanders auszutreten. Ausgänge auf dem Tor-Modul reichen die
SOCKS-Zugangsdaten pro Website von Tor Browser standardmäßig durch
(`--socks-auth passthrough`).

## Wie es verdrahtet ist { #how-it-is-wired }

**Jeder Provider stellt SOCKS5 bereit und sonst nichts.** Ein Provider-Container
braucht seinen eigenen Weg nach draußen, also kann er nicht im Namespace eines
Gateways leben, wo alles außer einem Ziel verworfen wird. Die beiden treffen sich
auf einer rootless Podman-Bridge, `kf-providers`, auf der jedes Modul eine feste
Adresse bekommt:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** spricht bereits SOCKS5. kiwi-proxy schickt Zugangsdaten pro Ausgang, und
  Tors `IsolateSOCKSAuth` gibt jedem Ausgang seinen eigenen Circuit.
- **VPN und Mysterium** fahren auf einem Tunnel, der kein SOCKS5 spricht, also tritt
  ein kleiner microsocks-Adapter dem Netzwerk-Namespace des Tunnels bei und bietet
  SOCKS5 an, das über den Tunnel läuft.
- **9proxy** führt den 9proxy-Client aus, der einen SOCKS5-Port auf einem
  Residential-Ausgang öffnet.

Ein Provider-Container bedient jeden Ausgang auf demselben Modul und Lease. Ein
Tunnel, der seine Sitzung verliert, schließt fail-closed und wird neu gestartet.

## Konfiguration { #configuration }

Der Zustand jedes Moduls liegt in `~/.local/share/kiwi-proxy/modules-state/<module>/`,
außerhalb jedes Repositorys:

- **vpn**: `vpn.json` mit den Einstellungen für gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; jeder großgeschriebene Schlüssel geht
  unverändert an gluetun), eine optionale Liste `leases` und ein optionales
  Verzeichnis `gluetun/` (zum Beispiel eine `wireguard.conf` für den Provider
  `custom` von gluetun). Das ist eine Konfiguration pro Maschine: Ausgänge darauf
  unterscheiden sich im Serverland.
- **9proxy**: `config/account.conf`. Leg den proprietären Client in das Verzeichnis
  `module/containers/vendor/` des Plugins und füge `COPY vendor/ /opt/9proxy/` zu
  seinem `Containerfile` hinzu, bevor du `kiwi-proxy module setup 9proxy` ausführst.
  Ohne ihn baut das Image, aber der Provider weigert sich hochzufahren, statt einen
  Port zu öffnen.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase` oder *Configure…* in der App Kiwi Proxy. Die Passphrase wird
  zu einem Podman-Secret. Eine Identität hält immer nur eine Verbindung gleichzeitig.

## Status { #status }

Tor braucht kein Konto. Mysterium wurde am 2026-11-07 Ende-zu-Ende geprüft. Die
Module VPN und 9proxy sind vollständig und mit Unit-Tests versehen, wurden aber
noch nicht Ende-zu-Ende gegen ein echtes Abo oder Konto betrieben, wie ihre READMEs
sagen.
