# syncman

syncman hält auf einem Linux-Rechner Paare von Ordnern in beide Richtungen
synchron. Egal in welchem Ordner eines Paars eine Datei neu dazukommt oder sich
ändert, sie wird in den anderen Ordner kopiert. Gebaut wurde syncman für
Spielstände, es funktioniert aber mit beliebigen Ordnern. **Die einzige
Abhängigkeit ist rsync**, inotify-tools ist optional. syncman wird nur im
Scope user installiert und läuft dort, also nur für dein eigenes Benutzerkonto.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Aktuelles Release: **v0.4.1**. Es steht im [Kiwi-Katalog](catalogs.md), Scope user.

Was synchronisiert wird, beschreibst du in einem **Job**. Ein Job ist eine
einfache Textdatei mit einem Ordnerpaar pro Zeile. Das Format ist kein YAML und
kommt ohne Anführungszeichen aus. Einen Pfad mit Leerzeichen schreibst du also
so hin, wie er ist:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Jeder Job läuft als systemd-Benutzerdienst namens `syncjob@<name>.service`.
Im Abstand von `INTERVAL`, standardmäßig alle 30 Sekunden, führt der Dienst
`rsync -a --update` in beide Richtungen aus. Gibt es eine Datei auf beiden
Seiten, ersetzt die neuere die ältere, und **gelöscht wird nie etwas**. Ist
`inotifywait` installiert, werden Änderungen synchronisiert, sobald sie
passieren.

```bash
kiwi install syncman            # oder ./install.sh
syncman add game-saves          # einen Job anlegen und bearbeiten
syncman start game-saves        # ein Hintergrunddienst, der Neustarts übersteht
syncman list                    # Jobs und der Zustand ihrer Dienste
syncman sync all                # einmalig, ohne Dienst
syncman stop all
syncman log game-saves
syncman-panel                   # GTK4-Panel: ein Schalter pro Job, Knöpfe für sofortiges Synchronisieren
```

Die Einstellungen stehen in `~/.config/syncman/syncman.conf`. Die Datei legt
`INTERVAL` fest und auf Wunsch auch `JOBS_DIR`. Wenn du syncman deinstallierst,
bleiben deine Jobs erhalten, außer du gibst `--purge` an.
