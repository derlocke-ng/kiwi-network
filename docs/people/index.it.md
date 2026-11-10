# Hub, non piattaforme

La rete collega le tue macchine. Gli **hub** collegano le persone. Un hub è un insieme di
app web (un mercato aperto, un feed, una chat, la condivisione di file, liste condivise, un
gestore di password, un calendario) che girano interamente nel browser e si sincronizzano attraverso
i relay [nostr](https://nostr.com) scelti dalla comunità. Non c'è un server degli
account né un backend nel mezzo, e tutto ciò che è privato viene cifrato sul
dispositivo prima di uscirne. Chiunque può gestire un hub per qualsiasi comunità. Vedi
[le app del framework](apps.md).

Tre repository compongono il tutto:

| Repository | Cos'è |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Il motore: identità e account, relay e sincronizzazione, persone e condivisione, moderazione, il kit di design, le pagine dell'hub e dieci app. Da solo non fornisce nulla che un utente apra. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | La prima **distribuzione**: un hub costruito con il framework, con un nome, relay predefiniti e tutte e dieci le app montate con nomi propri. Il template da cui fare un fork per la tua. GPL-3.0-or-later. **Online:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Un catalogo git di hub e delle loro app, con la stessa forma del [kiwi-catalog](../desktop/catalogs.md) per il desktop |

## Come si incastra tutto { #how-it-fits-together }

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

## Le parole { #the-words }

- **Hub**: ciò che una distribuzione produce. File statici, quindi ospitarne uno significa
  servire una cartella. Ogni hub ha una pagina iniziale, le impostazioni e una pagina dell'account.
- **Distribuzione**: un hub costruito sul framework, con un nome e un aspetto,
  relay predefiniti e un insieme scelto di app su spazi scelti. Tutto ciò che un fork
  cambia sta in un solo file, `distribution.js`, più le sue traduzioni.
- **App**: una cartella con un manifest che si inserisce in qualsiasi distribuzione. Le app
  parlano solo con l'API pubblica del framework e non toccano mai direttamente lo storage o le chiavi.
- **Spazio** (space): una comunità con un nome e un proprietario, con i propri moderatori e, se vuole,
  i propri relay (sul modello delle comunità moderate NIP-72). Un altro hub può
  servire lo stesso spazio indicandone l'indirizzo.
- **Mount**: il codice di un'app su uno spazio, con nome, percorso e icona propri. Un'app può
  essere montata molte volte. Il *Trading Post* di Armory è l'app `market` del framework
  montata sullo spazio `tradingpost` di Armory.

Due persone su distribuzioni diverse sono amiche, condividono e chattano esattamente come
se fossero sulla stessa, perché l'identità e i dati sono eventi nostr, non appartengono all'hub.

## Account e chiavi { #accounts-and-keys }

- Ogni dispositivo riceve una chiave alla prima visita, conservata nel browser.
- Un **account** è un nome utente e una password, costruito su semplici eventi nostr
  senza alcun registro: la password viene rafforzata con scrypt e sblocca la tua
  chiave. Nessuno può prendere o sovrascrivere un account senza la password. **Non
  c'è modo di reimpostare la password**.
- Puoi anche accedere con una chiave nostr esistente (`nsec`, hex o `ncryptsec`).
  I firmatari tramite estensione del browser e remoti (NIP-07, NIP-46) sono pianificati, non realizzati.
- Un account funziona in tutte le app dell'hub e su ogni dispositivo dove accedi.

## Modello di privacy { #privacy-model }

**Cosa è cifrato.** I contenuti vengono sigillati nel browser prima di andare
ovunque: AES-256-GCM con chiavi derivate tramite HKDF. I messaggi privati sono messaggi NIP-17
in gift wrap NIP-59. Ogni file riceve una chiave AES-256-GCM casuale prima
di andare su un server multimediale, e le foto vengono ricodificate, il che elimina i metadati
della fotocamera. Il Vault è sigillato con una frase segreta propria (scrypt + AES-256-GCM).
Le chiamate vanno da browser a browser, cifrate da WebRTC.

**Prima in locale.** Ogni scrittura va prima nel database del browser, poi
ai relay. Le letture arrivano dal dispositivo, quindi le app funzionano offline. Quando un dispositivo
si riconnette ripristina ciò che un relay ha dimenticato: i dati vanno persi solo se ogni dispositivo
che li conteneva è sparito *e* non c'è alcun backup.

**Cosa possono vedere gli altri.** I repository sono espliciti sui limiti:

- I relay vedono i metadati: chi scrive a quali indirizzi, quando, quanto e da
  quale indirizzo IP. Usa una VPN o Tor se ti importa.
- La chiave di uno spazio non è un segreto. Tiene i post di una comunità lontani dalla vista diretta.
  I mi piace, le segnalazioni e chi ha commentato cosa sono visibili ai relay.
- Le note di DevBoard e le segnalazioni di moderazione sono pubbliche per scelta progettuale.
- La tua chiave si trova nello storage del browser. Tutti i siti GitHub Pages di un account
  condividono la stessa origine, quindi un hub sul proprio (sotto)dominio è la configurazione più robusta.
- I trasferimenti diretti e le chiamate rivelano gli indirizzi IP dei due browser l'uno all'altro
  e ai server STUN (di default quelli di Google e di Cloudflare; un hub può impostare
  i propri).
- "Nessun server nostro" significa nessuno nel percorso critico. Le app usano comunque i
  relay, i server multimediali e, per il calendario, il server CalDAV che scegli tu o
  il tuo hub.

## Moderazione { #moderation }

Tre livelli: la tua lista di blocco (cifrata, solo tu puoi leggerla), le segnalazioni
(pubbliche, firmate) e la policy dei relay stessi. Uno spazio ha dei moderatori. La
segnalazione di un moderatore comprime subito un post. Altrimenti servono tre segnalazioni da
persone non bloccate. I post possono essere segnati come 18+ o come pubblicità, e
questi vengono mostrati solo a chi ha un account.

## Continua a leggere { #read-on }

- [Armory e le sue app](armory.md)
- [Gestire un proprio hub](hubs.md)
- L'[architettura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  e il [protocollo](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md) del framework
