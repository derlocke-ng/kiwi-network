# Module

Ein Modul ist ein Dienst, den eine Maschine in deinem Kiwi Network übernehmen
kann, zum Beispiel der VPN-Server, der DNS-Server mit Werbeblocker, Nextcloud
oder das nächtliche Backup. Über die Module legst du fest, was jede Maschine
tut. Eine [Rolle](roles.md) bringt eine Auswahl an Modulen mit, und in der
Fleet-Datei kannst du diese Auswahl ändern.

Ein Renderer macht aus den Modulen eines Hosts einen **Stack**, also alles, was
die Maschine braucht, um diese Dienste zu betreiben. Der Renderer ist
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), und kiwi-server
enthält eine Kopie davon. Ein Stack besteht aus einer Compose-Datei,
**podman-Quadlets** (eine systemd-Unit pro Container), den
Konfigurationsdateien, den systemd-Units für den Host und `stack.sh`, einem
Manifest, das all das auflistet. [kiwi-stack](single.md) installiert den Stack
auf der Maschine. Alle Vorlagen werden auf dem Rechner ausgefüllt, der den Stack
erzeugt. Die Maschine, auf der der Stack läuft, braucht nur podman 4.4 oder
neuer oder, wenn du `runtime: docker` setzt, docker mit dem Compose-Plugin.

Dieser Befehl listet jedes Modul mit seinen Einstellungen auf.

```bash
kiwi-server modules -v      # jedes Modul und jede Einstellung mit ihrem Standardwert
```

## Das Netzwerk { #the-network }

Diese Module bauen das Mesh auf, also das private WireGuard-Netzwerk, in dem
alle deine Maschinen hängen, und sie bestimmen, wie dessen Verkehr ins Internet
gelangt.

| Modul | Was es ist | Läuft auf | Setzt voraus | Auf dem Host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, der WireGuard-Server, mit dem sich jeder Client und jeder Node verbindet. Seine Standardroute ist der VPN-Client, Verkehr ins Internet läuft also weiter über das kommerzielle VPN des Masters (der Double Hop) | Master | nichts | `51820/udp` und die Weboberfläche unter `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, der VPN-Tunnel, durch den der Verkehr einer Maschine läuft. Auf einem Node führt der Tunnel zum Master, auf dem Master zu einem kommerziellen VPN | Master und Node | nichts | nichts |
| `dns` | **Pi-hole 6**, ein DNS-Server, der für das Mesh oder das LAN Werbung blockiert. Er beantwortet die Namen der Fleet und kann außerdem Namen für die SOCKS5-Proxys von Mullvad bereitstellen | Master und Node | nichts | `53` auf einem Node |
| `tor` | Ein **Tor-SOCKS5**-Proxy für Clients im Mesh. Er nutzt nur Tor-Knoten in den Ländern, die du festlegst | Master und Node | nichts | `127.0.0.1:9050` auf einem Node, auf einem Master die Mesh-Adresse `:9050` |
| `reverse-proxy` | **nginx** mit TLS. Es hat einen Server-Block pro Dienst, sodass jeder Dienst unter seinem eigenen Namen erreichbar ist. Admin-Seiten sind nur aus dem Mesh erreichbar. Öffentliche Namen mit Let's-Encrypt-Zertifikaten sind optional | Master und Node | nichts | `80`, `443` auf einem Node, oder auf einem Master mit eingeschaltetem `public` |
| `gateway` | Policy-Routing auf dem Host. Geräte im LAN, die diese Maschine als Gateway nutzen, schicken ihren Internetverkehr durch das VPN | Node | vpn-client | eine systemd-Unit auf dem Host |
| `dhcp-relay` | Reicht die DHCP-Anfragen des LAN an Pi-hole weiter, damit Pi-hole der DHCP-Server des LAN sein kann | Node | dns | `67/udp` |

## Dienste { #services }

| Modul | Was es ist | Läuft auf | Setzt voraus |
|---|---|---|---|
| `cloud` | **Nextcloud**, aufgebaut aus den Containern des AIO-Projekts, aber *ohne* dessen Master-Container. Es braucht deshalb keinen docker-Socket und läuft unter podman. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, die Volltextsuche und Whiteboard lassen sich jeweils ein- und ausschalten | Node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, ein Passwortmanager, der mit Bitwarden kompatibel ist | Node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** und **JDownloader**. Beide laufen im Netzwerk-Namespace des VPN-Clients, nutzen also dessen Netzwerkverbindung und haben keine eigene. Solange der Tunnel nicht steht, übertragen sie nichts | Node | vpn-client |
| `sftp` | Ein SFTP-Server auf einem eigenen Port (`2224`), über den du die Downloads abholen kannst | Node | nichts |
| `portainer` | **Portainer CE**, eine Weboberfläche für die Container. Erreichbar unter `127.0.0.1:9443` und unter `portainer.<host>` | Master und Node | nichts |
| `opencloud` | **OpenCloud** für Dateien und zum Teilen von Dateien, als ein einziges Go-Programm (zum Ausprobieren) | Node | vpn-client, reverse-proxy |
| `immich` | **Immich** für Fotos und Videos (zum Ausprobieren) | Node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx** für eingescannte Dokumente, mit Texterkennung (OCR) und Volltextsuche (zum Ausprobieren) | Node | vpn-client, reverse-proxy |

Die letzten drei Module gehören zu keinem Preset. Wenn du eines davon nutzen
willst, trag es in `modules:` ein.

## Hubs { #people }

Ein Hub ist die eigene Seite einer Community im Browser. Diese beiden Module
betreiben einen Hub und das Relay, auf dem der Hub seine Events speichert.

| Modul | Was es ist | Läuft auf | Setzt voraus |
|---|---|---|---|
| `nostr-relay` | **strfry**, das Relay, auf dem ein Hub seine Events ablegt. Erreichbar unter `relay.<host>`. Wer sich aus dem Internet verbindet, darf nur schreiben, wenn er Mitglied ist und nachgewiesen hat, dass ihm sein Schlüssel gehört (NIP-42). Mit `approved` sind die Mitglieder die Schlüssel auf einer Liste, die die Admins signieren. Mit `registered` ist jeder Mitglied, der ein Konto hat. Verbindungen aus dem Mesh dürfen immer schreiben | Master | reverse-proxy |
| `hub` | Ein **kiwi-framework-Hub**, der als Container läuft. Standardmäßig ist das Armory, erreichbar unter `hub.<host>`. Ein Hub kann privat, halböffentlich oder öffentlich sein | Master | reverse-proxy |

Siehe [Einen eigenen Hub betreiben](../people/hubs.md).

## Backups und Festplatten { #backups-and-disks }

| Modul | Was es ist | Läuft auf | Setzt voraus |
|---|---|---|---|
| `backup` | Sichert die Daten dieser Maschine verschlüsselt mit **restic** auf einen Node, auf dem das Modul backup-server läuft. Das Backup läuft jede Nacht um `03:00` oder bis zu 15 Minuten später und außerdem immer dann, wenn du `kiwi-stack backup` ausführst. Jedes Modul legt selbst fest, welche seiner Daten gesichert werden. Für das nächste Release sind Backups auf mehrere Server geplant und dass eine neu aufgesetzte Maschine ihre Daten selbst wiederherstellt ([Details](operations.md#coming-in-the-next-release)) | Master und Node | nichts |
| `backup-server` | Ein **restic-REST-Server**, der die Backups speichert. Jede Maschine erreicht nur ihr eigenes Repository und kann dort nur etwas hinzufügen, nicht löschen (append-only) | Node | vpn-client, reverse-proxy |
| `tang` | **Tang**-Server, mit deren Hilfe Maschinen ihre verschlüsselten Festplatten beim Start entsperren, ohne dass jemand dabei sein muss. Ein Ring ist ein Tang-Server mit eigenen Schlüsseln. Standardmäßig gibt es einen Ring namens `infra` auf Port `7500` | Node | nichts |

Siehe [Betrieb](operations.md).

## Wichtige Einstellungen { #important-settings }

| Modul | Einstellung | Standard | Hinweise |
|---|---|---|---|
| vpn-server | `wg_host` | (Pflicht) | der Name oder die IP-Adresse, mit der sich Clients verbinden |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | siehe [Client-Gruppen](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | Ports auf dem Master, über die Maschinen hinter NAT ihren Tang-Ring erreichen |
| vpn-client | `vpn_provider` | `custom` | `custom` verwendet die WireGuard-Konfiguration, die der Master ausgestellt hat, und das braucht ein Node. Ansonsten gibst du einen Anbieter an, den gluetun kennt (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | die Länder und Städte der kommerziellen VPN-Server, die genutzt werden sollen |
| | `dot_providers` | `quad9` | der DNS-over-TLS-Anbieter, den gluetun nutzt |
| | `extra_dnat_rules` | `[]` | zusätzliche Weiterleitungsregeln, zum Beispiel für SSH aus dem Mesh auf den Host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | wird nur genutzt, solange der Master nicht erreichbar ist |
| | `dhcp_enabled` | `false` | zusammen mit `dhcp_start`, `dhcp_end` und `dhcp_router` |
| | `mullvad_socks` | `true` auf einem Master | [die Proxys von Mullvad per Namen](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | die Länder der Tor-Eingangs- und Exit-Knoten, durchgesetzt mit `StrictNodes` |
| reverse-proxy | `public` | `false` | nur auf dem Master. Öffnet 80/443 und nutzt Let's Encrypt für Namen außerhalb der Fleet-Domain |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | leg es auf eine große Festplatte |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | einschalten, um das erste Konto anzulegen, danach wieder ausschalten |
| downloader | `download_dir` | (Pflicht) | |
| nostr-relay | `members` | `approved` | oder `registered` |
| | `write_pubkeys` | `[]` | die Schlüssel der Admins. Admins dürfen immer schreiben, und nur ihre Mitglieder- und Sperrlisten gelten |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | das Image eines beliebigen Hubs, der mit kiwi-framework gebaut ist |
| | `public_relays`, `public_mounts` | `[]` | für einen halböffentlichen Hub |
| backup | `server` | (Pflicht) | die `https://…`-Adresse eines Backup-Server-Nodes, der diese Maschine in seiner Liste führt |
| tang | `rings` | `{ infra: "7500" }` | Name und Port jedes Rings |

Lässt du ein Passwort oder einen Schlüssel weg, wird er aus dem Seed der Fleet
erzeugt.

## Namen { #names }

Jedes Modul meldet die Namen seiner Dienste beim Reverse-Proxy und im DNS der
Fleet an. Jeder Name setzt sich aus dem Namen des Dienstes und dem Namen des
Hosts zusammen.

| Dienst | Name |
|---|---|
| wg-easy (Master) | `wg.<host>` |
| Pi-hole (jeder Host mit `dns` und dem Reverse-Proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| Relay / Hub | `relay.<host>` / `hub.<host>` |
| Backup-Server | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Container { #containers }

- Unter podman ist jeder Dienst ein Quadlet in `/etc/containers/systemd`.
  Gestartet werden die Quadlets über `kiwi-stack.target`, und ihre Logs landen
  im systemd-Journal. Ein Container, der den Netzwerk-Namespace eines anderen
  Containers mitbenutzt, ist an diesen gebunden und wird deshalb zusammen mit
  ihm neu gestartet.
- Secrets werden in `kiwi/env/<service>.env`-Dateien geschrieben, die nur root
  lesen kann. In den Units selbst stehen sie nie.
- Die Container haben feste Adressen nach dem Adressplan von v1. Eine Maschine,
  die von v1 übernommen wurde, behält deshalb ihre Adressen. Die Adressen sind:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` und
  sftp `.251`. Andere Module bekommen Adressen, die ab `.100` hochgezählt
  werden. Container ohne feste Adresse bekommen eine aus dem dritten Viertel des
  Netzes (`.128/26`).
- Fedora CoreOS und uCore laufen mit eingeschaltetem SELinux, deshalb bekommen
  Bind-Mounts das Label `:z`. Die Mounts des Container-Sockets und von
  `/lib/modules` bekommen nie ein Label.

## Ein eigenes Modul schreiben { #writing-a-module }

Ein Modul ist ein Verzeichnis mit diesen Dateien:

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` beschreibt das Modul. Darin stehen die Metadaten des Moduls und
die Node-Typen, auf denen es läuft, seine Abhängigkeiten und die Ports, die es
auf dem Host öffnet. Es nennt die Vorlagen des Moduls und wohin deren Ausgabe
geschrieben wird, seine Speicherorte und welche seiner Daten gesichert werden.
Außerdem legt es die Einbindung in den Host fest (sysctls und Kernelmodule), die
nginx-Server-Blöcke, die das Modul anmeldet, die URLs, die nach dem Einrichten
der Rolle ausgegeben werden, die Prüfregeln und die `settings` des Moduls.

Das Schema der Einstellungen dient zwei Zwecken: Es prüft die Fleet-Datei, und
die App Kiwi Server baut daraus ihr Einstellungsformular. Die Vorlagen sind in
Jinja2 geschrieben und können auf den Kontext des Hosts zugreifen. Dazu gehören
der Name und der Typ des Hosts, die Adresse jedes Moduls, das Mesh, die Namen
der Fleet, die eingeschalteten Module und die Einstellungen jedes Moduls.

Unter podman wird die Compose-Datei in Quadlets übersetzt. Die Übersetzung kennt
eine feste Auswahl an Compose-Schlüsseln. Jeder andere Schlüssel führt zu einem
Fehler, wenn der Stack erzeugt wird.

Module werden in [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules)
entwickelt und veröffentlicht. Die vollständige Referenz des Formats steht in
[docs/modules.md von
kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
