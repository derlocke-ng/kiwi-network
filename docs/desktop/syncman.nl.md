# syncman

Tweerichtings-mappensynchronisatie in paren voor Linux. Het is gebouwd voor
savegames en werkt voor elke map. **rsync is de enige afhankelijkheid**
(inotify-tools is optioneel), en het draait alleen in je gebruikersscope.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Nieuwste release: **v0.4.1**. Het staat in de [Kiwi-catalogus](catalogs.md), gebruikersscope.

Een **job** is een gewoon tekstbestand met één paar per regel. Er is geen YAML
en geen quoting, en spaties in paden werken gewoon:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Elke job draait als systemd-gebruikersservice, `syncjob@<name>.service`. Elke
`INTERVAL` (standaard 30 seconden) voert hij `rsync -a --update` in beide
richtingen uit: het nieuwere bestand wint, en **er wordt nooit iets
verwijderd**. Met `inotifywait` geïnstalleerd worden wijzigingen meteen
gesynchroniseerd.

```bash
kiwi install syncman            # of ./install.sh
syncman add game-saves          # een job aanmaken en bewerken
syncman start game-saves        # een achtergrondservice die herstarts overleeft
syncman list                    # jobs en de status van hun service
syncman sync all                # eenmalig, zonder service
syncman stop all
syncman log game-saves
syncman-panel                   # GTK4-paneel: een schakelaar per job, knoppen om nu te synchroniseren
```

Instellingen staan in `~/.config/syncman/syncman.conf` (`INTERVAL`, optioneel
`JOBS_DIR`). Bij een deïnstallatie blijven je jobs bewaard, tenzij je `--purge`
meegeeft.
