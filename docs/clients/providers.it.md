# Moduli provider

In [kiwi-proxy](kiwi-proxy.md) un exit è una connessione a un upstream, salvata
con un nome, attraverso cui le tue box e i tuoi browser mandano il loro
traffico. Di solito è una connessione che ti è stata fornita, come il proxy
SOCKS5 che porta nella rete di un cliente. Un modulo provider serve per l’altro
caso: è il modulo stesso a creare l’exit, attraverso Tor, un abbonamento VPN, 9proxy o
Mysterium. Tor e Mysterium, in particolare, servono a darti altri indirizzi IP
per i test.

Ogni modulo ha il suo repository. kiwi-updater lo installa nella directory dei
moduli di kiwi-proxy, e da quel momento è kiwi-proxy a gestirlo: costruisce
l’immagine container del modulo, avvia il modulo quando un exit ne ha bisogno e
lo ferma quando nessun gateway lo usa più. Un gateway è il container che
kiwi-proxy esegue per un exit finché l’exit è attivo.

| Modulo | Repository | Release | Exit | Requisiti |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | la rete Tor, con un circuito per ogni exit e un paese di uscita qualsiasi | nessuno (è gratuito) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | un tunnel WireGuard o OpenVPN tramite [gluetun](https://github.com/qdm12/gluetun) | un abbonamento VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | un exit residenziale di [9proxy](https://9proxy.com/) | un account 9proxy e il client proprietario di 9proxy, che non viene ridistribuito |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | la dVPN [Mysterium](https://mysterium.network/) (una VPN decentralizzata), con un elenco di nodi tra cui scegliere per paese e per tipo di IP | un’identità consumer registrata con un saldo in MYST |

Tutti e quattro i moduli hanno licenza GPL-3.0-or-later e sono nel
[catalogo Kiwi](../desktop/catalogs.md). Ognuno dichiara `DEPENDS=kiwi-proxy`,
quindi kiwi-updater installa prima kiwi-proxy. Tor e Mysterium sono il modo più
rapido per ottenere altri indirizzi IP di uscita, per esempio per i test.

## Installazione e uso { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # costruisce la sua immagine (kiwi-proxy setup le fa tutte)
kiwi-proxy module list
kiwi-proxy module countries tor                  # da quali paesi Tor può uscire
kiwi-proxy add tor-de --module tor --country de  # un exit creato dal modulo
kiwi-custodia new test --exit tor-de             # una box che lo usa, oppure:
kiwi-fox new test --exit tor-de                  # un profilo del browser che lo usa
```

Per un exit Tor il paese viene imposto con l’opzione `StrictNodes` di Tor. Un
circuito che non può uscire in quel paese fallisce, e non esce mai in un altro
paese. Gli exit del modulo tor inoltrano le credenziali SOCKS che Tor Browser
invia per ogni sito. È la loro impostazione predefinita
(`--socks-auth passthrough`).

## Come un provider si collega a un gateway { #how-it-is-wired }

**Ogni provider offre SOCKS5 e nient’altro.** Un container provider ha bisogno
di una propria connessione a Internet. Non può quindi girare nel namespace di
rete di un gateway, perché lì viene scartato tutto il traffico tranne quello
verso un’unica destinazione. Provider e gateway sono invece collegati da una
rete bridge di Podman rootless, `kf-providers`, su cui ogni modulo ha un
indirizzo fisso:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** offre SOCKS5 da sé. kiwi-proxy invia credenziali diverse per ogni
  exit, e l’opzione `IsolateSOCKSAuth` di Tor dà così a ogni exit il suo
  circuito, cioè un suo percorso attraverso la rete Tor.
- **VPN e Mysterium** usano un tunnel, e un tunnel non offre SOCKS5. Per questo
  un piccolo adattatore, microsocks, entra nel namespace di rete del tunnel:
  offre SOCKS5 e manda il traffico attraverso il tunnel.
- **9proxy** esegue il client di 9proxy, che apre una porta SOCKS5 verso un exit
  residenziale.

Un solo container provider serve tutti gli exit che usano lo stesso modulo e lo
stesso lease. Un lease è uno degli exit selezionabili che un modulo offre, per
esempio il paese di un server VPN o un nodo Mysterium. Se un tunnel perde la
sessione, si comporta in modo fail-closed, cioè non lascia uscire alcun
traffico, e viene riavviato.

## Configurazione { #configuration }

Lo stato di ogni modulo è salvato in
`~/.local/share/kiwi-proxy/modules-state/<module>/`, al di fuori di qualsiasi
repository:

- **vpn**: il file `vpn.json` contiene le impostazioni di gluetun, come
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` e `WIREGUARD_ADDRESSES`. Ogni chiave
  scritta in maiuscolo viene passata a gluetun senza modifiche. Il file può
  contenere anche un elenco `leases`. Una directory `gluetun/` facoltativa
  contiene altri file, per esempio un `wireguard.conf` per il provider `custom`
  di gluetun. Esiste una sola configurazione di questo tipo per macchina, e i
  suoi exit si distinguono per il paese del server.
- **9proxy**: il file di configurazione è `config/account.conf`. Il client
  proprietario non è incluso. Prima di eseguire
  `kiwi-proxy module setup 9proxy`, metti il client nella directory
  `module/containers/vendor/` del plugin e aggiungi `COPY vendor/ /opt/9proxy/`
  al `Containerfile` del plugin. Senza il client l’immagine viene costruita lo
  stesso, ma il provider si rifiuta di partire e non apre alcuna porta.
- **mysterium**: esegui `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, oppure usa *Configure…* nell’app Kiwi Proxy. La passphrase
  viene conservata come secret di Podman. Un’identità può avere una sola
  connessione alla volta.

## Stato { #status }

Tor non richiede alcun account. Il modulo Mysterium è stato testato
end-to-end il 7 novembre 2026. Secondo i rispettivi README, i moduli VPN e
9proxy sono completi e hanno i loro unit test, ma non sono ancora stati testati
end-to-end con un abbonamento o un account reale.
