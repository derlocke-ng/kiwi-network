# Eine Maschine ohne Fleet

kiwi-server verwaltet viele Maschinen gemeinsam. Wenn du nur auf einer einzelnen
Maschine einen Stack betreiben willst, brauchst du es nicht. Ein Stack umfasst
alle Container und Dienste, die auf einer Maschine laufen. kiwi-server besteht
aus zwei kleineren Werkzeugen, und die kannst du auch für sich allein verwenden:

| Repository | Was es ist |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Die Module und ihr Renderer. Er liest **eine Maschinendatei und schreibt daraus ein Stack-Bundle**, ein Verzeichnis mit der erzeugten Konfiguration des Stacks dieser Maschine. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Der Teil, der auf der Maschine läuft. Er besteht aus dem Befehl `kiwi-stack` und einer Bibliothek, die ein Bundle auf eine CoreOS-, uCore- oder Debian-Maschine bringen und es dort am Laufen halten. v0.5.0, GPL-3.0-or-later |

Die beiden Werkzeuge sind das Richtige, wenn du einen Stack auf einer Maschine
willst, aber den Rest von kiwi-server nicht brauchst. Beispiele sind ein Node,
den du von Hand einrichtest, ein Modul, das du gerade entwickelst, oder eine
Maschine, die ihren Stack selbst erzeugt. kiwi-server enthält eine Kopie beider
Werkzeuge, jeweils auf ein Release-Tag festgelegt. Am Ende ist eine Maschine
genau gleich eingerichtet, egal ob du sie mit kiwi-server oder mit den beiden
Werkzeugen einrichtest, und beide Wege leiten aus demselben Seed dieselben
Secrets ab.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Eine Maschine erzeugen { #render-a-machine }

Die folgenden Befehle installieren kiwi-modules, legen einen Seed an und
erzeugen aus der Beispiel-Maschinendatei ein Bundle. Die letzte Zeile kopiert
das Bundle auf die Maschine und wendet es dort an.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # anpassen: TLS-Dateien, die WireGuard-Konfiguration
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules braucht Python 3 mit PyYAML und Jinja2. `kiwi-modules modules -v`
listet jedes Modul und jede Einstellung auf, `kiwi-modules profiles` die Rollen
und ihre Presets.

Eine Maschinendatei beschreibt eine einzelne Maschine, so wie in diesem
Beispiel:

```yaml
# ein Cloud-Node
name: sh3
domain: home
target: ucore
timezone: Europe/Berlin
admin: { user: core }
role: node
node:
  preset: cloud
  cloud: { collabora: true, talk: true }
  reverse-proxy:
    tls_fullchain: secrets/sh3-fullchain.pem
    tls_privkey: secrets/sh3-privkey.pem
dns_records:                    # die Namen im Netzwerk
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # vertrauenswürdig in den Containern und auf dem Host
seed: secrets/seed              # daraus werden die Passwörter abgeleitet
```

kiwi-modules hat keine eigene Zertifizierungsstelle. Wenn du eine Maschine ohne
kiwi-server erzeugst, musst du das TLS-Zertifikat und die Schlüsseldatei deshalb
selbst bereitstellen. Nennt die Maschinendatei keine WireGuard-Konfiguration,
sucht kiwi-modules sie unter `secrets/<hostname>.conf`.

## Auf die Maschine bringen { #put-it-on-the-machine }

Installiere auf der Maschine kiwi-stack und wende das Bundle an:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack und seine Bibliothek
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack braucht bash und systemd. Außerdem braucht es die Container-Laufzeit,
die unter `runtime` im Bundle steht, also entweder podman 4.4+ mit catatonit
oder docker mit dem Compose-Plugin. Unter Debian installiert kiwi-stack podman
selbst.

`apply` macht mit einem Stack dasselbe wie eine Rolle von kiwi-server (siehe
[Maschinen](machines.md#apply)), setzt aber weder den Hostnamen noch die
Zeitzone. Du kannst es beliebig oft ausführen, und dasselbe Bundle noch einmal
anzuwenden ändert nichts. Einen Rollback gibt es nicht. Daten holst du mit
`kiwi-stack restore` aus dem Modul backup zurück. Eine ältere Konfiguration
bekommst du zurück, indem du ein älteres Bundle anwendest.

Einige Namen auf der Maschine lauten noch `kiwi-server`, zum Beispiel
`/etc/kiwi-server/stack.env` und `/var/lib/kiwi-server/`. Das ist Absicht, denn
diese Namen sind die vereinbarte Schnittstelle zwischen den beiden.
