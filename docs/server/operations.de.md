# Betrieb

Die tägliche Arbeit an einer laufenden Fleet, alles von der Maschine des Betreibers
aus.

## Status { #status }

```bash
kiwi-server status fleet.yaml            # jeder Host
kiwi-server status fleet.yaml papaya        # einer
```

Jede Maschine meldet über SSH (nur lesend): ihre Rolle, ihren Stack, Probleme (eine
gescheiterte Rolle, ein gestoppter Container), ihre Festplatten und ob sie
verschlüsselt oder gesperrt sind, ihre Backups und wie lange ihre Zertifikate noch
gültig sind. Ein Backup-Node meldet außerdem seine Kapazität. Die App Kiwi Server
zeigt dasselbe in der *Overview* jedes Hosts.

## Secrets { #secrets }

Alles Geheime liegt in `secrets/` neben der Fleet-Datei: der Seed, aus dem jedes
erzeugte Passwort abgeleitet wird, die CA der Fleet, WireGuard-Konfigurationen,
LUKS-Schlüssel und SSH-Host-Schlüssel.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ becomes one age-encrypted file
kiwi-server secrets unlock fleet.yaml    # open it into memory (--for 8h; 0 keeps it open)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` legt einen Schlüssel im GNOME-Schlüsselbund ab und zeigt einmal einen
**Wiederherstellungsschlüssel**. Solange der Speicher offen ist, kann alles, was als
du läuft, ihn lesen.

## Die Fleet selbst sichern { #backing-up-the-fleet-itself }

Nach jedem erfolgreichen Rendern oder Bauen wird das Fleet-Verzeichnis verschlüsselt
(AES-256 mit PBKDF2, 600.000 Iterationen) und auf die in `backup.hosts` aufgeführten
Nodes kopiert, die die neuesten zehn behalten. Auf einer frischen Maschine:

```bash
kiwi-server restore --from core@lychee.home  # das Fleet-Verzeichnis zurückholen
kiwi-server backup fleet.yaml --local /mnt/usb   # oder jederzeit eine Kopie in ein Verzeichnis
```

## Die Daten der Maschinen sichern { #backing-up-the-machines-data }

Gib einem Node das Modul `backup-server` (ein restic-REST-Server) und jeder Maschine,
die gesichert werden soll, das Modul `backup`, das darauf zeigt:

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

Jede Nacht um 03:00 (innerhalb von 15 Minuten danach) schickt restic verschlüsselt,
was jedes Modul aufbewahrt haben will. Jede Maschine kann nur ihr eigenes Repository
erreichen und nur etwas hinzufügen. Das Entfernen alter Snapshots läuft deshalb von
der Maschine des Betreibers aus:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # auf der Maschine
kiwi-server prune fleet.yaml            # 7 tägliche, 4 wöchentliche, 6 monatliche behalten
```

Eine Wiederherstellung wurde von Node zu Node getestet: die Backups von papaya auf
lychee.

### Kommt im nächsten Release { #coming-in-the-next-release }

!!! info "Auf dem Branch `several-servers`"
    Diese Arbeit ist auf die Branches `several-servers` von kiwi-modules und
    kiwi-server gepusht, aber noch nicht gemergt oder veröffentlicht. Mehrere Server
    und die automatische Wiederherstellung wurden auf Hardware getestet. Der
    Health-Check für das VPN nicht.

- **Mehrere Backup-Server.** `backup.servers` nimmt eine Liste, und jeder Server
  bekommt eine eigene vollständige Kopie. Fällt ein Server aus, fehlt nur seine
  Kopie. Eine Wiederherstellung nimmt die frischeste Kopie von dem Server, der sie
  hat, und `kiwi-stack snapshots` listet sie Server für Server auf. Das einzelne
  `server` funktioniert weiterhin.
- **Eine neu aufgebaute Maschine stellt sich selbst wieder her.** Findet sich eine
  Maschine in den Backups, hat aber keines davon selbst erstellt (ein Neuaufbau),
  stellt sie vor ihrem ersten Backup jedes Modul von selbst wieder her und sichert
  dann wie zuvor (`backup.restore:
  auto`, der Standard). Mit `hold` wartet sie auf `kiwi-stack restore` oder
  `kiwi-stack backup --new`.
- **Bereinigen per Timer.** `kiwi-server prune fleet.yaml --every week` (oder `day`)
  installiert einen systemd-Benutzer-Timer auf deinem Computer, dem einzigen Ort, der
  die Schlüssel hält, die löschen dürfen. Ein verpasster Lauf kommt bei der nächsten
  Anmeldung. `kiwi-server status` zeigt jede Backup-Kopie und warnt, wenn ein
  Backup-Node drei Wochen lang nicht bereinigt wurde.
- **Ein hängender kommerzieller Ausgang startet neu.** gluetun bekommt einen
  Health-Check. Nach fünf ungesunden Minuten wird der Container beendet, und sein
  nächster Start wählt einen anderen Server.

## Verschlüsselte Festplatten und Entsperren { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) installiert mit einem einmaligen Schlüssel,
  den du beim ersten Booten eintippst (`secrets/luks/<host>.once`). Das erste
  `apply` ersetzt ihn durch `secrets/luks/<host>.key`, und ein Master bekommt
  außerdem einen frischen Volume-Schlüssel. Geht diese Schlüsseldatei verloren, ist
  die Festplatte gesperrt, also halte die Fleet gesichert.
- **CoreOS / uCore** verschlüsseln bei der Installation über Ignition (mit etwa
  4 GiB RAM beim ersten Booten).
- **Tang-Ringe** lassen verschlüsselte Maschinen beim Booten entsperren, ohne dass
  jemand dabei sein muss. Ein Node betreibt das Modul `tang` (jeder Ring ist ein
  Tang-Server mit eigenen Schlüsseln, standardmäßig `infra` auf Port 7500), und der
  Block `unlock:` eines Hosts bindet seine Festplatte mit einem Schwellenwert an
  Ringe.
- **SSH im initramfs** (`unlock.ssh: true`: dropbear unter Debian, dracut-sshd unter
  CoreOS) benutzt einen eigenen eingeschränkten Schlüssel,
  `secrets/unlock_ed25519`, der nur das Entsperren ausführen kann.
- `kiwi-server unlock fleet.yaml <host>` reicht einen Ring an eine Maschine weiter,
  die beim Booten wartet, und `--manual` übergibt den Schlüssel selbst. Ein Ring
  `operator` wird von deiner eigenen Maschine aus bereitgestellt, solange er
  gebraucht wird. `vpn-server.unlock_relay` erreicht Maschinen hinter NAT.

## Tunnel-MTU { #tunnel-mtu }

WireGuard fügt eigene Header hinzu, also trägt ein Tunnel kleinere Pakete als die
Leitung darunter, und ein mobiler Weg noch kleinere. Ein Paket, das für irgendeine
Verbindung unterwegs zu groß ist, wird verworfen oder zerteilt, und Verbindungen
bleiben hängen. Kiwi behandelt das in drei Schichten:

- **Zwei Einstellungen.** `wg_mtu` (Standard **1376**, ein Vielfaches von 16, weil
  WireGuard auf 16 auffüllt) ist die MTU von gluetun, der Client-Konfigurationen von
  wg-easy und von `wg0`. `bridge_mtu` (Standard **1500**) ist die MTU des
  Stack-Netzwerks. `validate` lehnt ein `wg_mtu` ab, dessen aufgefülltes Paket plus
  80 Byte Header nicht in die Bridge passt, und alles unter 1280, dem Minimum, mit
  dem IPv6 funktioniert.
- **Die MSS wird in beide Richtungen** auf `wg_mtu - 40` **begrenzt**, in wg-easy und
  im VPN-Client, sodass TCP nie ein Segment versucht, das nicht durchpasst.
- **TCP tastet selbst.** Der VPN-Client läuft mit `net.ipv4.tcp_mtu_probing=1` und
  `tcp_base_mss=1024`, sodass eine Verbindung, die auf einen Weg trifft, der große
  Pakete stillschweigend verwirft, eine funktionierende Größe findet, statt hängen
  zu bleiben.

### Einen Weg messen: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # ein Node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # ein Gerät aus secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # und wg_mtu in die Fleet-Datei schreiben
```

Die Messung schickt Pings mit gesetztem Don't-Fragment-Bit durch den Tunnel, aus dem
Namespace heraus, der ihn hält. Einen Node misst sie von seinem eigenen VPN-Client
aus (dessen Firewall eingehende Pings verwirft), ein Gerät vom WireGuard-Server aus.
Sie beginnt mit einem gewöhnlichen Ping, versucht dann jedes Vielfache von 16 ab 1280
aufwärts und meldet das größte, das **unzerteilt** ankommt. Während sie pingt, liest
sie die Reassembly-Zähler des Kernels, sodass eine Antwort, die unterwegs zerteilt
und wieder zusammengesetzt wurde, nicht als passend zählt.

Sie sagt auch, was einzustellen ist. Für ein **Gerät** ist das das eigene `MTU =` des
Geräts in seiner WireGuard-Konfiguration, und sonst ist niemand betroffen. Für einen
**Node** ist es `wg_mtu` auf diesem Node und auf seinem Master, das `--write` in die
Fleet-Datei schreibt (und dabei nur diese Zeilen ändert). Ein Paket, das nur auf
seinem Weg hinaus zerteilt und vom anderen Ende wieder zusammengesetzt wird, ist von
diesem Ende aus nicht zu sehen.

Die Standardwerte wurden auf der Test-Fleet gemessen. Für ein Telefon im
Mobilfunknetz, wo Wege oft reines IPv6 hinter 464XLAT mit verschachtelter
Kapselung sind, miss das Telefon selbst und senke sein eigenes `MTU =`, wenn die
Messung das sagt.

## netcup-VPSes { #netcup-vpses }

netcup ist der Hoster, auf dem kiwi-server heute von selbst installieren kann,
über seine Server-Control-Panel-API. Weitere Hoster sind als Plugins
[geplant](roadmap.md#more-hosters-and-network-boot).

```bash
kiwi-server vps login fleet.yaml         # Anmeldung per Device Flow; das Token kommt nach secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # den Server löschen und die ISO des Hosts installieren
```

`vps install` fragt vorher nach, außer du übergibst `--yes`. Es lehnt eine ISO ab,
die Rollen-Secrets trägt, ein falsches `disk:` und CoreOS-Festplattenverschlüsselung
bei weniger als 3500 MiB RAM.
