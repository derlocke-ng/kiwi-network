# ensconce

Modulare Einrichtung nach der Installation für [Bluefin-DX](https://projectbluefin.io/).
ensconce macht aus einer frischen Bluefin-Installation deine fertig konfigurierte
Workstation, aus einfachen Listendateien: geschichtete Pakete, Flatpaks,
GNOME-Erweiterungen, Nextcloud-Sync, eine synchronisierte SSH-Konfiguration,
Einstellungen für Desktop und Anmeldebildschirm und deine Kiwi-Apps.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (laut Manifest; die README sagt GPL-3.0)
- Aktuelles Release: **v2.5.0**. Es steht im [Kiwi-Katalog](catalogs.md), Benutzerbereich.

```bash
kiwi install ensconce
ensconce --init          # ~/.config/ensconce aus den Beispielen anlegen
ensconce                 # die Einrichtung ausführen
```

Oder aus einem Klon: `./ensconce.sh --init`, `config/` bearbeiten, dann
`./ensconce.sh`.

## Schritte { #steps }

Jede Phase ist ein Skript in `steps/`, ausgeführt der Reihe nach:

| # | Schritt | Tut |
|---|---|---|
| 01 | `rebase` | auf Bluefin-DX wechseln |
| 02 | `ujust` | Entwicklergruppen und CLI-Werkzeuge |
| 03 | `repos` | RPM-Repositories hinzufügen |
| 04 | `packages` | RPM-Pakete schichten |
| 05 | `flatpaks` | Flatpak-Apps installieren (`FLATPAK_LANGUAGES` wählt ihre Übersetzungen) |
| 06 | `overrides` | Überschreibungen von Flatpak-Berechtigungen |
| 07 | `extensions` | GNOME-Shell-Erweiterungen |
| 08 | `cacert` | eigene CA-Zertifikate |
| 09 | `nextcloud` | Nextcloud-Ordnersynchronisation vorbelegen |
| 10 | `dconf` | GNOME-Desktop-Einstellungen |
| 11 | `gdm` | der Anmeldebildschirm |
| 12 | `ssh` | eine synchronisierte SSH-Konfiguration, mit Bitwarden oder GNOME als SSH-Agent |
| 13 | `kiwi` | kiwi-updater installieren (`KIWI_INSTALL=recommended\|manual\|minimal`) und jede App in `kiwi-apps.list` |
| 14 | `sysctl` | Drop-ins aus `sysctl.d/` (ein Beispiel begrenzt das Dirty-Writeback für langsame SSDs) |
| 15 | `power` | `SYSTEM_SLEEP=off` maskiert die Sleep-Targets |

ensconce prüft zuerst die Umgebung (ein Bluefin-Image, `rpm-ostree`, `flatpak`,
`dconf`, `jq`, `curl`). Es speichert seinen Fortschritt und macht nach Neustarts
weiter, hält die Maschine während des ganzen Laufs wach und stellt danach deine
Energieeinstellungen wieder her.

```bash
ensconce --dry-run                  # Vorschau, ohne etwas zu ändern
ensconce --skip rebase,ujust        # Schritte überspringen
ensconce --only extensions,dconf    # nur diese ausführen
ensconce --status | --list-steps | --reset
ensconce --log [file]               # die Ausgabe speichern
ensconce --config-dir               # das aktive Konfigurationsverzeichnis ausgeben
```

## Konfiguration { #configuration }

Das Konfigurationsverzeichnis ist das erste vorhandene von: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (über kiwi installiert), `config/` in einem Klon und
`config.example/` (mit einer Warnung).

| Datei / Verzeichnis | Zweck |
|---|---|
| `settings.sh` | Server-URLs und Schalter: SSH, kiwi-updater, Flatpak-Sprachen, Ruhezustand |
| `packages.list`, `flatpaks.list`, `extensions.list` | ein Eintrag pro Zeile |
| `kiwi-apps.list` | die zu installierenden Kiwi-Apps |
| `repos.d/`, `flatpak-overrides/` | Repo-Dateien; Überschreibungen pro App im eigenen Format von Flatpak |
| `nextcloud/folders.list` | Sync-Ordner als `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | globale und ordnerbezogene (getaggte) Sync-Ausschlüsse |
| `certs/` | CA-Zertifikate (`.pem`), zum Beispiel die `kiwiCA.pem` deiner Fleet |
| `sysctl.d/` | Kernel-Einstellungen |
| `dconf-settings.ini`, `gtk3-bookmarks` | GNOME-Einstellungen, Nautilus-Lesezeichen |
| `gdm/dconf.d/`, `gdm/monitors.xml` | die Einstellungen und das Bildschirm-Layout des Anmeldebildschirms |

Ein ordnerbezogener Ausschluss-Tag wie `browser` legt `exclude.d/browser.lst` in
diesen Ordner, was verhindert, dass die Datenbanken eines Browserprofils
synchronisiert (und beschädigt) werden, während `user.js` weiterhin synchronisiert
wird.

## Eine Maschine klonen { #cloning-a-machine }

`--export` liest das laufende System und schreibt einen ensconce-Konfigurationsbaum,
die Umkehrung der Schritte:

```bash
ensconce --export ./my-setup        # auf der konfigurierten Maschine
ensconce --init                     # auf der neuen
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Es erfasst nur, was du hinzugefügt hast: angeforderte Pakete statt des ganzen
Images, Erweiterungen, die wirklich von extensions.gnome.org stammen, deine eigenen
Repo-Dateien und ausgewählte dconf-Teilbäume statt eines vollständigen Dumps.
Betrachte es als Ausgangspunkt. `certs/` und `nextcloud/` können private Daten
enthalten.

ensconce ist eine App im **Benutzerbereich**. Die Schritte, die root brauchen,
fragen selbst danach. Füge einen eigenen Schritt als `steps/NN-<name>.sh` mit einer
Funktion `step_<name>()` hinzu.
