# kiwi-server

kiwi-server ist das Werkzeug, mit dem du ein Kiwi Network aufbaust und
verwaltest. Du beschreibst alle Maschinen in einer einzigen Datei, `fleet.yaml`,
und kiwi-server richtet sie danach ein. Du musst also nicht jede Maschine von
Hand installieren und konfigurieren.

Für jeden Host erzeugt kiwi-server ein **Installations-ISO**, das Fedora CoreOS,
uCore oder Debian installiert, ohne eine einzige Frage zu stellen, und die
Maschine danach ausschaltet. Anschließend richtet kiwi-server die Maschine per
SSH für ihre Rolle ein und macht sie so zum `kiwi-master` oder zum `kiwi-node`.
Auch danach arbeitet kiwi-server mit deinen Maschinen weiter: Es nimmt
WireGuard-Clients ins Netzwerk auf, fragt den Zustand jeder Maschine ab,
verwahrt die Secrets (Passwörter und Schlüssel), sichert die Fleet-Datei samt
Secrets und entsperrt verschlüsselte Festplatten.

kiwi-server gibt es als Kommandozeilenwerkzeug (CLI), `kiwi-server`, und als
GTK4-App, **Kiwi Server**. Beide werden nach `~/.local` installiert und brauchen
keine Root-Rechte.

- Repository:
  [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server),
  GPL-3.0-or-later
- Aktuelles Release: **v2.71.1**. Es steht im
  [Kiwi-Katalog](../desktop/catalogs.md).
- kiwi-server baut auf zwei Teilen auf: auf [kiwi-modules](single.md) v0.29.1
  mit den Modulen und dem Programm, das aus ihnen die Konfiguration erzeugt, und
  auf [kiwi-stack](single.md) v0.7.1, dem Teil, der auf jeder Maschine läuft.
  Beide sind vendored: kiwi-server enthält von jedem eine Kopie, festgelegt auf
  ein bestimmtes Tag.

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

Du kannst es auch aus einem Checkout des Repositorys installieren: Führe
`./install.sh install` aus und danach `kiwi-server doctor`.

kiwi-server braucht Python 3.9+ mit PyYAML und Jinja2 sowie die Programme
`openssl` und `ssh`. Für den Secret-Speicher wird `age` gebraucht. Um ISOs zu
bauen, brauchst du `butane`, `coreos-installer` und `xorriso`, für Debian
außerdem `cpio`, `gzip` und `curl`. Auf Silverblue oder Bluefin solltest du
diese Pakete nicht ins System layern. Bau die ISO-Werkzeuge stattdessen als ein
einziges Container-Image:

```bash
kiwi-server toolchain build     # wird automatisch genutzt, wenn die Werkzeuge fehlen
```

`qrencode` (für `enroll --qr`), `shellcheck` und `docker compose` sind optional.

## Vom leeren Verzeichnis zum laufenden Netzwerk { #from-nothing-to-a-running-network }

Mit den folgenden Befehlen kommst du von einem leeren Verzeichnis zu einem
laufenden Netzwerk mit einem Master, einem Node und deinen eigenen Geräten:

```bash
kiwi-server init                          # eine kommentierte fleet.yaml
$EDITOR fleet.yaml                        # Hosts, Rollen, dein SSH-Schlüssel, die Zielfestplatte
kiwi-server secrets init fleet.yaml       # optional: secrets/ als ein mit age verschlüsselter Speicher
kiwi-server validate fleet.yaml

# der Master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   davon booten; die Maschine installiert sich und schaltet sich aus; dann wieder einschalten
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# jeder Node: zuerst sein WireGuard-Client, dann das Installationsmedium, dann die Rolle
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# deine eigenen Geräte
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # was jede Maschine meldet
```

Standardmäßig enthält ein Installations-ISO **keines der Secrets des Stacks**,
sondern nur das Grundsystem. Die Rolle und ihren Stack schickt erst `apply` auf
die Maschine. Ist eine Maschine per SSH nicht erreichbar, packt
`build --offline` stattdessen die ganze Rolle samt Secrets auf das ISO. Lade ein
solches ISO nicht in den ISO-Speicher eines Hosters hoch, und lösche es nach der
Installation.

**Wenn du gar kein ISO verwenden willst,** gibt
`kiwi-server script fleet.yaml papaya` das Skript für eine Maschine aus, die du
selbst installiert hast. Mit `--offline` enthält das Skript die ganze Rolle.

Auf einem VPS von netcup löscht `kiwi-server vps install fleet.yaml sorbet` den
Server und installiert das ISO über die API von netcup. Niemand muss dafür an
einer Konsole sitzen. netcup ist bisher der einzige unterstützte Hoster, weitere
sind [geplant](roadmap.md#more-hosters-and-network-boot).

## Befehle { #commands }

| Befehl | Was er tut |
|---|---|
| `init [fleet.yaml]` | Schreibt die Beispiel-Fleet-Datei. `--domain` legt die Domain fest, Standard ist `home`. |
| `validate fleet.yaml [host…]` | Prüft die Fleet-Datei. Dabei erzeugt er jeden Stack, sodass auch Fehler in Modulen auffallen. |
| `list` / `show fleet.yaml <host>` | Der erste listet die Hosts auf und was für sie schon erzeugt wurde. Der zweite zeigt die tatsächlich wirksame Konfiguration eines Hosts, mit verdeckten Secrets. |
| `render fleet.yaml [host…]` | Schreibt die Rollenskripte, Stacks und Installationskonfigurationen nach `output/<host>/`. |
| `build fleet.yaml [host…]` | Erzeugt die Konfiguration und baut dann das ISO. Standardmäßig enthält das ISO nur das Grundsystem, mit `--offline` die ganze Rolle. |
| `script fleet.yaml <host>` | Gibt das Skript für eine beliebige Maschine aus. Mit `--offline` enthält das Skript die ganze Rolle. |
| `apply fleet.yaml <host…>` | Erzeugt die Konfiguration neu, schickt die Rolle per SSH auf die Maschine und führt sie dort aus (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Zeigt, was die Maschinen melden: Rolle, Stack, Probleme, Festplatten, Backups und Zertifikate. |
| `enroll fleet.yaml <host\|name>` | Legt auf dem Master einen WireGuard-Client an oder holt einen, den es schon gibt (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Verwaltet `secrets/` als eine mit age verschlüsselte Datei, die beim Entsperren in den Arbeitsspeicher geöffnet wird (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Zeigt die erzeugten Passwörter eines Hosts. |
| `ca fleet.yaml` | Zeigt die CA der Fleet. |
| `mtu fleet.yaml <node\|device\|address>` | Misst die tatsächliche MTU eines Tunnels und sagt dir, welchen Wert du einstellen solltest (`--write`). |
| `openwrt fleet.yaml` | Schreibt ein Skript, das einen OpenWrt-Router ins Mesh holt ([Router](../network/routers.md)). |
| `backup` / `restore` / `prune` | Sichern das Fleet-Verzeichnis auf Nodes, holen es von dort zurück und löschen alte Backups der Maschinen ([Betrieb](operations.md)). |
| `unlock fleet.yaml <host>` | Leitet einen Tang-Ring an eine Maschine weiter, die beim Start darauf wartet, dass ihre verschlüsselte Festplatte entsperrt wird ([Betrieb](operations.md)). |
| `vps login\|list\|probe\|install` | Arbeiten mit der API des Server Control Panels von netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Zeigen, was verfügbar ist, mit jeder Einstellung und ihrem Standardwert. |
| `toolchain [status\|build]`, `doctor` | Verwalten die ISO-Werkzeuge und prüfen diesen Rechner. |

Jeder Befehl versteht `--porcelain` (Ausgabe als JSON), `-o/--output-dir`,
`--quiet` und `-v`. `kiwi-server <command> -h` erklärt einen einzelnen Befehl.

## Die App { #the-app }

Die App **Kiwi Server** öffnet die Fleet, an der du zuletzt gearbeitet hast. In
ihrer Seitenleiste stehen eine Übersicht, eine Zeile pro Host und die
Standardwerte. Die Seite *Overview* eines Hosts zeigt aktuelle Angaben aus
`kiwi-server status`. Die App holt sie einmal pro Minute, solange das Fenster im
Vordergrund ist, per SSH und nur lesend. Die Seite *Settings* eines Hosts ist
ein Formular, das aus den Rollen und Modulen aufgebaut wird. *Apply*, *Build*
und *Render* starten das Kommandozeilenwerkzeug und zeigen seine Ausgabe laufend
an. Bevor *Build* loslegt, listet es die Festplatten auf, die es löschen wird.
*Unlock* und *Lock* öffnen und schließen den Secret-Speicher. Die App schreibt
schlichtes YAML. Kommentare in einer Fleet-Datei, die du von Hand geschrieben
hast, gehen deshalb verloren, sobald die App sie speichert.

## Worauf du achten solltest { #mind }

!!! danger "Die ISOs löschen die Festplatte, für die sie gebaut sind"
    Ein Installations-ISO löscht ohne Nachfrage die Festplatte, für die es
    gebaut wurde, sobald eine Maschine davon bootet. Beschrifte deine ISOs.
    Genau deshalb verlangt `build` die Einstellung `disk:`.

- **Die Ausgabe enthält Secrets**, nämlich Passwort-Hashes, WireGuard-Schlüssel,
  TLS-Schlüssel und LUKS-Schlüssel. Die Dateien werden mit den Rechten 0600
  geschrieben, und git ignoriert `output/`. Geh mit ISOs, die mit `--offline`
  gebaut wurden, genauso sorgfältig um.
- **Passwörter für Dienste werden erzeugt**, und zwar aus `secrets/seed`, wenn
  du sie in der Fleet-Datei weglässt. `validate` warnt dich vor Passwörtern, die
  in der Fleet-Datei stehen, und `kiwi-server secrets show` gibt die erzeugten
  aus. Eine Maschine verweigert ein `apply`, das mit einem anderen Seed erzeugt
  wurde.
- **SSH-Hostschlüssel** werden in `secrets/known_hosts` eingetragen, wenn
  kiwi-server sich zum ersten Mal mit einer Maschine verbindet. Ändert sich der
  Schlüssel einer Maschine später, wird die Verbindung abgelehnt. Wenn du eine
  Maschine neu installiert hast, lösch ihre Zeile aus dieser Datei.
- **Ein Rollenskript läuft als root.** Bevor du einer Rolle vertraust, die du
  nicht selbst geschrieben hast, lies die Ausgabe von
  `kiwi-server script fleet.yaml <host>
  --offline`.
- **Eine fehlgeschlagene Rolle wird gemeldet.** Die Maschine behält die Datei
  `/var/lib/kiwi-server/role.failed`, in der der Schritt und der Befehl stehen,
  die fehlgeschlagen sind, und `status` zeigt sie an.

## Stand { #status }

Der ganze Ablauf, von der Fleet-Datei bis zur laufenden Maschine, wurde im
Oktober und November 2026 auf echter Hardware getestet. Debian, uCore und Fedora
CoreOS haben ihn auf zwei VPS, einem Mini-PC und einer VM vollständig
durchlaufen. In einer Übung, in der der Ausfall eines Nodes nachgestellt wurde,
wurde eine verschlüsselte Debian-Maschine in etwa 14 Minuten neu aufgesetzt.
Backups eines Nodes wurden auf einem anderen wiederhergestellt (von papaya auf
lychee). Die Tunnel-MTU wurde auf echten Verbindungen gemessen und angepasst,
auch auf Mobilfunkverbindungen. Die automatischen Tests (CI) erzeugen jede
Rolle, prüfen jedes Skript mit shellcheck und validieren jede
Butane-Konfiguration. Außerdem vergleichen sie vier Referenz-Stacks, die
sogenannten Golden Stacks, Byte für Byte mit ihrer gespeicherten Ausgabe.

Die Föderation zwischen zwei Netzwerken wurde im November 2026 zwischen zwei VPS
getestet. Alles läuft über IPv4. arm64-Boards laufen als Node: Ein Odroid N2+
mit Armbian wurde aus einem Image eingerichtet, das kiwi-server erzeugt hat
(`target: armbian`); andere Boards sind ungetestet. Ein Control Node
(`kiwi-server serve`, das Modul `control`) lässt kiwi-server auf einem Server zu
Hause laufen, mit einer Webseite fürs Handy; er wurde mit einer Fleet getestet.

Weiterlesen: [Die Fleet-Datei](fleet.md) · [Rollen](roles.md) ·
[Module](modules.md) · [Maschinen](machines.md) · [Betrieb](operations.md) ·
[Eine Maschine ohne Fleet](single.md)
