# Hub, non piattaforme

**kiwi-framework** è un software con cui qualsiasi comunità può gestire il
proprio **hub**. Un hub è un sito web con una serie di app per i membri della
comunità: un mercato aperto, un feed, una chat, la condivisione di file, le
liste condivise, un gestore di password e un calendario. Chiunque può mettere in
piedi un hub per una comunità qualsiasi, e quella comunità non dipende più da
una piattaforma centrale che custodisce gli account e i dati di tutti.

Le app girano interamente nel browser. Si sincronizzano attraverso i relay
[nostr](https://nostr.com), cioè server che conservano messaggi firmati e li
inoltrano, ed è la comunità a scegliere quali relay usa il suo hub. Tra il
browser e i relay non c’è nessun server degli account e nessun backend, e tutto
ciò che è privato viene cifrato sul dispositivo prima di essere inviato. Le
altre parti di Kiwi Network collegano le tue macchine, gli hub collegano le
persone. Ogni app è descritta in [Le app del framework](apps.md).

Armory è il primo hub costruito con il framework. È un esempio di hub, ed è
anche il modello che le altre comunità copiano per costruire il
proprio.

Il software si trova in tre repository:

| Repository | Che cos’è |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Il software generico da cui nasce ogni hub. Contiene identità e account, relay e sincronizzazione, amici e condivisione, moderazione, il kit grafico, le pagine dell’hub e dieci app. Da solo il framework non si può aprire come sito web: è una distribuzione a farne un hub. La versione attuale è la v0.32.1, la licenza è GPL-3.0-or-later. |
| [**Armory**](armory.md) | La prima **distribuzione**, cioè un hub costruito con il framework. Aggiunge un nome, i relay predefiniti e tutte e dieci le app, ognuna con un nome scelto da Armory. È il modello di cui fare il fork per creare il tuo hub. La licenza è GPL-3.0-or-later. **Online:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Un catalogo, cioè un repository git che elenca gli hub e le loro app. Ha lo stesso formato del [kiwi-catalog](../desktop/catalogs.md) per il desktop. |

## Come si incastrano i pezzi { #how-it-fits-together }

Lo schema mostra come il framework diventa un hub nel tuo browser, e con quali
server il browser comunica da quel momento in poi.

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## I termini usati in queste pagine { #the-words }

- **Hub**: il sito web che una comunità usa. È ciò che ottieni quando compili
  una distribuzione. È fatto soltanto di file statici, quindi ospitarne uno
  significa pubblicare una cartella di file. Ogni hub ha una pagina iniziale,
  una pagina delle impostazioni e una pagina dell’account.
- **Distribuzione**: il framework insieme alle scelte che ne fanno un hub
  preciso, cioè un nome e un aspetto, i relay predefiniti e una selezione di app
  montate su determinati spazi. Quando fai il fork di una distribuzione, tutto
  quello che cambi sta in un solo file, `distribution.js`, e nelle sue
  traduzioni.
- **App**: una cartella con un file manifest. Si può aggiungere a qualsiasi
  distribuzione. Le app usano soltanto l’API pubblica del framework e non
  accedono mai direttamente all’archivio dei dati o alle chiavi.
- **Spazio**: una comunità con un nome, un proprietario, i suoi moderatori e, se
  li vuole, i suoi relay. Riprende il modello delle comunità moderate di nostr
  (NIP-72). Un altro hub può offrire lo stesso spazio: gli basta indicarne
  l’indirizzo.
- **Mount**: un’app usata per uno spazio. Ogni mount ha un nome, una route (il
  suo indirizzo all’interno dell’hub) e un’icona tutti suoi. La stessa app si
  può montare più volte. Per esempio, il *Trading Post* di Armory è l’app
  `market` del framework montata sullo spazio `tradingpost` di Armory.

Due persone che usano hub di distribuzioni diverse possono essere amiche,
condividere contenuti e chattare esattamente come se usassero lo stesso hub. È
possibile perché l’identità e i dati di una persona sono eventi nostr, cioè
messaggi firmati conservati sui relay, e non appartengono a un hub.

## Account e chiavi { #accounts-and-keys }

- La prima volta che apri un hub su un dispositivo, il browser crea una chiave
  per quel dispositivo e la conserva.
- Un **account** è un nome utente con una password. Si basa su normali eventi
  nostr, e non esiste alcun registro degli account. Dalla password, con scrypt
  (una funzione volutamente lenta da calcolare), si ricava il valore che sblocca
  la tua chiave. Senza la password nessuno può impadronirsi di un account né
  sovrascriverlo. **La password non si può reimpostare.**
- Puoi accedere anche con una chiave nostr che possiedi già, indicata come
  `nsec`, in esadecimale o come `ncryptsec`. L’accesso tramite un’estensione del
  browser (NIP-07) o un firmatario remoto (NIP-46) è previsto, ma non è ancora
  stato realizzato.
- Un solo account vale per tutte le app dell’hub e su ogni dispositivo da cui
  accedi.

## Il modello di privacy { #privacy-model }

**Che cosa è cifrato.** Il browser cifra i contenuti prima di inviarli da
qualsiasi parte. Usa AES-256-GCM con chiavi derivate tramite HKDF. I messaggi
privati sono messaggi NIP-17 racchiusi in gift wrap NIP-59. Un gift wrap è un
secondo strato di cifratura, grazie al quale un relay vede soltanto che una
certa chiave ha ricevuto un messaggio impacchettato. Ogni file viene cifrato con una
chiave AES-256-GCM casuale, diversa per ciascun file, prima di essere caricato
su un server multimediale. Le foto vengono prima ricodificate, e questo elimina
i metadati aggiunti dalle fotocamere. Il Vault è cifrato con una frase segreta
tutta sua (scrypt + AES-256-GCM). Le chiamate passano direttamente da un browser
all’altro e sono cifrate da WebRTC.

**Prima in locale.** Tutto ciò che scrivi viene salvato innanzitutto nel
database del browser, e solo dopo inviato ai relay. Le app leggono da quel
database, sul dispositivo, e per questo funzionano anche offline. Quando un
dispositivo si ricollega, rimanda al relay i dati che il relay non ha più. I
dati vanno quindi persi soltanto se spariscono tutti i dispositivi che li
conservavano *e* non esiste alcun backup.

**Che cosa possono vedere gli altri.** I limiti sono dichiarati dai repository
stessi:

- I relay vedono i metadati: chi scrive a quali indirizzi, quando, quanto e da
  quale indirizzo IP. Se per te è un problema, usa una VPN o Tor.
- La chiave di uno spazio non è un segreto. Serve soltanto a evitare che i post
  di una comunità siano leggibili in chiaro da chiunque. I relay possono vedere
  i mi piace, le segnalazioni e chi ha commentato che cosa.
- Le note di DevBoard e le segnalazioni di moderazione sono pubbliche per
  scelta.
- La tua chiave è conservata nell’archivio del browser. Tutti i siti GitHub
  Pages di uno stesso account condividono un’unica origine, e i browser separano
  l’archivio dei siti web in base all’origine. Un hub con un proprio dominio o
  sottodominio è quindi la soluzione più solida.
- In un trasferimento diretto di file o in una chiamata, ciascuno dei due
  browser viene a conoscere l’indirizzo IP dell’altro, e li vedono entrambi
  anche i server STUN che li aiutano a collegarsi. Per impostazione predefinita
  sono i server STUN di Google e di Cloudflare. Un hub può impostare i propri.
- «Nessun server nostro» significa che le app non dipendono da alcun server
  gestito dal progetto. Usano comunque dei relay, dei server multimediali e, per
  il calendario, un server CalDAV. Quali, lo decidi tu o lo decide il tuo hub.

## Moderazione { #moderation }

La moderazione ha tre livelli. Il primo è la tua lista di blocco, cifrata in
modo che possa leggerla solo tu. Il secondo sono le segnalazioni, pubbliche e
firmate. Il terzo sono le regole di ciascun relay.

Ogni spazio ha dei moderatori. Quando un moderatore segnala un post, il post
viene subito ripiegato. Negli altri casi un post viene ripiegato dopo tre segnalazioni da parte di persone non bloccate. Un post può
essere contrassegnato come 18+ o come pubblicità, e i post contrassegnati sono
mostrati soltanto a chi ha un account.

## Per approfondire { #read-on }

- [Armory e le sue app](armory.md)
- [Gestire il tuo hub](hubs.md)
- [L’architettura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  e il [protocollo di rete](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  del framework, documentati nel suo repository
