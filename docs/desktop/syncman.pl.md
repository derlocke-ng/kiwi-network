# syncman

syncman synchronizuje pary folderów na maszynie z Linuksem w obu kierunkach.
Niezależnie od tego, w którym folderze pary pojawi się nowy lub zmieniony plik,
zostanie on skopiowany do drugiego. syncman powstał z myślą o zapisach gier,
ale działa z dowolnymi folderami. **Jedyną zależnością jest rsync**,
a inotify-tools jest opcjonalne. syncman instaluje się i działa wyłącznie
w zakresie użytkownika, czyli na twoim własnym koncie.

- Repozytorium: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Najnowsze wydanie: **v0.4.1**. Jest w [katalogu Kiwi](catalogs.md), zakres użytkownika.

To, co ma być synchronizowane, opisujesz w **zadaniu** (job). Zadanie to
zwykły plik tekstowy z jedną parą folderów w każdym wierszu. To nie jest YAML
i nie trzeba niczego brać w cudzysłów, więc ścieżkę ze spacjami wpisujesz tak,
jak jest:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Każde zadanie działa jako usługa użytkownika systemd o nazwie
`syncjob@<name>.service`. Co `INTERVAL`, domyślnie co 30 sekund, usługa
uruchamia `rsync -a --update` w obu kierunkach. Gdy plik istnieje po obu
stronach, nowszy zastępuje starszy, a **nic nigdy nie jest usuwane**. Jeśli
zainstalowany jest `inotifywait`, zmiany są synchronizowane od razu, gdy
nastąpią.

```bash
kiwi install syncman            # albo ./install.sh
syncman add game-saves          # tworzy zadanie i otwiera je do edycji
syncman start game-saves        # usługa w tle, która działa także po ponownym uruchomieniu
syncman list                    # zadania i stan ich usług
syncman sync all                # jednorazowo, bez usługi
syncman stop all
syncman log game-saves
syncman-panel                   # panel GTK4: przełącznik dla każdego zadania, przyciski „synchronizuj teraz”
```

Ustawienia znajdują się w `~/.config/syncman/syncman.conf`. Ten plik ustawia
`INTERVAL` i opcjonalnie `JOBS_DIR`. Gdy odinstalujesz syncmana, twoje zadania
zostają, chyba że podasz `--purge`.
