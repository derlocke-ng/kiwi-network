# kiwi-proxy

Uscite SOCKS5 e VPN sigillate in Podman rootless, per browser, strumenti di test,
applicazioni dell'host e macchine kiwi-server.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Ultima release: **v0.7.3**. È nel [catalogo Kiwi](../desktop/catalogs.md), ambito utente.
- Una CLI (`kiwi-proxy`), un'app GTK4 (**Kiwi Proxy**) e unità utente systemd. È
  il motore proxy che prima viveva in kiwi-fox, separato perché serva più
  di un'app.

Un'**uscita** (exit) è un upstream con un nome: un SOCKS5 che ti è stato fornito, o uno prodotto da un
[modulo provider](providers.md) (Tor, un tunnel VPN, 9proxy,
Mysterium). Un'uscita è solo un insieme di dati. Avviarla crea un **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Qualsiasi cosa si agganci al namespace del gateway (un browser kiwi-fox, una box
kiwi-custodia, un container di strumenti) non ha altra route che quell'upstream. Se il gateway muore, i suoi
membri perdono la route.

## Installazione { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox e kiwi-custodia lo portano con sé
kiwi-proxy setup             # immagine del gateway, dati DNS, immagini dei moduli provider
```

Richiede Podman rootless, Python 3.12+ con pydantic, e GTK4 + libadwaita per
l'app. Le password vanno nel portachiavi del desktop (`secret-tool`), oppure in file 0600
su una macchina che non ne ha uno.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # nuova uscita; per ora non parte nulla
kiwi-proxy add tor-de --module tor --country de        # nuova uscita da un modulo provider
kiwi-proxy list
kiwi-proxy check client-a      # cosa vede il mondo attraverso di essa
kiwi-proxy up client-a         # avvia il suo gateway e lo tiene attivo
kiwi-proxy down client-a       # lo smonta, insieme a chi vi si era agganciato
kiwi-proxy ps                  # i gateway attivi, qualunque app li abbia avviati
kiwi-proxy reap                # smonta i gateway che nessuno usa
kiwi-proxy-gui                 # "Kiwi Proxy" in the app grid
```

Gli endpoint sono `socks5://user:pass@host:port`, `http://…`, `https://…`, oppure il
formato dei fornitori `host:port:user:pass`. `kiwi-proxy test ENDPOINT` ne sonda uno
senza creare nulla.

### Uscite per le applicazioni dell'host { #exits-for-host-applications }

Qualsiasi programma sull'host può usare un'uscita tramite una porta SOCKS5 pubblicata, una
porta per uscita:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Di default la porta ascolta su `127.0.0.1`. Un altro indirizzo richiede un nome utente
(`--expose-user`) oppure un `--expose-open` esplicito.
`systemctl --user enable --now kiwi-proxy@NAME` tiene attiva un'uscita dal login.

### DNS { #dns }

- **Modalità resolver** (il default): dnscrypt-proxy risolve via DoH attraverso
  l'uscita (con Google, Cloudflare, Quad9 o Mullvad come upstream), con blocklist
  (OISD) aggiornate ogni giorno.
- **Modalità remota** (`--dns remote`): i nomi vanno all'upstream stesso, per Tor e
  i nomi `.onion`. Le blocklist si applicano comunque.

### Regole del gateway { #rules-of-the-gateway }

- L'UDP non esce da nessuna parte: niente QUIC, niente media WebRTC, niente DNS in chiaro.
- Verso il mondo un'uscita è IPv4. Un nome senza indirizzo IPv4 viene rifiutato.
- Un gateway avviato da un consumer sparisce quando se ne va il suo ultimo membro. Uno avviato
  con `kiwi-proxy up` resta finché non si esegue `kiwi-proxy down`.
- Un'uscita, un gateway, un numero qualsiasi di membri. I membri che devono restare separati
  usano uscite diverse.

## L'app { #the-app }

**Kiwi Proxy** aggiunge e modifica le uscite (un SOCKS5 che ti è stato fornito, o un modulo
provider, con un elenco di paesi in cui cercare o un selettore di nodi), le avvia e le
ferma, ne offre una come porta SOCKS5 su questo computer e ne copia l'indirizzo,
controlla cosa vede il mondo, mostra chi si è agganciato a un gateway e i relativi log, e
installa e configura i moduli provider.

## Su una macchina kiwi-server { #on-a-kiwi-server-machine }

kiwi-proxy contiene anche un modulo kiwi-server che ospita uscite per l'intera mesh
(un gateway per uscita, pubblicato sull'indirizzo mesh dell'host). Non è ancora
nell'albero di kiwi-server e non è mai stato eseguito su una macchina, come dice la sua documentazione.
I moduli provider sono un meccanismo per il desktop e lì non girano.

Per approfondire: [architettura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumer](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[sistema di plugin](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
