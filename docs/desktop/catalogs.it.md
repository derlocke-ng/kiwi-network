# Cataloghi e pubblicazione delle app

## Il catalogo Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) è il
catalogo di app della Kiwi Network. L'installazione di kiwi-updater lo registra, e
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` lo registra
a mano.

| App | Release | Ambiti | Cos'è |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | l'updater stesso |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | kill switch VPN fail-closed per GNOME |
| [ensconce](ensconce.md) | v2.5.0 | user | configurazione post-installazione per Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | uscite SOCKS5/VPN sigillate in Podman rootless |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | identità del browser isolate sulle uscite di kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | box di distribuzioni il cui traffico esce solo attraverso un'uscita |
| [kiwi-server](../server/index.md) | v2.42.0 | user | costruisci e gestisci la tua rete |
| [syncman](syncman.md) | v0.4.1 | user | sincronizzazione bidirezionale di cartelle |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | disposizioni degli schermi per GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | provider per kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | provider per kiwi-proxy: una VPN tramite gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | provider per kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | provider per kiwi-proxy: Mysterium |

kiwi sincronizza il catalogo prima di ogni controllo e aggiornamento, quindi gestire una flotta di
desktop è solo questione di git:

- **aggiungere un'app**: aggiungi il suo URL ad `apps.list` e fai commit;
- **fissare una versione o tornare indietro**: aggiungi `ref=<tag>` alla sua riga (su una sola macchina,
  `kiwi pin <app> <tag>` fa lo stesso);
- **rimuoverla**: elimina la riga (le copie installate restano finché non le disinstalli).

## Il tuo catalogo { #your-own-catalog }

Un catalogo è un repository git con un `apps.list` e, se vuoi, un
`catalog.manifest` che lo descrive:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: una riga per app, anche quando ha una metà root e una metà utente
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Opzione | Significato |
|---|---|
| `branch=<name>` | segue un branch invece dei tag di release |
| `ref=<tag>` | fissa una versione esatta |
| `scope=user\|system` | installa solo quella metà sulle macchine che usano questo elenco. È un *filtro*, non una dichiarazione |

L'elenco proprio di una macchina (`~/.config/kiwi-updater/apps.list`, oppure
`/etc/kiwi-updater/apps.list` per root) ha sempre la precedenza su un catalogo. `kiwi add <url>`
vi aggiunge una riga.

## Pubblicare un'app { #publishing-an-app }

Metti un `kiwi.manifest` e un `install.sh` nella radice del tuo repository. I template sono nella
cartella [`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates) di kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Altre chiavi: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (un file che Kiwi
Apps mostra), `DEPENDS` e, per tutto ciò che ha una metà di sistema, `ROOT_REASON`.
`ICON=` è un SVG o PNG di al massimo 1 MiB dentro il repository. La maggior parte delle app Kiwi prende
la propria da [kiwi-icons](../project/brand.md).

!!! warning "I commenti vanno su una riga a sé"
    Un valore arriva fino alla fine della riga. `COMPONENTS=cli  # … gui …` rende il
    commento parte del valore, e l'app viene quindi trattata come se avesse una GUI.

kiwi esegue il tuo installer una volta **per ogni ambito dichiarato**, con:

| Variabile | Valore |
|---|---|
| `KIWI_SCOPE` | `user` o `system` |
| `KIWI_PREFIX` | `~/.local` o `/usr/local` |
| `KIWI_APP_DIR` | percorso assoluto del clone |
| `KIWI_ACTION` | `install`, `update` o `uninstall` |
| `KIWI_GUI` | `0` su una macchina senza interfaccia grafica, o con `--cli-only` |
| `KIWI_PURGE` | `1` quando l'utente ha chiesto `--purge` |
| `PATH` | prima `$KIWI_PREFIX/bin`; un percorso di sistema fisso per l'ambito di sistema |

Un installer a doppio ambito si dirama in base a `KIWI_SCOPE` e ogni volta fa solo quella metà.
Senza `--purge`, lascia la configurazione dell'utente dov'è.

**Rilascia con un tag firmato**, così che una metà di sistema si aggiorni senza
password:

```bash
git config gpg.format ssh            # firma con la tua chiave SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

Il `templates/release.yml` di kiwi-updater pubblica una release GitHub solo per un tag
firmato da una chiave in `.github/allowed_signers`, e non crea mai tag da solo.
Poi apri una pull request che aggiunge il tuo URL al catalogo. Qualsiasi cosa open source
e davvero utilizzabile senza un account, un abbonamento o un tracker è benvenuta.

## Fiducia { #trust }

Il catalogo è **curato, non verificato**. Essere in elenco significa che qualcuno ha pensato che
valesse la pena avere l'app, non che il suo codice sia stato esaminato. Leggi
`kiwi info <app>` prima di installare qualcosa che non conosci già, e
`kiwi info --installer <app>` per vedere esattamente cosa verrà eseguito.
