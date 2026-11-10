# Armory

**Strumenti web peer-to-peer, armati di nostr.** Ogni strumento gira interamente nel tuo
browser e si sincronizza attraverso i relay che scegli tu. Nessuna registrazione, nessun server
nostro, nessun tracciamento, e tutto viene cifrato prima di lasciare il tuo dispositivo.
Installalo come web app dalla pagina iniziale.

- **Aprilo:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repository: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Una distribuzione di [kiwi-framework](index.md) 0.32.1 (fissato per commit). Non
  ci sono ancora tag di release.
- In inglese, tedesco, francese, spagnolo, italiano, olandese, polacco e portoghese.

Prima Armory si chiamava weaponized.js.

## Gli strumenti { #the-tools }

| Strumento | Cosa fa |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Liste della spesa e cose da fare condivise, inventari di casa e note in Markdown tra i tuoi dispositivi e con chi vuoi. Cifrati end-to-end, con link di modifica o di sola lettura. Funziona offline, e i tuoi dispositivi ripristinano ciò che i relay dimenticano. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Messaggi e file agli amici (NIP-17, sigillati sul tuo dispositivo), gruppi che restano finché chi li ospita non li chiude, e stanze dal vivo in cui entra chiunque abbia il link, che spariscono quando si svuotano. Risposte, reazioni, modifiche, messaggi fissati, ricerca sul dispositivo, messaggi effimeri, e chiamate vocali e video fino a sei persone. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Condivisione di file: un link che aspetta cifrato sui tuoi server multimediali finché non lo elimini; file ad amici e gruppi in Uplink; o direttamente dal tuo browser al loro, senza salvarli da nessuna parte. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Un gestore di password: accessi, note, carte e codici a due fattori su ogni dispositivo dove accedi. Un generatore, un rapporto sulla salute (password deboli, riutilizzate, vecchie e, se lo attivi, compromesse), importazione ed esportazione, chiavi SSH, un'autorità di certificazione SSH, una CA X.509 e certificati TLS. Sigillato da una frase segreta propria. Niente compilazione automatica. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Codici a due fattori (TOTP) per i tuoi account altrove: aggiungine uno da un codice QR, un link o un segreto, o da un'esportazione di Google Authenticator. Conservati nello stesso vault sigillato. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | I tuoi calendari dal tuo Nextcloud o da qualsiasi server CalDAV: i prossimi giorni o un mese, eventi che si ripetono, promemoria mentre una pagina è aperta. Nulla va ai relay; l'accesso è sigillato nel tuo account. Il tuo server deve consentire l'origine di Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Report e diari di coltivazione: voci con foto, settimana dopo settimana, per tutti in Outpost, i tuoi amici, una cerchia o solo te. Hashtag, mi piace e commenti. Sigillati sul tuo dispositivo, foto cifrate. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Un mercato della canapa: semi, talee e attrezzatura con foto, trovati per categoria e per dove spediscono. "Message seller" apre Uplink. Per chi ha un account (nessun controllo dell'età). I venditori devono prima farsi vedere in Outpost (tre post, ciascuno con il mi piace di tre persone) o essere approvati da un moderatore. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Una bacheca per freelance: scrivi che cerchi persone o che sei disponibile, firmato con la tua chiave, sostenuto da proof of work, votato, sparisce alla scadenza (da 24 ore a 30 giorni). Pubblico per scelta progettuale. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Pong retrò per due giocatori tra due browser. Condividi un link o un codice QR, oppure scegli una partita aperta, o allenati offline contro il computer. |

È previsto un blog.

Ogni strumento è una delle app del framework, montata con il nome che le dà Armory: Loadout
è `boards`, Uplink `chat`, Outpost `feed`, Trading Post `market`, DevBoard
`notices`, pongjs `pong`.

## Un account, ogni strumento { #one-account-every-tool }

Accedi o crea un account nella pagina iniziale (nome utente e password, oppure una
chiave nostr) e ogni strumento lo usa. Le liste che hai creato su un dispositivo prima di accedere
vengono portate con te. Senza un account, ogni dispositivo usa una chiave propria.

La pagina delle impostazioni copre tutto l'hub: il tuo account e i tuoi dispositivi, amici e
cerchie, persone bloccate, relay, spazi e server multimediali, notifiche e
backup cifrati.

## Relay e server multimediali { #relays-and-media-servers }

I relay predefiniti di Armory sono `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` e `wss://relay.primal.net`. I suoi server multimediali (Blossom) predefiniti
sono `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (solo
foto) e `blossom.primal.net`. Puoi scegliere i tuoi nelle impostazioni.

I relay passano i dati, ma non possono leggere ciò che è stato cifrato prima. Il
[modello di privacy](index.md#privacy-model) elenca cosa possono vedere.

## Moderazione { #moderation }

I moderatori di Armory moderano Outpost, Trading Post e DevBoard. Le voci di Outpost
possono essere segnate come 18+ o come pubblicità da chi le ha scritte, da due segnalazioni o da un
moderatore. Queste voci vengono mostrate solo a chi ha un account.

## La tua Armory { #your-own-armory }

Armory è il template per il tuo hub. Fanne un fork (o usalo come template),
cambia `distribution.js` e le traduzioni, e pubblicalo. Vedi
[Gestire un proprio hub](hubs.md).
