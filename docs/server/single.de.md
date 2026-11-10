# Eine Maschine, ohne Fleet

kiwi-server besteht aus zwei kleineren Werkzeugen, und du kannst sie auch einzeln
benutzen:

| Repository | Was es ist |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Die Module und ihr Renderer: **eine Maschinendatei rein, ein Stack-Bundle raus**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Die Maschinenseite: der Befehl `kiwi-stack` und die Bibliothek, die ein Bundle auf CoreOS, uCore oder Debian bringen und am Laufen halten. v0.5.0, GPL-3.0-or-later |

Nutze sie, wenn du einen Stack auf einer Maschine ohne den Rest willst: einen Node,
den du von Hand einrichtest, ein Modul, das du entwickelst, oder eine Maschine, die
ihren eigenen Stack rendert. kiwi-server bringt beide mit, festgelegt per Tag. Eine
Maschine, die auf die eine oder andere Weise eingerichtet wurde, ist am Ende
identisch, und beide leiten aus demselben Seed dieselben Secrets ab.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Eine Maschine rendern { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # anpassen: TLS-Dateien, die WireGuard-Konfiguration
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Es braucht Python 3 mit PyYAML und Jinja2. `kiwi-modules modules -v` listet jedes
Modul und jede Einstellung auf, und `kiwi-modules profiles` listet die Rollen und
ihre Presets.

```yaml
# a cloud node
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
dns_records:                    # the network's names
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # trusted inside the containers and on the host
seed: secrets/seed              # generated passwords derive from it
```

kiwi-modules hat keine eigene Zertifizierungsstelle, daher braucht ein
eigenständiges Rendern die Dateien mit TLS-Zertifikat und Schlüssel. Die
WireGuard-Konfiguration wird unter `secrets/<hostname>.conf` gefunden, wenn die
Maschinendatei keine nennt.

## Auf die Maschine bringen { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack und seine Bibliothek
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Es braucht bash und systemd, dazu podman 4.4+ mit catatonit (oder docker mit dem
Compose-Plugin), je nachdem, welche `runtime` das Bundle hat. Unter Debian
installiert es podman selbst.

`apply` tut das, was eine kiwi-server-Rolle mit einem Stack tut (siehe
[Maschinen](machines.md#apply)), außer Hostname und Zeitzone zu setzen. Es ist
wiederholbar: Dasselbe Bundle noch einmal ändert nichts. Es gibt kein Rollback.
Daten kommen mit `kiwi-stack restore` aus dem Backup-Modul zurück, und eine ältere
Konfiguration, indem du ein älteres Bundle anwendest.

Auf der Maschine heißen die Namen weiterhin `kiwi-server`
(`/etc/kiwi-server/stack.env`, `/var/lib/kiwi-server/`), mit Absicht: Sie sind der
Vertrag zwischen den beiden.
