# Le app del framework

kiwi-framework è il software con cui una comunità gestisce il proprio hub.
Questa pagina descrive le dieci app che ne fanno parte, tra cui un mercato
aperto, un feed per la comunità, una chat e la condivisione di file.

Nel framework le app hanno nomi semplici, come `market`. Una distribuzione, cioè
un hub specifico costruito con il framework, **monta** le app che le servono.
Montare un’app significa usarla per uno spazio, cioè per una comunità con i suoi
moderatori e i suoi relay, e darle un nome scelto dall’hub. La stessa app si può
montare più volte. Una banca dei semi e un negozio di pietre preziose, per
esempio, sono lo stesso codice di `market` su due spazi diversi. Ciascuno ha i
suoi moderatori e i suoi relay, e sullo stesso hub compaiono come due riquadri
distinti.

| App | Che cos’è | Nome in Armory |
|---|---|---|
| `market` | **Un mercato aperto** per la comunità a cui il mount è dedicato. Un annuncio ha delle foto, un prezzo e l’indicazione dei luoghi da cui e verso cui si spedisce, oppure la proposta di ritiro di persona. Chi compra trova gli annunci per categoria e in base a dove si trova. La ricerca usa etichette che i relay possono confrontare ma non leggere. Chi compra scrive al venditore nella chat, dove trova già pronta la bozza di un messaggio sull’annuncio. Un annuncio si può segnare come prenotato o come venduto, rinnovare e segnalare, e scade dopo un periodo compreso tra 30 e 90 giorni. Un mount può richiedere che i venditori siano prima stati attivi in un feed o siano stati approvati da un moderatore. | Trading Post |
| `feed` | **Un feed per la comunità.** Le persone pubblicano voci con foto e hashtag, e gli altri possono mettere mi piace e commentare. Una voce può essere destinata a tutto lo spazio, ai tuoi amici, a una cerchia (un gruppo di tuoi amici) o soltanto a te. Un diario è una serie di voci con una copertina. Le voci si possono contrassegnare come 18+ o come pubblicità. | Outpost |
| `chat` | **Messaggi.** Mandi messaggi privati e file agli amici (NIP-17). I gruppi esistono finché chi li ospita non li chiude, mentre le stanze dal vivo spariscono quando esce l’ultima persona. La chat ha risposte, reazioni, modifica dei messaggi, messaggi fissati, ricerca sul dispositivo e messaggi effimeri. Le chiamate vocali e le videochiamate funzionano fino a sei persone. | Uplink |
| `notices` | **Una bacheca** per note pubbliche. Ogni nota è firmata dal suo autore e richiede una proof of work, cioè un piccolo calcolo che rende costoso pubblicare in massa. Le note si possono votare e segnalare, e hanno una scadenza. | DevBoard |
| `boards` | **Liste condivise e note.** Sono liste di cose da spuntare, inventari con le quantità e note in Markdown. Sono cifrate end-to-end, e le condividi con link che consentono la modifica oppure la sola lettura. | Loadout |
| `payload` | **Condivisione di file** in tre modi: con un link a file conservati cifrati sui tuoi server multimediali, con l’invio di file ad amici e gruppi, oppure direttamente da un browser all’altro. | Payload |
| `vault` | **Un gestore di password** per accessi, note, carte e codici a due fattori. Ha un generatore di password e un rapporto sulla salute. Gestisce anche chiavi SSH, una CA SSH, una CA X.509 e certificati TLS. È cifrato con una frase segreta tutta sua. | Vault |
| `authenticator` | **Codici a due fattori** (TOTP). Sono conservati nella stessa cassaforte cifrata che contiene le voci del gestore di password. | Authenticator |
| `calendar` | **I tuoi calendari**, presi da Nextcloud o da qualsiasi altro server CalDAV. Ai relay non viene inviato nulla. | Calendar |
| `pong` | **Pong per due giocatori**, tra due browser. | pongjs |

Ogni hub ha inoltre una pagina iniziale, una pagina dell’account e una pagina
delle impostazioni. Dalle impostazioni gestisci account e dispositivi, amici e
cerchie, persone bloccate, relay, spazi, server multimediali e backup. Le
notifiche non sono un’app a parte: fanno parte dell’hub stesso.

## Spazi e mount { #spaces-and-mounts }

- Uno **spazio** è una comunità con un nome e un proprietario. Ha un
  identificativo, la chiave del proprietario, un nome, dei moderatori, i suoi
  relay e un indicatore che lo segnala come riservato agli adulti. Riprende il
  modello delle comunità moderate di nostr (NIP-72), quindi anche altri client
  nostr possono leggerlo. Ogni post e ogni annuncio appartiene a un solo spazio.
- Un **mount** è un’app usata per uno spazio, con un identificativo, un nome e
  un’icona tutti suoi. Per aggiungere al tuo hub il negozio di un’altra comunità
  ti basta una riga, quella che definisce il mount.
- **Un link indica l’app, lo spazio e l’elemento, ma mai l’host.** Un hub apre
  un link del genere con il proprio mount di quell’app e di quello spazio. Se
  non ne ha uno, ti dice a chi appartiene lo spazio e ti propone un modo per
  tornare indietro.
- **Gli spazi sono federati**, cioè uno spazio non è legato a un solo hub. Due
  hub possono offrire lo stesso spazio. Sui relay di uno spazio passano soltanto
  i contenuti di quello spazio.

Tre cose sono previste e non ancora realizzate. Gli hub si annunceranno con un
manifest firmato, in modo che gli altri possano trovarli. Tra gli strumenti di
moderazione arriveranno le approvazioni. E si potrà seguire uno spazio anche se
il proprio hub non lo include.

## Scrivere un’app { #writing-an-app }

Questo comando crea lo scheletro di una nuova app nella tua distribuzione:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Ne risulta un’app React che usa il kit di interfaccia del framework. Contiene
una shell (la cornice attorno alle pagine dell’app), una pagina iniziale e una
pagina delle impostazioni, i testi in tutte le lingue, una voce nel registro
delle app e un mount. Le app usano soltanto l’API pubblica del framework e non
accedono mai direttamente all’archivio dei dati o alle chiavi.
[Gestire il proprio hub](hubs.md) spiega come compilare e pubblicare un hub.
