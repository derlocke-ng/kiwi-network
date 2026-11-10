# Gestire il tuo hub

Questa pagina spiega come gestire un hub per la tua comunità. Un hub è il sito
web che una comunità ottiene da kiwi-framework: un mercato aperto, un feed, una
chat e altre app che girano nel browser. È fatto soltanto di file statici,
quindi ospitarne uno significa pubblicare una cartella di file via HTTPS. Ci
sono tre strade:

- **Usare Armory così com’è.** Armory è il primo hub costruito con il framework,
  ed è aperto a tutti all’indirizzo
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Creare una tua distribuzione.** Una distribuzione è il framework con un
  nome, dei relay e una selezione di app scelti da te. Puoi pubblicarla su
  qualsiasi hosting statico.
- **Eseguire il container dell’hub.** Puoi farlo, per esempio, dentro la tua
  Kiwi Network, insieme a un relay tutto tuo. Ottieni così un hub privato,
  raggiungibile soltanto dalla mesh, cioè dalla rete privata che collega le tue
  macchine.

## Tipi di hub { #kinds-of-hub }

| Tipo | Come funziona | Esempio |
|---|---|---|
| **Pubblico** | L’hub usa relay pubblici e chiunque può aprirlo. | Armory |
| **Privato** | Chi usa l’hub non può sostituire i relay (`policy.relays: 'locked'`), e le pagine restano in attesa finché uno di questi relay non risponde (`requireHub`). I relay si trovano dentro una VPN. | l’hub di un’azienda sul suo kiwi-master |
| **Semipubblico** | Un hub privato che ha anche un’area pubblica. Lì alcune app scelte, per esempio la chat, usano relay pubblici. | |

I relay di un hub formano reti separate: la rete propria dell’hub, l’area
pubblica e le reti dei suoi spazi. Ogni evento, cioè ogni messaggio nostr
firmato, appartiene a una sola di queste reti e non viene mai passato a
un’altra.

## La tua distribuzione { #your-own-distribution }

Parti da Armory, che fa da modello. Su GitHub il pulsante *Use this template* ti
dà una copia del repository senza la sua cronologia. Poi segui questi passaggi:

1. Modifica **`distribution.js`**. In questo file si impostano identificativo,
   nome, logo, descrizione, homepage, repository, relay, server multimediali,
   spazi, app e mount. Se il tuo hub deve offrire anche gli spazi di Armory,
   copia i loro `owner` e `id` dal file `hub.json` di Armory.
2. Modifica **`locales/*.json`**. Questi file contengono il titolo, il testo
   introduttivo e il piè di pagina, più il testo della scheda di ciascun mount.
   L’inglese è la lingua di riserva.
3. Aggiorna **`kiwi.manifest`**. Se vuoi, aggiungi anche il tuo hub a
   [kiwi-web-catalog](#kiwi-web-catalog).
4. Su GitHub scegli *Settings → Pages → Source: GitHub Actions*, poi fai il
   push.

Questi sono i comandi che ti servono mentre lavori a una distribuzione:

```bash
npm install
npm run dev                  # l’hub con hot reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # un relay di prova locale su ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # crea lo scheletro di una nuova app
```

Fissa kiwi-framework a un commit o a un tag, mai a un branch. La build controlla
il tuo `distribution.js`. Per esempio, un hub con un mount pubblico deve avere
dei relay pubblici, e un hub con dei relay pubblici deve avere un mount
pubblico.

Tutto ciò che vedi nel browser è scritto in TypeScript con React 19 e compilato
con Vite. Lo strato dei dati, in `shared/`, è JavaScript puro con tipi JSDoc. I
test girano nel test runner di node, e quelli che hanno bisogno di un browser
girano in Playwright.

## Il container dell’hub { #the-hub-container }

Armory è disponibile anche come immagine container,
`ghcr.io/derlocke-ng/armory`. L’immagine viene costruita dal file
`container/Dockerfile` del framework e pubblica l’hub con nginx. All’avvio del
container, lo script di entrypoint scrive il file `hub.local.json` a partire
dalle variabili `HUB_*`, e la pagina legge questo file prima di collegarsi. In
questo modo chi installa l’hub può sceglierne i relay e le regole, ma non può
aggiungere codice. Se non è impostata alcuna variabile, l’hub funziona così
com’è stato compilato.

Questo esempio avvia un hub con un proprio relay non sostituibile e con un mount
su un relay pubblico:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variabile | Significato |
|---|---|
| `HUB_RELAYS` | I relay propri dell’hub. |
| `HUB_PUBLIC_RELAYS` | I relay dell’area pubblica. Se la variabile è impostata ma vuota, l’area pubblica non c’è. |
| `HUB_DIRECTORY_RELAYS` | I relay su cui vengono pubblicati e cercati gli elenchi di relay. |
| `HUB_RELAYS_LOCKED` | Con `true`, chi usa l’hub non può sostituirne i relay. |
| `HUB_REQUIRE_HUB` | Con `true`, le pagine restano in attesa finché nessuno dei relay dell’hub risponde. |
| `HUB_PUBLIC_MOUNTS` | I mount che usano l’area pubblica, elencati per identificativo. |
| `HUB_ACCOUNT_MOUNTS` | I mount che richiedono un account. |
| `HUB_REQUIRE_ACCOUNT` | Con `true`, tutti i mount richiedono un account. |
| `HUB_SPACE_RELAYS` | I relay di ciascuno spazio, nella forma `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | Le chiavi delle persone che moderano tutti gli spazi definiti dall’hub. |
| `HUB_REGISTER_POW` | Il numero di bit di proof of work richiesti a un nuovo account. Serve per i relay che accettano soltanto i membri. |
| `HUB_CALDAV` | Un server Nextcloud. nginx gli inoltra `/remote.php/dav/`, così il calendario non ha bisogno di CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | I server STUN/TURN per le chiamate e i trasferimenti diretti, che aiutano due browser a collegarsi tra loro. Le credenziali TURN sono visibili nella pagina, quindi creane di apposite, usate soltanto da questo hub. |

`HUB_USER_MOUNTS` viene letta ma per ora non ha alcun effetto. Appartiene a una
funzione che deve ancora arrivare: seguire uno spazio che l’hub non include.

L’hub va pubblicato via HTTPS, perché WebCrypto richiede un contesto sicuro. I
suoi relay vanno pubblicati via `wss://`. Se l’hub viene aperto in semplice
`http://` da un indirizzo diverso da localhost, la pagina lo segnala e si ferma.

### Un hub nella tua Kiwi Network { #on-a-kiwi-network }

Un kiwi-master è l’unico server di una Kiwi Network raggiungibile da Internet.
Può ospitare un relay e un hub propri, grazie a due moduli. Il modulo
`nostr-relay` esegue strfry, il software del relay, all’indirizzo
`relay.<host>`. Il modulo `hub` esegue questa immagine container, con Armory
come impostazione predefinita, all’indirizzo `hub.<host>`.

Per impostazione predefinita sono entrambi privati: sono raggiungibili soltanto
dalla mesh e usano il certificato della fleet. Per un hub semipubblico aggiungi
`public_relays` e `public_mounts`. Per un hub pubblico aggiungi
`reverse-proxy.public`, che ottiene i certificati da Let's Encrypt.

Il relay di un hub pubblico accetta i post che arrivano dalla mesh. Da Internet
accetta soltanto quelli dei membri che dimostrano di possedere la propria chiave
(NIP-42). I membri sono le persone presenti nell’elenco firmato dagli
amministratori (`write_pubkeys`). Con `members: registered` è membro chiunque
abbia un account sull’hub. Vedi il
[riferimento dei moduli](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
è un catalogo, cioè un repository git che elenca altri repository. Elenca gli
hub, le loro app e il framework, e ha lo stesso formato del catalogo per il
desktop. Il file `apps.list` contiene un URL git per riga. Una riga può avere
`path=`, per un’app che si trova dentro il repository di un hub, e `ref=`, per
fissare una versione. Ogni voce contiene un `kiwi.manifest` con `CATEGORY`
uguale a `Framework`, `Hub` oppure `App`.

Oggi elenca kiwi-framework, Armory e le dieci app di Armory. **Non** è pensato
per `kiwi catalog add`: le sue voci non hanno un programma di installazione, e
per ora niente legge il catalogo in automatico. Secondo il suo README, i file
del catalogo sono di pubblico dominio (CC0).

Per aggiungere il tuo hub fai il fork del catalogo, aggiungi una riga,
assicurati che il tuo repository contenga un `kiwi.manifest` e apri una pull
request.

## Non ancora realizzato { #not-built-yet }

Queste voci sono nella roadmap del framework e ancora non esistono:

- Il blog.
- Le approvazioni come strumento di moderazione (NIP-72, kind 4550).
- Seguire uno spazio che il tuo hub non include.
- L’accesso tramite un’estensione del browser (NIP-07) o un firmatario remoto
  (NIP-46).
- Un server TURN nello stack Kiwi. Il lavoro su questo punto è in sospeso in
  kiwi-modules. Senza TURN, due telefoni collegati con la rete mobile spesso non
  riescono a stabilire una connessione diretta.
