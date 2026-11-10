# Die Fleet-Datei

`fleet.yaml` beschreibt jede Maschine, die kiwi-server baut. Sie hat zwei
Schlüssel: `defaults`, das für jeden Host gilt, und `hosts`, mit einem Eintrag pro
Maschine. Alles, was ein Host setzt, überschreibt die Standardwerte.
`kiwi-server init` schreibt einen kommentierten Ausgangspunkt, und die vollständige
Referenz ist
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Ein Host hat ein **Ziel** (was installiert wird) und eine **Rolle** (was aus ihm
wird):

- `target`: `coreos`, `ucore` (der Standard) oder `debian`. Siehe [Maschinen](machines.md).
- `role`: `bare` (der Standard), `master` oder `node`. Siehe [Rollen](roles.md).

## Beispiel { #example }

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # aus papaya wird papaya.home; Dienste sind cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # wird von der ISO ohne Rückfrage GELÖSCHT
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
        wg_host: vpn.example.org     # womit sich Clients und Nodes verbinden

  lychee:                                # ein Gateway-Node
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # die LAN-Seite
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # ein Cloud-Node auf uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # für das erste Konto; danach ausschalten
```

Darin stehen keine Dienstpasswörter. Jedes Passwort, das du weglässt, wird aus
`secrets/seed` erzeugt, und `kiwi-server secrets show fleet.yaml papaya` gibt sie
aus. Auch die WireGuard-Konfigurationen der Nodes werden nicht genannt:
`kiwi-server enroll` schreibt `secrets/<hostname>.conf`, das jeder Node von selbst
findet, und die Mesh-Adresse des Nodes wird daraus gelesen.

## Standardwerte { #defaults }

| Schlüssel | Standard |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | keiner; für `build` erforderlich, muss mit `/dev/` beginnen |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; gib einen `password_hash` für die Konsole an |
| `network` | `dhcp: true`; statisch mit `address` (CIDR), `gateway`, `dns` oder einer `iprange`, die Adressen in der Reihenfolge der Datei vergibt |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (oder `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Tang-Ringe, an die die Festplatte gebunden wird (siehe [Betrieb](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | wohin das Fleet-Verzeichnis gesichert wird (`hosts: []`, `keep: 10`) |
| `vps` | `server:` eine Server-ID, ein Name oder ein Spitzname bei netcup |

## Wie Einstellungen zusammenwirken { #how-settings-combine }

- Hosts überschreiben Standardwerte **Schlüssel für Schlüssel**. Die Listen
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` und die Listen
  `coreos.*` werden stattdessen zu den Standardwerten *hinzugefügt*.
- Eine Modulrolle hält ihre Einstellungen in einem Block, der nach der Rolle benannt
  ist (`master:`, `node:`): zuerst die **Stack-Einstellungen**, dann **ein Block pro
  Modul**.
- `modules:` in diesem Block **ersetzt** die Modulliste des Presets. Benötigte Module
  werden von selbst hinzugefügt.
- **Datei-Einstellungen** (Zertifikate, Konfigurationen) sind Pfade relativ zur
  Fleet-Datei. Ihr Inhalt wird in das Rollenskript des Hosts eingebettet.
- Eine Einstellung ohne Wert bedeutet den Standardwert. Ein falsch geschriebener
  Schlüssel ist ein Fehler, mit einem Vorschlag.

## Stack-Einstellungen { #stack-settings }

| Einstellung | Standard | Hinweise |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` oder `minimal` |
| `runtime` | `podman` | Podman-Quadlets; `docker` betreibt docker compose |
| `auto_update` | `registry` | wöchentliches `podman auto-update`; `off`: Images ändern sich mit einem Apply |
| `docker_dir` | `/home/user/docker` | der Stack und seine Daten |
| `service_user` | der Admin-Benutzer | besitzt die Datenverzeichnisse |
| `vpn_ip` | aus der WireGuard-Konfiguration | die Mesh-Adresse der Maschine |
| `master_ip` | aus der Fleet | die Mesh-Adresse des Masters |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | mit `kiwi-server mtu` messen |
| `docker_subnet` | `172.64.0.0/24` Master, `172.128.0.0/24` Node | |
| `pub_iface` | aus der Standardroute | die LAN-Schnittstelle |
| `daily_vpn_restart` | `07:00` | leer: nie |
| `weekly_update` | `Sun *-*-* 00:00` | leer: nie |

`kiwi-server roles -v` und `kiwi-server modules -v` listen jede Einstellung mit
ihrem Standardwert auf.

## Prüfen, was du geschrieben hast { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # errors and warnings
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server prüft auch die Domain: `.local` wird abgelehnt, `.lan` und öffentliche
Top-Level-Domains bekommen eine Warnung (siehe [DNS](../network/dns.md#names-servicehostnamehome)).

## Eine v1-Maschine übernehmen { #taking-over-a-v1-machine }

Eine Maschine, auf der einer der alten v1-Stacks lief, kann ohne Datenverlust
übernommen werden. Die Standard-Runtime ist jetzt podman, und das Rollenskript
stoppt keine docker-Container. Setz also entweder `runtime: docker`, oder stopp
vorher den alten Stack. Setz dann `docker_subnet` auf das, was der alte Stack
benutzt hat, und benenne die Datenverzeichnisse nach den Modulnamen um
(`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`, …). Die Container behalten
ihre Adressen, und wg-easy behält seine Peers.
