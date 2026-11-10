# syncman

syncman tiene sincronizzate in entrambe le direzioni delle coppie di cartelle su
una macchina Linux. In qualunque delle due cartelle compaia un file nuovo o
modificato, il file viene copiato nell’altra. syncman è nato per i salvataggi
dei giochi, ma funziona con qualsiasi cartella. **L’unica dipendenza è rsync**,
e inotify-tools è facoltativo. syncman si installa e gira soltanto
nell’ambito utente, cioè per il tuo account.

- Repository: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Ultima release: **v0.4.1**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

Che cosa sincronizzare lo descrivi in un **job**. Un job è un semplice file di
testo con una coppia di cartelle per riga. Il formato non è YAML e non richiede
virgolette, quindi un percorso che contiene spazi lo scrivi così com’è:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Ogni job gira come servizio utente di systemd, con il nome
`syncjob@<name>.service`. A ogni `INTERVAL`, per impostazione predefinita 30
secondi, il servizio esegue `rsync -a --update` in entrambe le direzioni. Se un
file esiste da tutte e due le parti, quello più recente sostituisce quello più
vecchio, e **non viene mai cancellato nulla**. Se è installato `inotifywait`, le
modifiche vengono sincronizzate non appena avvengono.

```bash
kiwi install syncman            # oppure ./install.sh
syncman add game-saves          # crea e modifica un job
syncman start game-saves        # un servizio in background che sopravvive ai riavvii
syncman list                    # i job e lo stato dei loro servizi
syncman sync all                # una sola volta, senza servizio
syncman stop all
syncman log game-saves
syncman-panel                   # pannello GTK4: un interruttore per job, pulsanti per sincronizzare subito
```

Le impostazioni sono in `~/.config/syncman/syncman.conf`. Il file imposta
`INTERVAL` e, se vuoi, `JOBS_DIR`. Quando disinstalli syncman, i tuoi job
restano, a meno che tu non passi `--purge`.
