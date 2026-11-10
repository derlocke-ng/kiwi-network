# syncman

Dwukierunkowa synchronizacja folderów parami dla Linuksa. Powstała dla
zapisów gier i działa dla dowolnych folderów. **rsync to jedyna zależność**
(inotify-tools jest opcjonalne), a narzędzie działa tylko w twoim zakresie
użytkownika.

- Repozytorium: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Najnowsze wydanie: **v0.4.1**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

**Zadanie** (job) to zwykły plik tekstowy z jedną parą na linię. Nie ma YAML
ani cudzysłowów, a spacje w ścieżkach po prostu działają:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Każde zadanie działa jako usługa użytkownika systemd,
`syncjob@<name>.service`. Co `INTERVAL` (domyślnie 30 sekund) uruchamia
`rsync -a --update` w obie strony: nowszy plik wygrywa i **nic nigdy nie jest
usuwane**. Z zainstalowanym `inotifywait` zmiany synchronizują się od razu.

```bash
kiwi install syncman            # albo ./install.sh
syncman add game-saves          # utwórz i edytuj zadanie
syncman start game-saves        # usługa w tle, która przetrwa restarty
syncman list                    # zadania i stan ich usług
syncman sync all                # jednorazowo, bez usługi
syncman stop all
syncman log game-saves
syncman-panel                   # panel GTK4: przełącznik dla każdego zadania, przyciski synchronizacji
```

Ustawienia są w `~/.config/syncman/syncman.conf` (`INTERVAL`, opcjonalnie
`JOBS_DIR`). Odinstalowanie zachowuje twoje zadania, chyba że podasz
`--purge`.
