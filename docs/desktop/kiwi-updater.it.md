# kiwi-updater

kiwi-updater installa app open source sul tuo desktop e le tiene aggiornate. Il
suo comando è `kiwi`. Prende le app dai **cataloghi git** e funziona su Fedora
Silverblue, Bluefin e altri sistemi ostree. Un catalogo è un repository git che
elenca delle app. Un’app è un repository git con un file `kiwi.manifest` e uno
script `install.sh`. kiwi clona il repository dell’app, passa al suo tag di
release più recente ed esegue il suo script di installazione. Da quel momento
aggiorna l’app in background, e allo stesso modo aggiorna sé stesso.

Non ti serve alcun account, e non ci sono né app store né fornitori. Un catalogo
è un repository che puoi leggere, di cui puoi fare il fork e a cui puoi mandare
una pull request.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Ultima release: **v2.4.0**, una release di sicurezza
- **`kiwi`** è lo strumento da riga di comando (CLI). Ha bisogno di `git`,
  coreutils, `util-linux` e `awk`, che fanno tutti parte dell’immagine di base.
  Per verificare le firme serve anche `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) è l’app per il desktop, realizzata con GTK4. Puoi
  cercare e filtrare le app, e ogni app ha una pagina di dettaglio con la sua
  icona, gli screenshot e le dipendenze. Prima di installare un’app, Kiwi Apps
  ti mostra lo script di installazione, e prima di aggiornarla ti mostra che
  cosa cambia l’aggiornamento. Se fai clic su più azioni di seguito, le mette
  in coda. I dati li prende dalla CLI. Icone e screenshot li legge dai cloni
  locali delle app, quindi per mostrarli non scarica nulla.

## Installazione { #install }

kiwi lavora in due ambiti. L’ambito utente è tutto ciò che sta nella tua
cartella home, e non richiede mai root. L’ambito di sistema è una parte che
appartiene a root, per le app che hanno bisogno di root. Durante
l’installazione decidi quanta parte dell’ambito di sistema vuoi usare:

```bash
# consigliato: ambito utente più l’ambito di sistema di proprietà di root, una sola richiesta di password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimo: 100% a livello utente, solo ~/.local, mai root e mai password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# nessuna azione senza password: ogni modifica al sistema chiede la password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

L’installazione registra il [catalogo Kiwi](catalogs.md), quindi puoi eseguire
subito `kiwi list` o aprire **Kiwi Apps**.

Alcune app sono fatte soltanto di file nella tua cartella home, per esempio gli
strumenti da riga di comando, ensconce e syncman. Con l’installazione minima
queste app sono complete. Un’app con una metà che gira come root, come
kiwi-killswitch, ha bisogno dell’ambito di sistema. Su un’installazione minima,
`kiwi install kiwi-killswitch` prepara l’ambito di sistema in quel momento e ti
chiede la password una volta.

## Comandi { #commands }

```bash
kiwi list [--check]          # tutte le app note a questa macchina
kiwi search vpn              # cerca un’app in tutti i cataloghi registrati
kiwi info kiwi-killswitch    # che cos’è, che cosa installa, se ha bisogno di root
kiwi install <app>           # un nome, oppure esplicitamente --all
kiwi update [<app>]          # tutto ciò che ha una nuova release
kiwi uninstall <app>         # --purge elimina anche la sua configurazione
kiwi check                   # codice di uscita 10 se c’è qualche aggiornamento

kiwi add <https-url>         # segue direttamente un repository, senza catalogo
kiwi catalog add|list|remove # gestisce i cataloghi
kiwi sync                    # aggiorna subito i cataloghi
kiwi self-update
kiwi trust --system <app>    # dimentica la chiave di firma fissata per un’app di sistema
```

I comandi seguenti ti mostrano che cosa farà un’app prima che tu la esegua, e ti
aiutano quando qualcosa va storto:

```bash
kiwi info --installer <app>  # lo script che un’installazione eseguirebbe, prima che venga eseguito
kiwi diff <app>              # che cosa cambierebbe un aggiornamento, script di installazione compreso
kiwi pin <app> v1.2.0        # resta lì; con kiwi unpin <app> torna a seguire le release
kiwi install <app> --dry-run # ambito, URL, ref, percorso dello script di installazione, e nient’altro
kiwi doctor                  # lock rimasti, versioni non allineate, file di elenco errati, timer
```

## Le release sono tag { #releases-are-tags }

kiwi usa i tag git come release. Un’app segue il suo **tag di versione** più
recente. Un tag di versione è un tag che corrisponde a
`^v?[0-9]+(\.[0-9]+){0,3}$`, per esempio `v1`, `v1.2`, `1.2.3` o `v1.2.3.4`. I
tag di pre-release e i tag temporanei non corrispondono, quindi non vengono mai
usati al posto di una release. Un repository senza tag di versione segue il suo
branch predefinito. Per chiedere una versione precisa, aggiungi `ref=<tag>` alla
riga dell’app in un elenco.

## Dipendenze { #dependencies }

La riga `DEPENDS=` di un manifest indica di che cosa ha bisogno un’app. Se una
parola di quella riga è il nome di un’app presente nel tuo catalogo o nel tuo
elenco, kiwi installa quell’app **prima**, nello stesso ambito, nel momento in
cui installi l’app che ne ha bisogno. Per esempio, `kiwi install kiwi-plugin-tor`
installa anche kiwi-proxy. Ogni altra parola kiwi la considera il nome di un
programma, e con `command -v` controlla che quel programma sia presente.

## Un’app, due metà { #one-app-two-halves }

Alcune app sono un solo programma in `~/.local/bin`. Altre, come un kill switch
per la VPN, sono fatte di un daemon che gira come root **e** di un’app per il
desktop **e** di un’estensione di GNOME. Un’app del genere ha due metà, una metà
utente e una metà di sistema, che vengono installate con privilegi diversi. Il
motivo è che **root non deve mai eseguire un file che l’utente può modificare**.
L’app dichiara le sue parti e i suoi ambiti nel manifest:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Un catalogo elenca un’app del genere una volta sola, e kiwi installa ciascuna
metà nell’ambito giusto. Prima di chiederti la password, kiwi ti mostra il
`ROOT_REASON`.

| Parte | Dove | Perché |
|---|---|---|
| `kiwi`, Kiwi Apps, app utente | `~/.local` | non richiede root, e resta al suo posto quando il sistema passa (rebase) a un’altra immagine ostree |
| la copia di kiwi propria di root | `/usr/local/bin`, clonata in `/var/lib/kiwi-updater/repos/` | root non esegue mai un file che puoi modificare tu |
| app di sistema | `/var/lib`, `/etc` | sui sistemi ostree queste directory sono scrivibili e appartengono a root |
| elenchi | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | le voci nell’elenco della macchina hanno la precedenza su qualsiasi catalogo |
| chiavi di firma fissate | `/etc/kiwi-updater/signers/<app>` | vedi la sezione successiva |

kiwi non modifica mai nulla nella `/usr` immutabile.

## Root, password e firme { #root-passwords-and-signatures }

La tabella mostra quali azioni richiedono root e quali chiedono una password.

| | Richiede root | Chiede una password |
|---|---|---|
| qualsiasi cosa nell’ambito utente | no | no |
| **aggiornare** un’app di sistema | sì | **no**, se la release è firmata con la chiave che root ha fissato per quell’app. **Sì**, se la release non è firmata, e sempre in modalità `manual` |
| **installare** o **disinstallare** un’app di sistema | sì | sì |

Dalla versione 2.4.0 valgono queste regole:

- **Release firmate.** Per ogni app di sistema root fissa una chiave di firma
  SSH. Fissare una chiave significa ricordarla e da quel momento accettare
  soltanto quella. Root fissa la prima chiave che vede per l’app: è il principio
  detto trust on first use, la fiducia al primo utilizzo. Se un tag di release è
  firmato con la chiave fissata, l’aggiornamento viene installato senza
  password. Se una release non è firmata, kiwi ti chiede la password e ti
  avvisa che non ha potuto verificarla. kiwi rifiuta un tag firmato con una
  chiave diversa, e rifiuta un tag non firmato se i tag precedenti erano
  firmati. Li rifiuta finché non esegui `kiwi trust --system <app>`. Queste
  regole valgono per l’ambito di sistema.
- **Root installa soltanto da fonti che elenca lui stesso.** Queste fonti sono
  `/etc/kiwi-updater/apps.list` e i cataloghi registrati per root. Se un’app
  arriva da qualsiasi altra fonte, kiwi installa soltanto la metà utente e ti
  indica il comando `kiwi add --system <https-url>` da eseguire. In questo caso
  Kiwi Apps offre il pulsante *Register and Install*, che registra la fonte e
  installa l’app.
- **Solo https.** kiwi rifiuta le fonti `http://` ovunque.

Gli aggiornamenti di sistema senza password li esegue un unico programma di
supporto, `/usr/local/libexec/kiwi-system-update`, che serve soltanto a questo.
Una regola di polkit consente agli utenti del gruppo `wheel` di eseguirlo quando
la loro sessione è attiva. Il programma accetta soltanto nomi di app, e un nome
può selezionare soltanto un’app presente negli elenchi propri di root.

## Aggiornamenti in background { #background-updates }

Per gli aggiornamenti in background c’è un solo timer, ed è un timer utente di
systemd: gira quindi con il tuo utente e non come root. `kiwi-updater.timer`
esegue `kiwi update --all` sei ore dopo l’ultima esecuzione e dieci minuti dopo
l’avvio, con un ritardo casuale. Questa esecuzione aggiorna direttamente le metà
utente, mentre le metà di sistema le aggiorna attraverso il programma di
supporto descritto sopra. Non esiste un timer di root. In modalità `manual` il
timer non aggiorna le metà di sistema: aspettano che tu esegua `kiwi update`.

## Fiducia { #trust }

Quando installi un’app, kiwi **esegue lo `install.sh` del repository di
quell’app**. Se l’app dichiara l’ambito di sistema, kiwi esegue questo script
**come root**. I cataloghi sono curati, non verificati: qualcuno ha scelto le
app, ma questo non significa che il loro codice sia stato controllato. Aggiungi
soltanto i cataloghi di cui ti fidi, come faresti con un repository di
pacchetti. Usa `kiwi info --installer`, `kiwi diff` e `kiwi pin` per vedere che
cosa fa un’app prima di decidere. Una firma limita *chi può pubblicare* una
release, ma non dice nulla su *che cosa fa la release pubblicata*.

È ancora prevista una cosa: un registro ospitato di cataloghi fidati, con il
comando `kiwi catalog browse` e con le impronte dei firmatari per ogni voce.
