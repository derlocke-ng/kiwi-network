# Der Desktop

Beim Desktop-Teil von Kiwi Network geht es um den Rechner, an dem du arbeitest:
eine Linux-Workstation, die sich automatisch einrichtet und ihre Apps aus
git-Katalogen bezieht. Ein Katalog ist ein git-Repository, das Apps auflistet.
Du musst den Rechner nicht von Hand einrichten, und den nächsten richtest du
genauso ein.

Die Desktop-Werkzeuge von Kiwi sind für **Fedora Atomic Desktops** gemacht:
Fedora Silverblue und [Bluefin](https://projectbluefin.io/), vor allem
Bluefin-DX. Diese Systeme werden als ein vollständiges Image installiert und
aktualisiert. Ihr Verzeichnis `/usr` ist unveränderlich, kann also nicht geändert werden,
und ein Update lässt sich problemlos zurücknehmen. Ein eigenes Kiwi-Image gibt es nicht. Du installierst ein
normales Image von Silverblue oder Bluefin und ergänzt es um drei Dinge.

1. **[kiwi-updater](kiwi-updater.md)** installiert Apps aus git-Katalogen und
   hält sie aktuell. Alles landet in deinem Home-Verzeichnis. Nur eine App, die
   Root-Rechte braucht, bekommt zusätzlich einen Teil, der root gehört.
   kiwi-updater aktualisiert sich auch selbst.
2. **[ensconce](ensconce.md)** richtet ein frisch installiertes Bluefin-DX ein.
   Du beschreibst deine Einrichtung in einfachen Listendateien, und ensconce
   setzt sie um: Pakete, Flatpaks, GNOME-Erweiterungen, die Synchronisation mit
   Nextcloud, SSH, sysctl- und Energieeinstellungen, den Anmeldebildschirm und
   deine Kiwi-Apps. Mit `--export` schreibt ensconce die Einrichtung eines
   vorhandenen Rechners in solche Dateien, sodass du diesen Rechner klonen
   kannst.
3. **Die Apps**, die du aus dem [Kiwi-Katalog](catalogs.md) installierst:

| App | Was sie macht |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Ein VPN-Kill-Switch für GNOME. Er ist fail-closed: Solange das VPN nicht steht, bleibt der gesamte Verkehr gesperrt |
| [Kundennetze](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Ein Exit pro VPN- oder SOCKS-Endpunkt. Ein Exit ist ein abgeschotteter Container, der nur diesen einen Endpunkt erreicht. Distro-Boxen und Browser lassen sich an einen Exit hängen, dann läuft ihr gesamter Verkehr darüber |
| [kiwi-server](../server/index.md) | Das Werkzeug, mit dem du dein eigenes Netzwerk aufbaust und betreibst |
| [gnome-monitor](gnome-monitor.md) | Speichert Bildschirmanordnungen und wechselt zwischen ihnen. Außerdem schaltet es einzelne Monitore aus und wieder ein |
| [syncman](syncman.md) | Synchronisiert Ordner in beide Richtungen, zum Beispiel Spielstände. Die Synchronisation läuft in systemd-Benutzerdiensten |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Außerdem beschreibt dieser Abschnitt [kiwi-gen](kiwi-gen.md), eine Verwaltung
für Schlüssel und Zertifikate, die im Browser läuft und offline funktioniert.

## Von der frischen Installation an { #from-a-fresh-install }

Mit diesen Befehlen kommst du von einem frisch installierten System zu einem
Desktop mit den Kiwi-Apps:

```bash
# 1. kiwi-updater: Scope user und system, eine Passwortabfrage; der Kiwi-Katalog ist schon dabei
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. den Rechner einrichten
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. die Apps, die du willst (oder in kiwi-apps.list von ensconce eintragen)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

Apps lassen sich auch ohne Terminal installieren. **Kiwi Apps** (`kiwi-gui`)
in der Anwendungsübersicht installiert eine App mit einem Klick.

## Mit deinem Netzwerk verbinden { #joining-your-network }

Ein Desktop kommt genauso ins Mesh wie jedes andere Gerät. Das Mesh ist das
private WireGuard-Netzwerk, das deine Server und Geräte verbindet. Der Befehl
`kiwi-server enroll fleet.yaml laptop --group devices` schreibt eine
WireGuard-Konfigurationsdatei, die du in den GNOME-Einstellungen importierst.
Importiere außerdem die Zertifizierungsstelle (CA) deines Netzwerks,
`kiwiCA.pem`. Dann vertraut der Desktop den HTTPS-Zertifikaten der Namen in
deinem Netzwerk. ensconce installiert jede `.pem`-Datei aus seinem Verzeichnis
`certs/` systemweit.

Danach schützt [kiwi-killswitch](kiwi-killswitch.md) diese Verbindung und
sorgt dafür, dass der Rechner fail-closed bleibt: Verkehr, der nicht über die
Verbindung läuft, wird gesperrt, auch wenn die Verbindung gerade nicht steht.
Zu Hause schickt vielleicht schon ein Gateway-Node in deinem LAN deinen Verkehr
durch einen Tunnel. Mit der Einstellung *trusted kiwi-nodes* akzeptiert der
Kill-Switch einen solchen Gateway-Node anstelle des Tunnels.
