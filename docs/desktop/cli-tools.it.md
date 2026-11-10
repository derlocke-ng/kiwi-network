# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop è un pacchetto di quattro piccoli strumenti da riga di
comando per un desktop Linux. `torlink` raggiunge un servizio su un’altra
macchina attraverso Tor, `pweb` condivide una cartella via HTTPS,
`select-server` ti fa scegliere un host SSH da un menu e `tethering` corregge il
TTL del traffico dei dispositivi collegati in tethering.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Ultima release: **v1.2.1**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

```bash
kiwi install kiwi-cli-tools-desktop   # oppure ./install.sh install, in ~/.local/bin
```

## `torlink`: raggiungere una macchina attraverso Tor { #torlink-reach-a-machine-over-tor }

Con `torlink` raggiungi qualsiasi servizio TCP su un’altra macchina, per esempio
SSH, un’interfaccia web o un database, attraverso la rete Tor. È un semplice
sostituto di una VPN: nessuna delle due macchine ha bisogno di una porta aperta,
non serve alcun account e non c’è nessun server da gestire. Tor e socat girano
insieme in un unico container Podman rootless, quindi ti basta Podman.

Una macchina che offre dei servizi è identificata dal suo indirizzo onion, cioè
un indirizzo all’interno della rete Tor. Su quella macchina crei un **codice di
invito** per un peer, cioè per la persona o la macchina che deve ottenere
l’accesso. Il peer accetta il codice sull’altra macchina. Il codice contiene una
chiave di autorizzazione client di Tor: chi non ha questa chiave non può
nemmeno vedere che il servizio esiste. Custodisci quindi il codice come una
password.

```bash
# macchina A: offre SSH e un’interfaccia web a "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # stampa torlink1:…  (segreto!)

# macchina B: li usa
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH attraverso Tor
torlink connect alice web           # 127.0.0.1:2200 → l’interfaccia web di alice
torlink ssh-config >> ~/.ssh/config # poi `ssh alice-tor`; `select-server tor` li elenca
```

Ogni invito è un onion service a sé, che contiene soltanto i servizi che ci hai
messo. Per questo `torlink revoke bob` toglie quell’accesso in modo definitivo.
`torlink ls` mostra i tuoi servizi, i tuoi peer e i tuoi inoltri, cioè le porte
locali che portano ai servizi di un peer. Tor trasporta soltanto TCP, e la prima
connessione richiede un po’ di tempo. La porta SOCKS del container (19050) è in
ascolto soltanto sull’interfaccia di loopback. Lo stato di `torlink`, comprese le
tue chiavi onion, è salvato in `~/.local/share/torlink`, e `torlink purge` lo
cancella.

## `pweb`: condividere una cartella via HTTPS { #pweb-share-a-folder-over-https }

`pweb` pubblica la **directory corrente** via HTTPS su una porta libera scelta a
caso. Serve per passare un file a un’altra macchina della stessa rete. Al primo
avvio crea un certificato autofirmato, che poi riutilizza. Finché `pweb` è in
esecuzione, qualsiasi macchina della rete locale può raggiungere la cartella.
Avvialo nella cartella che vuoi davvero condividere, e fermalo con Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: scegliere un host SSH { #select-server-pick-an-ssh-host }

`select-server` mostra un menu numerato con tutti gli alias `Host` concreti del
tuo `~/.ssh/config`, cioè tutti gli alias che non sono pattern con caratteri
jolly. Ne scegli uno, e select-server si collega a quell’host. Per filtrare il menu, assegna
dei tag ai tuoi host: aggiungi un commento come `# tags: work prod` dentro il
blocco `Host` e passa un tag sulla riga di comando:

```
$ select-server work            # solo gli host con il tag "work"
$ select-server --tags          # i tag che hai
$ select-server -f other.conf   # un altro file di configurazione
```

## `tethering`: impostare il TTL per i dispositivi in tethering { #tethering-the-ttl-fix }

`tethering` serve quando altri dispositivi usano la connessione a Internet di
questa macchina, cioè quando fai tethering. Alcuni operatori telefonici contano i salti di
rete del traffico, e in questo modo distinguono i dispositivi collegati in
tethering dalla macchina stessa. `tethering` imposta il TTL a 64 su tutto il
traffico che arriva da una certa interfaccia. Per l’operatore, il traffico dei
dispositivi collegati sembra così quello della macchina stessa. Lo strumento
chiede sudo e aggiunge una regola `iptables` nella tabella mangle. La regola
**non** sopravvive a un riavvio.

```
tethering            # scegli l’interfaccia e imposta la regola
tethering --status
tethering --off
```
