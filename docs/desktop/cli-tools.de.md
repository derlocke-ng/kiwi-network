# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop ist ein Paket mit vier kleinen Kommandozeilenwerkzeugen
für einen Linux-Desktop. Mit `torlink` erreichst du einen Dienst auf einem
anderen Rechner über Tor, `pweb` gibt einen Ordner über HTTPS frei, mit
`select-server` wählst du einen SSH-Host aus einem Menü, und `tethering` passt
die TTL des Verkehrs von angebundenen Geräten an.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Aktuelles Release: **v1.2.1**. Es steht im [Kiwi-Katalog](catalogs.md), Scope user.

```bash
kiwi install kiwi-cli-tools-desktop   # oder ./install.sh install, nach ~/.local/bin
```

## `torlink`: einen Rechner über Tor erreichen { #torlink-reach-a-machine-over-tor }

Mit `torlink` erreichst du jeden TCP-Dienst auf einem anderen Rechner, etwa
SSH, eine Weboberfläche oder eine Datenbank, über das Tor-Netzwerk. Es ist ein
schlichter Ersatz für ein VPN: Keiner der beiden Rechner braucht einen offenen
Port, du brauchst kein Konto, und du musst keinen Server betreiben. Tor und
socat laufen gemeinsam in einem Rootless-Container von Podman. Du brauchst also
nur Podman.

Ein Rechner, der Dienste anbietet, ist über seine Onion-Adresse erreichbar,
eine Adresse innerhalb des Tor-Netzwerks. Auf diesem Rechner erzeugst du einen
**Einladungscode** für einen Peer, also für die Gegenstelle, die Zugriff
bekommen soll. Der Peer nimmt den Code auf dem anderen Rechner an. Der Code
enthält einen Schlüssel für die Client-Autorisierung von Tor. Wer diesen
Schlüssel nicht hat, kann nicht einmal sehen, dass es den Dienst gibt. Behandle
den Code deshalb wie ein Passwort.

```bash
# Rechner A: SSH und eine Weboberfläche für "bob" anbieten
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # gibt torlink1:… aus  (geheim!)

# Rechner B: die Dienste nutzen
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH über Tor
torlink connect alice web           # 127.0.0.1:2200 → Weboberfläche von alice
torlink ssh-config >> ~/.ssh/config # danach `ssh alice-tor`; `select-server tor` listet sie auf
```

Jede Einladung ist ein eigener Onion-Dienst, der nur die Dienste enthält, die
du in ihr aufgeführt hast. Deshalb entzieht `torlink revoke bob` diesen Zugriff
endgültig. `torlink ls` zeigt deine Dienste, deine Peers und deine
Weiterleitungen, also die lokalen Ports, die zu den Diensten eines Peers
führen. Tor überträgt nur TCP, und die erste Verbindung dauert eine Weile. Der
SOCKS-Port des Containers (19050) lauscht nur auf der Loopback-Schnittstelle.
Der Zustand von `torlink`, einschließlich deiner Onion-Schlüssel, liegt in
`~/.local/share/torlink`, und `torlink purge` löscht ihn.

## `pweb`: einen Ordner über HTTPS freigeben { #pweb-share-a-folder-over-https }

`pweb` liefert das **aktuelle Verzeichnis** über HTTPS auf einem zufälligen
freien Port aus. Damit gibst du eine Datei an einen anderen Rechner im selben
Netz weiter. Beim ersten Start erzeugt `pweb` ein selbstsigniertes Zertifikat
und verwendet es danach wieder. Solange `pweb` läuft, kann jeder Rechner im
lokalen Netz auf den Ordner zugreifen. Starte es in dem Ordner, den du
wirklich freigeben willst, und beende es mit Strg+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: einen SSH-Host auswählen { #select-server-pick-an-ssh-host }

`select-server` zeigt ein nummeriertes Menü mit jedem konkreten `Host`-Alias
aus deiner `~/.ssh/config`, also mit jedem Alias, der kein Platzhaltermuster
ist. Du wählst einen aus, und `select-server` verbindet sich mit diesem Host.
Um das Menü zu filtern, versiehst du deine Hosts mit Tags. Schreib dazu einen
Kommentar wie `# tags: work prod` in den `Host`-Block und gib auf der
Kommandozeile ein Tag an:

```
$ select-server work            # nur Hosts mit dem Tag "work"
$ select-server --tags          # die Tags, die du vergeben hast
$ select-server -f other.conf   # eine andere Konfigurationsdatei
```

## `tethering`: die TTL für angebundene Geräte setzen { #tethering-the-ttl-fix }

`tethering` ist für den Fall gedacht, dass andere Geräte die
Internetverbindung dieses Rechners mitbenutzen, was man Tethering nennt.
Manche Mobilfunkanbieter zählen die Netzwerk-Hops des Verkehrs und können so
angebundene Geräte vom Rechner selbst unterscheiden. `tethering` setzt die TTL
für den gesamten Verkehr, der über eine bestimmte Schnittstelle hereinkommt,
auf 64. Für den Anbieter sieht der Verkehr der angebundenen Geräte dann aus
wie der eigene Verkehr des Rechners. Das Werkzeug fragt nach sudo und fügt eine
`iptables`-Mangle-Regel hinzu. Die Regel übersteht einen Neustart **nicht**.

```
tethering            # Schnittstelle auswählen, Regel setzen
tethering --status
tethering --off
```
