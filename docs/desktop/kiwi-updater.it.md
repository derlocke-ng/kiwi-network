# kiwi-updater

`kiwi` installa e aggiorna app open source da **cataloghi git** su Fedora
Silverblue, Bluefin e altri sistemi ostree. Un'app è un repository git con un
`kiwi.manifest` e un `install.sh`. kiwi lo clona, fa il checkout del suo ultimo
tag di release, esegue il suo installer e lo tiene aggiornato in background,
sé stesso compreso.

Niente account, niente store e niente vendor. Un catalogo è un repository che puoi leggere,
di cui puoi fare un fork e a cui puoi mandare una pull request.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Ultima release: **v2.4.0**, una release di sicurezza
- **`kiwi`** è la CLI. Richiede `git`, coreutils, `util-linux` e `awk`, tutti
  nell'immagine di base, più `ssh-keygen` per il controllo delle firme.
- **Kiwi Apps** (`kiwi-gui`) è l'app GTK4: ricerca, filtri, una vista di dettaglio per ogni
  app con la sua icona, gli screenshot e le dipendenze. Mostra l'installer e
  il diff di un aggiornamento prima di eseguire l'uno o l'altro, e mette in coda i tuoi clic. I suoi dati vengono
  dalla CLI; icone e screenshot vengono letti dai cloni delle app, quindi per essi non
  si scarica nulla.

## Installazione { #install }

```bash
# consigliata: ambito utente più ambito di sistema di proprietà di root, una sola richiesta di password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minima: 100 % a livello utente, solo ~/.local, niente root e niente password, mai
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# nessuna azione senza password: ogni modifica al sistema chiede una password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

Il [catalogo Kiwi](catalogs.md) viene registrato dall'installazione. Passa subito a
`kiwi list` oppure apri **Kiwi Apps**.

Le app che sono solo file nella tua home (gli strumenti CLI, ensconce, syncman) sono
complete con l'installazione minima. Un'app con una metà root, come
kiwi-killswitch, richiede l'ambito di sistema. Su un'installazione minima,
`kiwi install kiwi-killswitch` lo configura sul momento con una sola password.

## Comandi { #commands }

```bash
kiwi list [--check]          # ogni app che questa macchina conosce
kiwi search vpn              # cerca app in ogni catalogo registrato
kiwi info kiwi-killswitch    # cosa è, cosa installa, se richiede root
kiwi install <app>           # un nome, oppure un --all esplicito
kiwi update [<app>]          # tutto ciò che ha una nuova release
kiwi uninstall <app>         # --purge elimina anche la sua configurazione
kiwi check                   # esce con 10 se qualcosa ha un aggiornamento

kiwi add <https-url>         # segue direttamente un repository, senza catalogo
kiwi catalog add|list|remove # gestisce i cataloghi
kiwi sync                    # aggiorna subito i cataloghi
kiwi self-update
kiwi trust --system <app>    # dimentica la chiave di firma fissata per questa app di sistema
```

Prima di eseguire qualcosa, e quando qualcosa va storto:

```bash
kiwi info --installer <app>  # lo script che verrebbe eseguito installando, prima che parta
kiwi diff <app>              # cosa cambierebbe un aggiornamento, installer compreso
kiwi pin <app> v1.2.0        # resta lì; kiwi unpin <app> per seguire di nuovo le release
kiwi install <app> --dry-run # ambito, URL, ref, percorso del file installer, e niente altro
kiwi doctor                  # lock vecchi, versioni disallineate, file di elenco errati, timer
```

## Le release sono tag { #releases-are-tags }

Un'app segue il suo ultimo **tag di versione**, uno che corrisponde a
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Le pre-release
e i tag provvisori non scavalcano mai una release. Un repository senza tag di versione segue
il suo branch predefinito. `ref=<tag>` su una riga dell'elenco ne richiede uno specifico.

## Dipendenze { #dependencies }

`DEPENDS=` in un manifest indica ciò di cui un'app ha bisogno. Una parola che è un'app nel tuo
catalogo o nel tuo elenco viene installata **prima**, nello stesso ambito, al momento dell'installazione.
`kiwi install kiwi-plugin-tor`, per esempio, porta con sé kiwi-proxy. Qualsiasi altra
parola è un programma, controllato con `command -v`.

## Un'app, due metà { #one-app-two-halves }

Alcune app sono solo un binario in `~/.local/bin`. Altre, come un kill switch VPN,
sono un demone root **e** un'app desktop **e** un'estensione di GNOME. Le metà
si installano con privilegi diversi, perché **root non deve mai eseguire un file che
l'utente può scrivere**. L'app lo dichiara:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Un catalogo elenca quell'app una volta sola, e kiwi installa correttamente ciascuna metà. Prima di
chiederti la password, mostra il `ROOT_REASON`.

| Parte | Dove | Perché |
|---|---|---|
| `kiwi`, Kiwi Apps, app utente | `~/.local` | non serve root; sopravvive a un rebase ostree |
| la copia di kiwi propria di root | `/usr/local/bin`, clonata in `/var/lib/kiwi-updater/repos/` | root non esegue mai un file che puoi scrivere tu |
| app di sistema | `/var/lib`, `/etc` | scrivibili su ostree, di proprietà di root |
| elenchi | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | le voci proprie di una macchina hanno la precedenza su qualsiasi catalogo |
| chiavi di firma fissate | `/etc/kiwi-updater/signers/<app>` | vedi sotto |

La `/usr` immutabile non viene mai toccata.

## Root, password e firme { #root-passwords-and-signatures }

| | Richiede root | Chiede una password |
|---|---|---|
| qualsiasi cosa nell'ambito utente | no | no |
| **aggiornare** un'app di sistema | sì | **no**, per una release firmata dalla chiave che root ha fissato per quell'app. **Sì** per una release non firmata, e sempre in modalità `manual` |
| **installare** o **disinstallare** un'app di sistema | sì | sì |

Dalla 2.4.0:

- **Release firmate.** Root fissa una chiave di firma SSH per ogni app di sistema, la prima
  che vede (trust on first use). Un tag di release firmato da quella chiave
  si aggiorna senza password. Una release non firmata ne chiede una e dice che non ha potuto
  verificarla. Un tag firmato da una chiave diversa, o un tag non firmato dopo tag firmati,
  viene rifiutato finché non esegui `kiwi trust --system <app>`. Questo vale per
  l'ambito di sistema.
- **Root installa solo dalle fonti che elenca**: `/etc/kiwi-updater/apps.list` e
  i cataloghi registrati per root. Per tutto il resto kiwi installa la metà utente
  e indica il comando `kiwi add --system <https-url>` da eseguire. Kiwi Apps offre
  *Register and Install*.
- **Solo https.** Le fonti `http://` vengono rifiutate ovunque.

Gli aggiornamenti di sistema senza password passano per un unico helper con uno scopo fisso,
`/usr/local/libexec/kiwi-system-update`. Una regola polkit lo consente per le sessioni
`wheel` attive, e accetta nomi di app solo come selezione dagli elenchi propri di root.

## Aggiornamenti in background { #background-updates }

C'è un solo timer, ed è tuo: `kiwi-updater.timer` esegue
`kiwi update --all` sei ore dopo l'ultima esecuzione (dieci minuti dopo l'avvio, con
un certo ritardo casuale). Aggiorna direttamente le metà utente, e le metà di sistema tramite
l'helper descritto sopra. Non c'è alcun timer di root. In modalità `manual`, le metà di sistema aspettano
il tuo prossimo `kiwi update` interattivo.

## Fiducia { #trust }

Installare un'app **esegue l'`install.sh` di quel repository**, e un'app che dichiara
l'ambito di sistema lo esegue **come root**. I cataloghi sono curati, non verificati. Aggiungi
quelli di cui ti fidi, come aggiungeresti un repository di pacchetti, e usa
`kiwi info --installer`, `kiwi diff` e `kiwi pin` per decidere a occhi
aperti. Una firma restringe *chi può pubblicare*. Non dice nulla su *cosa fa
ciò che viene pubblicato*.

Ancora pianificato: un registro ospitato di cataloghi fidati (`kiwi catalog browse`)
con le impronte dei firmatari per ogni voce.
