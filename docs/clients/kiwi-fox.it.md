# kiwi-fox

kiwi-fox ti dà un browser separato per ogni rete di un cliente in cui lavori, e
per ogni account che gestisci. Il profilo del browser dedicato a un cliente
raggiunge le console web di quel cliente attraverso la sua connessione, e non ha
altre strade verso l’esterno. Per questo non ti serve una connessione VPN
sull’host.

Ogni profilo è un’identità permanente. Ha il proprio archivio dei dati, esegue
uno di tre browser in un container Podman rootless (un container che gira con il
tuo utente, senza permessi di root) e di solito usa un exit di
[kiwi-proxy](kiwi-proxy.md). Un exit è una connessione a un upstream, salvata
con un nome, per esempio il proxy SOCKS5 di un cliente. Per ogni exit kiwi-proxy
esegue un gateway: un container la cui unica rotta porta a quell’upstream, e che
contiene un resolver DNS che blocca i domini pubblicitari.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Ultima release: **v0.7.1**. È nel [catalogo Kiwi](../desktop/catalogs.md), ambito utente.
- I browser, che kiwi-fox chiama motori, vengono scaricati sulla tua macchina e
  mai ridistribuiti. Camoufox (MPL-2.0) viene scaricato durante il setup.
  Firefox e Tor Browser vengono scaricati quando li richiedi
  (`kiwi-fox engine fetch`), e le loro firme vengono verificate.

| Motore | Che cosa vede una pagina |
|---|---|
| **Camoufox** (predefinito) | Una normale macchina Windows 11 con una sua area geografica, i cui valori sono tutti coerenti tra loro. Questa impronta (l’insieme dei valori che una pagina può leggere da un browser per riconoscerlo in seguito) è falsificata e non cambia |
| **Firefox** | Mozilla Firefox non modificato, che non falsifica nulla. Una pagina vede i valori reali di questa macchina. La connessione passa comunque dall’exit del profilo |
| **Tor Browser** | Tor Browser non modificato, collegato tramite un exit del modulo tor. Ogni sito riceve il suo circuito (un suo percorso attraverso la rete Tor), e i nomi `.onion` funzionano |

kiwi-fox è pensato per chi gestisce diversi account che possiede o che è
autorizzato a gestire, e non vuole che questi account vengano collegati tra loro
attraverso l’impronta del browser o l’indirizzo IP.

## Installazione { #install }

```bash
kiwi install kiwi-fox      # porta con sé kiwi-proxy; oppure ./install.sh install
kiwi-fox setup             # immagini, un motore di browser da ~630 MB, dati DNS; esegue anche il setup di kiwi-proxy
kiwi-fox engine fetch --engine firefox     # oppure torbrowser: con verifica della firma
```

kiwi-fox richiede Podman rootless, kiwi-proxy, Python 3.12+, GTK4 con
libadwaita e `secret-tool`. È pensato per una sessione Wayland. Funziona anche
con X11, ma lì l’isolamento è più debole. Per verificare Firefox e Tor Browser
servono `gpg`/`gpgv`. Con il driver proprietario NVIDIA, kiwi-fox ha bisogno
anche di `nvidia-container-toolkit` con la sua specifica CDI.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # un exit, definito una volta sola, in kiwi-proxy
kiwi-fox new work --exit client-a     # un profilo che lo usa: misura l’exit e sceglie un’identità adatta
kiwi-fox new plain --no-proxy         # la connessione di questa macchina, nessun isolamento
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # oppure dall’app
kiwi-fox stop work
kiwi-fox check                        # ogni profilo è ancora coerente?
kiwi-fox selfcheck work               # misura che cosa vedono le pagine, poi lo verifica
kiwi-fox-gui                          # "Kiwi Fox" nella griglia delle applicazioni
```

Con `--desktop-entry` un profilo riceve una sua voce nella griglia delle
applicazioni. Con i tag puoi raggruppare i profili.

## Profili ed exit { #profiles-and-exits }

Un profilo non possiede un exit: fa riferimento a uno, e più profili possono
fare riferimento allo stesso exit. I profili sullo stesso exit ne condividono il
gateway, e con esso un unico namespace di rete, un unico indirizzo IP di uscita
e un unico insieme di circuiti Tor. Le identità che non devono condividere un
exit hanno bisogno di exit diversi. Un profilo creato con `--no-proxy` non ha un
gateway. Il suo container del browser ha una rete propria e usa la connessione
di questa macchina. In quel caso non c’è alcun isolamento: il suo traffico non è
vincolato a un’unica strada.

Il container del browser entra nel namespace di rete del gateway. Gli vengono
tolte tutte le capability di Linux tranne `SYS_CHROOT`, che serve alla sandbox
di Firefox. Il container gira con `no-new-privileges`, e il motore è montato in
sola lettura.

## Un profilo Camoufox { #a-camoufox-profile }

Un profilo Camoufox si presenta come la macchina più comune che ci sia, perché i
sistemi di rilevamento segnalano i valori rari. Dichiara uno schermo 1920×1080,
i font presenti in ogni installazione di Windows 11 e nessun altro, e la vera
scheda grafica di questa macchina, con il nome che le darebbe Firefox su
Windows. Area geografica, lingua, fuso orario e voci vengono scelti in modo da
corrispondere all’exit. Puoi cambiare tutto in seguito con `kiwi-fox set`,
`kiwi-fox webgl` e `kiwi-fox fonts`. Una modifica viene salvata soltanto se il
profilo resta coerente, cioè se i suoi valori continuano a stare bene insieme.

## Che cosa non fa { #what-it-does-not-do }

kiwi-fox non promette che un profilo sia «non rilevabile». I profili sono
separati tra loro nell’archivio dei dati, nell’indirizzo IP e in ogni valore che
il motore può falsificare. **Non** sono separati negli identificativi che
derivano dall’hardware e sono uguali in qualsiasi browser. I fotogrammi che la
GPU disegna davvero e i tempi di risposta dell’hardware vengono dalla macchina
reale, quindi sono gli stessi per ogni profilo che gira su di essa. Il file
`docs/detection-notes.md` del repository documenta che cosa viene misurato.

kiwi-fox non ha alcuna automazione. Non esegue bot e non crea account in serie.
È fatto soltanto per la navigazione interattiva.
