# kiwi-updater

kiwi-updater installa app open source sul tuo computer e le tiene aggiornate.
Il suo comando è `kiwi`. Prende le app dai **cataloghi git**. Un catalogo è un
repository git che elenca delle app, e un’app è un repository git con un file
`kiwi.manifest` e uno script `install.sh`. kiwi clona l’app, passa al suo tag
di release più recente ed esegue il suo script di installazione. Da quel
momento aggiorna l’app in background, e allo stesso modo aggiorna sé stesso.

Non ti serve alcun account, e non ci sono né app store né fornitori. Un
catalogo è un repository che puoi leggere, di cui puoi fare il fork e a cui
puoi mandare una pull request. Tutte le app desktop di Kiwi si installano in
questo modo.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Ultima release: **v2.5.1**
- **`kiwi`** è lo strumento da riga di comando. **Kiwi Apps** (`kiwi-gui`) è
  l’app per il desktop. Con Kiwi Apps puoi sfogliare e cercare le app,
  installarle e leggere lo script di installazione di un’app prima che venga
  eseguito.

## Dove funziona { #where-it-runs }

kiwi-updater è nato per i desktop Fedora Atomic, e ora funziona anche su altre
distribuzioni Linux. Ogni modifica a kiwi-updater viene provata su questi
sistemi con la suite di test completa e con un’installazione vera:

| Sistema | Cosa funziona |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | tutto |
| Alpine | tutto, dopo aver installato gli strumenti GNU |
| Debian 12, Ubuntu 22.04 (testati, ma non a ogni modifica) | `kiwi` e le app da riga di comando. La libadwaita di questi sistemi è troppo vecchia per le app desktop |

## Installazione { #install }

Questo comando installa la parte utente nella tua cartella home e la parte root
per le app che hanno bisogno di root. La password ti viene chiesta una sola
volta:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Se fuori dalla tua cartella home non deve finire niente e non vuoi che ti
venga mai chiesta una password, installa soltanto la parte utente:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

Lo script di installazione verifica che la release che installa sia firmata con
la chiave con cui kiwi-updater firma le proprie release, e rifiuta qualsiasi
release che non lo sia. Durante l’installazione viene registrato anche il catalogo Kiwi.
Poi puoi cominciare:

```bash
kiwi list                    # tutte le app che puoi installare
kiwi install <app>           # installane una
kiwi info --installer <app>  # leggi il suo script di installazione prima che venga eseguito
kiwi-gui                     # l'app per il desktop
```

## Parti root e release firmate { #root-parts-and-signed-releases }

Alcune app hanno bisogno di root, per esempio kiwi-killswitch, che ha un daemon
per il firewall. La loro parte root viene installata da una copia di kiwi di
proprietà di root, e soltanto da fonti che root elenca lui stesso. Quando
installi o rimuovi un’app di questo tipo, ti viene sempre chiesta la password.
Nella modalità predefinita un aggiornamento avviene senza password solo se la
release è firmata con la chiave che root ha memorizzato per quell’app.

## La documentazione completa { #the-full-documentation }

kiwi-updater è documentato nel suo repository:

| Pagina | Di che cosa parla |
|---|---|
| [Installazione](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | sistemi supportati, pacchetti per ogni distribuzione, modalità di installazione, disinstallazione |
| [Usare kiwi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | tutti i comandi, Kiwi Apps, aggiornamenti in background, impostazioni |
| [Cataloghi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | aggiungere cataloghi, `apps.list`, fissare una versione, sostituire una voce di un catalogo |
| [Sicurezza](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | che cosa gira come root, quando digiti una password, che cosa controlla kiwi |
| [Scrivere un’app](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, dipendenze, icone, release |
| [Release firmate](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | firmare le release della tua app con `kiwi-release` |
| [Sviluppo](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | test, CI, pubblicare una release di kiwi-updater |

Dalla prossima release di kiwi-updater queste pagine compariranno anche qui,
nel menu sotto kiwi-updater.

Per pubblicare una tua app, vedi [Cataloghi e pubblicazione](catalogs.md).
