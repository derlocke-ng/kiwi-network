# Lavorare nelle reti di molti clienti

Se lavori da remoto per molti clienti, di solito ti serve una connessione VPN o
SOCKS separata per raggiungere la rete di ciascuno. Dieci clienti significano
allora dieci connessioni. Tenerle tutte sull’host crea problemi: dieci tunnel
attivi contemporaneamente, rotte che si ostacolano a vicenda e traffico
destinato alla rete di un cliente che rischia di finire in quella di un altro.

Le app desktop di Kiwi ti permettono di lavorare nella rete di ogni cliente in
modo isolato. L’host non si riempie di tunnel e di rotte, e non hai dieci
connessioni VPN attive nello stesso momento. Ogni connessione viene messa in un
container tutto suo, e l’unica strada per uscire da quel container porta a
quel cliente. Una connessione di questo tipo si chiama **exit**. I tuoi
strumenti girano in un container o in un profilo del browser che usa l’exit di
cui hanno bisogno, e sull’host non cambia nient’altro.

| App | Che cosa fa |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Il motore su cui si basano le altre app. Un **exit** è una connessione a un upstream, salvata con un nome. L’upstream è il proxy a cui viene inviato il tuo traffico: un proxy SOCKS5 che ti è stato fornito, oppure uno creato da un modulo provider. Quando attivi un exit, kiwi-proxy crea un **gateway** dedicato. Un gateway è un namespace di rete (uno stack di rete separato, con rotte e firewall propri) la cui unica rotta porta a quell’upstream. I programmi sull’host possono usare un exit attraverso una porta SOCKS5 locale |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distribuzioni Linux in box che usano un exit.** Una box è un container rootless (cioè che gira senza permessi di root) con Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky o Alpine e con una sua cartella home. *Tutto* il traffico di rete della box passa dall’exit, compreso quello dei gestori di pacchetti, dei giochi e dei programmi compilati staticamente che ignorano le impostazioni del proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Profili del browser che usano un exit.** Ogni profilo esegue Camoufox, Firefox o Tor Browser e ha un proprio archivio dei dati |
| [**Moduli provider**](providers.md) | Moduli che creano exit attraverso Tor, una VPN (con gluetun), 9proxy o Mysterium. Tor e Mysterium sono un modo rapido per ottenere altri indirizzi IP, utile per i test |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Come gli exit restano separati { #how-it-stays-clean }

- **Un gateway è fail-closed.** Significa che un guasto interrompe il traffico e
  non gli apre mai un’altra strada. Il firewall di un gateway scarta tutto ciò
  che non è diretto all’unico upstream del gateway. Se il gateway si ferma,
  tutto ciò che gli è collegato resta senza rotta. Nessun programma deve
  accorgersi del guasto e reagire, perché senza il gateway una rotta non c’è.
- **Gira soltanto ciò che usi.** Quando una box o un browser avvia un gateway,
  il gateway viene rimosso non appena si ferma l’ultima box o l’ultimo browser
  che lo usava. Restano attivi soltanto gli exit che avvii tu stesso con
  `kiwi-proxy up`.
- **I clienti restano separati.** Box e browser che usano lo stesso exit lo
  condividono, quindi hanno lo stesso indirizzo IP e lo stesso namespace di
  rete. I clienti che non devono vedersi a vicenda ricevono exit diversi. Ogni
  box ha inoltre la sua cartella home, così le chiavi SSH e i profili del
  browser di un cliente non sono disponibili nella box di un altro.
- **Nessun permesso di root e nessuna rotta sull’host.** Tutto gira in Podman
  rootless, che esegue i container con il tuo utente. La rete dell’host non
  viene modificata.
- **Anche le query DNS passano dall’exit.** Per impostazione predefinita i nomi
  vengono risolti con DNS over HTTPS (DoH) attraverso l’exit, e i domini
  pubblicitari presenti nelle liste di blocco vengono bloccati. Per risolvere i **nomi host interni** di
  un cliente usa invece `--dns remote`: i nomi vengono passati dalla parte del
  cliente e risolti lì. Anche Tor e i nomi `.onion` hanno bisogno di questa
  modalità.

## Limiti { #limits }

Questi limiti sono dichiarati nei repository:

- **Solo TCP e solo IPv4.** UDP non viene inoltrato, quindi QUIC e i flussi
  multimediali di WebRTC non funzionano. Per IPv6 non c’è alcuna rotta.
- **Una sola configurazione VPN per macchina.** Il modulo provider per le VPN ha
  un’unica configurazione di gluetun, con un solo `vpn.json` e una sola
  configurazione WireGuard personalizzata. I suoi exit si distinguono soltanto
  per il paese del server. Se ti servono contemporaneamente le VPN di più
  clienti, oggi la soluzione è un endpoint SOCKS5 per ciascun cliente.
- **Una box limita la rete, ma non è una sandbox.** Come un container di
  distrobox, condivide il tuo schermo, il bus della tua sessione e i tuoi
  appunti. Quello che non può fare è raggiungere la rete in un modo diverso dal
  suo exit.
- **Mysterium:** un’identità può avere una sola connessione alla volta.

## Primi passi { #get-started }

I comandi seguenti installano le app, salvano come exit il proxy SOCKS5 di un
cliente e aprono una shell in una box Fedora che usa quell’exit:

```bash
kiwi install kiwi-custodia            # porta con sé kiwi-proxy
kiwi-custodia setup                   # immagini e dati DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # una shell che può uscire soltanto dal SOCKS5 del cliente A
```
