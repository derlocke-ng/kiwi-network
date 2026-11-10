# Moduli dei provider

Un modulo provider dà a [kiwi-proxy](kiwi-proxy.md) un'uscita che produce da sé,
invece di un SOCKS5 che ti è stato fornito. Ognuno vive nel proprio repository,
si installa tramite kiwi-updater nella directory dei moduli di kiwi-proxy, ed è
gestito da kiwi-proxy: costruisce l'immagine del modulo, lo avvia quando un'uscita
ne ha bisogno e lo smonta quando nessun gateway lo usa più.

| Modulo | Repository | Release | Uscita | Richiede |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | la rete Tor, un circuito per uscita, qualsiasi paese d'uscita | niente (gratuito) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | un tunnel WireGuard o OpenVPN tramite [gluetun](https://github.com/qdm12/gluetun) | un abbonamento VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | un'uscita residenziale [9proxy](https://9proxy.com/) | un account 9proxy e il suo client proprietario (non ridistribuito) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | la dVPN [Mysterium](https://mysterium.network/), con un selettore dei nodi per paese e tipo di IP | un'identità consumer registrata con un saldo MYST |

Tutti e quattro sono GPL-3.0-or-later, sono nel [catalogo Kiwi](../desktop/catalogs.md)
e dichiarano `DEPENDS=kiwi-proxy`, così kiwi installa prima kiwi-proxy. Tor e
Mysterium sono il modo rapido per avere più IP d'uscita, per esempio per i test.

## Installazione e uso { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # costruisce la sua immagine (kiwi-proxy setup le fa tutte)
kiwi-proxy module list
kiwi-proxy module countries tor                  # dove Tor può uscire
kiwi-proxy add tor-de --module tor --country de  # nuova uscita dal modulo
kiwi-custodia new test --exit tor-de             # una box su di essa, oppure:
kiwi-fox new test --exit tor-de                  # un profilo del browser su di essa
```

Per Tor, il paese viene mantenuto con `StrictNodes`, quindi il circuito fallisce piuttosto
che uscire altrove. Le uscite sul modulo tor lasciano passare di default le credenziali SOCKS
per sito di Tor Browser (`--socks-auth passthrough`).

## Come è collegato { #how-it-is-wired }

**Ogni provider espone SOCKS5 e nient'altro.** Un container provider ha bisogno
di una propria via d'uscita, quindi non può vivere nel namespace di un gateway, dove tutto
tranne una destinazione viene scartato. I due si incontrano su un bridge Podman rootless,
`kf-providers`, dove ogni modulo riceve un indirizzo fisso:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** parla già SOCKS5. kiwi-proxy invia una credenziale per uscita, e
  `IsolateSOCKSAuth` di Tor dà a ogni uscita il suo circuito.
- **VPN e Mysterium** viaggiano su un tunnel che non parla SOCKS5, quindi un piccolo
  adattatore microsocks si aggancia al namespace di rete del tunnel e offre un SOCKS5 che
  passa nel tunnel.
- **9proxy** esegue il client 9proxy, che apre una porta SOCKS5 su un'uscita
  residenziale.

Un solo container provider serve ogni uscita sullo stesso modulo e sullo stesso lease. Un
tunnel che perde la sessione si chiude in sicurezza (fail closed) e viene riavviato.

## Configurazione { #configuration }

Lo stato di ogni modulo si trova in `~/.local/share/kiwi-proxy/modules-state/<module>/`,
fuori da qualsiasi repository:

- **vpn**: `vpn.json` con le impostazioni di gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; ogni chiave in maiuscolo va a gluetun così
  com'è), una lista `leases` opzionale e una directory `gluetun/` opzionale (per
  esempio un `wireguard.conf` per il provider `custom` di gluetun). È una sola
  configurazione per macchina: le uscite su di essa differiscono per il paese del server.
- **9proxy**: `config/account.conf`. Metti il client proprietario in
  `module/containers/vendor/` del plugin e aggiungi `COPY vendor/ /opt/9proxy/` al suo
  `Containerfile` prima di `kiwi-proxy module setup 9proxy`. Senza di esso l'immagine
  si costruisce, ma il provider si rifiuta di partire invece di aprire una porta.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, oppure *Configure…* nell'app Kiwi Proxy. La passphrase
  diventa un secret di Podman. Un'identità mantiene una sola connessione alla volta.

## Stato { #status }

Tor non richiede un account. Mysterium è stato verificato dall'inizio alla fine il 2026-11-07. I moduli VPN
e 9proxy sono completi e coperti da unit test, ma non sono stati eseguiti dall'inizio alla
fine con un abbonamento o un account reali, come dicono i loro README.
