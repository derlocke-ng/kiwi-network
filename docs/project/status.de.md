# Repositories & Status

Jedes Repository liegt unter [github.com/derlocke-ng](https://github.com/derlocke-ng).
„Veröffentlicht“ heißt ein Versions-Tag, und das ist es, was kiwi-updater
installiert. Die Versionen sind auf dem Stand von November 2026.

## Das Netzwerk { #the-network }

| Repository | Was es ist | Release | Katalog | Lizenz |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | das Netzwerk bauen und betreiben: Fleet-Datei → Installations-ISOs → Anwenden über SSH | v2.42.0 | ja | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | die 20 Module und ihr Renderer: eine Maschinendatei → ein Stack-Bundle | v0.23.0 | nein | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | die Maschinenseite: bringt ein Bundle auf eine Maschine und hält es am Laufen | v0.5.0 | nein | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | die SOCKS5-Proxys von Mullvad als Listen und DNS-Einträge, alle 6 Stunden neu gebaut | der Branch `list` | nein | MIT (README) |

## Menschen { #people }

| Repository | Was es ist | Release | Lizenz |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | der Motor föderierter Community-Hubs auf nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | der erste Hub: zehn Peer-to-Peer-Webtools ([live](https://derlocke-ng.github.io/armory/)) | folgt `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | ein Katalog von Hubs und ihren Apps | (eine Liste) | CC0 (README) |

## Der Desktop { #the-desktop }

| Repository | Was es ist | Release | Katalog | Lizenz |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installiert und aktualisiert Apps aus Git-Katalogen | v2.4.0 | ja | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | der Kiwi-App-Katalog | (eine Liste) | entfällt | keine angegeben |
| [ensconce](https://github.com/derlocke-ng/ensconce) | Einrichtung nach der Installation für Bluefin-DX | v2.5.0 | ja | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | Fail-Closed-VPN-Kill-Switch für GNOME | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | versiegelte SOCKS5/VPN-Ausgänge in rootless Podman | v0.7.3 | ja | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | Distro-Boxen, deren Verkehr nur über einen Ausgang hinausgeht | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | isolierte Browser-Identitäten an Ausgängen von kiwi-proxy | v0.7.1 | ja | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | kiwi-proxy-Provider: Tor | v0.3.0 | ja | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | kiwi-proxy-Provider: ein VPN über gluetun | v0.2.2 | ja | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | kiwi-proxy-Provider: 9proxy | v0.2.0 | ja | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | kiwi-proxy-Provider: Mysterium | v0.5.2 | ja | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | Bildschirm-Layouts für GNOME | v0.3.2 | ja | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | Zweiwege-Ordnersynchronisation als Benutzerdienste | v0.4.1 | ja | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | ja | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | SSH- und TLS-Schlüssel und -Zertifikate, offline im Browser ([live](https://derlocke-ng.github.io/kiwi-gen/)) | Webseite | nein | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | die App-Icons ([Vorschau](https://derlocke-ng.github.io/kiwi-icons/)) | keine Tags | nein | keine angegeben |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | diese Website und Dokumentation | entfällt | entfällt | AGPL-3.0 |

## Bekannte Lücken { #known-gaps }

Aus den Repositories selbst:

- **kiwi-server**: im Oktober–November 2026 auf Hardware erprobt, mit
  Node-Backups, die über Nodes hinweg wiederhergestellt wurden, und abgestimmter
  Tunnel-MTU, mobile Wege eingeschlossen. Mehrere Backup-Server, die automatische
  Wiederherstellung einer neu aufgebauten Maschine, ein Prune-Timer und ein
  Health-Check für einen hängenden kommerziellen Ausgang liegen auf den Branches
  `several-servers` von kiwi-server und kiwi-modules, noch nicht veröffentlicht.
  Föderation zwischen Netzwerken ist noch nicht erprobt. Nur IPv4, und die
  Debian-ISO gibt es nur für amd64. Die Control Plane ist entworfen, nicht gebaut.
- **kiwi-modules**: OpenCloud, Immich und Paperless-ngx sind „zum Ausprobieren“.
  Ein TURN-Server für Anrufe wartet darauf, gemergt zu werden.
- **kiwi-stack**: kein Rollback über das Wiederherstellen von Daten und das erneute
  Anwenden eines älteren Bundles hinaus.
- **kiwi-framework**: der Blog, Freigaben durch Moderatoren, das Folgen von Spaces,
  die ein Hub nicht mitbringt, und Signer nach NIP-07/NIP-46 kommen erst noch.
- **kiwi-updater**: ein gehostetes Verzeichnis vertrauenswürdiger Kataloge ist
  geplant. Die Release-Tags der anderen Apps sind noch nicht signiert, daher fragt
  die Root-Hälfte von kiwi-killswitch für Updates nach einem Passwort.
- **kiwi-proxy**: Sein kiwi-server-Modul ist noch auf keiner Maschine gelaufen.
  Ausgänge sind nur TCP und IPv4. Das VPN-Modul hält eine Konfiguration pro
  Maschine.
- **Provider-Module**: VPN und 9proxy sind nicht Ende-zu-Ende gegen ein echtes Konto
  geprüft; Mysterium schon (7. November 2026).
- **kiwi-custodia**: Einige Teile müssen noch auf einer echten Maschine gemessen
  werden (tun2socks in einem rootless Gateway, Compositors außer GNOME).
- **Lizenzen**: kiwi-icons, kiwi-catalog und mullvad-socks5 haben keine
  LICENSE-Datei, und kiwi-killswitch nennt seine Lizenz nur in seiner README und
  seinem Manifest.
