# syncman

syncman keeps pairs of folders on a Linux machine in sync in both directions.
Whichever folder of a pair gets a new or changed file, the file is copied to
the other folder. syncman was built for game saves, and it works for any
folders. **rsync is the only dependency**, and inotify-tools is optional.
syncman is installed and runs in your user scope only, which means for your
own user account.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Latest release: **v0.4.1**. It is in the [Kiwi catalog](catalogs.md), user scope.

You describe what to sync in a **job**. A job is a plain text file with one
pair of folders on each line. The format is not YAML and needs no quoting, so
you can write a path that contains spaces as it is:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Each job runs as a systemd user service named `syncjob@<name>.service`. At
every `INTERVAL`, which is 30 seconds by default, the service runs
`rsync -a --update` in both directions. When a file exists on both sides, the
newer one replaces the older one, and **nothing is ever deleted**. If
`inotifywait` is installed, changes are synced as soon as they happen.

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

The settings are in `~/.config/syncman/syncman.conf`. The file sets `INTERVAL`
and, optionally, `JOBS_DIR`. When you uninstall syncman, your jobs are kept
unless you pass `--purge`.
