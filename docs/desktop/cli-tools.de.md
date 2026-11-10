# kiwi-cli-tools-desktop

Vier kleine Kommandozeilen-Helfer für einen Linux-Desktop.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Aktuelles Release: **v1.2.1**. Es steht im [Kiwi-Katalog](catalogs.md), Benutzerbereich.

```bash
kiwi install kiwi-cli-tools-desktop   # oder ./install.sh install, nach ~/.local/bin
```

## `torlink`: eine Maschine über Tor erreichen { #torlink-reach-a-machine-over-tor }

Ein VPN für Arme: Erreiche jeden TCP-Dienst (SSH, eine Web-Oberfläche, eine
Datenbank) auf einer anderen Maschine über Tor, ohne offene Ports, ohne Konten und
ohne Server. Tor und socat laufen in einem rootless Podman-Container, also ist
Podman alles, was du brauchst.

Eine Onion-Adresse ist die Identität. Die anbietende Seite erstellt einen
**Einladungscode** für einen Peer, und die andere Seite nimmt ihn an. Der Code
enthält einen Tor-Client-Autorisierungsschlüssel, sodass der Dienst für alle ohne
ihn unsichtbar ist: Behandle den Code wie ein Passwort.

```bash
# machine A: offer SSH and a web UI to "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # prints torlink1:…  (secret!)

# machine B: use them
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH over Tor
torlink connect alice web           # 127.0.0.1:2200 → alice's web UI
torlink ssh-config >> ~/.ssh/config # then `ssh alice-tor`; `select-server tor` lists them
```

Jede Einladung ist ein eigener Onion-Dienst mit nur den Diensten, die du
aufgeführt hast, daher entfernt `torlink revoke bob` diesen Zugang endgültig.
`torlink ls` zeigt Dienste, Peers und Weiterleitungen. Tor kann nur TCP, und die
erste Verbindung dauert eine Weile. Der SOCKS-Port des Containers (19050) lauscht
nur auf Loopback. Der Zustand, einschließlich deiner Onion-Schlüssel, liegt in
`~/.local/share/torlink`, und `torlink purge` löscht ihn.

## `pweb`: einen Ordner über HTTPS teilen { #pweb-share-a-folder-over-https }

Liefert das **aktuelle Verzeichnis** über HTTPS auf einem zufälligen freien Port
aus, um einer anderen Maschine im selben Netzwerk eine Datei zu geben. Beim ersten
Start wird ein selbstsigniertes Zertifikat erstellt und danach wiederverwendet. Es
liefert an das ganze LAN aus, also starte es in dem Ordner, den du teilen willst,
und beende es mit Strg+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: einen SSH-Host auswählen { #select-server-pick-an-ssh-host }

Ein nummeriertes Menü aller konkreten `Host`-Aliase in deiner `~/.ssh/config`. Wähl
einen aus, und es verbindet sich. Markiere Hosts mit einem Kommentar
`# tags: work prod` im `Host`-Block, um zu filtern:

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # the tags you have
$ select-server -f other.conf   # another config file
```

## `tethering`: der TTL-Fix { #tethering-the-ttl-fix }

Setzt TTL 64 auf den Verkehr, der von einer Schnittstelle ankommt, damit Geräte,
die über diese Maschine getethert sind, für einen Mobilfunkanbieter, der Hops
zählt, wie der eigene Verkehr der Maschine aussehen. Es fragt nach sudo, fügt eine
`iptables`-Mangle-Regel hinzu, und die Regel übersteht einen Neustart **nicht**.

```
tethering            # die Schnittstelle wählen, die Regel setzen
tethering --status
tethering --off
```
