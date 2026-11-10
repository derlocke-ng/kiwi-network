# syncman

syncman houdt paren van mappen op een Linux-machine in beide richtingen
gelijk. In welke map van een paar er ook een bestand bijkomt of verandert, het
wordt naar de andere map gekopieerd. syncman is gemaakt voor opgeslagen
spellen, maar werkt voor elke map. **rsync is de enige afhankelijkheid**,
inotify-tools is optioneel. syncman wordt alleen in je user-scope geïnstalleerd
en draait ook alleen daar, dus voor je eigen gebruikersaccount.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Nieuwste release: **v0.4.1**. Staat in de [Kiwi-catalogus](catalogs.md), scope user.

Wat er gesynchroniseerd wordt, beschrijf je in een **job**: een gewoon
tekstbestand met op elke regel één paar mappen. Het formaat is geen YAML en
heeft geen aanhalingstekens nodig, dus een pad met spaties schrijf je gewoon
zoals het is:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Elke job draait als systemd-service voor je eigen gebruiker (user service), met
de naam `syncjob@<name>.service`. Na elk `INTERVAL`, standaard 30 seconden,
voert de service `rsync -a --update` in beide richtingen uit. Staat een bestand
aan beide kanten, dan vervangt het nieuwere het oudere, en **er wordt nooit iets
verwijderd**. Is `inotifywait` geïnstalleerd, dan worden wijzigingen meteen
gesynchroniseerd.

```bash
kiwi install syncman            # of ./install.sh
syncman add game-saves          # een job aanmaken en bewerken
syncman start game-saves        # een achtergrondservice die herstarts overleeft
syncman list                    # jobs en de toestand van hun service
syncman sync all                # één keer, zonder service
syncman stop all
syncman log game-saves
syncman-panel                   # GTK4-paneel: een schakelaar per job, knoppen om nu te synchroniseren
```

De instellingen staan in `~/.config/syncman/syncman.conf`. Daarin staan
`INTERVAL` en, als je wilt, `JOBS_DIR`. Verwijder je syncman, dan blijven je jobs
bewaard, tenzij je `--purge` meegeeft.
