# Der Desktop

Die Kiwi-Desktop-Werkzeuge sind für **Fedora-Atomic-Desktops** gebaut: Fedora
Silverblue und [Bluefin](https://projectbluefin.io/) (insbesondere Bluefin-DX).
Das sind imagebasierte Systeme mit einem unveränderlichen `/usr` und einfachem
Rollback. Es gibt kein spezielles Kiwi-Image: Du installierst ein Standard-Image
und legst drei Schichten darüber.

1. **[kiwi-updater](kiwi-updater.md)** installiert und aktualisiert Apps aus
   Git-Katalogen: alles in deinem Home-Verzeichnis, dazu einen Teil, der root
   gehört, nur für Apps, die einen brauchen. Es aktualisiert sich auch selbst.
2. **[ensconce](ensconce.md)** richtet ein frisches Bluefin-DX aus einfachen
   Listendateien ein: Pakete, Flatpaks, GNOME-Erweiterungen, Nextcloud-Sync, SSH,
   sysctl- und Energieeinstellungen, den Anmeldebildschirm und deine Kiwi-Apps.
   `--export` klont eine Maschine.
3. **Die Apps**, aus dem [Kiwi-Katalog](catalogs.md):

| App | Was sie tut |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Ein Fail-Closed-VPN-Kill-Switch für GNOME |
| [Kundennetze](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | Ein versiegelter Ausgang pro VPN- oder SOCKS-Endpunkt, und Distro-Boxen und Browser, die darin leben |
| [kiwi-server](../server/index.md) | Dein eigenes Netzwerk bauen und betreiben |
| [gnome-monitor](gnome-monitor.md) | Bildschirm-Layouts speichern und wechseln; einzelne Monitore aus- und einschalten |
| [syncman](syncman.md) | Zweiwege-Ordnersynchronisation (Spielstände und mehr) als Benutzerdienste |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Außerdem hier: [kiwi-gen](kiwi-gen.md), ein Schlüssel- und Zertifikatsmanager, der
offline im Browser läuft.

## Von einer frischen Installation aus { #from-a-fresh-install }

```bash
# 1. kiwi-updater: Benutzer- und Systembereich, eine Passwortabfrage; der Kiwi-Katalog kommt gleich mit
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. die Maschine einrichten
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. die Apps, die du willst (oder trag sie in die kiwi-apps.list von ensconce ein)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

**Kiwi Apps** (`kiwi-gui`) im App-Raster erledigt dasselbe mit einem Klick.

## Deinem Netzwerk beitreten { #joining-your-network }

Ein Desktop tritt dem Mesh bei wie jedes andere Gerät: `kiwi-server enroll fleet.yaml
laptop --group devices` schreibt eine WireGuard-Konfiguration, die du in die
GNOME-Einstellungen importierst. Importiere die CA der Fleet (`kiwiCA.pem`), damit
ihren HTTPS-Namen vertraut wird. ensconce installiert jede `.pem` aus seinem
Verzeichnis `certs/` systemweit.

[kiwi-killswitch](kiwi-killswitch.md) hält die Maschine dann rund um diese
Verbindung fail-closed. Seine Einstellung *trusted kiwi-nodes* lässt zu Hause einen
Gateway-Node in deinem LAN an die Stelle des Tunnels treten.
