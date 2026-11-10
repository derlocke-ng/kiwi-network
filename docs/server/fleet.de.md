# Die Fleet-Datei

In der Fleet-Datei, `fleet.yaml`, beschreibst du jede Maschine deines Kiwi
Network. Für jede Maschine steht darin, welches Betriebssystem sie bekommt,
wofür sie gedacht ist und wie ihre Dienste eingerichtet werden. kiwi-server baut
jede Maschine nach dieser Beschreibung. Du schreibst also einmal auf, was du
haben willst, und musst keine Maschine von Hand konfigurieren.

Die Datei hat zwei Schlüssel. Unter `defaults` stehen die Einstellungen, die für
alle Hosts gelten, und unter `hosts` gibt es einen Eintrag pro Maschine. Eine
Einstellung im Eintrag eines Hosts überschreibt dieselbe Einstellung aus
`defaults`. `kiwi-server init` schreibt eine kommentierte Datei, mit der du
anfangen kannst. Die vollständige Referenz findest du in
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Jeder Host hat ein **Zielsystem**, also das Betriebssystem, das installiert
wird, und eine **Rolle**, also die Aufgabe, die die Maschine danach übernimmt.

- `target` ist `coreos`, `ucore` (Standard) oder `debian`. Siehe
  [Maschinen](machines.md).
- `role` ist `bare` (Standard), `master` oder `node`. Siehe [Rollen](roles.md).

## Beispiel { #example }

Diese Fleet-Datei beschreibt drei Maschinen. Die erste ist der Master, mit dem
sich alle anderen verbinden, auf einem Debian-VPS (einem gemieteten virtuellen
Server). Die zweite ist ein Gateway-Node, der den Verkehr eines lokalen Netzes
durch das VPN leitet. Die dritte ist ein Cloud-Node, auf dem Nextcloud und
Vaultwarden laufen.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # aus papaya wird papaya.home; Dienste heißen cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # wird vom ISO OHNE NACHFRAGE GELÖSCHT
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # der Master, ein Debian-VPS
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # damit verbinden sich Clients und Nodes

  lychee:                                # ein Gateway-Node
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # die Seite zum LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # ein Cloud-Node auf uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # für das erste Konto; danach wieder ausschalten
```

Im Beispiel stehen keine Passwörter für Dienste. Jedes Passwort, das du
weglässt, erzeugt kiwi-server aus dem Seed in `secrets/seed`, und
`kiwi-server secrets show fleet.yaml papaya` zeigt dir die Passwörter dieses
Hosts.

Auch die WireGuard-Konfigurationsdateien der Nodes stehen nicht im Beispiel.
`kiwi-server enroll` schreibt die Konfiguration eines Nodes nach
`secrets/<hostname>.conf`, und der VPN-Client des Nodes findet sie dort, ohne
dass sie in der Fleet-Datei eingetragen sein muss. Aus derselben Datei wird auch
die Mesh-Adresse des Nodes gelesen. Das Mesh ist das private WireGuard-Netzwerk,
in dem alle deine Maschinen hängen, und die Mesh-Adresse ist die Adresse einer
Maschine darin.

## Standardwerte { #defaults }

Ist ein Schlüssel weder in deinem `defaults`-Block noch bei einem Host gesetzt,
verwendet kiwi-server den eingebauten Wert aus dieser Tabelle.

| Schlüssel | Standard |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Kein Standardwert. `build` braucht ihn, und der Wert muss mit `/dev/` beginnen |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Setze einen `password_hash`, wenn du dich an der Konsole anmelden willst |
| `network` | `dhcp: true`. Für eine statische Adresse setzt du `address` (in CIDR-Schreibweise), `gateway` und `dns`. Oder du setzt einen `iprange`, aus dem die Hosts ihre Adressen in der Reihenfolge bekommen, in der sie in der Datei stehen |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (oder `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Die Tang-Ringe, an die die Festplatte gebunden ist. Ein Ring ist ein Tang-Server, mit dessen Hilfe eine verschlüsselte Maschine ihre Festplatte beim Start entsperrt (siehe [Betrieb](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | Die Hosts, auf die das Fleet-Verzeichnis gesichert wird, und wie viele Backups aufbewahrt werden (`hosts: []`, `keep: 10`) |
| `vps` | `server:` die ID, der Name oder der Spitzname eines netcup-Servers |

## Wie Einstellungen zusammenwirken { #how-settings-combine }

- Ein Host überschreibt die Standardwerte **Schlüssel für Schlüssel**. Er muss
  also nur die Schlüssel nennen, die abweichen. Ausnahmen sind die Listen
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` und die
  `coreos.*`-Listen: Die Einträge eines Hosts werden dort zu den Standardwerten
  *hinzugefügt*, statt sie zu ersetzen.
- Die Rollen, die aus Modulen bestehen, also `master` und `node`, haben ihre
  Einstellungen in einem Block, der wie die Rolle heißt (`master:` oder
  `node:`). In diesem Block stehen zuerst die **Stack-Einstellungen** und dann
  **ein Block pro Modul**. Der Stack umfasst alle Container, die eine Maschine
  für ihre Module betreibt, und die Stack-Einstellungen gelten für alle diese
  Container.
- Eine `modules:`-Liste in diesem Block **ersetzt** die Modulliste des Presets.
  Ein Preset ist eine fertige Liste von Modulen. Module, die von den
  aufgeführten vorausgesetzt werden, kommen automatisch dazu.
- **Datei-Einstellungen**, etwa Zertifikate und Konfigurationsdateien, gibst du
  als Pfade relativ zur Fleet-Datei an. kiwi-server kopiert den Inhalt dieser
  Dateien in das Rollenskript des Hosts, also das Skript, das die Maschine für
  ihre Rolle einrichtet.
- Eine Einstellung, die du ohne Wert schreibst, bekommt ihren Standardwert.
  Vertippst du dich bei einem Schlüssel, meldet kiwi-server einen Fehler und
  schlägt den Schlüssel vor, den du vermutlich gemeint hast.

## Stack-Einstellungen { #stack-settings }

Die Stack-Einstellungen gelten für den gesamten Stack einer Maschine. Du
schreibst sie direkt in den Block der Rolle.

| Einstellung | Standard | Hinweise |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` oder `minimal` |
| `runtime` | `podman` | `podman` betreibt die Container als podman-Quadlets, also als systemd-Units für Container. `docker` nutzt docker compose |
| `auto_update` | `registry` | `registry` führt einmal pro Woche `podman auto-update` aus. Mit `off` ändern sich die Container-Images nur, wenn du die Konfiguration des Hosts erneut anwendest |
| `docker_dir` | `/home/user/docker` | das Verzeichnis, in dem der Stack und seine Daten liegen |
| `service_user` | der Admin-Benutzer | der Benutzer, dem die Datenverzeichnisse gehören |
| `vpn_ip` | aus der WireGuard-Konfiguration | die Mesh-Adresse der Maschine |
| `master_ip` | aus der Fleet | die Mesh-Adresse des Masters |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | du kannst sie mit `kiwi-server mtu` messen |
| `docker_subnet` | `172.64.0.0/24` Master, `172.128.0.0/24` Node | |
| `pub_iface` | aus der Standardroute | die Netzwerkschnittstelle auf der LAN-Seite |
| `daily_vpn_restart` | `07:00` | ein leerer Wert schaltet den täglichen Neustart ab |
| `weekly_update` | `Sun *-*-* 00:00` | ein leerer Wert schaltet das wöchentliche Update ab |

`kiwi-server roles -v` und `kiwi-server modules -v` listen jede Einstellung mit
ihrem Standardwert auf.

## Prüfen, was du geschrieben hast { #checking-what-you-wrote }

kiwi-server kann die Fleet-Datei für dich prüfen und dir zeigen, was es für
einen Host daraus macht.

```bash
kiwi-server validate fleet.yaml          # Fehler und Warnungen
kiwi-server show fleet.yaml papaya          # die wirksame Konfiguration eines Hosts, Secrets verdeckt
```

kiwi-server prüft auch die Domain. `.local` lehnt es ab, bei `.lan` und bei
öffentlichen Top-Level-Domains warnt es (siehe
[DNS](../network/dns.md#names-servicehostnamehome)).

## Eine v1-Maschine übernehmen { #taking-over-a-v1-machine }

Eine Maschine, auf der einer der alten v1-Stacks lief, kannst du in die Fleet
aufnehmen, ohne ihre Daten zu verlieren. Die Standard-Laufzeit ist inzwischen
podman, und das Rollenskript stoppt keine docker-Container, die noch laufen.
Setze deshalb entweder `runtime: docker`, oder stoppe vorher den alten Stack.
Setze dann `docker_subnet` auf das Subnetz, das der alte Stack verwendet hat,
und benenne die Datenverzeichnisse nach den neuen Modulnamen um (`kmvpn-server`
→ `km-vpn-server`, `knvault` → `kn-vault`, …). Die Container behalten dann ihre
Adressen, und wg-easy behält seine Peers.
