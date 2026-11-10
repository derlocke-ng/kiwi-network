# Kataloge & Apps veröffentlichen

## Der Kiwi-Katalog { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) ist der
App-Katalog für das Kiwi Network. Die Installation von kiwi-updater registriert ihn,
und `kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` registriert
ihn von Hand.

| App | Release | Bereiche | Was sie ist |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | Benutzer | der Updater selbst |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | Benutzer + System | Fail-Closed-VPN-Kill-Switch für GNOME |
| [ensconce](ensconce.md) | v2.5.0 | Benutzer | Einrichtung nach der Installation für Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | Benutzer | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | Benutzer | versiegelte SOCKS5/VPN-Ausgänge in rootless Podman |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | Benutzer | isolierte Browser-Identitäten an Ausgängen von kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | Benutzer | Distro-Boxen, deren Verkehr nur über einen Ausgang hinausgeht |
| [kiwi-server](../server/index.md) | v2.42.0 | Benutzer | dein eigenes Netzwerk bauen und betreiben |
| [syncman](syncman.md) | v0.4.1 | Benutzer | Zweiwege-Ordnersynchronisation |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | Benutzer | Bildschirm-Layouts für GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | Benutzer | kiwi-proxy-Provider: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | Benutzer | kiwi-proxy-Provider: ein VPN über gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | Benutzer | kiwi-proxy-Provider: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | Benutzer | kiwi-proxy-Provider: Mysterium |

kiwi synchronisiert den Katalog vor jeder Prüfung und jedem Update, also ist eine
Fleet von Desktops zu verwalten einfach nur git:

- **eine App hinzufügen**: ihre URL in `apps.list` eintragen und committen;
- **festlegen oder zurückrollen**: `ref=<tag>` an ihre Zeile anhängen (auf einer
  einzelnen Maschine tut `kiwi pin <app> <tag>` dasselbe);
- **entfernen**: die Zeile löschen (installierte Kopien bleiben, bis du sie
  deinstallierst).

## Dein eigener Katalog { #your-own-catalog }

Ein Katalog ist ein Git-Repository mit einer `apps.list` und optional einem
`catalog.manifest`, das ihn selbst beschreibt:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: eine Zeile pro App, auch wenn sie eine Root-Hälfte und eine Benutzer-Hälfte hat
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Option | Bedeutung |
|---|---|
| `branch=<name>` | einem Branch statt Release-Tags folgen |
| `ref=<tag>` | eine exakte Version festlegen |
| `scope=user\|system` | auf Maschinen, die diese Liste nutzen, nur diese Hälfte installieren. Das ist ein *Filter*, keine Deklaration |

Die eigene Liste einer Maschine (`~/.config/kiwi-updater/apps.list` oder
`/etc/kiwi-updater/apps.list` für root) schlägt immer einen Katalog.
`kiwi add <url>` fügt ihr eine Zeile hinzu.

## Eine App veröffentlichen { #publishing-an-app }

Leg ein `kiwi.manifest` und ein `install.sh` ins Wurzelverzeichnis deines
Repositorys. Vorlagen liegen in
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates) von
kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Weitere Schlüssel: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (eine Datei,
die Kiwi Apps anzeigt), `DEPENDS` und, für alles mit einer System-Hälfte,
`ROOT_REASON`. `ICON=` ist ein SVG oder PNG von höchstens 1 MiB im Repository. Die
meisten Kiwi-Apps nehmen ihres aus [kiwi-icons](../project/brand.md).

!!! warning "Kommentare gehören in eine eigene Zeile"
    Ein Wert reicht bis zum Zeilenende. `COMPONENTS=cli  # … gui …` macht den
    Kommentar zum Teil des Werts, und die App wird dann so behandelt, als hätte sie
    eine GUI.

kiwi führt deinen Installer einmal **pro deklariertem Bereich** aus, mit:

| Variable | Wert |
|---|---|
| `KIWI_SCOPE` | `user` oder `system` |
| `KIWI_PREFIX` | `~/.local` oder `/usr/local` |
| `KIWI_APP_DIR` | absoluter Pfad des Klons |
| `KIWI_ACTION` | `install`, `update` oder `uninstall` |
| `KIWI_GUI` | `0` auf einer Maschine ohne Bildschirm oder mit `--cli-only` |
| `KIWI_PURGE` | `1`, wenn der Benutzer `--purge` verlangt hat |
| `PATH` | `$KIWI_PREFIX/bin` zuerst; ein fester Systempfad für den Systembereich |

Ein Installer für beide Bereiche verzweigt anhand von `KIWI_SCOPE` und erledigt
jedes Mal nur diese Hälfte. Ohne `--purge` lass die Konfiguration des Benutzers, wo
sie ist.

**Veröffentliche mit einem signierten Tag**, damit sich eine System-Hälfte ohne
Passwort aktualisiert:

```bash
git config gpg.format ssh            # mit deinem SSH-Schlüssel signieren
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

`templates/release.yml` von kiwi-updater veröffentlicht ein GitHub-Release nur für
einen Tag, der mit einem Schlüssel aus `.github/allowed_signers` signiert ist, und
legt nie selbst Tags an. Öffne dann einen Pull Request, der deine URL zum Katalog
hinzufügt. Alles, was Open Source ist und ohne Konto, Abo oder Tracker wirklich
benutzbar, ist willkommen.

## Vertrauen { #trust }

Der Katalog ist **kuratiert, nicht geprüft**. Gelistet zu sein heißt, dass jemand die
App für lohnend hielt, nicht, dass ihr Code begutachtet wurde. Lies
`kiwi info <app>`, bevor du etwas installierst, das du noch nicht kennst, und
`kiwi info --installer <app>`, um genau zu sehen, was ausgeführt wird.
