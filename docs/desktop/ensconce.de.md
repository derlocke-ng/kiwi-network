# ensconce

ensconce richtet ein frisch installiertes [Bluefin-DX](https://projectbluefin.io/)
für dich ein, damit du nicht jeden neuen Rechner von Hand konfigurieren musst.
Du beschreibst deinen Arbeitsplatz in einfachen Listendateien, und ensconce
macht aus der frischen Installation genau diesen Arbeitsplatz. Es kümmert sich
um geschichtete Pakete, Flatpaks, GNOME-Erweiterungen, die Synchronisation mit
Nextcloud, eine SSH-Konfiguration, die zwischen deinen Rechnern synchron
bleibt, die Einstellungen des Desktops und des Anmeldebildschirms sowie deine
Kiwi-Apps. Geschichtete Pakete (Layered Packages) sind RPM-Pakete, die
zusätzlich zum System-Image installiert werden. Die Einrichtung ist modular:
Sie besteht aus einzelnen Schritten, die du ausführen oder überspringen kannst.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  Laut Manifest ist die Lizenz GPL-3.0-or-later, in der README steht GPL-3.0.
- Aktuelles Release: **v2.5.0**. Es steht im [Kiwi-Katalog](catalogs.md) und
  wird im Scope user installiert, also in deinem Home-Verzeichnis.

```bash
kiwi install ensconce
ensconce --init          # ~/.config/ensconce aus den Beispielen anlegen
ensconce                 # die Einrichtung ausführen
```

Du kannst ensconce auch aus einem Klon des Repositorys starten. Führe
`./ensconce.sh --init` aus, bearbeite die Dateien in `config/` und starte dann
`./ensconce.sh`.

## Schritte { #steps }

Die Einrichtung ist in Schritte aufgeteilt. Jeder Schritt ist ein Skript in
`steps/`, und die Schritte laufen in dieser Reihenfolge:

| # | Schritt | Was er macht |
|---|---|---|
| 01 | `rebase` | stellt das System auf Bluefin-DX um |
| 02 | `ujust` | richtet Entwicklergruppen und CLI-Werkzeuge ein |
| 03 | `repos` | fügt RPM-Repositories hinzu |
| 04 | `packages` | installiert RPM-Pakete als geschichtete Pakete |
| 05 | `flatpaks` | installiert Flatpak-Apps. `FLATPAK_LANGUAGES` legt fest, in welchen Sprachen ihre Übersetzungen installiert werden |
| 06 | `overrides` | setzt Overrides für die Berechtigungen von Flatpaks |
| 07 | `extensions` | installiert Erweiterungen für die GNOME Shell |
| 08 | `cacert` | installiert eigene CA-Zertifikate |
| 09 | `nextcloud` | konfiguriert die Ordner-Synchronisation mit Nextcloud im Voraus |
| 10 | `dconf` | setzt die Einstellungen des GNOME-Desktops |
| 11 | `gdm` | konfiguriert den Anmeldebildschirm |
| 12 | `ssh` | richtet die synchronisierte SSH-Konfiguration ein, mit Bitwarden oder GNOME als SSH-Agent |
| 13 | `kiwi` | installiert kiwi-updater in der Variante, die `KIWI_INSTALL=recommended\|manual\|minimal` auswählt, und danach jede App aus `kiwi-apps.list` |
| 14 | `sysctl` | installiert die Dateien mit Kernel-Einstellungen aus `sysctl.d/`. Eine Beispieldatei begrenzt, wie viele noch nicht geschriebene Daten der Kernel im Speicher hält. Das hilft bei langsamen SSDs |
| 15 | `power` | maskiert mit `SYSTEM_SLEEP=off` die Ruhezustands-Targets, sodass der Rechner nicht in den Ruhezustand gehen kann |

Bevor ensconce loslegt, prüft es die Umgebung. Das System muss ein
Bluefin-Image sein, und `rpm-ostree`, `flatpak`, `dconf`, `jq` und `curl`
müssen vorhanden sein. ensconce speichert seinen Fortschritt und macht nach
einem Neustart dort weiter, wo es aufgehört hat. Während des ganzen Laufs hält
es den Rechner wach und stellt danach deine Energieeinstellungen wieder her.

Mit diesen Optionen steuerst du einen Lauf:

```bash
ensconce --dry-run                  # Vorschau, ohne etwas zu ändern
ensconce --skip rebase,ujust        # Schritte überspringen
ensconce --only extensions,dconf    # nur diese ausführen
ensconce --status | --list-steps | --reset
ensconce --log [file]               # die Ausgabe speichern
ensconce --config-dir               # das aktive Konfigurationsverzeichnis ausgeben
```

## Konfiguration { #configuration }

ensconce sucht sein Konfigurationsverzeichnis an vier Stellen und nimmt das
erste, das es gibt. Zuerst schaut es in `$ENSCONCE_CONFIG`, dann in
`~/.config/ensconce/`, das verwendet wird, wenn ensconce mit kiwi installiert
wurde, dann in `config/` in einem Klon und zuletzt in `config.example/`. Nimmt
es `config.example/`, gibt es eine Warnung aus.

| Datei / Verzeichnis | Zweck |
|---|---|
| `settings.sh` | Server-URLs und die Schalter für SSH, kiwi-updater, Flatpak-Sprachen und Ruhezustand |
| `packages.list`, `flatpaks.list`, `extensions.list` | die Pakete, Flatpaks und GNOME-Erweiterungen, die installiert werden, eins pro Zeile |
| `kiwi-apps.list` | die Kiwi-Apps, die installiert werden |
| `repos.d/`, `flatpak-overrides/` | Repository-Dateien und Overrides für einzelne Apps im eigenen Format von Flatpak |
| `nextcloud/folders.list` | die Ordner, die synchronisiert werden, in der Form `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | was von der Synchronisation ausgenommen wird, für alle Ordner und für einzelne Ordner mit einem Tag |
| `certs/` | CA-Zertifikate (`.pem`), zum Beispiel die `kiwiCA.pem` deines Netzwerks |
| `sysctl.d/` | Kernel-Einstellungen |
| `dconf-settings.ini`, `gtk3-bookmarks` | GNOME-Einstellungen und Lesezeichen für Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | die Einstellungen und die Bildschirmanordnung des Anmeldebildschirms |

Ein Tag in `nextcloud/folders.list` gibt einem Ordner eigene Ausnahmen. Das Tag
`browser` zum Beispiel legt `exclude.d/browser.lst` in diesen Ordner. Die
Datenbanken eines Browser-Profils werden dann nicht synchronisiert, weil sie
dabei kaputtgehen können, `user.js` dagegen schon.

## Einen Rechner klonen { #cloning-a-machine }

`--export` macht das Gegenteil der Schritte: Es liest das laufende System aus
und schreibt daraus ein Konfigurationsverzeichnis für ensconce. Mit diesem
Verzeichnis richtest du dann einen neuen Rechner ein:

```bash
ensconce --export ./my-setup        # auf dem eingerichteten Rechner
ensconce --init                     # auf dem neuen
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Der Export enthält nur das, was du dem System hinzugefügt hast. Er führt die
Pakete auf, die du angefordert hast, nicht das ganze Image. Er nennt nur die
Erweiterungen, die wirklich von extensions.gnome.org stammen. Er enthält deine
eigenen Repository-Dateien und ausgewählte dconf-Teilbäume statt eines
vollständigen Abzugs. Sieh den Export als Ausgangspunkt. In `certs/` und
`nextcloud/` können private Daten liegen.

ensconce ist eine App für den Scope **user**. Die Schritte, die Root-Rechte
brauchen, fordern sie selbst an. Für einen eigenen Schritt legst du eine Datei
`steps/NN-<name>.sh` mit einer Funktion `step_<name>()` an.
