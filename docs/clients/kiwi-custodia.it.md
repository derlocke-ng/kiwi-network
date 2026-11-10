# kiwi-custodia

Container di distribuzioni il cui ogni byte esce attraverso un'uscita di
[kiwi-proxy](kiwi-proxy.md). *Pensa a distrobox, con la rete sotto
custodia.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Ultima release: **v0.2.3**. È nel [catalogo Kiwi](../desktop/catalogs.md), ambito utente.
- Una CLI (`kiwi-custodia`) e un'app GTK4 (**Kiwi Custodia**)

Una **box** è una distribuzione Linux in un container Podman rootless, con una home
propria, agganciata al gateway sigillato di un'uscita. Installaci qualsiasi cosa con
il suo gestore di pacchetti, esegui le sue app desktop sul tuo desktop e mettile nella
griglia delle app. La box non ha altra route che l'uscita: non per `dnf`, non per il client
di un gioco, non per un binario statico che non ha mai sentito parlare di `$ALL_PROXY`. Se l'uscita
cade, la box non ha alcuna route.

Questo rende una box per ogni rete di cliente un modo pulito di lavorare: gli strumenti, le
chiavi e la cronologia della shell del cliente A in una box, quelli del cliente B in un'altra, ciascuna
in grado di raggiungere solo il proprio cliente.

## Installazione { #install }

```bash
kiwi install kiwi-custodia   # porta con sé kiwi-proxy; oppure ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

Richiede Podman rootless con `catatonit`, kiwi-proxy, una sessione Wayland,
Python 3.12+ con pydantic, GTK4 + libadwaita per l'app, e `/dev/net/tun`
utilizzabile dai container rootless. Le immagini delle distribuzioni vengono scaricate al primo avvio di una box.
Esegui di nuovo `kiwi-custodia setup` dopo un aggiornamento.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # uscita definita una volta sola, in kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # una box su di essa; il primo avvio installa una base
kiwi-custodia enter work                                   # una shell dentro: sudo dnf install …
kiwi-custodia run work -- firefox                          # un comando dentro la box
kiwi-custodia check work                                   # cosa vede il mondo da dentro
kiwi-custodia apps work                                    # le app desktop che contiene
kiwi-custodia export work firefox                          # "Firefox (work)" in the app grid
kiwi-custodia stop work
kiwi-custodia reset work                                   # riporta la box alla sua immagine di base; la home resta
kiwi-custodia-gui
```

Distribuzioni: `fedora` (il default), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine`, oppure `custom` con `--image`.

## Come è fatta una box { #how-a-box-is-built }

Tre container condividono un namespace di rete: il **gateway** di kiwi-proxy, un
**sidecar del tunnel** (tun2socks su un dispositivo TUN che diventa la route predefinita)
e la **box** stessa. Tutto il traffico esce attraverso il TUN verso il SOCKS5
dell'uscita, quindi sono coperti anche i programmi che ignorano le impostazioni del proxy.

- La box gira con il tuo utente, con lo stesso uid e `sudo` senza password. La sua
  home è `~/.local/share/kiwi-custodia/boxes/<id>/home`, una per box invece
  della tua vera home: due box sono due identità.
- Le modifiche dentro una box vengono conservate in uno snapshot per box quando si ferma, e
  `reset` torna all'immagine di base.
- Wayland, X11 (tramite Xwayland), PipeWire, il session bus e `/dev/dri`
  vengono passati alla box, così le app desktop e i giochi funzionano.
- Il DNS passa per il resolver del gateway (con blocco della pubblicità), oppure per
  l'upstream su un'uscita con DNS remoto.

## Cosa non è { #what-it-is-not }

Una box è **custodia della rete, non una sandbox rispetto al tuo desktop**. Come distrobox,
riceve il tuo display e il tuo session bus, quindi un programma nella box può mostrare finestre,
leggere gli appunti e usare i portali. Quello che non può fare è raggiungere la rete
se non attraverso la sua uscita. L'UDP non ha vie d'uscita (niente QUIC, niente media WebRTC), e
l'IPv6 non ha route.

Le box che non devono condividere un'uscita usano uscite diverse.
