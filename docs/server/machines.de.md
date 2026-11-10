# Maschinen: installieren, einrichten, aktualisieren

Diese Seite begleitet eine Maschine von ihrem Eintrag in der Fleet-Datei bis zum
laufenden System, das sich selbst aktualisiert. kiwi-server baut ein
Installations-Image, das das Betriebssystem installiert, ohne dass jemand an der
Tastatur sitzt. Danach richtet es die Maschine mit dem Befehl `apply` per SSH
für ihre Rolle ein. Von da an installiert die Maschine ihre Updates selbst und
startet nur zu den Zeiten neu, die du erlaubst.

## Zielsysteme { #targets }

Das Zielsystem ist das Betriebssystem, das kiwi-server auf einer Maschine
installiert.

| Zielsystem | Was installiert wird | Installationsmedium |
|---|---|---|
| `coreos` | Fedora CoreOS, Stream „stable“ | Das unveränderte Live-ISO, ergänzt um die Ignition-Konfiguration des Hosts (Butane `fcos` 1.6.0). Die Installation braucht keine Netzwerkverbindung |
| `ucore` | Fedora CoreOS, das danach selbst auf ein `ghcr.io/ublue-os/ucore*`-Image wechselt (Rebase). Die Images sind `ucore-minimal`, `ucore` und `ucore-hci`, jeweils auch mit `-nvidia` / `-zfs`. Der Rebase funktioniert wie im Autorebase-Beispiel von uCore selbst | Dasselbe wie bei CoreOS, dazu die Autorebase-Units |
| `debian` | Debian stable (trixie), amd64 | Das unveränderte netinst-Image mit dem Preseed (der Datei mit den Antworten für den Installer) in seiner initrd, sodass der Installer schon ab der ersten Frage seine Antworten hat. Die Dateien des Hosts liegen auf dem Image unter `/kiwi-server`. Das Image bootet weiterhin sowohl per BIOS als auch per UEFI |

Auf jedem Zielsystem darf der Admin-Benutzer sudo ohne Passwort verwenden. SSH
akzeptiert nur Schlüssel, es sei denn, du setzt `ssh_password_auth: true`.

## Installationsmedien { #install-media }

Der erste Befehl baut das Installations-Image (ISO) für einen Host, der zweite
kopiert es auf einen USB-Stick.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Das ISO installiert auf die Festplatte, die unter `disk:` steht, und zwar
  **ohne nachzufragen**. Diese Festplatte wird dabei gelöscht. Ist die
  Installation fertig, **schaltet es die Maschine aus**
  (`install.on_done: poweroff`, oder `reboot`, damit sie stattdessen neu
  startet). Beschrifte deine USB-Sticks.
- Standardmäßig enthalten die Installationsmedien **nur das Grundsystem**: den
  Hostnamen, die Netzwerkeinstellungen, den Admin-Benutzer mit den
  SSH-Schlüsseln und die Update-Regeln. Keines der Secrets des Stacks ist
  darauf. Ihre Rolle bekommt die Maschine erst später, wenn du `apply`
  ausführst.
- Mit `--offline` kommen die ganze Rolle und ihre Secrets auf das ISO. Das ist
  für Maschinen gedacht, die per SSH nicht erreichbar sind. Wer dieses ISO hat,
  hat damit auch diese Secrets.
- Der Live-Installer zeigt die Festplatten der Maschine an (`lsblk`) und bietet
  eine Shell, in der das Konsolenpasswort und die SSH-Schlüssel der Fleet
  gelten.

## Einrichten mit `apply` { #apply }

`apply` richtet eine Maschine per SSH für ihre Rolle ein.

```bash
kiwi-server apply fleet.yaml papaya                         # über Name, Adresse oder Mesh-Adresse
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # beim ersten Mal über die Adresse
```

Zuerst erzeugt `apply` die Dateien des Hosts noch einmal neu aus der
Fleet-Datei. Dann kopiert es das Rollenskript des Hosts per SSH nach
`/var/lib/kiwi-server/role.sh`. Das Rollenskript ist das Skript, das die
Maschine für ihre Rolle einrichtet, und `apply` führt es als root aus. Danach
bindet `apply` die Festplatte an ihre Tang-Ringe, also an die Server, mit deren
Hilfe eine verschlüsselte Maschine ihre Festplatte beim Start entsperrt. Auf
einem Master sichert es außerdem den Zustand von WireGuard zusammen mit den
Secrets der Fleet. Auf einer verschlüsselten Debian-Maschine ersetzt das erste
`apply` den Einmalschlüssel, mit dem installiert wurde.

Die SSH-Verbindung nutzt den eigenen Schlüssel der Fleet und prüft den
Hostschlüssel der Maschine gegen `secrets/known_hosts`. `apply` und `status`
erreichen eine Maschine über ihren Namen, ihre statische Adresse, die
öffentliche Adresse des Masters oder ihre Mesh-Adresse, also ihre Adresse im
privaten WireGuard-Netzwerk. Sie verwenden aber nur Adressen, deren
Hostschlüssel schon eingetragen ist.

Bei einer Rolle, die aus Modulen besteht, übergibt das Rollenskript den Stack an
`kiwi-stack`. Der Stack umfasst alle Container, die die Maschine für ihre Module
betreibt. `kiwi-stack` arbeitet dann diese Schritte ab:

1. Es installiert oder aktiviert podman 4.4+ oder docker und sorgt dafür, dass
   der Dienstbenutzer existiert. Unter Debian kommen mit podman auch `netavark`,
   `aardvark-dns` und `catatonit`.
2. Es lädt Kernelmodule und setzt sysctls. Gehört Pi-hole zum Stack, wird
   aardvark-dns von podman auf Port 5533 verlegt, und der Host selbst löst Namen
   über das Pi-hole des Stacks auf. Außerdem trägt es das Mesh in die Netze ein,
   denen firewalld vertraut.
3. Es verweigert einen Stack, der aus einem anderen Seed erzeugt wurde. Der Seed
   ist der geheime Ausgangswert, aus dem die Passwörter der Fleet erzeugt
   werden. Passt der Seed, entpackt es den Stack nach `docker_dir`. Die
   Quadlets, also die systemd-Units für die Container, installiert es in
   `/etc/containers/systemd`, dazu die Units für den Host. Außerdem entfernt es
   alles, was ein Modul installiert hatte, das nicht mehr zum Stack gehört.
4. Es öffnet die Ports des Stacks in firewalld oder ufw, falls eine der beiden
   Firewalls aktiv ist.
5. Es lädt jedes Container-Image herunter und startet dann `kiwi-stack.service`,
   das wiederum `kiwi-stack.target` startet.
6. Es führt `kiwi-stack verify` aus, das prüft, ob jeder Container läuft. Läuft
   einer nicht, schlägt `apply` fehl und meldet den Schritt, der gescheitert
   ist.

Wendest du dieselbe erzeugte Konfiguration noch einmal an, ändert sich auf der
Maschine nichts. Eine neu erzeugte Konfiguration ersetzt, was sich geändert hat.
Beachte aber, dass jedes `apply` alle Container des Stacks neu startet, auch
wenn sich nichts geändert hat.

## Der erste Start { #first-boot }

Beim ersten Start führt `kiwi-role.service` das Rollenskript
`/var/lib/kiwi-server/role.sh` einmal aus. Der Dienst startet, sobald das
Netzwerk steht, und wartet bis zu 120 Sekunden auf DNS. Die Datei `role.done`
zeigt an, dass die Rolle fertig ist. Sie wird erst geschrieben, wenn jeder
Container läuft. Schlägt das Skript fehl, hinterlässt es die Datei
`/var/lib/kiwi-server/role.failed`, in der der Schritt und der Befehl stehen,
die fehlgeschlagen sind, und beim nächsten Start läuft das Skript erneut. Das
Log steht in `/var/log/kiwi-server-role.log`. Unter uCore wartet das
Rollenskript, bis die Maschine das signierte uCore-Image ausführt. Von Hand
startest du das Skript erneut mit
`sudo bash /var/lib/kiwi-server/role.sh --force`.

## Updates { #updates }

Die Maschinen installieren die Updates ihres Betriebssystems laufend. Der
**Neustart**, mit dem die Updates wirksam werden, findet aber nur in dem
Wartungsfenster statt, das du mit `updates.days`, `time` und `length_minutes` in
Ortszeit festlegst.

| Zielsystem | Installiert Updates | Startet neu |
|---|---|---|
| `coreos` | Zincati, laufend | nur im Wartungsfenster (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` lädt sie herunter und bereitet sie vor (Staging) | `kiwi-staged-reboot.timer` im Wartungsfenster |
| `debian` | unattended-upgrades, täglich | `kiwi-reboot-if-required.timer` im Wartungsfenster, wenn ein Update einen Neustart verlangt |

Mit `updates.days: []` ist der Neustart an jedem Tag erlaubt, und
`updates.enabled: false` schaltet Updates und Neustarts ab. Eine verschlüsselte
Maschine startet nicht von selbst neu, wenn sie dafür einen Tang-Ring braucht,
den ihr jemand von Hand weiterleiten muss. Sonst würde sie beim Start warten,
bis jemand sie entsperrt.

Die Container werden nach einem eigenen Zeitplan aktualisiert. Einmal pro Woche,
sonntags um 00:00 Uhr, führt `kiwi-stack update` den Befehl `podman auto-update`
aus, sofern `auto_update: registry` gesetzt ist. Der VPN-Client wird jeden Tag
um 07:00 Uhr neu gestartet und bekommt dadurch eine neue Ausgangsadresse. Die
Ausgangsadresse ist die öffentliche Adresse, die Websites sehen, wenn der
Verkehr aus dem VPN herauskommt.

## Auf der Maschine: `kiwi-stack` { #on-the-machine-kiwi-stack }

`kiwi-stack` ist der Befehl, mit dem du dir den Stack direkt auf der Maschine
ansiehst und ihn steuerst.

```bash
sudo kiwi-stack status          # Container, Host-Units, verify
sudo kiwi-stack verify          # läuft jeder Container?
sudo kiwi-stack logs [service]  # aus dem Journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # der VPN-Client und jeder Container in seinem Namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # mit dem Modul backup
sudo kiwi-stack apply DIR       # ein Stack-Bundle, ohne Rollenskript
```

Die Dateien des Stacks liegen in `docker_dir` (standardmäßig
`/home/user/docker`), seine Einstellungen in `/etc/kiwi-server/stack.env`. Die
systemd-Units sind `kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` und
`kiwi-stack-update.timer`, dazu alle Units, die ein Modul mitbringt.

## Was kiwi-server erzeugt { #what-a-render-produces }

Für jeden Host erzeugt kiwi-server aus der Fleet-Datei eine Reihe von Dateien.
Sie landen in `output/<host>/`:

| Datei | Inhalt |
|---|---|
| `<host>.role.sh` | Die Rolle als ein einziges Skript. Es enthält die Einstellungen, den eingebetteten Stack, den Befehl kiwi-stack samt Bibliothek und den eigentlichen Rumpf der Rolle. Die Datei hat die Rechte 0600 |
| `<host>.stack/` | Das Stack-Bundle, damit du es dir ansehen kannst. Es enthält `docker-compose.yml`, `quadlets/`, die Konfigurationsdateien der Module, die Host-Units und `stack.sh`. Du kannst es auch von Hand mit `kiwi-stack apply` installieren |
| `<host>.bu`, `<host>.ign` | Unter CoreOS und uCore die Butane- und die Ignition-Konfiguration |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Unter Debian die Preseed-Datei und die Dateien, die sie auf die Maschine kopiert |
| `<host>.iso` | Das Installations-Image, das ohne Zutun installiert |
