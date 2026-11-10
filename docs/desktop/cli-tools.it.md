# kiwi-cli-tools-desktop

Quattro piccoli strumenti da riga di comando per un desktop Linux.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Ultima release: **v1.2.1**. È nel [catalogo Kiwi](catalogs.md), ambito utente.

```bash
kiwi install kiwi-cli-tools-desktop   # oppure ./install.sh install, in ~/.local/bin
```

## `torlink`: raggiungere una macchina via Tor { #torlink-reach-a-machine-over-tor }

Una VPN dei poveri: raggiungi qualsiasi servizio TCP (SSH, una UI web, un database) su un'altra
macchina via Tor, senza porte aperte, senza account e senza server. Tor e socat
girano in un unico container Podman rootless, quindi ti serve solo Podman.

Un indirizzo onion è l'identità. Il lato che offre crea un **codice di invito**
per un peer, e l'altro lato lo accetta. Il codice contiene una chiave di autorizzazione
client di Tor, quindi il servizio è invisibile a chiunque non ce l'abbia: tratta
il codice come una password.

```bash
# macchina A: offre SSH e una UI web a "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # stampa torlink1:…  (segreto!)

# macchina B: li usa
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH via Tor
torlink connect alice web           # 127.0.0.1:2200 → alice's web UI
torlink ssh-config >> ~/.ssh/config # then `ssh alice-tor`; `select-server tor` lists them
```

Ogni invito è un servizio onion a sé con solo i servizi che hai elencato, quindi
`torlink revoke bob` rimuove quell'accesso per sempre. `torlink ls` mostra servizi,
peer e inoltri. Tor è solo TCP, e la prima connessione richiede un po' di tempo. La
porta SOCKS del container (19050) ascolta solo su loopback. Lo stato, comprese le tue
chiavi onion, si trova in `~/.local/share/torlink`, e `torlink purge` lo elimina.

## `pweb`: condividere una cartella via HTTPS { #pweb-share-a-folder-over-https }

Serve la **directory corrente** via HTTPS su una porta libera casuale, per passare
un file a un'altra macchina sulla stessa rete. Un certificato autofirmato viene
creato al primo avvio e riutilizzato in seguito. Lo serve a tutta la LAN, quindi
avvialo nella cartella che intendi condividere e fermalo con Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: scegliere un host SSH { #select-server-pick-an-ssh-host }

Un menu numerato con ogni alias `Host` concreto del tuo `~/.ssh/config`. Scegline uno
e si connette. Etichetta gli host con un commento `# tags: work prod` dentro il blocco
`Host` per filtrarli:

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # i tag che hai
$ select-server -f other.conf   # un altro file di configurazione
```

## `tethering`: la correzione del TTL { #tethering-the-ttl-fix }

Imposta il TTL a 64 sul traffico che arriva da un'interfaccia, così i dispositivi in tethering attraverso
questa macchina sembrano traffico della macchina stessa a un operatore che conta gli hop.
Chiede sudo, aggiunge una regola mangle di `iptables`, e la regola **non**
sopravvive a un riavvio.

```
tethering            # scegli quale interfaccia, imposta la regola
tethering --status
tethering --off
```
