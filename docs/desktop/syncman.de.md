# syncman

Zweiwege-Ordnersynchronisation zwischen Paaren für Linux. Gebaut wurde es für
Spielstände, es funktioniert aber mit beliebigen Ordnern. **rsync ist die einzige
Abhängigkeit** (inotify-tools ist optional), und es läuft nur in deinem
Benutzerbereich.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Aktuelles Release: **v0.4.1**. Es steht im [Kiwi-Katalog](catalogs.md), Benutzerbereich.

Ein **Job** ist eine einfache Textdatei mit einem Paar pro Zeile. Es gibt kein YAML
und keine Anführungszeichen, und Leerzeichen in Pfaden funktionieren einfach:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Jeder Job läuft als systemd-Benutzerdienst, `syncjob@<name>.service`. Alle
`INTERVAL` (standardmäßig 30 Sekunden) führt er `rsync -a --update` in beide
Richtungen aus: Die neuere Datei gewinnt, und **es wird nie etwas gelöscht**. Ist
`inotifywait` installiert, werden Änderungen sofort synchronisiert.

```bash
kiwi install syncman            # oder ./install.sh
syncman add game-saves          # einen Job anlegen und bearbeiten
syncman start game-saves        # ein Hintergrunddienst, der Neustarts übersteht
syncman list                    # Jobs und der Zustand ihrer Dienste
syncman sync all                # einmalig, ohne Dienst
syncman stop all
syncman log game-saves
syncman-panel                   # GTK4-Panel: ein Schalter pro Job, Jetzt-synchronisieren-Knöpfe
```

Die Einstellungen stehen in `~/.config/syncman/syncman.conf` (`INTERVAL`, optional
`JOBS_DIR`). Eine Deinstallation behält deine Jobs, außer du übergibst `--purge`.
