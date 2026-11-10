# Maschinen: installieren, anwenden, aktualisieren

## Ziele { #targets }

| Ziel | Was installiert wird | Installationsmedium |
|---|---|---|
| `coreos` | Fedora CoreOS, Stream stable | die Standard-Live-ISO, angepasst mit dem Ignition des Hosts (Butane `fcos` 1.6.0); für die Installation ist kein Netzwerk nötig |
| `ucore` | Fedora CoreOS, das sich selbst auf ein Image `ghcr.io/ublue-os/ucore*` rebased (`ucore-minimal`, `ucore`, `ucore-hci`, mit `-nvidia` / `-zfs`), wie im Autorebase-Beispiel von uCore selbst | wie bei CoreOS, plus die Autorebase-Units |
| `debian` | Debian stable (trixie), amd64 | das Standard-netinst mit dem Preseed in seiner initrd, sodass es ab der ersten Frage antwortet, und die Dateien des Hosts unter `/kiwi-server`; Booten per BIOS und UEFI bleibt erhalten |

Der Admin-Benutzer bekommt überall sudo ohne Passwort. SSH nimmt nur Schlüssel an,
außer du setzt `ssh_password_auth: true`.

## Installationsmedien { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Eine ISO installiert auf `disk:` **ohne Rückfrage** und **schaltet die Maschine
  dann aus** (`install.on_done: poweroff` oder `reboot`). Beschrifte deine Sticks.
- Standardmäßig tragen die Medien **nur das Basissystem**: Hostname, Netzwerk,
  Admin-Benutzer und Schlüssel, Update-Richtlinie. Keines der Secrets des Stacks ist
  darauf. Die Rolle kommt später mit `apply`.
- `--offline` legt die ganze Rolle samt ihren Secrets auf die ISO, für eine Maschine,
  die SSH nicht erreicht. Wer diese ISO hat, hat diese Secrets.
- Der Live-Installer zeigt die Festplatten (`lsblk`) und hat eine Shell mit dem
  Konsolenpasswort und den Schlüsseln der Fleet.

## Anwenden { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # per Name, Adresse oder Mesh-Adresse
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # beim ersten Mal per Adresse
```

`apply` rendert den Host neu und schickt sein Rollenskript über SSH nach
`/var/lib/kiwi-server/role.sh`. Es führt das Skript als root aus, bindet dann die
Festplatte an ihre Tang-Ringe und sichert auf einem Master den WireGuard-Zustand
zusammen mit den Secrets der Fleet. Auf einer verschlüsselten Debian-Maschine
ersetzt das erste Apply den einmaligen Installationsschlüssel. SSH benutzt den
eigenen Schlüssel der Fleet und prüft Host-Schlüssel gegen `secrets/known_hosts`.
`apply` und `status` finden eine Maschine über ihren Namen, ihre statische Adresse,
die öffentliche Adresse des Masters oder ihre Mesh-Adresse, aber nur über Adressen,
deren Host-Schlüssel festgehalten ist.

Bei einer Modulrolle übergibt das Skript den Stack an `kiwi-stack`:

1. Es installiert oder aktiviert podman 4.4+ (unter Debian mit `netavark`,
   `aardvark-dns` und `catatonit`) oder docker sowie den Dienstbenutzer.
2. Es lädt Kernel-Module und setzt sysctls. Mit Pi-hole zieht aardvark-dns auf Port
   5533 um, und der Host löst über das Pi-hole des Stacks auf. Außerdem vertraut es
   dem Mesh in firewalld.
3. Es lehnt einen Stack ab, der aus einem anderen Seed gerendert wurde. Es entpackt
   den Stack nach `docker_dir`, installiert die Quadlets in
   `/etc/containers/systemd` und die Host-Units und entfernt, was ein entferntes
   Modul installiert hatte.
4. Es öffnet die Ports des Stacks in firewalld oder ufw, falls eines davon aktiv ist.
5. Es lädt jedes Image und startet dann `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Es führt `kiwi-stack verify` aus: Jeder Container muss laufen, sonst scheitert
   das Apply und sagt, welcher Schritt gescheitert ist.

Dasselbe Rendering noch einmal anzuwenden ändert nichts, und ein neues Rendering
ersetzt, was sich geändert hat. Ein erneutes Apply startet allerdings jeden
Container des Stacks neu.

## Erster Start { #first-boot }

`kiwi-role.service` führt `/var/lib/kiwi-server/role.sh` einmal aus, nachdem das
Netzwerk steht (und wartet bis zu 120 Sekunden auf DNS). `role.done` wird erst
geschrieben, wenn jeder Container läuft. Ein Fehlschlag hinterlässt
`/var/lib/kiwi-server/role.failed` (den Schritt und den Befehl) und wird beim
nächsten Booten erneut versucht. Das Log ist `/var/log/kiwi-server-role.log`. Unter
uCore wartet die Rolle, bis das Image signiert ist.
`sudo bash /var/lib/kiwi-server/role.sh --force` führt sie erneut aus.

## Updates { #updates }

Updates werden laufend installiert. Der **Neustart** in sie hinein geschieht nur
innerhalb deines Zeitfensters (`updates.days`, `time`, `length_minutes`, Ortszeit):

| Ziel | Installiert Updates | Startet neu |
|---|---|---|
| `coreos` | Zincati, laufend | nur im Zeitfenster (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` bereitet sie vor | `kiwi-staged-reboot.timer` im Zeitfenster |
| `debian` | unattended-upgrades, täglich | `kiwi-reboot-if-required.timer` im Zeitfenster, wenn einer nötig ist |

`updates.days: []` heißt an jedem Tag, und `updates.enabled: false` schaltet alles
ab. Eine verschlüsselte Maschine, deren Tang-Ring hineingereicht werden muss,
startet nicht von selbst neu.

Die Container haben ihren eigenen Zeitplan: Ein wöchentliches `kiwi-stack update`
(Sonntag 00:00) führt `podman auto-update` aus, solange `auto_update: registry`
gesetzt ist. Ein täglicher Neustart des VPN-Clients um 07:00 sorgt für eine frische
Ausgangsadresse.

## Auf der Maschine: `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # Container, Host-Units, verify
sudo kiwi-stack verify          # läuft jeder Container?
sudo kiwi-stack logs [service]  # aus dem Journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # der VPN-Client und jeder Container in seinem Namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # mit dem Backup-Modul
sudo kiwi-stack apply DIR       # ein Stack-Bundle, ohne Rollenskript
```

Der Stack liegt in `docker_dir` (Standard `/home/user/docker`) und seine
Einstellungen in `/etc/kiwi-server/stack.env`. Die Units sind `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` und `kiwi-stack-update.timer`, plus alle, die ein
Modul hinzufügt.

## Was ein Rendering erzeugt { #what-a-render-produces }

`output/<host>/` enthält:

| Datei | Was |
|---|---|
| `<host>.role.sh` | die Rolle als ein Skript: Einstellungen, der Stack (eingebettet), der Befehl und die Bibliothek von kiwi-stack und der Rumpf der Rolle. Modus 0600 |
| `<host>.stack/` | das Stack-Bundle, zur Durchsicht: `docker-compose.yml`, `quadlets/`, Modulkonfigurationen, Host-Units und `stack.sh`. `kiwi-stack apply` kann es von Hand installieren |
| `<host>.bu`, `<host>.ign` | CoreOS und uCore: Butane und Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: das Preseed und die Dateien, die es hineinkopiert |
| `<host>.iso` | der unbeaufsichtigte Installer |
