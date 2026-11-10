# syncman

Two-way, pair-wise folder sync for Linux. It was built for game saves and works
for any folders. **rsync is the only dependency** (inotify-tools is optional),
and it runs in your user scope only.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Latest release: **v0.4.1**. It is in the [Kiwi catalog](catalogs.md), user scope.

A **job** is a plain text file with one pair per line. There is no YAML and no
quoting, and spaces in paths just work:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Each job runs as a systemd user service, `syncjob@<name>.service`. Every
`INTERVAL` (30 seconds by default) it runs `rsync -a --update` both ways: the
newer file wins, and **nothing is ever deleted**. With `inotifywait` installed,
changes sync at once.

```bash
kiwi install syncman            # or ./install.sh
syncman add game-saves          # create and edit a job
syncman start game-saves        # a background service that survives reboots
syncman list                    # jobs and their service state
syncman sync all                # one-shot, no service
syncman stop all
syncman log game-saves
syncman-panel                   # GTK4 panel: a switch per job, sync-now buttons
```

Settings are in `~/.config/syncman/syncman.conf` (`INTERVAL`, optionally
`JOBS_DIR`). An uninstall keeps your jobs unless you pass `--purge`.
