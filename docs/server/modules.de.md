# Module

Ein Modul ist ein Dienst einer Maschine im Kiwi Network. Eine [Rolle](roles.md)
wählt eine Reihe von Modulen aus, und der Renderer macht daraus einen **Stack** für
einen Host. Der Renderer ist [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules),
das kiwi-server mitbringt. Der Stack besteht aus einer Compose-Datei,
**Podman-Quadlets** (eine systemd-Unit pro Container), den Konfigurationen und
Host-Units und `stack.sh`, dem Manifest, das sie alle nennt.
[kiwi-stack](single.md) bringt ihn auf die Maschine. Alles Templating geschieht auf
der Maschine, die rendert. Das Ziel braucht nur podman 4.4 oder neuer (oder docker
mit dem Compose-Plugin, mit `runtime: docker`).

```bash
kiwi-server modules -v      # jedes Modul und jede Einstellung mit ihrem Standardwert
```

## Das Netzwerk { #the-network }

| Modul | Was es ist | Läuft auf | Benötigt | Auf dem Host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: der Einstiegspunkt für jeden Client und jeden Node; seine Standardroute ist der VPN-Client (der Double Hop) | Master | nichts | `51820/udp`; die Oberfläche auf `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: der Tunnel, an dem jede Maschine hängt: auf einem Node zum Master, auf dem Master zu einem kommerziellen VPN | beiden | nichts | nichts |
| `dns` | **Pi-hole 6**: blockiert Werbung für das Mesh oder das LAN, liefert die Namen der Fleet und optional die SOCKS5-Proxys von Mullvad per Name | beiden | nichts | `53` auf einem Node |
| `tor` | ein **Tor-SOCKS5**-Proxy für Mesh-Clients, auf Länder festgelegt | beiden | nichts | `127.0.0.1:9050` auf einem Node; die Mesh-Adresse `:9050` auf einem Master |
| `reverse-proxy` | **nginx** mit TLS: ein Server-Block pro Dienst; Admin-Seiten antworten nur dem Mesh; optional öffentliche Namen mit Let's Encrypt | beiden | nichts | `80`, `443` auf einem Node oder auf einem öffentlichen Master |
| `gateway` | Policy-Routing auf dem Host: LAN-Clients, die diese Maschine als Gateway benutzen, gehen über das VPN hinaus | Node | vpn-client | eine Host-Unit |
| `dhcp-relay` | leitet das DHCP des LANs an Pi-hole weiter, sodass Pi-hole der DHCP-Server des LANs sein kann | Node | dns | `67/udp` |

## Dienste { #services }

| Modul | Was es ist | Läuft auf | Benötigt |
|---|---|---|---|
| `cloud` | **Nextcloud** aus den Containern des AIO-Projekts, *ohne* den AIO-Master-Container (kein Docker-Socket, läuft unter podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, Volltextsuche und Whiteboard sind Schalter | Node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, der Bitwarden-kompatible Passwortmanager | Node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** und **JDownloader** im Netzwerk-Namespace des VPN-Clients: kein Tunnel, kein Verkehr | Node | vpn-client |
| `sftp` | ein SFTP-Server auf einem eigenen Port (`2224`), um Downloads abzuholen | Node | nichts |
| `portainer` | **Portainer CE**, eine Web-Oberfläche für die Container (`127.0.0.1:9443` und `portainer.<host>`) | beiden | nichts |
| `opencloud` | **OpenCloud**: Dateien und Teilen in einem einzigen Go-Binary (zum Ausprobieren) | Node | vpn-client, reverse-proxy |
| `immich` | **Immich**: Fotos und Videos (zum Ausprobieren) | Node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: gescannte Dokumente mit OCR und Volltextsuche (zum Ausprobieren) | Node | vpn-client, reverse-proxy |

Die letzten drei stecken in keinem Preset; füge sie zu `modules:` hinzu.

## Menschen { #people }

| Modul | Was es ist | Läuft auf | Benötigt |
|---|---|---|---|
| `nostr-relay` | **strfry**, das Relay, auf dem ein Hub seine Events hält (unter `relay.<host>`). Aus dem Internet dürfen Mitglieder posten, nachdem sie ihren Schlüssel nachgewiesen haben (NIP-42): `approved`-Schlüssel auf der signierten Liste der Admins oder jeder, der mit einem Konto `registered` ist. Das Mesh darf immer posten | Master | reverse-proxy |
| `hub` | ein **kiwi-framework-Hub** als Container (standardmäßig Armory, unter `hub.<host>`), privat, halböffentlich oder öffentlich | Master | reverse-proxy |

Siehe [Einen eigenen Hub betreiben](../people/hubs.md).

## Backups und Festplatten { #backups-and-disks }

| Modul | Was es ist | Läuft auf | Benötigt |
|---|---|---|---|
| `backup` | die Daten dieser Maschine mit **restic**, verschlüsselt, auf einen Backup-Server-Node: nachts um `03:00` (innerhalb von 15 Minuten danach) und mit `kiwi-stack backup`. Jedes Modul sagt, was davon aufbewahrt wird. Nächstes Release: mehrere Server und eine neu aufgebaute Maschine, die sich selbst wiederherstellt ([Details](operations.md#coming-in-the-next-release)) | beiden | nichts |
| `backup-server` | ein **restic-REST-Server**; jede Maschine erreicht nur ihr eigenes Repository, nur anhängend | Node | vpn-client, reverse-proxy |
| `tang` | **Tang**-Server, damit verschlüsselte Maschinen beim Booten entsperren; ein Ring ist ein Server mit eigenen Schlüsseln (Standard `infra` auf `7500`) | Node | nichts |

Siehe [Betrieb](operations.md).

## Wichtige Einstellungen { #important-settings }

| Modul | Einstellung | Standard | Hinweise |
|---|---|---|---|
| vpn-server | `wg_host` | (erforderlich) | der Name oder die IP, mit der sich Clients verbinden |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | siehe [Client-Gruppen](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | Tang-Ports für Maschinen hinter NAT |
| vpn-client | `vpn_provider` | `custom` | `custom`: die WireGuard-Konfiguration, die der Master ausgestellt hat (ein Node); oder ein gluetun-Anbieter (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | wo ein kommerzieller Ausgang liegt |
| | `dot_providers` | `quad9` | das DNS-over-TLS von gluetun |
| | `extra_dnat_rules` | `[]` | z. B. SSH aus dem Mesh zum Host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | nur, solange der Master nicht erreichbar ist |
| | `dhcp_enabled` | `false` | mit `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` auf einem Master | [die Proxys von Mullvad per Name](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | Eingangs- und Ausgangs-Nodes, `StrictNodes` |
| reverse-proxy | `public` | `false` | nur Master: 80/443 mit Let's Encrypt für Namen außerhalb der Domain der Fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | auf eine große Festplatte zeigen lassen |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | für das erste Konto einschalten, dann aus |
| downloader | `download_dir` | (erforderlich) | |
| nostr-relay | `members` | `approved` | oder `registered` |
| | `write_pubkeys` | `[]` | die Admins: Sie dürfen immer posten, und nur ihre Mitglieder- und Sperrlisten zählen |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | jeder kiwi-framework-Hub |
| | `public_relays`, `public_mounts` | `[]` | ein halböffentlicher Hub |
| backup | `server` | (erforderlich) | `https://…` eines Backup-Server-Nodes, der diese Maschine aufführt |
| tang | `rings` | `{ infra: "7500" }` | Name und Port |

Passwörter und Schlüssel, die du weglässt, werden aus dem Seed der Fleet erzeugt.

## Namen { #names }

Jedes Modul kündigt seine Namen beim Reverse Proxy und beim DNS der Fleet an,
unterhalb des Namens des Hosts:

| Dienst | Name |
|---|---|
| wg-easy (Master) | `wg.<host>` |
| Pi-hole (jeder Host mit `dns` und dem Reverse Proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| Relay / Hub | `relay.<host>` / `hub.<host>` |
| Backup-Server | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Container { #containers }

- Unter podman ist jeder Dienst ein Quadlet in `/etc/containers/systemd`, gestartet
  über `kiwi-stack.target`, mit seinem Log im Journal. Ein Container, der im
  Netzwerk-Namespace eines anderen lebt, ist an diesen gebunden und kommt mit ihm
  zurück.
- Secrets landen in Dateien `kiwi/env/<service>.env`, die nur root lesen kann, nie in
  den Units.
- Feste Adressen folgen dem v1-Plan, sodass eine migrierte Maschine sie behält:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Andere Module zählen ab `.100` hoch. Container ohne feste Adresse benutzen
  das dritte Viertel des Netzwerks (`.128/26`).
- Fedora CoreOS und uCore laufen mit eingeschaltetem SELinux, daher tragen
  Bind-Mounts das Label `:z`. Mounts des Container-Sockets und von `/lib/modules`
  werden nie gelabelt.

## Ein Modul schreiben { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` deklariert die Metadaten und Node-Typen des Moduls, seine
Abhängigkeiten, die Host-Ports, die es öffnet, seine Templates und wohin ihre
Ausgabe geht, Speicher, was davon gesichert wird, die Host-Integration (sysctls,
Kernel-Module), die nginx-Server-Blöcke, die es ankündigt, die URLs, die ausgegeben
werden, wenn die Rolle fertig ist, seine Validierungsregeln und seine `settings`.
Das Settings-Schema validiert die Fleet-Datei und baut das Formular der App.
Templates sind Jinja2 und sehen den Host-Kontext: Name und Typ des Hosts, die
Adresse jedes Moduls, das Mesh, die Namen der Fleet, jedes aktivierte Modul und die
Einstellungen jedes Moduls.

Unter podman wird die Compose-Datei in Quadlets übersetzt. Nur eine bekannte Menge
von Compose-Schlüsseln wird übersetzt, und alles andere ist beim Rendern ein Fehler.

Module werden in [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules)
entwickelt und veröffentlicht. Die vollständige Referenz des Formats ist
[docs/modules.md von kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
