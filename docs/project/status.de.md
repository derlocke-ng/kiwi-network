# Repositories & Status

Diese Seite führt jedes Repository des Projekts Kiwi Network auf: was es ist,
sein aktuelles Release und seine Lizenz. Am Ende steht, was bekanntermaßen noch
fehlt oder noch nicht getestet ist.

Alle Repositories liegen unter
[github.com/derlocke-ng](https://github.com/derlocke-ng). „Veröffentlicht“
heißt, dass ein Repository ein Versions-Tag hat, denn kiwi-updater installiert
genau das, worauf ein Versions-Tag zeigt. Die Versionen sind auf dem Stand von
November 2026.

## Das Netzwerk { #the-network }

| Repository | Was es ist | Release | Katalog | Lizenz |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | baut und betreibt das Netzwerk: macht aus der Fleet-Datei Installations-ISOs und richtet jede Maschine per SSH für ihre Rolle ein | v2.42.0 | ja | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | die 20 Module und ihr Renderer, der aus einer Maschinendatei ein Stack-Bundle erzeugt | v0.23.0 | nein | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | der Teil, der auf der Maschine läuft: bringt ein Bundle auf die Maschine und hält es am Laufen | v0.5.0 | nein | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | Listen und DNS-Einträge der SOCKS5-Proxys von Mullvad, alle 6 Stunden neu erstellt | der Branch `list` | nein | MIT (README) |

## Hubs { #people }

| Repository | Was es ist | Release | Lizenz |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | das Framework, mit dem föderierte Community-Hubs auf nostr gebaut werden | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | der erste Hub, der mit kiwi-framework gebaut wurde, mit zehn Peer-to-Peer-Werkzeugen im Browser ([live](https://derlocke-ng.github.io/armory/)) | folgt `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | ein Katalog von Hubs und ihren Apps | (eine Liste) | CC0 (README) |

## Der Desktop { #the-desktop }

| Repository | Was es ist | Release | Katalog | Lizenz |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installiert und aktualisiert Apps aus git-Katalogen | v2.4.0 | ja | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | der App-Katalog von Kiwi | (eine Liste) | – | keine angegeben |
| [ensconce](https://github.com/derlocke-ng/ensconce) | richtet Bluefin-DX nach der Installation ein | v2.5.0 | ja | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | ein VPN-Kill-Switch für GNOME, der fail-closed ist: Bricht die VPN-Verbindung ab, wird der Verkehr gesperrt | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | SOCKS5- und VPN-Exits in rootless Podman, jeder in einem eigenen abgeschotteten Container, dessen einzige Route diese Verbindung ist | v0.7.3 | ja | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | Distro-Boxen (Linux-Distributionen in Containern), deren Verkehr nur über einen Exit von kiwi-proxy ins Internet gelangt | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | getrennte Browser-Identitäten, die sich über Exits von kiwi-proxy verbinden | v0.7.1 | ja | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | Provider für kiwi-proxy: Tor | v0.3.0 | ja | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | Provider für kiwi-proxy: ein VPN über gluetun | v0.2.2 | ja | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | Provider für kiwi-proxy: 9proxy | v0.2.0 | ja | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | Provider für kiwi-proxy: Mysterium | v0.5.2 | ja | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | Bildschirmanordnungen für GNOME | v0.3.2 | ja | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | Ordner-Synchronisation in beide Richtungen, als systemd-Benutzerdienste | v0.4.1 | ja | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | ja | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | erzeugt SSH- und TLS-Schlüssel und -Zertifikate offline im Browser ([live](https://derlocke-ng.github.io/kiwi-gen/)) | Webseite | nein | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | die App-Icons ([Vorschau](https://derlocke-ng.github.io/kiwi-icons/)) | keine Tags | nein | keine angegeben |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | diese Website und Dokumentation | – | – | AGPL-3.0 |

## Bekannte Lücken { #known-gaps }

Diese Lücken nennen die Repositories selbst:

- **kiwi-server**: Es wurde im Oktober und November 2026 auf echter Hardware
  getestet. Dabei wurden Backups eines Nodes auf einem anderen Node
  wiederhergestellt, und die Tunnel-MTU wurde angepasst, auch für
  Mobilfunkverbindungen. Vier Neuerungen liegen auf den
  `several-servers`-Branches von kiwi-server und kiwi-modules und sind noch
  nicht veröffentlicht: mehrere Backup-Server, die automatische
  Wiederherstellung einer neu aufgesetzten Maschine, ein Timer zum Aufräumen
  alter Snapshots und ein Health-Check, der eine hängende Verbindung zum
  kommerziellen VPN-Anbieter neu startet. Dass die Föderation zwischen
  Netzwerken funktioniert, ist noch nicht gezeigt. Alles läuft nur über IPv4,
  und das Debian-ISO gibt es nur für amd64. Die Control Plane ist entworfen,
  aber noch nicht umgesetzt.
- **kiwi-modules**: Die Module für OpenCloud, Immich und Paperless-ngx sind als
  „zum Ausprobieren“ gekennzeichnet. Ein TURN-Server für Anrufe wartet darauf,
  gemergt zu werden.
- **kiwi-stack**: Es gibt keinen Rollback. Du kannst nur Daten wiederherstellen
  und ein älteres Bundle erneut anwenden.
- **kiwi-framework**: Mehrere Teile stehen noch aus, nämlich der Blog, Freigaben
  durch die Moderation, das Folgen von Spaces, die ein Hub nicht mitbringt, und
  Signer nach NIP-07/NIP-46.
- **kiwi-updater**: Ein gehostetes Verzeichnis vertrauenswürdiger Kataloge ist
  geplant. Die Release-Tags der anderen Apps sind noch nicht signiert. Deshalb
  fragt der Teil von kiwi-killswitch, der als root läuft, bei einem Update nach
  einem Passwort.
- **kiwi-proxy**: Sein Modul für kiwi-server ist noch auf keiner Maschine
  gelaufen. Exits übertragen nur TCP und IPv4. Das VPN-Modul speichert eine
  Konfiguration pro Maschine.
- **Provider-Module**: Die Module für VPN und 9proxy wurden noch nicht
  durchgängig mit einem echten Konto geprüft. Das Modul für Mysterium wurde
  am 7. November 2026 geprüft.
- **kiwi-custodia**: Einige Teile müssen noch auf einer echten Maschine
  nachgemessen werden, nämlich tun2socks in einem Rootless-Gateway und andere
  Compositors als GNOME.
- **Lizenzen**: kiwi-icons, kiwi-catalog und mullvad-socks5 haben keine
  LICENSE-Datei, und kiwi-killswitch nennt seine Lizenz nur in seiner README und
  seinem Manifest.
