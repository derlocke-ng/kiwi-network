# ensconce

Configurazione post-installazione modulare per [Bluefin-DX](https://projectbluefin.io/).
ensconce trasforma un Bluefin appena installato nella tua postazione di lavoro configurata, a partire da
semplici file di elenco: pacchetti aggiunti al sistema, Flatpak, estensioni GNOME, sincronizzazione Nextcloud,
una configurazione SSH sincronizzata, impostazioni del desktop e della schermata di login, e le tue app Kiwi.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (secondo il suo manifest; il README dice GPL-3.0)
- Ultima release: **v2.5.0**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

```bash
kiwi install ensconce
ensconce --init          # crea ~/.config/ensconce dagli esempi
ensconce                 # esegue la configurazione
```

Oppure da un clone: `./ensconce.sh --init`, modifica `config/`, poi `./ensconce.sh`.

## Passi { #steps }

Ogni fase è uno script in `steps/`, eseguito in ordine:

| # | Passo | Cosa fa |
|---|---|---|
| 01 | `rebase` | passa a Bluefin-DX |
| 02 | `ujust` | gruppi per sviluppatori e strumenti CLI |
| 03 | `repos` | aggiunge repository RPM |
| 04 | `packages` | aggiunge pacchetti RPM al sistema |
| 05 | `flatpaks` | installa app Flatpak (`FLATPAK_LANGUAGES` sceglie le loro traduzioni) |
| 06 | `overrides` | override dei permessi Flatpak |
| 07 | `extensions` | estensioni di GNOME Shell |
| 08 | `cacert` | certificati CA personalizzati |
| 09 | `nextcloud` | preconfigura la sincronizzazione delle cartelle Nextcloud |
| 10 | `dconf` | impostazioni del desktop GNOME |
| 11 | `gdm` | la schermata di login |
| 12 | `ssh` | una configurazione SSH sincronizzata, con Bitwarden o GNOME come agente SSH |
| 13 | `kiwi` | installa kiwi-updater (`KIWI_INSTALL=recommended\|manual\|minimal`) e ogni app in `kiwi-apps.list` |
| 14 | `sysctl` | drop-in da `sysctl.d/` (un esempio limita il dirty writeback per gli SSD lenti) |
| 15 | `power` | `SYSTEM_SLEEP=off` maschera i target di sospensione |

ensconce controlla prima l'ambiente (un'immagine Bluefin, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). Salva i suoi progressi e riprende dopo i
riavvii, e tiene la macchina sveglia per tutta l'esecuzione, ripristinando poi le tue impostazioni
di alimentazione.

```bash
ensconce --dry-run                  # anteprima senza cambiare nulla
ensconce --skip rebase,ujust        # salta dei passi
ensconce --only extensions,dconf    # esegue solo questi
ensconce --status | --list-steps | --reset
ensconce --log [file]               # salva il suo output
ensconce --config-dir               # stampa la directory di configurazione attiva
```

## Configurazione { #configuration }

La directory di configurazione è la prima che esiste tra: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (installata tramite kiwi), `config/` in un clone, e
`config.example/` (con un avviso).

| File / directory | Scopo |
|---|---|
| `settings.sh` | URL dei server e interruttori: SSH, kiwi-updater, lingue Flatpak, sospensione |
| `packages.list`, `flatpaks.list`, `extensions.list` | un elemento per riga |
| `kiwi-apps.list` | le app Kiwi da installare |
| `repos.d/`, `flatpak-overrides/` | file dei repository; override per app nel formato di Flatpak |
| `nextcloud/folders.list` | cartelle da sincronizzare come `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | esclusioni dalla sincronizzazione globali e per cartella (con tag) |
| `certs/` | certificati CA (`.pem`), per esempio il `kiwiCA.pem` della tua fleet |
| `sysctl.d/` | impostazioni del kernel |
| `dconf-settings.ini`, `gtk3-bookmarks` | impostazioni di GNOME, segnalibri di Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | le impostazioni e la disposizione degli schermi della schermata di login |

Un tag di esclusione per cartella come `browser` mette `exclude.d/browser.lst` in
quella cartella, il che evita che i database di un profilo del browser vengano sincronizzati (e
corrotti), mentre `user.js` continua a sincronizzarsi.

## Clonare una macchina { #cloning-a-machine }

`--export` legge il sistema in uso e scrive un albero di configurazione di ensconce,
l'inverso dei passi:

```bash
ensconce --export ./my-setup        # sulla macchina configurata
ensconce --init                     # su quella nuova
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Cattura solo ciò che hai aggiunto tu: i pacchetti richiesti invece dell'intera
immagine, le estensioni che vengono davvero da extensions.gnome.org, i tuoi file dei repository, e
sottoalberi dconf selezionati invece di un dump completo. Consideralo un punto di partenza.
`certs/` e `nextcloud/` possono contenere materiale privato.

ensconce è un'app con **ambito utente**. I passi che richiedono root lo chiedono
da soli. Aggiungi un tuo passo come `steps/NN-<name>.sh` con una funzione
`step_<name>()`.
