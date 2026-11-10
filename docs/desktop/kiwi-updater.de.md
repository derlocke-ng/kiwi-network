# kiwi-updater

kiwi-updater installiert quelloffene Apps auf deinem Desktop und hält sie
aktuell. Sein Befehl heißt `kiwi`. Die Apps holt es aus **git-Katalogen**, und
es läuft auf Fedora Silverblue, Bluefin und anderen ostree-Systemen. Ein
Katalog ist ein git-Repository, das Apps auflistet. Eine App ist ein
git-Repository mit einer Datei `kiwi.manifest` und einem Skript `install.sh`.
kiwi klont das Repository der App, checkt ihr neuestes Release-Tag aus und
führt ihr Installationsskript aus. Danach aktualisiert es die App im
Hintergrund, und sich selbst aktualisiert es auf dieselbe Weise.

Du brauchst kein Konto, es gibt keinen App-Store und keinen Hersteller. Ein
Katalog ist ein Repository, das du lesen, forken und mit einem Pull Request
ändern kannst.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Aktuelles Release: **v2.4.0**, ein Sicherheitsrelease
- **`kiwi`** ist das Kommandozeilenwerkzeug (CLI). Es braucht `git`,
  coreutils, `util-linux` und `awk`, die alle zum Basis-Image gehören. Um
  Signaturen zu prüfen, braucht es außerdem `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) ist die Desktop-App, gebaut mit GTK4. Du kannst
  die Apps durchsuchen und filtern, und jede App hat eine Detailansicht mit
  Icon, Screenshots und Abhängigkeiten. Bevor Kiwi Apps eine App installiert,
  zeigt es dir das Installationsskript, und bevor es eine App aktualisiert,
  zeigt es dir, was sich ändert. Klickst du mehrere Aktionen nacheinander an,
  stellt es sie in eine Warteschlange. Seine Daten bekommt es von der CLI.
  Icons und Screenshots liest es aus den lokalen Klonen der Apps und muss dafür
  nichts herunterladen.

## Installation { #install }

kiwi arbeitet mit zwei Scopes, also zwei Bereichen, in die installiert wird.
Der Scope user umfasst alles in deinem Home-Verzeichnis und braucht nie
Root-Rechte. Der Scope system ist ein Bereich, der root gehört, für Apps, die
Root-Rechte brauchen. Bei der Installation legst du fest, wie viel vom Scope
system du haben willst:

```bash
# empfohlen: Scope user plus der root gehörende Scope system, eine Passwortabfrage
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimal: 100 % auf Benutzerebene, nur ~/.local, nie root und nie ein Passwort
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# gar nichts ohne Passwort: jede Änderung am System fragt nach dem Passwort
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

Die Installation trägt den [Kiwi-Katalog](catalogs.md) ein. Du kannst also
sofort `kiwi list` ausführen oder **Kiwi Apps** öffnen.

Manche Apps bestehen nur aus Dateien in deinem Home-Verzeichnis, zum Beispiel
die CLI-Werkzeuge, ensconce und syncman. Diese Apps funktionieren auch bei der
minimalen Installation vollständig. Eine App mit einem Teil, der als root
läuft, etwa kiwi-killswitch, braucht den Scope system. Bei einer minimalen
Installation richtet `kiwi install kiwi-killswitch` den Scope system in diesem
Moment ein und fragt einmal nach deinem Passwort.

## Befehle { #commands }

```bash
kiwi list [--check]          # alle Apps, die dieser Rechner kennt
kiwi search vpn              # eine App in allen eingetragenen Katalogen suchen
kiwi info kiwi-killswitch    # was sie ist, was sie installiert, ob sie root braucht
kiwi install <app>           # ein Name oder ausdrücklich --all
kiwi update [<app>]          # alles mit einem neuen Release
kiwi uninstall <app>         # --purge löscht auch die Konfiguration
kiwi check                   # Exit-Code 10, wenn es irgendwo ein Update gibt

kiwi add <https-url>         # einem einzelnen Repository direkt folgen, ohne Katalog
kiwi catalog add|list|remove # Kataloge verwalten
kiwi sync                    # Kataloge sofort aktualisieren
kiwi self-update
kiwi trust --system <app>    # den für eine System-App festgelegten Signaturschlüssel vergessen
```

Mit den folgenden Befehlen siehst du, was eine App tun wird, bevor du sie
ausführst. Sie helfen auch, wenn etwas schiefgeht:

```bash
kiwi info --installer <app>  # das Skript, das eine Installation ausführen würde, vorher ansehen
kiwi diff <app>              # was ein Update ändern würde, samt Installationsskript
kiwi pin <app> v1.2.0        # dort bleiben; mit kiwi unpin <app> wieder den Releases folgen
kiwi install <app> --dry-run # Scope, URL, Ref, Pfad des Installationsskripts, sonst nichts
kiwi doctor                  # veraltete Sperren, abweichende Versionen, fehlerhafte Listen, Timer
```

## Releases sind Tags { #releases-are-tags }

kiwi verwendet git-Tags als Releases. Eine App folgt ihrem neuesten
**Versions-Tag**. Das ist ein Tag, das auf `^v?[0-9]+(\.[0-9]+){0,3}$` passt,
zum Beispiel `v1`, `v1.2`, `1.2.3` oder `v1.2.3.4`. Tags für Vorabversionen und
vorübergehende Tags passen nicht und werden deshalb nie anstelle eines Release
verwendet. Ein Repository ohne Versions-Tag folgt seinem Standard-Branch. Willst
du genau eine bestimmte Version, ergänze `ref=<tag>` in der Zeile der App in
einer Liste.

## Abhängigkeiten { #dependencies }

Die Zeile `DEPENDS=` im Manifest nennt, was eine App braucht. Ist ein Wort in
dieser Zeile der Name einer App aus deinem eigenen Katalog oder deiner Liste,
installiert kiwi diese App **zuerst**, im selben Scope, und zwar dann, wenn du
die App installierst, die sie braucht. `kiwi install kiwi-plugin-tor`
installiert zum Beispiel auch kiwi-proxy. Jedes andere Wort behandelt kiwi als
Namen eines Programms und prüft mit `command -v`, ob es vorhanden ist.

## Eine App, zwei Teile { #one-app-two-halves }

Manche Apps sind nur ein Programm in `~/.local/bin`. Andere, etwa ein
VPN-Kill-Switch, bestehen aus einem Daemon, der als root läuft, **und** einer
Desktop-App **und** einer GNOME-Erweiterung. So eine App hat zwei Teile, einen
Benutzerteil und einen Systemteil, die mit unterschiedlichen Rechten
installiert werden. Der Grund: **root darf nie eine Datei ausführen, die der
Benutzer ändern kann.** Ihre Bestandteile und Scopes gibt die App in ihrem
Manifest an:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Ein Katalog führt so eine App nur einmal auf, und kiwi installiert jeden Teil
im richtigen Scope. Bevor kiwi nach deinem Passwort fragt, zeigt es dir den
`ROOT_REASON` an.

| Teil | Wo | Warum |
|---|---|---|
| `kiwi`, Kiwi Apps, Benutzer-Apps | `~/.local` | braucht kein root und bleibt erhalten, wenn das System auf ein anderes ostree-Image umgestellt wird (Rebase) |
| die eigene Kopie von kiwi für root | `/usr/local/bin`, geklont nach `/var/lib/kiwi-updater/repos/` | root führt nie eine Datei aus, die du ändern kannst |
| System-Apps | `/var/lib`, `/etc` | diese Verzeichnisse sind auf ostree-Systemen beschreibbar und gehören root |
| Listen | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | die Einträge in der eigenen Liste eines Rechners haben Vorrang vor jedem Katalog |
| festgelegte Signaturschlüssel | `/etc/kiwi-updater/signers/<app>` | siehe nächster Abschnitt |

Am unveränderlichen `/usr` ändert kiwi nie etwas.

## Root, Passwörter und Signaturen { #root-passwords-and-signatures }

Die Tabelle zeigt, welche Aktionen Root-Rechte brauchen und welche nach einem
Passwort fragen.

| | Braucht root | Fragt nach Passwort |
|---|---|---|
| alles im Scope user | nein | nein |
| eine System-App **aktualisieren** | ja | **nein**, wenn das Release mit dem Schlüssel signiert ist, den root für diese App festgelegt hat. **Ja**, wenn das Release nicht signiert ist, und im Modus `manual` immer |
| eine System-App **installieren** oder **deinstallieren** | ja | ja |

Seit Version 2.4.0 gelten diese Regeln:

- **Signierte Releases.** Für jede System-App legt root einen
  SSH-Signaturschlüssel fest. Das heißt, root merkt sich den Schlüssel und
  akzeptiert von da an nur noch ihn. Festgelegt wird der erste Schlüssel, den
  root für die App sieht. Dieses Verfahren heißt Trust on First Use. Ist ein
  Release-Tag mit dem festgelegten Schlüssel signiert, wird das Update ohne
  Passwort installiert. Ist ein Release nicht signiert, fragt kiwi nach deinem
  Passwort und weist darauf hin, dass es das Release nicht prüfen konnte. Ein
  Tag, das mit einem anderen Schlüssel signiert ist, lehnt kiwi ab, ebenso ein
  unsigniertes Tag, wenn frühere Tags signiert waren. Das bleibt so, bis du
  `kiwi trust --system <app>` ausführst. Diese Regeln gelten für den Scope
  system.
- **root installiert nur aus Quellen, die es selbst auflistet.** Das sind
  `/etc/kiwi-updater/apps.list` und die Kataloge, die für root eingetragen
  sind. Kommt eine App aus einer anderen Quelle, installiert kiwi nur den
  Benutzerteil und nennt dir den Befehl `kiwi add --system <https-url>`, den du
  ausführen musst. Kiwi Apps bietet in diesem Fall *Register and Install* an,
  also: Quelle eintragen und installieren.
- **Nur https.** kiwi lehnt `http://`-Quellen überall ab.

Updates von System-Apps ohne Passwort übernimmt ein einzelnes Hilfsprogramm,
`/usr/local/libexec/kiwi-system-update`, das nur diesen einen Zweck hat. Eine
polkit-Regel erlaubt Benutzern der Gruppe `wheel`, es auszuführen, solange ihre
Sitzung aktiv ist. Das Hilfsprogramm nimmt nur App-Namen an, und ein Name kann
nur eine App aus den eigenen Listen von root auswählen.

## Updates im Hintergrund { #background-updates }

Für Updates im Hintergrund gibt es einen einzigen Timer. Er ist ein
Benutzer-Timer, läuft also unter deinem Benutzer und nicht als root.
`kiwi-updater.timer` startet `kiwi update --all` sechs Stunden nach dem letzten
Lauf und zehn Minuten nach dem Hochfahren, jeweils mit einer zufälligen
Verzögerung. Benutzerteile aktualisiert dieser Lauf direkt, Systemteile über
das oben beschriebene Hilfsprogramm. Einen Timer für root gibt es nicht. Im
Modus `manual` aktualisiert der Timer keine Systemteile. Sie warten, bis du
selbst `kiwi update` ausführst.

## Vertrauen { #trust }

Wenn du eine App installierst, **führt kiwi das `install.sh` aus dem Repository
dieser App aus**. Gibt die App den Scope system an, läuft dieses Skript **als
root**. Kataloge sind kuratiert, aber nicht geprüft. Jemand hat die Apps also
ausgewählt, aber ihr Code wurde nicht unbedingt durchgesehen. Trag nur
Kataloge ein, denen du vertraust, so wie du es auch bei einer Paketquelle
machen würdest. Mit `kiwi info --installer`, `kiwi diff` und `kiwi pin` siehst
du, was eine App tut, bevor du dich entscheidest. Eine Signatur schränkt ein,
*wer* ein Release veröffentlichen darf. Über das, *was das Release tut*, sagt
sie nichts.

Geplant ist noch: ein gehostetes Verzeichnis vertrauenswürdiger Kataloge, mit
dem Befehl `kiwi catalog browse` und mit den Fingerprints der Signaturschlüssel
zu jedem Eintrag.
