# syncman

Sincronizzazione bidirezionale di cartelle a coppie per Linux. È nato per i salvataggi dei giochi e funziona
con qualsiasi cartella. **rsync è l'unica dipendenza** (inotify-tools è opzionale),
e gira solo nel tuo ambito utente.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Ultima release: **v0.4.1**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

Un **job** è un semplice file di testo con una coppia per riga. Niente YAML e niente
virgolette, e gli spazi nei percorsi funzionano e basta:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Ogni job gira come servizio utente systemd, `syncjob@<name>.service`. Ogni
`INTERVAL` (30 secondi di default) esegue `rsync -a --update` in entrambe le direzioni: vince il file
più recente, e **non viene mai eliminato nulla**. Con `inotifywait` installato,
le modifiche si sincronizzano subito.

```bash
kiwi install syncman            # oppure ./install.sh
syncman add game-saves          # crea e modifica un job
syncman start game-saves        # un servizio in background che sopravvive ai riavvii
syncman list                    # i job e lo stato dei loro servizi
syncman sync all                # una tantum, senza servizio
syncman stop all
syncman log game-saves
syncman-panel                   # pannello GTK4: un interruttore per job, pulsanti per sincronizzare subito
```

Le impostazioni sono in `~/.config/syncman/syncman.conf` (`INTERVAL`, e se vuoi
`JOBS_DIR`). Una disinstallazione conserva i tuoi job, a meno che tu non passi `--purge`.
