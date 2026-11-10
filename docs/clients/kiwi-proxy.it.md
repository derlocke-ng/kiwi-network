# kiwi-proxy

kiwi-proxy è pensato per chi lavora nelle reti di molti clienti e raggiunge
ciascuna attraverso una propria connessione VPN o SOCKS. Ogni connessione la
salvi come **exit** con un nome, e la attivi soltanto quando ti serve. Ogni exit
è tenuto separato dagli altri, e un programma che usa un exit può raggiungere la
rete soltanto attraverso di esso. Dieci clienti non significano quindi dieci
connessioni VPN attive contemporaneamente sull’host. Un exit possono usarlo i
browser, gli strumenti di test, i programmi sull’host e le macchine gestite con
kiwi-server. kiwi-proxy gira in Podman rootless, cioè in container eseguiti con
il tuo utente, senza permessi di root.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Ultima release: **v0.7.3**. È nel [catalogo Kiwi](../desktop/catalogs.md), ambito utente.
- È composto da uno strumento da riga di comando (`kiwi-proxy`), da un’app GTK4
  (**Kiwi Proxy**) e da unità utente di systemd. È il motore proxy che prima
  faceva parte di kiwi-fox. È diventato un progetto a sé perché possano usarlo
  più app.

Un **exit** è una connessione a un upstream, con un nome. L’upstream è il proxy
a cui viene inviato il traffico: un proxy SOCKS5 che ti è stato fornito, oppure
uno che un [modulo provider](providers.md) crea per te attraverso Tor, un tunnel
VPN, 9proxy o Mysterium. Di per sé un exit è soltanto una voce salvata, e non fa
girare nulla. Quando attivi un exit, kiwi-proxy avvia per lui un container
**gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Il gateway ha un proprio namespace di rete, cioè uno stack di rete separato con
rotte e regole del firewall proprie. Un browser di kiwi-fox, una box di
kiwi-custodia o un container con degli strumenti entra in questo namespace e
diventa un membro del gateway. Da quel momento la sua unica rotta porta
all’upstream dell’exit. Se il gateway si ferma, i suoi membri restano senza
rotta. È questo il comportamento fail-closed: un guasto interrompe la
connessione e non apre mai un’altra strada.

## Installazione { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox e kiwi-custodia lo portano con sé
kiwi-proxy setup             # l’immagine del gateway, i dati DNS, le immagini dei moduli provider
```

kiwi-proxy richiede Podman rootless e Python 3.12+ con pydantic. L’app richiede
anche GTK4 e libadwaita. Le password vengono conservate nel portachiavi del
desktop tramite `secret-tool`. Su una macchina senza portachiavi vengono salvate
in file con permessi 0600, che può leggere soltanto il tuo utente.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # un exit; per ora non gira nulla
kiwi-proxy add tor-de --module tor --country de        # un exit da un modulo provider
kiwi-proxy list
kiwi-proxy check client-a      # che cosa vede il resto del mondo attraverso di lui
kiwi-proxy up client-a         # attiva il suo gateway e lo tiene attivo
kiwi-proxy down client-a       # lo spegne, insieme a chi lo stava usando
kiwi-proxy ps                  # i gateway in esecuzione, qualunque app li abbia avviati
kiwi-proxy reap                # spegne i gateway che nessuno usa
kiwi-proxy-gui                 # "Kiwi Proxy" nella griglia delle applicazioni
```

Un endpoint è l’indirizzo di un upstream. Puoi scriverlo come
`socks5://user:pass@host:port`, `http://…` o `https://…`, oppure nel formato dei
fornitori `host:port:user:pass`. `kiwi-proxy test ENDPOINT` prova un endpoint
senza creare un exit.

### Exit per le applicazioni dell’host { #exits-for-host-applications }

Un programma sull’host non deve per forza girare in un container per usare un
exit. kiwi-proxy può pubblicare un exit come porta SOCKS5 sull’host, con una
porta per ogni exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Per impostazione predefinita la porta è in ascolto soltanto su `127.0.0.1`. Se
la metti in ascolto su un altro indirizzo, devi impostare un nome utente con
`--expose-user` oppure consentire esplicitamente l’accesso libero con
`--expose-open`. Per avere un exit attivo fin dal login, esegui
`systemctl --user enable --now kiwi-proxy@NAME`.

### DNS { #dns }

- **La modalità resolver** è quella predefinita. dnscrypt-proxy risolve i nomi
  con DNS over HTTPS (DoH) e manda queste query attraverso l’exit. Il resolver
  DoH può essere Google, Cloudflare, Quad9 o Mullvad. Vengono applicate liste di
  blocco (OISD), aggiornate ogni giorno.
- **La modalità remota** (`--dns remote`) passa i nomi all’upstream, che li
  risolve da sé. È pensata per Tor e per i nomi `.onion`. Anche in questa
  modalità valgono le liste di blocco.

### Le regole del gateway { #rules-of-the-gateway }

- UDP non viene inoltrato: niente QUIC, niente flussi multimediali di WebRTC e
  niente DNS in chiaro.
- Un exit raggiunge il mondo esterno soltanto via IPv4. Un nome che non ha un
  indirizzo IPv4 viene rifiutato.
- Un gateway avviato da un’altra app, come kiwi-fox o kiwi-custodia, viene
  rimosso quando se ne va il suo ultimo membro. Un gateway che hai avviato tu
  con `kiwi-proxy up` resta attivo finché non esegui `kiwi-proxy down`.
- Ogni exit ha esattamente un gateway, a cui può collegarsi un numero qualsiasi
  di membri. I membri che devono restare separati tra loro usano exit diversi.

## L’app { #the-app }

Nell’app **Kiwi Proxy** puoi aggiungere e modificare gli exit, a partire da un
proxy SOCKS5 che ti è stato fornito oppure da un modulo provider. Per un exit di
un modulo scegli da un elenco di paesi in cui puoi cercare, oppure da un elenco
di nodi. Puoi attivare e spegnere gli exit, offrire un exit come porta SOCKS5 su
questo computer e copiarne l’indirizzo, e controllare che cosa vede il mondo
esterno quando ti colleghi attraverso di lui. L’app mostra anche quali membri
usano un gateway e i loro log, e installa e configura i moduli provider.

## Su una macchina kiwi-server { #on-a-kiwi-server-machine }

Il repository di kiwi-proxy contiene anche un modulo per kiwi-server. Con questo
modulo una macchina gestita con kiwi-server ospita degli exit per tutta la mesh,
cioè per la rete WireGuard privata che collega le tue macchine kiwi-server. Il
modulo esegue un gateway per ogni exit e lo pubblica sull’indirizzo dell’host
nella mesh. Secondo la sua documentazione il modulo non è ancora nel codice
sorgente di kiwi-server e non è mai stato eseguito su una macchina. I moduli
provider funzionano soltanto sul desktop e non girano su una macchina
kiwi-server.

Per approfondire: [architettura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[programmi che lo usano](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[sistema dei plugin](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
