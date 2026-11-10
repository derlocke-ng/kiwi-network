# kiwi-updater

`kiwi` installiert und aktualisiert Open-Source-Apps aus **Git-Katalogen** auf Fedora
Silverblue, Bluefin und anderen ostree-Systemen. Eine App ist ein Git-Repository mit
einem `kiwi.manifest` und einem `install.sh`. kiwi klont es, checkt seinen neuesten
Release-Tag aus, führt seinen Installer aus und hält es im Hintergrund aktuell, sich
selbst eingeschlossen.

Es gibt keine Konten, keinen Store und keinen Anbieter. Ein Katalog ist ein
Repository, das du lesen, forken und an das du einen Pull Request schicken kannst.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Aktuelles Release: **v2.4.0**, ein Sicherheits-Release
- **`kiwi`** ist die CLI. Sie braucht `git`, coreutils, `util-linux` und `awk`, alles
  im Basis-Image, dazu `ssh-keygen` für Signaturprüfungen.
- **Kiwi Apps** (`kiwi-gui`) ist die GTK4-App: Suche, Filter, eine Detailansicht pro
  App mit Icon, Screenshots und Abhängigkeiten. Sie zeigt den Installer und den Diff
  eines Updates, bevor sie eines davon ausführt, und reiht deine Klicks in eine
  Warteschlange ein. Ihre Daten kommen von der CLI; Icons und Screenshots werden aus
  den Klonen der Apps gelesen, sodass dafür nichts heruntergeladen wird.

## Installation { #install }

```bash
# empfohlen: Benutzerbereich plus der Systembereich, der root gehört, eine Passwortabfrage
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimal: zu 100 % auf Benutzerebene, nur ~/.local, kein root und nie ein Passwort
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# überhaupt keine Aktion ohne Passwort: jede Systemänderung fragt nach einem Passwort
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

Der [Kiwi-Katalog](catalogs.md) wird bei der Installation registriert. Geh direkt zu
`kiwi list` oder öffne **Kiwi Apps**.

Apps, die nur aus Dateien in deinem Home-Verzeichnis bestehen (die CLI-Werkzeuge,
ensconce, syncman), sind mit der minimalen Installation vollständig. Eine App mit
einer Root-Hälfte, wie kiwi-killswitch, braucht den Systembereich. Bei einer
minimalen Installation richtet `kiwi install kiwi-killswitch` ihn an Ort und Stelle
mit einem Passwort ein.

## Befehle { #commands }

```bash
kiwi list [--check]          # jede App, die diese Maschine kennt
kiwi search vpn              # eine App in jedem registrierten Katalog finden
kiwi info kiwi-killswitch    # was sie ist, was sie installiert, ob sie root braucht
kiwi install <app>           # ein Name oder ausdrücklich --all
kiwi update [<app>]          # alles mit einem neuen Release
kiwi uninstall <app>         # --purge entfernt auch ihre Konfiguration
kiwi check                   # Exit-Code 10, wenn irgendetwas ein Update hat

kiwi add <https-url>         # ein Repository direkt verfolgen, ohne Katalog
kiwi catalog add|list|remove # Kataloge verwalten
kiwi sync                    # Kataloge jetzt aktualisieren
kiwi self-update
kiwi trust --system <app>    # den für eine System-App festgelegten Signaturschlüssel vergessen
```

Bevor du etwas ausführst, und wenn etwas schiefgeht:

```bash
kiwi info --installer <app>  # das Skript, das eine Installation ausführen würde, bevor es läuft
kiwi diff <app>              # was ein Update ändern würde, samt seinem Installer
kiwi pin <app> v1.2.0        # dort bleiben; kiwi unpin <app>, um wieder den Releases zu folgen
kiwi install <app> --dry-run # Bereich, URL, Ref, Pfad des Installers und sonst nichts
kiwi doctor                  # veraltete Locks, Versionsabweichungen, fehlerhafte Listendateien, Timer
```

## Releases sind Tags { #releases-are-tags }

Eine App folgt ihrem neuesten **Versions-Tag**, einem, der auf
`^v?[0-9]+(\.[0-9]+){0,3}$` passt (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Pre-Releases
und Wegwerf-Tags überholen nie ein Release. Ein Repository ohne Versions-Tag folgt
seinem Standard-Branch. `ref=<tag>` in einer Listenzeile verlangt einen bestimmten.

## Abhängigkeiten { #dependencies }

`DEPENDS=` in einem Manifest nennt, was eine App braucht. Ein Wort, das eine App in
deinem eigenen Katalog oder deiner Liste ist, wird bei der Installation **zuerst**
installiert, im selben Bereich. `kiwi install kiwi-plugin-tor` zum Beispiel bringt
kiwi-proxy mit. Jedes andere Wort ist ein Programm und wird mit `command -v`
geprüft.

## Eine App, zwei Hälften { #one-app-two-halves }

Manche Apps sind nur ein Binary in `~/.local/bin`. Andere, wie ein
VPN-Kill-Switch, sind ein Root-Daemon **und** eine Desktop-App **und** eine
GNOME-Erweiterung. Die Hälften werden mit unterschiedlichen Rechten installiert,
denn **root darf nie eine Datei ausführen, die der Benutzer schreiben kann**. Die App
deklariert es:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Ein Katalog listet diese App einmal, und kiwi installiert jede Hälfte richtig. Bevor
es nach deinem Passwort fragt, zeigt es den `ROOT_REASON`.

| Teil | Wo | Warum |
|---|---|---|
| `kiwi`, Kiwi Apps, Benutzer-Apps | `~/.local` | kein root nötig; übersteht ein ostree-Rebase |
| die eigene kiwi-Kopie von root | `/usr/local/bin`, geklont nach `/var/lib/kiwi-updater/repos/` | root führt nie eine Datei aus, die du schreiben kannst |
| System-Apps | `/var/lib`, `/etc` | auf ostree beschreibbar, gehören root |
| Listen | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | die eigenen Einträge einer Maschine schlagen jeden Katalog |
| festgelegte Signaturschlüssel | `/etc/kiwi-updater/signers/<app>` | siehe unten |

Das unveränderliche `/usr` wird nie angefasst.

## Root, Passwörter und Signaturen { #root-passwords-and-signatures }

| | Braucht root | Fragt nach einem Passwort |
|---|---|---|
| alles im Benutzerbereich | nein | nein |
| eine System-App **aktualisieren** | ja | **nein** bei einem Release, das mit dem Schlüssel signiert ist, den root für diese App festgelegt hat. **Ja** bei einem unsignierten Release und immer im Modus `manual` |
| eine System-App **installieren** oder **deinstallieren** | ja | ja |

Seit 2.4.0:

- **Signierte Releases.** Root legt pro System-App einen SSH-Signaturschlüssel fest,
  den ersten, den es sieht (Trust on First Use). Ein Release-Tag, der mit diesem
  Schlüssel signiert ist, aktualisiert ohne Passwort. Ein unsigniertes Release fragt
  nach einem und sagt, dass es nicht prüfen konnte. Ein Tag, der mit einem anderen
  Schlüssel signiert ist, oder ein unsignierter Tag nach signierten wird abgelehnt,
  bis du `kiwi trust --system <app>` ausführst. Das gilt für den Systembereich.
- **Root installiert nur Quellen, die es selbst listet**:
  `/etc/kiwi-updater/apps.list` und für root registrierte Kataloge. Für alles andere
  installiert kiwi die Benutzer-Hälfte und nennt den auszuführenden Befehl
  `kiwi add --system <https-url>`. Kiwi Apps bietet *Register and Install* an.
- **Nur https.** `http://`-Quellen werden überall abgelehnt.

Updates des Systems ohne Passwort laufen über einen einzigen Helfer mit festem
Zweck, `/usr/local/libexec/kiwi-system-update`. Eine polkit-Regel erlaubt ihn für
aktive `wheel`-Sitzungen, und er nimmt App-Namen nur als Auswahl aus den eigenen
Listen von root an.

## Updates im Hintergrund { #background-updates }

Es gibt einen Timer, und er gehört dir: `kiwi-updater.timer` führt
`kiwi update --all` sechs Stunden nach dem letzten Lauf aus (zehn Minuten nach dem
Booten, mit etwas zufälliger Verzögerung). Er aktualisiert Benutzer-Hälften direkt
und System-Hälften über den Helfer oben. Es gibt keinen Root-Timer. Im Modus
`manual` warten System-Hälften auf dein nächstes interaktives `kiwi update`.

## Vertrauen { #trust }

Eine App zu installieren **führt das `install.sh` dieses Repositorys aus**, und eine
App, die den Systembereich deklariert, führt es **als root** aus. Kataloge sind
kuratiert, nicht geprüft. Füge die hinzu, denen du vertraust, so wie du ein
Paket-Repository hinzufügen würdest, und nutze `kiwi info --installer`, `kiwi diff`
und `kiwi pin`, um mit offenen Augen zu entscheiden. Eine Signatur grenzt ein, *wer
veröffentlichen darf*. Sie sagt nichts darüber, *was das Veröffentlichte tut*.

Weiterhin geplant: ein gehostetes Verzeichnis vertrauenswürdiger Kataloge
(`kiwi catalog browse`) mit Signer-Fingerabdrücken pro Eintrag.
