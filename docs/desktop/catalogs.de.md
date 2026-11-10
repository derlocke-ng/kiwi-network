# Kataloge und Apps veröffentlichen

Ein Katalog ist eine Liste von Apps, die kiwi-updater installieren kann. Er ist
ein git-Repository. Du kannst ihn also lesen, kopieren und Änderungen daran
vorschlagen. Diese Seite stellt den Kiwi-Katalog vor, zeigt, wie du einen
eigenen Katalog anlegst, zum Beispiel für alle Desktops, um die du dich
kümmerst, und erklärt, wie du eine App veröffentlichst, damit andere sie mit
kiwi installieren können.

## Der Kiwi-Katalog { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) ist der
App-Katalog von Kiwi Network. Er wird automatisch eingetragen, wenn du
kiwi-updater installierst. Von Hand trägst du ihn mit
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` ein.

Die Tabelle zeigt die Apps im Katalog. Die Spalte *Scopes* gibt an, wo eine App
installiert wird. Bei user landet sie in deinem Home-Verzeichnis, bei system
bekommt sie zusätzlich einen Teil, der root gehört.

| App | Release | Scopes | Was es ist |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | der Updater selbst |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | VPN-Kill-Switch für GNOME. Er ist fail-closed: Solange das VPN nicht steht, bleibt der gesamte Verkehr gesperrt |
| [ensconce](ensconce.md) | v2.5.0 | user | richtet ein frisch installiertes Bluefin-DX ein |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | Exits für SOCKS5- und VPN-Verbindungen. Ein Exit ist ein abgeschotteter Container in rootless Podman |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | getrennte Browser-Identitäten, die Exits von kiwi-proxy nutzen |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | Distro-Boxen (Container mit einer Linux-Distribution), deren Verkehr ausschließlich über einen Exit läuft |
| [kiwi-server](../server/index.md) | v2.42.0 | user | das Werkzeug, mit dem du dein eigenes Netzwerk aufbaust und betreibst |
| [syncman](syncman.md) | v0.4.1 | user | synchronisiert Ordner in beide Richtungen |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | speichert Bildschirmanordnungen in GNOME und wechselt zwischen ihnen |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | Provider-Modul für kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | Provider-Modul für kiwi-proxy: ein VPN über gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | Provider-Modul für kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | Provider-Modul für kiwi-proxy: Mysterium |

kiwi holt sich vor jeder Prüfung und jedem Update den aktuellen Stand des
Katalogs. Die Apps auf einer ganzen Reihe von Desktops kannst du deshalb
allein mit git verwalten:

- **Eine App hinzufügen:** Trag ihre URL in `apps.list` ein und committe.
- **Eine App auf eine Version festlegen oder zurücksetzen:** Häng `ref=<tag>`
  an ihre Zeile an. Auf einem einzelnen Rechner erreichst du dasselbe mit
  `kiwi pin <app> <tag>`.
- **Eine App entfernen:** Lösch ihre Zeile. Bereits installierte Kopien bleiben
  installiert, bis du sie deinstallierst.

## Ein eigener Katalog { #your-own-catalog }

Ein Katalog ist ein git-Repository mit einer Datei `apps.list`. Zusätzlich kann
er eine Datei `catalog.manifest` enthalten, in der er sich selbst beschreibt:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: eine Zeile pro App, auch wenn sie einen root-Teil und einen Benutzerteil hat
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Hinter der URL kann eine Zeile in `apps.list` diese Optionen haben:

| Option | Bedeutung |
|---|---|
| `branch=<name>` | einem Branch folgen statt den Release-Tags |
| `ref=<tag>` | genau auf dieser Version bleiben |
| `scope=user\|system` | auf Rechnern, die diese Liste verwenden, nur diesen Teil der App installieren. Die Option ist ein *Filter*. Sie legt nicht fest, welche Scopes die App hat |

Jeder Rechner hat außerdem eine eigene Liste:
`~/.config/kiwi-updater/apps.list` für deinen Benutzer und
`/etc/kiwi-updater/apps.list` für root. Ein Eintrag in der Liste des Rechners
hat immer Vorrang vor einem Katalog. `kiwi add <url>` fügt dieser Liste eine
Zeile hinzu.

## Eine App veröffentlichen { #publishing-an-app }

Um eine App zu veröffentlichen, legst du eine Datei `kiwi.manifest` und ein
Skript `install.sh` ins oberste Verzeichnis deines Repositorys. Vorlagen dafür
findest du im Verzeichnis
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
von kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system oder beides
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Ein Manifest kann weitere Schlüssel haben: `AUTHOR`, `CATEGORY`, `TAGS`,
`SCREENSHOTS`, `ABOUT` (eine Datei, die Kiwi Apps anzeigt), `DEPENDS` und
`ROOT_REASON`. Jede App mit einem Systemteil braucht `ROOT_REASON`. `ICON=`
nennt eine SVG- oder PNG-Datei im Repository, die höchstens 1 MiB groß ist. Die
meisten Kiwi-Apps nehmen ihr Icon aus [kiwi-icons](../project/brand.md).

!!! warning "Kommentare in eine eigene Zeile"
    Ein Wert reicht bis zum Ende seiner Zeile. Schreibst du
    `COMPONENTS=cli  # … gui …`, wird der Kommentar Teil des Werts, und kiwi
    behandelt die App dann so, als hätte sie eine grafische Oberfläche.

kiwi führt dein Installationsskript einmal **für jeden Scope aus, den die App
angibt**. Dabei setzt es diese Variablen:

| Variable | Wert |
|---|---|
| `KIWI_SCOPE` | `user` oder `system` |
| `KIWI_PREFIX` | `~/.local` oder `/usr/local` |
| `KIWI_APP_DIR` | absoluter Pfad des Klons |
| `KIWI_ACTION` | `install`, `update` oder `uninstall` |
| `KIWI_GUI` | `0` auf einem Rechner ohne grafischen Desktop (headless) oder mit `--cli-only` |
| `KIWI_PURGE` | `1`, wenn der Benutzer `--purge` angegeben hat |
| `PATH` | `$KIWI_PREFIX/bin` steht an erster Stelle. Der Scope system bekommt einen festen Systempfad |

Das Installationsskript einer App mit beiden Scopes muss `KIWI_SCOPE` prüfen und
bei jedem Durchlauf nur die Arbeit für den jeweiligen Teil erledigen. Hat der
Benutzer nicht `--purge` angegeben, lass seine Konfiguration, wo sie ist.

**Veröffentliche jedes Release als signiertes Tag.** Nur dann lässt sich ein
Systemteil ohne Passwort aktualisieren:

```bash
git config gpg.format ssh            # mit deinem SSH-Schlüssel signieren
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater bringt einen Release-Workflow mit, `templates/release.yml`. Er
veröffentlicht ein GitHub-Release nur für ein Tag, das mit einem Schlüssel aus
`.github/allowed_signers` signiert ist, und legt selbst nie Tags an. Zum
Schluss stellst du einen Pull Request, der deine URL in den Katalog einträgt.
Willkommen ist jede App, die quelloffen ist und sich wirklich ohne Konto, Abo
oder Tracker benutzen lässt.

## Vertrauen { #trust }

Der Katalog ist **kuratiert, aber nicht geprüft**. Eine App steht darin, weil
jemand sie für nützlich hielt. Das heißt nicht, dass ihr Code durchgesehen
wurde. Bevor du eine App installierst, die du nicht kennst, lies die Ausgabe
von `kiwi info <app>`. Mit `kiwi info --installer <app>` siehst du genau, was
ausgeführt wird.
