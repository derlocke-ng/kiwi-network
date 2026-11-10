# Armory

Armory è il primo hub costruito con kiwi-framework, il software con cui
qualsiasi comunità può gestire il proprio hub. Nel linguaggio del framework
Armory è una **distribuzione**: il framework insieme a un nome, ai relay
predefiniti e a una selezione di app. Armory include tutte e dieci le app del
framework e dà a ciascuna un nome suo. Il mercato e il feed sono pensati per chi
coltiva canapa. L’argomento è una scelta di questo hub, non del framework:
un’altra comunità userebbe le stesse app per il proprio. Puoi usare Armory così
com’è, oppure copiarlo come modello per il tuo hub.

Ogni strumento gira interamente nel tuo browser. Gli strumenti si sincronizzano
attraverso i relay, cioè server che conservano i tuoi dati e li inoltrano, e
quali relay usare lo scegli tu. Non serve registrarsi, il progetto non gestisce
alcun server proprio per Armory e niente ti traccia. Tutto viene cifrato prima
di uscire dal tuo dispositivo. Dalla pagina iniziale puoi installare Armory come
app web.

- **Aprilo:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Il repository è [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  la licenza è GPL-3.0-or-later.
- Armory è una distribuzione di [kiwi-framework](index.md) 0.32.1, e fissa il
  framework a un commit preciso. Armory in sé non ha ancora tag di release.
- È disponibile in inglese, tedesco, francese, spagnolo, italiano, olandese,
  polacco e portoghese.

In passato Armory si chiamava weaponized.js.

## Gli strumenti { #the-tools }

| Strumento | Che cosa fa |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Liste della spesa e di cose da fare, inventari di casa e note in Markdown, condivisi. Restano allineati su tutti i tuoi dispositivi e per le persone con cui li condividi. Tutto è cifrato end-to-end, e una lista si condivide con un link che consente la modifica oppure la sola lettura. Loadout funziona offline, e i tuoi dispositivi rimandano ai relay tutto ciò che i relay hanno perso. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Messaggi e file agli amici (NIP-17, cifrati sul tuo dispositivo). I gruppi esistono finché chi li ospita non li chiude. Nelle stanze dal vivo entra chiunque abbia il link, e spariscono quando esce l’ultima persona. Uplink ha risposte, reazioni, modifica dei messaggi, messaggi fissati, ricerca sul dispositivo e messaggi effimeri. Le chiamate vocali e le videochiamate funzionano fino a sei persone. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Condivisione di file in tre modi. Puoi creare un link a file che restano cifrati sui tuoi server multimediali finché non li elimini. Puoi mandare file ad amici e gruppi in Uplink. Oppure puoi inviarli direttamente dal tuo browser a quello di un’altra persona, e in quel caso non vengono salvati da nessuna parte. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Un gestore di password per accessi, note, carte e codici a due fattori, disponibile su ogni dispositivo da cui accedi. Ha un generatore di password e un rapporto sulla salute. Il rapporto individua le password deboli, riutilizzate e vecchie e, se attivi questo controllo, anche quelle finite in una violazione di dati. Vault importa ed esporta le voci. Gestisce anche chiavi SSH, un’autorità di certificazione SSH, una CA X.509 e certificati TLS. È cifrato con una frase segreta tutta sua. Non compila le password nei siti web al posto tuo. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Codici a due fattori (TOTP) per i tuoi account su altri servizi. Aggiungi un account a partire da un codice QR, da un link o da un segreto, oppure da un’esportazione di Google Authenticator. I codici sono conservati nella stessa cassaforte cifrata usata da Vault. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | I tuoi calendari, presi dal tuo Nextcloud o da qualsiasi altro server CalDAV. Mostra i prossimi giorni oppure un mese, gestisce gli eventi che si ripetono e ti ricorda gli eventi finché una pagina resta aperta. Ai relay non viene inviato nulla, e le credenziali di accesso al tuo server sono conservate cifrate nel tuo account. Il tuo server deve accettare le richieste provenienti dall’origine di Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Il feed di Armory, usato per i resoconti e i diari di coltivazione. Pubblichi voci con foto, settimana dopo settimana. Ogni voce può essere destinata a tutti in Outpost, ai tuoi amici, a una cerchia di amici o soltanto a te. Le voci possono avere hashtag, mi piace e commenti. Sono cifrate sul tuo dispositivo, e così le foto. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Il mercato di Armory, usato per la canapa: semi, talee e attrezzatura. Gli annunci hanno delle foto, e chi compra li trova per categoria e in base a dove spediscono. Scegliendo «Scrivi al venditore» si apre Uplink. Per usare Trading Post serve un account, e non c’è alcuna verifica dell’età. Prima di poter vendere bisogna aver pubblicato in Outpost (tre post, ciascuno con il mi piace di tre persone) oppure essere stati approvati da un moderatore. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Una bacheca per freelance. Pubblichi una nota per dire che cerchi persone o che sei disponibile. Ogni nota è firmata con la tua chiave e richiede una proof of work, cioè un piccolo calcolo che rende costoso pubblicare in massa. Gli altri possono votare una nota. Una nota sparisce alla scadenza, cioè da 24 ore a 30 giorni dopo la pubblicazione. Tutte le note sono pubbliche per scelta. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Pong in stile retrò per due giocatori, su due browser. Per iniziare una partita condividi un link o un codice QR, oppure scegli una delle partite aperte. Puoi anche allenarti offline contro il computer. |

È previsto un blog.

Ogni strumento è una delle app del framework, con il nome che le ha dato Armory.
Loadout è l’app `boards` del framework, Uplink è `chat`, Outpost è `feed`,
Trading Post è `market`, DevBoard è `notices` e pongjs è `pong`.

## Un solo account per tutti gli strumenti { #one-account-every-tool }

Accedi o crei un account dalla pagina iniziale, con nome utente e password
oppure con una chiave nostr. Da quel momento tutti gli strumenti usano
quell’account. Le liste che avevi creato su un dispositivo prima di accedere
vengono trasferite nell’account. Se non usi un account, ogni dispositivo lavora
con la propria chiave.

La pagina delle impostazioni vale per tutto l’hub. Da lì gestisci account e
dispositivi, amici e cerchie, persone bloccate, relay, spazi e server
multimediali, notifiche e backup cifrati.

## Relay e server multimediali { #relays-and-media-servers }

I relay predefiniti di Armory sono `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` e `wss://relay.primal.net`. I server multimediali conservano i
file che carichi e usano un protocollo chiamato Blossom. Quelli predefiniti di
Armory sono `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (che
accetta soltanto foto) e `blossom.primal.net`. Nelle impostazioni puoi scegliere
relay e server multimediali diversi.

I relay conservano i dati e li inoltrano, ma non possono leggere nulla di ciò
che è stato cifrato prima dell’invio. Che cosa possono vedere è elencato nel
[modello di privacy](index.md#privacy-model).

## Moderazione { #moderation }

I moderatori di Armory sono responsabili di Outpost, Trading Post e DevBoard.
Una voce di Outpost può essere contrassegnata come 18+ o come pubblicità. Il
contrassegno può metterlo l’autore, può metterlo un moderatore, e scatta anche
dopo due segnalazioni. Le voci contrassegnate sono mostrate soltanto a chi ha un
account.

## Il tuo Armory { #your-own-armory }

Armory è anche il modello per il tuo hub. Fai il fork del repository oppure
usalo come template, modifica `distribution.js` e le traduzioni, e pubblica il
risultato. I passaggi sono descritti in [Gestire il proprio hub](hubs.md).
