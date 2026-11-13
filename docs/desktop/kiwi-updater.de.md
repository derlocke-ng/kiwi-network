# kiwi-updater

kiwi-updater installiert quelloffene Apps auf deinem Rechner und hält sie
aktuell. Sein Befehl heißt `kiwi`. Die Apps holt es aus **git-Katalogen**. Ein
Katalog ist ein git-Repository, das Apps auflistet, und eine App ist ein
git-Repository mit einer Datei `kiwi.manifest` und einem Skript `install.sh`.
kiwi klont die App, checkt ihr neuestes Release-Tag aus und führt ihr
Installationsskript aus. Danach aktualisiert es die App im Hintergrund, und
sich selbst hält es auf dieselbe Weise aktuell.

Du brauchst kein Konto, es gibt keinen App-Store und keinen Hersteller. Ein
Katalog ist ein Repository, das du lesen und forken kannst und an das du Pull
Requests schicken kannst. Alle Desktop-Apps von Kiwi werden auf diese Weise
installiert.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Aktuelles Release: **v2.5.1**
- **`kiwi`** ist das Kommandozeilenwerkzeug. **Kiwi Apps** (`kiwi-gui`) ist die
  Desktop-App. Darin kannst du in den Apps stöbern und nach ihnen suchen, sie
  installieren und das Installationsskript einer App lesen, bevor es läuft.

## Auf welchen Systemen es läuft { #where-it-runs }

kiwi-updater wurde für die Fedora Atomic Desktops entwickelt und läuft
inzwischen auch auf anderen Linux-Distributionen. Jede Änderung an kiwi-updater
wird auf den folgenden Systemen mit der vollständigen Testsuite und einer
echten Installation getestet:

| System | Was funktioniert |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | alles |
| Alpine | alles, sobald die GNU-Werkzeuge installiert sind |
| Debian 12, Ubuntu 22.04 (getestet, aber nicht bei jeder Änderung) | `kiwi` und Kommandozeilen-Apps. Für die Desktop-Apps ist die libadwaita dieser Systeme zu alt |

## Installation { #install }

Dieser Befehl installiert den Benutzerteil in dein Home-Verzeichnis und den
Root-Teil für Apps, die Root-Rechte brauchen. Dein Passwort gibst du dabei nur
einmal ein:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Wenn außerhalb deines Home-Verzeichnisses nichts landen soll und du nie nach
einem Passwort gefragt werden willst, installierst du nur den Benutzerteil:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

Das Installationsskript prüft, ob das Release, das es installiert, mit dem
Release-Schlüssel von kiwi-updater signiert ist. Ein Release ohne diese
Signatur installiert es nicht. Bei der Installation wird auch der Kiwi-Katalog
eingetragen. Danach geht es so weiter:

```bash
kiwi list                    # alle Apps, die du installieren kannst
kiwi install <app>           # eine davon installieren
kiwi info --installer <app>  # ihr Installationsskript lesen, bevor es läuft
kiwi-gui                     # die Desktop-App
```

## Root-Teile und signierte Releases { #root-parts-and-signed-releases }

Manche Apps brauchen Root-Rechte, zum Beispiel kiwi-killswitch mit seinem
Firewall-Daemon. Ihren Root-Teil installiert eine eigene Kopie von kiwi, die
root gehört, und zwar nur aus Quellen, die root selbst auflistet. Wenn du eine
solche App installierst oder entfernst, wirst du immer nach deinem Passwort
gefragt. Im Standardmodus läuft ein Update nur dann ohne Passwort, wenn das
Release mit dem Schlüssel signiert ist, den root sich für diese App gemerkt
hat.

## Die vollständige Dokumentation { #the-full-documentation }

kiwi-updater ist in seinem eigenen Repository dokumentiert:

| Seite | Was sie behandelt |
|---|---|
| [Installation](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | unterstützte Systeme, Pakete je Distribution, Installationsarten, Deinstallation |
| [kiwi benutzen](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | alle Befehle, Kiwi Apps, Updates im Hintergrund, Einstellungen |
| [Kataloge](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | Kataloge hinzufügen, `apps.list`, Apps auf eine Version festlegen, Katalogeinträge überschreiben |
| [Sicherheit](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | was als root läuft, wann du ein Passwort eingibst, was kiwi prüft |
| [Eine App schreiben](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, Abhängigkeiten, Icons, Releases |
| [Signierte Releases](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | die Releases deiner App mit `kiwi-release` signieren |
| [Entwicklung](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | Tests, CI, ein Release von kiwi-updater veröffentlichen |

Ab dem nächsten Release von kiwi-updater erscheinen diese Seiten auch hier, im
Menü unter kiwi-updater.

Wie du eine eigene App veröffentlichst, steht unter [Kataloge &
Veröffentlichen](catalogs.md).
