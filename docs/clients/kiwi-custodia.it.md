# kiwi-custodia

kiwi-custodia ti dà un ambiente Linux separato per ogni rete di un cliente in
cui lavori. Ogni ambiente è un container con una distribuzione Linux a tua
scelta, e tutto il suo traffico di rete passa da un exit di
[kiwi-proxy](kiwi-proxy.md). Un exit è una connessione a un upstream, salvata
con un nome: per esempio il proxy SOCKS5 che porta nella rete di un cliente. In
questo modo puoi lavorare per dieci clienti senza avere dieci connessioni VPN
sull’host, e gli strumenti e le chiavi di ogni cliente restano nell’ambiente di
quel cliente. *Se conosci distrobox: l’idea è la stessa, ma il container può
raggiungere la rete soltanto attraverso il suo exit.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Ultima release: **v0.2.3**. È nel [catalogo Kiwi](../desktop/catalogs.md), ambito utente.
- Ha uno strumento da riga di comando (`kiwi-custodia`) e un’app GTK4 (**Kiwi Custodia**).

Una **box** è una distribuzione Linux in un container Podman rootless, cioè un
container che gira con il tuo utente, senza permessi di root. La box ha una sua
cartella home ed è collegata al container gateway che kiwi-proxy avvia per un
exit: un container la cui unica strada verso l’esterno porta all’upstream
dell’exit. Dentro la box puoi installare qualsiasi cosa con il gestore di
pacchetti della distribuzione. Le sue app grafiche si aprono sul tuo desktop, e
puoi aggiungerle alla griglia delle applicazioni. La box non ha altra rotta che
l’exit, e questo vale per ogni programma al suo interno: per `dnf`, per il
client di un gioco e per un programma compilato staticamente che ignora
`$ALL_PROXY`. Se l’exit si ferma, la box resta del tutto senza rotta.

Per questo conviene lavorare con una box per ogni rete di un cliente. Gli
strumenti, le chiavi e la cronologia della shell del cliente A stanno in una
box, quelli del cliente B in un’altra, e ogni box raggiunge soltanto il proprio
cliente.

## Installazione { #install }

```bash
kiwi install kiwi-custodia   # porta con sé kiwi-proxy; oppure ./install.sh install
kiwi-custodia setup          # l’immagine del tunnel, più l’immagine del gateway e i dati DNS di kiwi-proxy
```

kiwi-custodia richiede Podman rootless con `catatonit`, kiwi-proxy, una sessione
Wayland e Python 3.12+ con pydantic. L’app richiede GTK4 e libadwaita. I
container rootless devono inoltre poter usare `/dev/net/tun`. Le immagini delle
distribuzioni non vengono scaricate durante il setup: un’immagine viene
scaricata la prima volta che si avvia una box che la usa. Dopo un aggiornamento
esegui di nuovo `kiwi-custodia setup`.

## Uso { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # un exit, definito una volta sola, in kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # una box che lo usa; al primo avvio installa una dotazione di base
kiwi-custodia enter work                                   # una shell al suo interno: sudo dnf install …
kiwi-custodia run work -- firefox                          # un singolo comando al suo interno
kiwi-custodia check work                                   # che cosa vede il resto del mondo da dentro
kiwi-custodia apps work                                    # le app grafiche che contiene
kiwi-custodia export work firefox                          # "Firefox (work)" nella griglia delle applicazioni
kiwi-custodia stop work
kiwi-custodia reset work                                   # torna all’immagine di base; la home resta
kiwi-custodia-gui
```

Le distribuzioni disponibili sono `fedora` (quella predefinita),
`fedora-toolbox`, `ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`,
`kali`, `arch`, `arch-toolbox`, `opensuse`, `rocky` e `alpine`. Puoi anche
scegliere `custom` e indicare tu un’immagine con `--image`.

## Come è fatta una box { #how-a-box-is-built }

Una box in esecuzione è composta da tre container che condividono un unico
namespace di rete, cioè le stesse interfacce di rete, le stesse rotte e le
stesse regole del firewall. Il primo è il **gateway** di kiwi-proxy. Il secondo
è un **sidecar del tunnel**, un container di supporto che esegue tun2socks su un
dispositivo TUN. Un dispositivo TUN è un’interfaccia di rete virtuale, e qui
diventa la rotta predefinita. Il terzo container è la **box** vera e propria.
Tutto il traffico della box entra nel dispositivo TUN e da lì va al proxy SOCKS5
dell’exit. Il meccanismo passa dalla rotta predefinita e non dalle impostazioni
del proxy, quindi vale anche per i programmi che ignorano quelle impostazioni.

- La box gira con il tuo utente, con lo stesso uid, e al suo interno `sudo`
  funziona senza password. La sua cartella home è
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Ogni box ha la sua home e non
  usa quella vera, quindi due box sono due identità separate.
- Quando una box si ferma, le modifiche fatte al suo interno vengono salvate in
  uno snapshot che appartiene a quella box. `reset` riporta la box all’immagine
  di base.
- Wayland, X11 (tramite Xwayland), PipeWire, il bus della sessione e `/dev/dri`
  sono resi disponibili dentro la box, così le app grafiche e i giochi
  funzionano.
- Alle query DNS risponde il resolver del gateway, che blocca anche i domini
  pubblicitari. Su un exit che usa il DNS remoto, i nomi li risolve invece
  l’upstream.

## Che cosa non è { #what-it-is-not }

Una box **limita la rete, ma non è una sandbox che protegge il tuo desktop dai
programmi che contiene.** Come un container di distrobox, la box riceve il tuo
schermo e il bus della tua sessione. Un programma nella box può quindi aprire
finestre, leggere gli appunti e usare i portali del desktop. Quello che non può
fare è raggiungere la rete in un modo diverso dal suo exit. UDP non viene
inoltrato, quindi QUIC e i flussi multimediali di WebRTC non funzionano, e per
IPv6 non c’è alcuna rotta.

Le box che usano lo stesso exit lo condividono. Le box che devono restare
separate tra loro hanno bisogno di exit diversi.
