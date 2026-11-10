# ensconce

ensconce configura al posto tuo un [Bluefin-DX](https://projectbluefin.io/)
appena installato, così non devi sistemare a mano ogni macchina nuova. Descrivi
la tua postazione in semplici file di elenco, ed ensconce trasforma
l’installazione nuova in quella postazione. Si occupa dei pacchetti stratificati,
dei Flatpak, delle estensioni di GNOME, della sincronizzazione con Nextcloud, di
una configurazione SSH sincronizzata tra le tue macchine, delle impostazioni del
desktop e della schermata di accesso, e delle tue app Kiwi. I pacchetti
stratificati sono pacchetti RPM aggiunti sopra l’immagine di sistema. La
configurazione è modulare: è divisa in passi separati, che puoi eseguire o
saltare.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  Secondo il manifest la licenza è GPL-3.0-or-later, mentre il README indica
  GPL-3.0.
- Ultima release: **v2.5.0**. È nel [catalogo Kiwi](catalogs.md) e viene
  installato nell’ambito utente, cioè nella tua cartella home.

```bash
kiwi install ensconce
ensconce --init          # crea ~/.config/ensconce a partire dagli esempi
ensconce                 # esegue la configurazione
```

Puoi eseguirlo anche da un clone del repository: lancia `./ensconce.sh --init`,
modifica i file in `config/` e poi lancia `./ensconce.sh`.

## I passi { #steps }

La configurazione è divisa in passi. Ogni passo è uno script in `steps/`, e i
passi vengono eseguiti in questo ordine:

| # | Passo | Che cosa fa |
|---|---|---|
| 01 | `rebase` | passa il sistema a Bluefin-DX |
| 02 | `ujust` | configura i gruppi per sviluppatori e gli strumenti da riga di comando |
| 03 | `repos` | aggiunge repository RPM |
| 04 | `packages` | aggiunge pacchetti RPM stratificati |
| 05 | `flatpaks` | installa app Flatpak. `FLATPAK_LANGUAGES` sceglie le lingue delle loro traduzioni |
| 06 | `overrides` | imposta eccezioni ai permessi dei Flatpak |
| 07 | `extensions` | installa estensioni di GNOME Shell |
| 08 | `cacert` | installa certificati di CA personalizzati |
| 09 | `nextcloud` | prepara in anticipo la sincronizzazione delle cartelle con Nextcloud |
| 10 | `dconf` | applica le impostazioni del desktop GNOME |
| 11 | `gdm` | configura la schermata di accesso |
| 12 | `ssh` | prepara la configurazione SSH sincronizzata, con Bitwarden o GNOME come agente SSH |
| 13 | `kiwi` | installa kiwi-updater nel modo scelto da `KIWI_INSTALL=recommended\|manual\|minimal`, e poi ogni app elencata in `kiwi-apps.list` |
| 14 | `sysctl` | installa i file di impostazioni del kernel presenti in `sysctl.d/`. Un file di esempio limita la quantità di dati non ancora scritti su disco che il kernel tiene in memoria, il che aiuta con gli SSD lenti |
| 15 | `power` | con `SYSTEM_SLEEP=off` maschera i target di sospensione, così la macchina non può andare in sospensione |

Prima di iniziare, ensconce controlla l’ambiente. Il sistema deve essere
un’immagine Bluefin, e devono essere disponibili `rpm-ostree`, `flatpak`,
`dconf`, `jq` e `curl`. ensconce salva i progressi, quindi dopo un riavvio
riprende da dove si era fermato. Per tutta la durata dell’esecuzione tiene la
macchina sveglia, e alla fine ripristina le tue impostazioni di risparmio
energetico.

Queste opzioni controllano un’esecuzione:

```bash
ensconce --dry-run                  # anteprima, senza cambiare nulla
ensconce --skip rebase,ujust        # salta dei passi
ensconce --only extensions,dconf    # esegue soltanto questi
ensconce --status | --list-steps | --reset
ensconce --log [file]               # salva l’output
ensconce --config-dir               # mostra la directory di configurazione attiva
```

## Configurazione { #configuration }

ensconce cerca la sua directory di configurazione in quattro posti e usa il
primo che esiste: prima `$ENSCONCE_CONFIG`, poi `~/.config/ensconce/` (usata
quando ensconce è stato installato con kiwi), poi `config/` in un clone, e
infine `config.example/`. Se usa `config.example/`, mostra un avviso.

| File / directory | A che cosa serve |
|---|---|
| `settings.sh` | gli URL dei server, e gli interruttori per SSH, kiwi-updater, le lingue dei Flatpak e la sospensione |
| `packages.list`, `flatpaks.list`, `extensions.list` | i pacchetti, i Flatpak e le estensioni di GNOME da installare, uno per riga |
| `kiwi-apps.list` | le app Kiwi da installare |
| `repos.d/`, `flatpak-overrides/` | i file dei repository, e le eccezioni per singole app nel formato proprio di Flatpak |
| `nextcloud/folders.list` | le cartelle da sincronizzare, nella forma `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | che cosa escludere dalla sincronizzazione, per tutte le cartelle e per le singole cartelle che hanno un tag |
| `certs/` | certificati di CA (`.pem`), per esempio il `kiwiCA.pem` della tua fleet |
| `sysctl.d/` | impostazioni del kernel |
| `dconf-settings.ini`, `gtk3-bookmarks` | impostazioni di GNOME e segnalibri di Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | le impostazioni e la disposizione degli schermi della schermata di accesso |

Un tag in `nextcloud/folders.list` dà a una cartella le sue esclusioni. Il tag
`browser`, per esempio, mette `exclude.d/browser.lst` in quella cartella. I
database di un profilo del browser non vengono allora sincronizzati, perché la
sincronizzazione potrebbe danneggiarli, mentre `user.js` continua a essere
sincronizzato.

## Clonare una macchina { #cloning-a-machine }

`--export` fa il contrario dei passi: legge il sistema in esecuzione e ne ricava
una directory di configurazione per ensconce. Con quella directory puoi poi
configurare una macchina nuova:

```bash
ensconce --export ./my-setup        # sulla macchina già configurata
ensconce --init                     # su quella nuova
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

L’esportazione contiene soltanto ciò che hai aggiunto al sistema. Elenca i
pacchetti che hai richiesto tu e non l’intera immagine. Elenca solo le
estensioni che provengono davvero da extensions.gnome.org. Contiene i tuoi file
di repository e, invece di un dump completo, alcuni sottoalberi di dconf scelti.
Considera l’esportazione un punto di partenza: `certs/` e `nextcloud/` possono
contenere materiale privato.

ensconce è un’app dell’**ambito utente**. I passi che hanno bisogno di root lo
chiedono da soli. Per aggiungere un passo tuo, crea un file
`steps/NN-<name>.sh` con una funzione `step_<name>()`.
