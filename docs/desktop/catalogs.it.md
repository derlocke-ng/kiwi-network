# Cataloghi e pubblicazione delle app

Un catalogo è un elenco di app che kiwi-updater può installare. È un repository
git, quindi puoi leggerlo, copiarlo e proporre modifiche. Questa pagina descrive
il catalogo Kiwi, mostra come creare un catalogo tuo, per esempio per tutti i
desktop di cui ti occupi, e spiega come pubblicare un’app perché altre persone
possano installarla con kiwi.

## Il catalogo Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) è il
catalogo delle app di Kiwi Network. Viene registrato automaticamente quando
installi kiwi-updater. Per registrarlo a mano esegui
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

La tabella elenca le app del catalogo. La colonna *Ambiti* indica dove viene
installata un’app. L’ambito utente è la tua cartella home, l’ambito di sistema è
una parte che appartiene a root.

| App | Release | Ambiti | Che cos’è |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | utente | il programma di aggiornamento stesso |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | utente + sistema | kill switch per la VPN, per GNOME. È fail-closed: finché la VPN non è attiva, tutto il traffico resta bloccato |
| [ensconce](ensconce.md) | v2.5.0 | utente | configura un Bluefin-DX appena installato |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | utente | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | utente | exit per connessioni SOCKS5 e VPN. Un exit è un container isolato in Podman rootless |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | utente | identità del browser isolate, che usano gli exit di kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | utente | box (container con una distribuzione Linux) il cui traffico passa soltanto da un exit |
| [kiwi-server](../server/index.md) | v2.42.0 | utente | lo strumento con cui costruisci e gestisci la tua rete |
| [syncman](syncman.md) | v0.4.1 | utente | sincronizza cartelle in entrambe le direzioni |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | utente | salva le disposizioni degli schermi in GNOME e passa dall’una all’altra |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | utente | modulo provider per kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | utente | modulo provider per kiwi-proxy: una VPN tramite gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | utente | modulo provider per kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | utente | modulo provider per kiwi-proxy: Mysterium |

Prima di ogni controllo e di ogni aggiornamento, kiwi scarica la versione
attuale del catalogo. Puoi quindi gestire le app di un intero gruppo di desktop
soltanto con git:

- **Per aggiungere un’app**, aggiungi il suo URL ad `apps.list` e fai il commit.
- **Per fissare un’app a una versione o tornare a una versione precedente**,
  aggiungi `ref=<tag>` in fondo alla sua riga. Su una singola macchina,
  `kiwi pin <app> <tag>` fa la stessa cosa.
- **Per togliere un’app**, cancella la sua riga. Le copie già installate restano
  installate finché non le disinstalli.

## Il tuo catalogo { #your-own-catalog }

Un catalogo è un repository git con un file `apps.list`. Può contenere anche un
file `catalog.manifest`, in cui il catalogo descrive sé stesso:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: una riga per app, anche quando l’app ha una metà root e una metà utente
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Una riga di `apps.list` può avere queste opzioni dopo l’URL:

| Opzione | Significato |
|---|---|
| `branch=<name>` | segue un branch invece dei tag di release |
| `ref=<tag>` | resta esattamente su questa versione |
| `scope=user\|system` | sulle macchine che usano questo elenco installa soltanto quella metà dell’app. L’opzione è un *filtro*: non dichiara quali ambiti ha l’app |

Ogni macchina ha anche un elenco tutto suo:
`~/.config/kiwi-updater/apps.list` per il tuo utente e
`/etc/kiwi-updater/apps.list` per root. Una voce nell’elenco della macchina ha
sempre la precedenza su un catalogo. `kiwi add <url>` aggiunge una riga a questo
elenco.

## Pubblicare un’app { #publishing-an-app }

Per pubblicare un’app, metti un file `kiwi.manifest` e uno script `install.sh`
nella directory principale del tuo repository. Trovi dei modelli nella directory
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
di kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, oppure entrambi
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Un manifest può avere altre chiavi: `AUTHOR`, `CATEGORY`, `TAGS`,
`SCREENSHOTS`, `ABOUT` (un file che Kiwi Apps mostra), `DEPENDS` e
`ROOT_REASON`. Ogni app con una metà di sistema deve avere `ROOT_REASON`.
`ICON=` indica un file SVG o PNG di al massimo 1 MiB all’interno del
repository. Quasi tutte le app Kiwi prendono la loro icona da
[kiwi-icons](../project/brand.md).

!!! warning "Metti i commenti su una riga a parte"
    Un valore continua fino alla fine della riga. Se scrivi
    `COMPONENTS=cli  # … gui …`, il commento diventa parte del valore, e kiwi
    tratta l’app come se avesse un’interfaccia grafica.

kiwi esegue il tuo script di installazione una volta **per ogni ambito
dichiarato dall’app**, e gli passa queste variabili:

| Variabile | Valore |
|---|---|
| `KIWI_SCOPE` | `user` oppure `system` |
| `KIWI_PREFIX` | `~/.local` oppure `/usr/local` |
| `KIWI_APP_DIR` | percorso assoluto del clone |
| `KIWI_ACTION` | `install`, `update` oppure `uninstall` |
| `KIWI_GUI` | `0` su una macchina headless (senza desktop grafico), oppure con `--cli-only` |
| `KIWI_PURGE` | `1` se l’utente ha chiesto `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` viene per primo. L’ambito di sistema riceve un percorso di sistema fisso |

Lo script di installazione di un’app con entrambi gli ambiti deve controllare
`KIWI_SCOPE` e, a ogni esecuzione, fare soltanto il lavoro di quella metà. Se
l’utente non ha chiesto `--purge`, lascia la sua configurazione dov’è.

**Pubblica ogni release come tag firmato.** Solo così la metà di sistema di
un’app si può aggiornare senza password:

```bash
git config gpg.format ssh            # firma con la tua chiave SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater offre un workflow per le release, `templates/release.yml`. Pubblica
una release su GitHub soltanto per un tag firmato con una chiave elencata in
`.github/allowed_signers`, e non crea mai tag da solo. Infine apri una pull
request che aggiunge il tuo URL al catalogo. È benvenuta qualsiasi app open
source che si possa usare davvero senza account, abbonamenti o sistemi di
tracciamento.

## Fiducia { #trust }

Il catalogo è **curato, non verificato**. Un’app è nell’elenco perché qualcuno
l’ha ritenuta utile, non perché il suo codice sia stato controllato. Prima di
installare un’app che non conosci, leggi l’output di `kiwi info <app>`. Con
`kiwi info --installer <app>` vedi esattamente che cosa verrà eseguito.
