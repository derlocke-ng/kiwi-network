# kiwi-server

kiwi-server legt ein Kiwi Network an und verwaltet es. Du beschreibst jede Maschine
in einer einzigen `fleet.yaml`. kiwi-server erstellt für jeden Host eine
**unbeaufsichtigte Installations-ISO**, die Fedora CoreOS, uCore oder Debian
installiert und die Maschine ausschaltet. Dann **wendet** es die Rolle über SSH
**an** und macht aus der Maschine einen `kiwi-master` oder einen `kiwi-node`. Danach
arbeitet es weiter mit der Fleet: Es nimmt WireGuard-Clients auf, liest den Zustand
jeder Maschine, verwahrt die Secrets, sichert die Fleet und entsperrt verschlüsselte
Festplatten.

Es hat eine CLI, `kiwi-server`, und eine GTK4-App, **Kiwi Server**. Beide werden nach
`~/.local` installiert und brauchen kein root.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Aktuelles Release: **v2.42.0**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md).
- Gebaut auf [kiwi-modules](single.md) v0.23.0 (die Module und ihr Renderer) und
  [kiwi-stack](single.md) v0.5.0 (die Maschinenseite), mitgeliefert und per Tag
  festgelegt.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Installation { #install }

```bash
kiwi install kiwi-server        # mit kiwi-updater
```

Oder aus einem Checkout: `./install.sh install`, dann `kiwi-server doctor`.

Es braucht Python 3.9+ mit PyYAML und Jinja2, `openssl` und `ssh`. Der
Secret-Speicher braucht `age`. Zum Bauen von ISOs braucht es `butane`,
`coreos-installer` und `xorriso` (dazu `cpio`, `gzip` und `curl` für Debian). Auf
Silverblue oder Bluefin baust du sie als ein Container-Image, statt Pakete zu
schichten:

```bash
kiwi-server toolchain build     # wird automatisch benutzt, wenn die Werkzeuge fehlen
```

`qrencode` (für `enroll --qr`), `shellcheck` und `docker compose` sind optional.

## Vom Nichts zum laufenden Netzwerk { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # eine kommentierte fleet.yaml
$EDITOR fleet.yaml                        # Hosts, Rollen, dein SSH-Schlüssel, die Installationsfestplatte
kiwi-server secrets init fleet.yaml       # optional: secrets/ als ein mit age verschlüsselter Speicher
kiwi-server validate fleet.yaml

# der Master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   davon booten; sie installiert und schaltet aus; wieder einschalten
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# jeder Node: zuerst sein WireGuard-Client, dann das Medium, dann die Rolle
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# deine eigenen Geräte
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # was jede Maschine meldet
```

Medien tragen standardmäßig **keines der Secrets des Stacks**: nur das Basissystem.
Die Rolle und ihr Stack kommen mit `apply`. Ist eine Maschine nicht über SSH
erreichbar, legt `build --offline` stattdessen die ganze Rolle samt ihren Secrets
auf die ISO. Halte eine solche ISO vom ISO-Speicher eines Providers fern und lösche
sie nach der Installation.

**Gar keine ISO?** `kiwi-server script fleet.yaml papaya` gibt das Skript für eine
Maschine aus, die du selbst installiert hast (`--offline` für die ganze Rolle).

Auf einem netcup-VPS löscht `kiwi-server vps install fleet.yaml sorbet` den Server
und installiert die ISO über die API von netcup.

## Befehle { #commands }

| Befehl | Was er tut |
|---|---|
| `init [fleet.yaml]` | die Beispiel-Fleet-Datei schreiben (`--domain`, Standard `home`) |
| `validate fleet.yaml [host…]` | sie prüfen und dabei jeden Stack rendern, um Modulfehler zu finden |
| `list` / `show fleet.yaml <host>` | die Hosts und was erzeugt wurde / die wirksame Konfiguration eines Hosts, Secrets maskiert |
| `render fleet.yaml [host…]` | Rollenskripte, Stacks und Installationskonfigurationen nach `output/<host>/` |
| `build fleet.yaml [host…]` | rendern, dann die ISO: standardmäßig das Basissystem, `--offline` für die ganze Rolle |
| `script fleet.yaml <host>` | das Skript für jede beliebige Maschine (`--offline` für die ganze Rolle) |
| `apply fleet.yaml <host…>` | neu rendern, die Rolle über SSH schicken und ausführen (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | was die Maschinen melden: Rolle, Stack, Probleme, Festplatten, Backups, Zertifikate |
| `enroll fleet.yaml <host\|name>` | einen WireGuard-Client auf dem Master anlegen oder abholen (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` als eine mit age verschlüsselte Datei, in den Speicher geöffnet (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | die erzeugten Passwörter eines Hosts |
| `ca fleet.yaml` | die CA der Fleet |
| `mtu fleet.yaml <node\|device\|address>` | die echte MTU eines Tunnels messen und sagen, was einzustellen ist (`--write`) |
| `openwrt fleet.yaml` | ein Skript, das einen OpenWrt-Router ins Mesh bringt ([Router](../network/routers.md)) |
| `backup` / `restore` / `prune` | das Fleet-Verzeichnis auf Nodes und zurück; alte Maschinen-Backups entfernt ([Betrieb](operations.md)) |
| `unlock fleet.yaml <host>` | einen Tang-Ring an eine Maschine weiterreichen, die beim Booten wartet ([Betrieb](operations.md)) |
| `vps login\|list\|probe\|install` | die Server-Control-Panel-API von netcup |
| `roles [-v]`, `modules [-v]`, `targets` | was verfügbar ist, mit jeder Einstellung und ihrem Standardwert |
| `toolchain [status\|build]`, `doctor` | die ISO-Werkzeuge; diese Maschine prüfen |

Jeder Befehl nimmt `--porcelain` (JSON), `-o/--output-dir`, `--quiet` und `-v`.
`kiwi-server <command> -h` erklärt einen Befehl.

## Die App { #the-app }

**Kiwi Server** öffnet deine letzte Fleet. Die Seitenleiste hat eine Übersicht, eine
Zeile pro Host und die Standardwerte. Die *Overview* eines Hosts zeigt Live-Daten aus
`kiwi-server status` (einmal pro Minute abgefragt, solange das Fenster den Fokus hat,
nur lesend über SSH). Seine *Settings* sind ein Formular, das aus den Rollen und
Modulen gebaut wird. *Apply*, *Build* und *Render* führen die CLI aus und zeigen
laufend ihre Ausgabe, und *Build* listet die Festplatten, die es löschen wird, bevor
es startet. *Unlock* und *Lock* öffnen und schließen den Secret-Speicher. Die App
schreibt einfaches YAML, daher gehen Kommentare in einer von Hand geschriebenen
Fleet-Datei beim Speichern verloren.

## Vorsicht { #mind }

!!! danger "Die ISOs löschen die Festplatte, die man ihnen nennt"
    Beim Booten, ohne Rückfrage. Beschrifte sie. `disk:` ist genau deshalb für
    `build` erforderlich.

- **Die Ausgabe enthält Secrets**: Passwort-Hashes, WireGuard-Schlüssel,
  TLS-Schlüssel, LUKS-Schlüssel. Dateien werden mit 0600 geschrieben, und `output/`
  wird von git ignoriert. Behandle mit `--offline` erstellte ISOs genauso.
- **Dienstpasswörter werden erzeugt**, aus `secrets/seed`, wenn du sie in der
  Fleet-Datei weglässt. `validate` warnt vor Passwörtern, die darin stehen.
  `kiwi-server secrets show` gibt sie aus. Eine Maschine verweigert ein Apply, das
  mit einem anderen Seed erstellt wurde.
- **SSH-Host-Schlüssel** werden beim ersten Kontakt in `secrets/known_hosts`
  festgehalten, und ein geänderter Schlüssel wird abgelehnt (nach einer
  Neuinstallation die Zeile löschen).
- **Ein Rollenskript läuft als root.** Lies `kiwi-server script fleet.yaml <host>
  --offline`, bevor du einer Rolle vertraust, die du nicht selbst geschrieben hast.
- **Eine gescheiterte Rolle sagt es.** Die Maschine behält
  `/var/lib/kiwi-server/role.failed` (den Schritt und den Befehl), und `status`
  zeigt es an.

## Status { #status }

Die Pipeline wurde im Oktober und November 2026 auf Hardware erprobt. Debian, uCore
und Fedora CoreOS wurden auf zwei VPSes, einem Mini-PC und einer VM Ende-zu-Ende
gebootet, und eine Übung mit einem ausgefallenen Node baute eine verschlüsselte
Debian-Maschine in etwa 14 Minuten neu auf. Node-Backups wurden von einem Node auf
einem anderen wiederhergestellt (papaya auf lychee), und die Tunnel-MTU wurde auf
echten Wegen gemessen und abgestimmt, mobile eingeschlossen. Die CI rendert jede
Rolle, prüft jedes Skript mit shellcheck, validiert jede Butane-Konfiguration und
hält vier Referenz-Stacks Byte für Byte fest.

Noch nicht erprobt: Föderation zwischen Netzwerken. Alles ist IPv4. Die Debian-ISO
gibt es nur für amd64. Eine geplante Control Plane (`kiwi-server serve`) ist
entworfen, aber nicht gebaut.

Weiterlesen: [Die Fleet-Datei](fleet.md) · [Rollen](roles.md) · [Module](modules.md) ·
[Maschinen](machines.md) · [Betrieb](operations.md) ·
[Eine Maschine ohne Fleet](single.md)
