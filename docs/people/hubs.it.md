# Gestire un proprio hub

Un hub è fatto di file statici, quindi ospitarne uno significa servire una cartella via HTTPS. Ci sono
tre modi per gestirne uno:

- **Usare Armory così com'è:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Creare una tua distribuzione:** il tuo nome, i tuoi relay e le tue app, su qualsiasi host statico.
- **Eseguire il container dell'hub:** per esempio dentro la tua Kiwi Network, con il tuo
  relay, come hub privato che solo la mesh può raggiungere.

## Tipi di hub { #kinds-of-hub }

| Tipo | Come | Esempio |
|---|---|---|
| **Pubblico** | Relay pubblici; chiunque può aprirlo | Armory |
| **Privato** | I relay dell'hub sono bloccati (`policy.relays: 'locked'`) e le pagine aspettano finché uno di essi non risponde (`requireHub`), con i relay dentro una VPN | l'hub di un'azienda sul suo kiwi-master |
| **Semi-pubblico** | Un hub privato con un'area pubblica per alcune app scelte (la chat, per esempio) su relay pubblici | |

Ogni evento appartiene a una sola rete (quella dell'hub, l'area pubblica o quella di
uno spazio) e non passa mai in un'altra.

## La tua distribuzione { #your-own-distribution }

Armory è il template (su GitHub, *Use this template* ti dà una copia senza
la sua cronologia):

1. Modifica **`distribution.js`**: id, nome, marchio, descrizione, homepage, repository,
   relay, server multimediali, spazi, app e mount. Per servire anche gli spazi di Armory,
   copia i loro `owner` e `id` dall'`hub.json` di Armory.
2. Modifica **`locales/*.json`**: il titolo, il testo introduttivo e il piè di pagina, e un testo di scheda per ogni
   mount. L'inglese è la lingua di riserva.
3. Aggiorna **`kiwi.manifest`** e, se vuoi, aggiungi il tuo hub a
   [kiwi-web-catalog](#kiwi-web-catalog).
4. Su GitHub: *Settings → Pages → Source: GitHub Actions*, poi fai push.

```bash
npm install
npm run dev                  # hub con ricaricamento a caldo, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # un relay di test locale su ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # crea lo scheletro di una nuova app
```

Fissa kiwi-framework per commit o tag, mai per branch. La build controlla il tuo
`distribution.js` (per esempio, un mount pubblico ha bisogno di relay pubblici e
viceversa).

Lo stack è TypeScript, React 19 e Vite per tutto ciò che si vede. Il livello dei dati
in `shared/` è JavaScript semplice con tipi JSDoc. I test girano nel test runner di node
e, per il browser, in Playwright.

## Il container dell'hub { #the-hub-container }

Armory è anche un'immagine container, `ghcr.io/derlocke-ng/armory`, costruita dal
`container/Dockerfile` del framework (nginx). All'avvio, il suo entrypoint scrive
`hub.local.json` dalle variabili `HUB_*`, e la pagina lo legge prima di
connettersi. Un deployment può scegliere così relay e policy, ma non può aggiungere
codice. Senza variabili impostate, l'hub gira così come è stato costruito.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variabile | Significato |
|---|---|
| `HUB_RELAYS` | i relay dell'hub |
| `HUB_PUBLIC_RELAYS` | i relay dell'area pubblica (impostata e vuota: nessuna area pubblica) |
| `HUB_DIRECTORY_RELAYS` | dove vengono pubblicati e cercati gli elenchi di relay |
| `HUB_RELAYS_LOCKED` | `true`: le persone non possono sostituire i relay dell'hub |
| `HUB_REQUIRE_HUB` | `true`: le pagine aspettano finché nessuno dei relay dell'hub risponde |
| `HUB_PUBLIC_MOUNTS` | mount sull'area pubblica, per id |
| `HUB_ACCOUNT_MOUNTS` | mount che richiedono un account |
| `HUB_REQUIRE_ACCOUNT` | `true`: ogni mount richiede un account |
| `HUB_SPACE_RELAYS` | relay per spazio: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | chiavi che moderano ogni spazio definito dall'hub |
| `HUB_REGISTER_POW` | bit di proof of work per un nuovo account (relay riservati ai membri) |
| `HUB_CALDAV` | un Nextcloud; nginx gli inoltra `/remote.php/dav/`, così il calendario non ha bisogno di CORS |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | server STUN/TURN per chiamate e trasferimenti diretti. Il login TURN è visibile nella pagina, quindi dagli un login solo per questo hub |

`HUB_USER_MOUNTS` viene letta ma per ora non fa nulla: seguire uno spazio che l'hub non
include deve ancora arrivare.

L'hub deve essere servito via HTTPS (WebCrypto richiede un contesto sicuro) e i suoi
relay via `wss://`. Su `http://` semplice (tranne localhost) la pagina lo
dice e si ferma.

### Su una Kiwi Network { #on-a-kiwi-network }

Un kiwi-master può ospitare un proprio relay e un proprio hub: il modulo `nostr-relay` (strfry
su `relay.<host>`) e il modulo `hub` (questa immagine, Armory di default, su
`hub.<host>`). Di default sono privati: raggiungibili solo dalla mesh, con
il certificato della fleet. Un hub semi-pubblico aggiunge `public_relays` e
`public_mounts`. Uno pubblico aggiunge `reverse-proxy.public`, che ottiene certificati Let's
Encrypt. Il relay accetta allora post dalla mesh e, da
Internet, solo dai membri che dimostrano la loro chiave (NIP-42): quelli nell'elenco firmato
dagli amministratori (`write_pubkeys`) oppure, con `members: registered`, chiunque abbia un
account sull'hub. Vedi il [riferimento dei moduli](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
elenca gli hub, le loro app e il framework, con la stessa forma del catalogo
per il desktop: un `apps.list` con un URL git per riga (`path=` per un'app dentro il
repository di un hub, `ref=` per fissare una versione), e un `kiwi.manifest` in ogni voce con una
`CATEGORY` tra `Framework`, `Hub` e `App`.

Oggi elenca kiwi-framework, Armory e le dieci app di Armory. **Non** è pensato per
`kiwi catalog add`: queste voci non hanno un installer, e per ora nulla legge il
catalogo in automatico. I file del catalogo sono di pubblico dominio (CC0, secondo il suo README).

Per aggiungere il tuo hub: fai un fork, aggiungi una riga, assicurati che il repository contenga un
`kiwi.manifest` e apri una pull request.

## Non ancora realizzato { #not-built-yet }

Questi punti vengono dalla roadmap del framework:

- Il blog.
- Le approvazioni di moderazione (NIP-72 kind 4550).
- Seguire spazi che un hub non include.
- Firmatari NIP-07 e NIP-46.
- Un server TURN nello stack kiwi. È in attesa in kiwi-modules; senza TURN,
  due telefoni con dati mobili spesso non trovano un percorso diretto.
