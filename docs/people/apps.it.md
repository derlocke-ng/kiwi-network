# Le app del framework

kiwi-framework fornisce le sue app con nomi semplici. Una distribuzione le **monta**
su uno spazio e con un nome proprio. Un'app può essere montata molte
volte: una banca dei semi e un negozio di pietre preziose sono lo stesso codice `market` su due spazi,
ciascuno con i propri moderatori e relay, come due riquadri sullo stesso hub.

| App | Cos'è | Armory la monta come |
|---|---|---|
| `market` | **Un mercato aperto** per la comunità servita da un mount. Gli annunci hanno foto, un prezzo, da dove e verso dove spediscono, oppure il ritiro di persona. Chi compra li trova per categoria e in base a dove si trova, tramite etichette di ricerca che i relay possono confrontare ma non leggere. Chi compra scrive al venditore nella chat, con un messaggio sull'annuncio già pronto. Gli annunci possono essere riservati, venduti, rinnovati e segnalati, e scadono dopo 30-90 giorni. Un mount può richiedere che i venditori si siano prima fatti vedere in un feed, o che siano stati approvati da un moderatore | Trading Post |
| `feed` | **Un feed della comunità**: voci con foto, hashtag, mi piace e commenti per lo spazio, per gli amici, per una cerchia o solo per te, più i diari (una serie di voci con una copertina). Le voci possono essere segnate come 18+ o come pubblicità | Outpost |
| `chat` | **Messaggi**: messaggi privati e file agli amici (NIP-17), gruppi che restano finché chi li ospita non li chiude, stanze dal vivo che spariscono quando si svuotano, risposte, reazioni, modifiche, messaggi fissati, ricerca sul dispositivo, messaggi effimeri, e chiamate vocali e video fino a sei persone | Uplink |
| `notices` | **Una bacheca** di note firmate e pubbliche con proof of work, voti, segnalazioni e una scadenza | DevBoard |
| `boards` | **Liste e note condivise**: checklist, inventari con quantità e note in Markdown, cifrate end-to-end, con link di modifica o di sola lettura | Loadout |
| `payload` | **Condivisione di file**: un link che aspetta cifrato sui tuoi server multimediali; file ad amici e gruppi; o direttamente da browser a browser | Payload |
| `vault` | **Un gestore di password**: accessi, note, carte, codici a due fattori, un generatore e un rapporto sulla salute, chiavi SSH, una CA SSH, una CA X.509 e certificati TLS. Sigillato da una frase segreta propria | Vault |
| `authenticator` | **Codici a due fattori** (TOTP), conservati nello stesso vault sigillato | Authenticator |
| `calendar` | **I tuoi calendari** da Nextcloud o da qualsiasi server CalDAV. Nulla va ai relay | Calendar |
| `pong` | **Pong per due giocatori** tra browser | pongjs |

Ogni hub ha anche una pagina iniziale, le impostazioni (il tuo account e i tuoi dispositivi, amici
e cerchie, persone bloccate, relay, spazi, server multimediali, backup) e una
pagina dell'account. Le notifiche stanno nell'hub stesso.

## Spazi e mount { #spaces-and-mounts }

- Uno **spazio** è una comunità con un nome e un proprietario: un id, una chiave del proprietario, un nome,
  i moderatori, i propri relay e un flag per contenuti per adulti. È modellato sulle
  comunità moderate di nostr (NIP-72), quindi altri client nostr possono leggerlo. Ogni
  post e ogni annuncio appartiene esattamente a uno spazio.
- Un **mount** è il codice di un'app su uno spazio, con id, nome e icona propri. Importare
  il negozio di un'altra comunità è una riga di mount.
- **I link indicano l'app, lo spazio e l'elemento, mai l'host.** Un hub apre
  un link con il proprio mount di quell'app e di quello spazio. Se non ne ha uno, dice di chi è
  quello spazio e offre la strada per tornare indietro.
- **Gli spazi sono federati.** Due hub possono servire lo stesso spazio, e i relay di uno spazio
  trasportano solo i suoi contenuti.

Pianificato: hub che si annunciano con un manifest firmato perché altri possano
trovarli, approvazioni di moderazione, e persone che seguono uno spazio che il loro hub non
include.

## Scrivere un'app { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Questo crea lo scheletro di un'app React sul kit UI del framework, con una shell, una pagina home e
una di impostazioni, le stringhe in ogni lingua, una voce nel registro e un mount. Le app
parlano con il framework solo tramite la sua API pubblica e non toccano mai direttamente lo storage o
le chiavi. Vedi [Gestire un proprio hub](hubs.md).
