# Betrieb

Auf dieser Seite geht es um alles, was ansteht, wenn die Maschinen installiert
sind und laufen: ihren Zustand prüfen, die Secrets sicher verwahren, die Fleet
und die Daten der Maschinen sichern, verschlüsselte Festplatten entsperren, die
Tunnel-MTU anpassen und auf einem netcup-Server installieren. All das erledigst
du mit kiwi-server von deinem eigenen Rechner aus, dem *Admin-Rechner*, auf dem
die Fleet-Datei und die Secrets liegen.

## Status { #status }

`kiwi-server status` zeigt, wie es den Maschinen der Fleet geht, entweder allen
oder nur der, die du angibst:

```bash
kiwi-server status fleet.yaml            # jeder Host
kiwi-server status fleet.yaml papaya        # einer
```

kiwi-server verbindet sich per SSH mit jeder Maschine und liest dort nur. Jede
Maschine meldet ihre Rolle und ihren Stack (die Container und Dienste, die sie
betreibt), Probleme wie eine fehlgeschlagene Rolle oder einen gestoppten
Container, ihre Festplatten und ob diese verschlüsselt oder gesperrt sind, ihre
Backups und wie lange ihre Zertifikate noch gültig sind. Ein Backup-Node meldet
außerdem seine Speicherkapazität. Die App Kiwi Server zeigt dieselben Angaben
auf der Seite *Overview* jedes Hosts.

## Secrets { #secrets }

Alles Geheime liegt in `secrets/`, dem Verzeichnis neben der Fleet-Datei. Darin
stehen der Seed, aus dem jedes erzeugte Passwort abgeleitet wird, die eigene
Zertifizierungsstelle (CA) der Fleet, die WireGuard-Konfigurationen, die
LUKS-Schlüssel der verschlüsselten Festplatten und die SSH-Hostschlüssel.
kiwi-server kann dieses Verzeichnis verschlüsselt aufbewahren und es nur öffnen,
solange du damit arbeitest:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ wird zu einer einzigen, mit age verschlüsselten Datei
kiwi-server secrets unlock fleet.yaml    # in den Arbeitsspeicher öffnen (--for 8h; 0 lässt es offen)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # die erzeugten Passwörter eines Hosts
```

`secrets init` legt den verschlüsselten Speicher an. Dabei legt es einen
Schlüssel im GNOME-Schlüsselbund ab und zeigt dir einen
**Wiederherstellungsschlüssel**. Der Wiederherstellungsschlüssel wird nur ein
einziges Mal angezeigt. Solange der Speicher offen ist, kann jedes Programm, das
unter deinem Benutzerkonto läuft, ihn lesen.

## Die Fleet selbst sichern { #backing-up-the-fleet-itself }

Im Fleet-Verzeichnis liegen die Fleet-Datei und `secrets/`, und kiwi-server
sichert es von selbst. Nach jedem erfolgreichen `render` oder `build` (den
beiden Schritten, die die Konfiguration der Hosts und ihre Installations-ISOs
erzeugen) verschlüsselt es das Fleet-Verzeichnis (AES-256 mit PBKDF2, 600.000
Iterationen) und kopiert es auf die Nodes, die unter `backup.hosts` stehen.
Jeder dieser Nodes bewahrt die zehn neuesten Kopien auf. Auf einem neuen Rechner
holst du dir das Fleet-Verzeichnis von einem dieser Nodes zurück. Außerdem
kannst du jederzeit eine Kopie in ein Verzeichnis deiner Wahl schreiben:

```bash
kiwi-server restore --from core@lychee.home  # das Fleet-Verzeichnis zurückholen
kiwi-server backup fleet.yaml --local /mnt/usb   # oder jederzeit eine Kopie in ein Verzeichnis
```

## Die Daten der Maschinen sichern { #backing-up-the-machines-data }

Die Daten auf den Maschinen werden mit dem Backup-Programm restic gesichert. Ein
Node speichert die Backups. Gib diesem Node das Modul `backup-server`, das einen
restic-REST-Server betreibt. Jede Maschine, die gesichert werden soll, bekommt
das Modul `backup` mit einer Einstellung, die auf diesen Server zeigt:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Jede Nacht um 03:00 Uhr oder bis zu 15 Minuten später schickt restic die Daten,
die jedes Modul aufbewahrt haben will, verschlüsselt an den Backup-Server. Eine
Maschine erreicht auf dem Server nur ihr eigenes Repository, und sie kann ihren
Backups dort nur etwas hinzufügen, aber nichts löschen. Deshalb läuft der
Befehl, der alte Snapshots löscht, auf dem Admin-Rechner. Ein Snapshot ist bei
restic der gesicherte Stand eines Backup-Laufs. Der erste Befehl unten ist für
die Maschine selbst, der zweite für deinen Rechner:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # auf der Maschine
kiwi-server prune fleet.yaml            # behält 7 tägliche, 4 wöchentliche, 6 monatliche
```

Die Wiederherstellung wurde zwischen zwei Nodes getestet: Die Backups von papaya
wurden auf lychee wiederhergestellt.

### Im nächsten Release { #coming-in-the-next-release }

!!! info "Auf dem Branch `several-servers`"
    Diese Arbeit liegt auf den `several-servers`-Branches von kiwi-modules und
    kiwi-server, ist aber noch nicht gemergt und nicht veröffentlicht. Mehrere
    Backup-Server und die automatische Wiederherstellung wurden auf Hardware
    getestet, der Health-Check für das VPN nicht.

- **Mehrere Backup-Server.** `backup.servers` nimmt eine Liste von Servern an,
  und jeder Server bekommt eine eigene, vollständige Kopie. Fällt ein Server
  aus, ist nur seine Kopie betroffen. Eine Wiederherstellung nimmt die neueste
  Kopie von dem Server, der sie hat, und `kiwi-stack snapshots` listet die
  Snapshots Server für Server auf. Die einzelne Einstellung `server`
  funktioniert weiterhin.
- **Eine neu aufgesetzte Maschine stellt sich selbst wieder her.** Eine
  Maschine, die neu aufgesetzt wurde, findet auf dem Server Backups von sich,
  obwohl sie selbst noch keines davon gemacht hat. In diesem Fall stellt sie
  jedes Modul von selbst wieder her, bevor sie ihr erstes Backup macht, und
  sichert danach wie gewohnt. Das ist der Standard, `backup.restore: auto`. Mit
  `hold` wartet die Maschine, bis du `kiwi-stack restore` oder
  `kiwi-stack backup --new` ausführst.
- **Aufräumen per Timer.** Aufräumen heißt hier: alte Snapshots löschen.
  `kiwi-server prune fleet.yaml --every week` (oder `day`) installiert auf
  deinem Rechner einen systemd-Timer für deinen Benutzer. Dein Rechner ist der
  einzige Ort, an dem die Schlüssel liegen, die löschen dürfen. Fällt ein Lauf
  aus, wird er bei der nächsten Anmeldung nachgeholt. `kiwi-server status` zeigt
  jede Backup-Kopie und warnt, wenn auf einem Backup-Node seit drei Wochen nicht
  mehr aufgeräumt wurde.
- **Eine hängende Verbindung zum kommerziellen VPN-Anbieter erholt sich von
  selbst.** gluetun, der Container des VPN-Clients, bekommt einen Health-Check,
  also eine regelmäßige Prüfung, ob die Verbindung noch funktioniert. Schlägt
  der Health-Check fünf Minuten lang fehl, wird der Container beendet und wählt
  beim nächsten Start einen anderen Server.

## Verschlüsselte Festplatten und Entsperren { #encrypted-disks-and-unlocking }

Eine verschlüsselte Festplatte muss bei jedem Start der Maschine entsperrt
werden. Dieser Abschnitt beschreibt, wie jedes Zielsystem (das Betriebssystem,
mit dem eine Maschine installiert wird) seine Festplatte verschlüsselt und wie
sie sich mit oder ohne einen Menschen vor Ort entsperren lässt.

- **Debian** (`debian.encrypt: true`) wird mit einem Einmalschlüssel
  installiert, den du beim ersten Start eintippst. Du findest ihn in
  `secrets/luks/<host>.once`. Das erste `apply` ersetzt ihn durch
  `secrets/luks/<host>.key`, und ein Master bekommt dabei außerdem einen neuen
  Volume-Schlüssel. Geht diese Schlüsseldatei verloren, bleibt die Festplatte
  gesperrt. Sorge also dafür, dass die Fleet gesichert ist.
- **CoreOS / uCore** verschlüsseln die Festplatte bei der Installation, und zwar
  über Ignition, das Werkzeug, das eine CoreOS-Maschine beim ersten Start
  konfiguriert. Dafür braucht die Maschine beim ersten Start etwa 4 GiB RAM.
- **Tang-Ringe** sorgen dafür, dass verschlüsselte Maschinen ihre Festplatten
  beim Start entsperren können, ohne dass jemand dabei sein muss. Tang ist ein
  kleiner Server, den eine Maschine über das Netzwerk um Hilfe beim Entsperren
  ihrer Festplatte bittet. Ein Node betreibt das Modul `tang`, und jeder Ring
  ist ein Tang-Server mit eigenen Schlüsseln. Standardmäßig gibt es einen Ring,
  `infra`, auf Port 7500. Der `unlock:`-Block eines Hosts bindet seine
  Festplatte an einen oder mehrere Ringe und legt einen Schwellenwert fest: die
  Zahl der Ringe, die antworten müssen.
- **SSH im initramfs** (`unlock.ssh: true`) macht eine Maschine erreichbar,
  während sie darauf wartet, dass ihre Festplatte entsperrt wird. Das initramfs
  ist das kleine System, das läuft, bevor die Festplatte offen ist. Der
  SSH-Server darin ist unter Debian dropbear und unter CoreOS dracut-sshd. Er
  akzeptiert einen eigenen, eingeschränkten Schlüssel, `secrets/unlock_ed25519`,
  mit dem sich nur das Entsperren ausführen lässt.
- `kiwi-server unlock fleet.yaml <host>` leitet einen Ring an eine Maschine
  weiter, die beim Start wartet. So kann die Maschine einen Ring nutzen, den sie
  selbst nicht erreicht. Mit `--manual` übergibt der Befehl direkt den
  Schlüssel. Ein Ring namens `operator` wird von deinem eigenen Rechner aus
  bereitgestellt, solange er gebraucht wird. `vpn-server.unlock_relay` macht
  einen Ring für Maschinen hinter NAT über den Master erreichbar.

## Tunnel-MTU { #tunnel-mtu }

Die MTU ist die größte Paketgröße, die eine Netzwerkverbindung am Stück
übertragen kann. WireGuard setzt jedem Paket eigene Header voran. Durch einen
Tunnel passen deshalb kleinere Pakete als durch die Verbindung darunter, und
durch eine Mobilfunkverbindung noch kleinere. Ist ein Paket für eine der
Verbindungen auf seinem Weg zu groß, wird es verworfen oder zerteilt, und
Verbindungen bleiben hängen. Kiwi geht auf drei Arten damit um:

- **Zwei Einstellungen.** `wg_mtu` ist die MTU von gluetun (dem VPN-Client), der
  Client-Konfigurationen, die wg-easy (der WireGuard-Server) ausstellt, und der
  WireGuard-Schnittstelle `wg0`. Ihr Standardwert ist **1376**. Das ist ein
  Vielfaches von 16, weil WireGuard jedes Paket auf das nächste Vielfache von 16
  Byte auffüllt. `bridge_mtu` ist die MTU des Stack-Netzwerks, über das die
  Container einer Maschine miteinander verbunden sind. Ihr Standardwert ist
  **1500**. `validate` lehnt einen `wg_mtu` ab, dessen aufgefülltes Paket plus
  80 Byte Header nicht in die Bridge passt. Ebenso lehnt es alles unter 1280 ab,
  der kleinsten MTU, mit der IPv6 funktioniert.
- **Die MSS wird in beiden Richtungen begrenzt.** Die MSS ist die größte
  Datenmenge, die TCP in ein einzelnes Paket packt. wg-easy und der VPN-Client
  begrenzen sie beide auf `wg_mtu - 40`. So versucht TCP nie, ein Segment zu
  senden, das nicht durchpasst.
- **TCP findet selbst eine passende Größe.** Der VPN-Client läuft mit
  `net.ipv4.tcp_mtu_probing=1` und `tcp_base_mss=1024`. Läuft eine Verbindung
  über einen Weg, der große Pakete stillschweigend verwirft, probiert TCP
  kleinere aus, bis es eine Größe findet, die funktioniert, statt hängen zu
  bleiben.

### Einen Weg messen: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Um herauszufinden, was der Weg zu einem Node oder einem Gerät tatsächlich
durchlässt, misst du ihn:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # ein Node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # ein Gerät aus secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # und wg_mtu in die Fleet-Datei schreiben
```

Für die Messung werden Pings mit gesetztem Don't-Fragment-Flag durch den Tunnel
geschickt, damit sie unterwegs nicht zerteilt werden können. Sie werden aus dem
Netzwerk-Namespace heraus gesendet, in dem der Tunnel liegt. Ein
Netzwerk-Namespace ist eine eigene, abgetrennte Netzwerkumgebung auf einer
Maschine, wie sie zum Beispiel ein Container hat. Ein Node wird von seinem
eigenen VPN-Client aus gemessen, weil dessen Firewall eingehende Pings verwirft.
Ein Gerät wird vom WireGuard-Server aus gemessen. Die Messung beginnt mit einem
gewöhnlichen Ping, probiert dann jedes Vielfache von 16 ab 1280 aufwärts und
meldet die größte Paketgröße, die **in einem Stück** ankommt. Während sie pingt,
liest sie die Zähler des Kernels für wieder zusammengesetzte Pakete mit. So
zählt eine Antwort, die unterwegs zerteilt und wieder zusammengesetzt wurde,
nicht als passend.

Die Messung sagt dir auch, was du einstellen solltest. Bei einem **Gerät** ist
das die Zeile `MTU =` in der eigenen WireGuard-Konfiguration des Geräts, und
sonst ist niemand betroffen. Bei einem **Node** ist es `wg_mtu` auf diesem Node
und auf seinem Master. Mit `--write` trägt kiwi-server den Wert in die
Fleet-Datei ein und ändert dabei nur diese Zeilen. Eines lässt sich von dieser
Seite aus nicht erkennen: ein Paket, das nur auf dem Hinweg zerteilt und am
anderen Ende wieder zusammengesetzt wird.

Die Standardwerte wurden auf der Test-Fleet gemessen. Ein Handy im Mobilfunknetz
braucht eine eigene Messung, weil im Mobilfunk oft reines IPv6 hinter 464XLAT
mit verschachtelter Kapselung zum Einsatz kommt. Miss das Handy selbst und senke
den Wert `MTU =` in seiner eigenen Konfiguration, wenn die Messung das
empfiehlt.

## VPS bei netcup { #netcup-vpses }

netcup ist ein Hoster und heute der einzige, bei dem kiwi-server einen
gemieteten Server (einen VPS) selbst installieren kann. Dafür nutzt es die API
des Server Control Panels von netcup. Weitere Hoster sind als Plugins
[geplant](roadmap.md#more-hosters-and-network-boot).

```bash
kiwi-server vps login fleet.yaml         # Anmeldung per Device-Flow; das Token landet in secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # den Server löschen und das ISO des Hosts installieren
```

`vps install` löscht den Server und fragt deshalb vorher nach, es sei denn, du
übergibst `--yes`. In drei Fällen verweigert es die Installation: wenn das ISO
Secrets der Rolle enthält, wenn `disk:` die falsche Festplatte nennt und wenn
eine CoreOS-Festplatte auf einem Server mit weniger als 3500 MiB RAM
verschlüsselt werden soll.
