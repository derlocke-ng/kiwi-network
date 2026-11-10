# Router: un’intera LAN nella mesh

Questa pagina spiega come collegare alla tua Kiwi Network un’intera rete locale
(LAN), per esempio la rete domestica o quella dell’ufficio, attraverso il suo
router. Un dispositivo nella mesh, cioè nella rete WireGuard privata delle tue
macchine, può risolvere tutti i nomi della fleet e raggiungere tutti i node. I
dispositivi di una LAN dietro un router possono fare lo stesso, senza che
ognuno di loro debba usare WireGuard. Ci sono due modi per arrivarci:

- **Il router è un client della mesh.** Sul router gira WireGuard, con una
  configurazione emessa da wg-easy, il server WireGuard del master
  (`kiwi-server enroll fleet.yaml router --group routers`). Il router instrada
  nel tunnel la sottorete della mesh (`10.8.0.0/16`). Questo si chiama tunnel
  *split*, perché ci passa soltanto il traffico destinato alla mesh. In un
  tunnel *full* passa invece tutto il traffico: l’intera LAN arriva allora a
  Internet attraverso l’uscita del master, cioè la connessione del master a
  Internet.
- **Il router ha una rotta statica verso un node gateway.** Il router non ha
  nessun tunnel. Manda il traffico destinato alla sottorete della mesh a un
  node della LAN su cui gira il modulo `gateway`, e quel node lo inoltra
  attraverso il proprio client VPN.

In entrambi i casi basta una sola regola DNS, e non servono voci per i singoli
host. La regola inoltra le query per il dominio della fleet (`*.home`) al
Pi-hole del master, che conosce tutti i nomi di host e tutti i nomi di
servizio. Per il resto, il DNS del router non cambia.

Una cosa non funziona: un dispositivo della LAN non può raggiungere un
dispositivo *dietro un altro router* usando l’indirizzo LAN di quest’ultimo. La
mesh trasporta soltanto il traffico diretto a indirizzi della mesh, ed è una
scelta voluta.

## OpenWrt { #openwrt }

Per OpenWrt, kiwi-server scrive l’intera configurazione sotto forma di script
`uci`:

```bash
# il router come client della mesh, con la configurazione emessa dal wg-easy del master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: solo la mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: tutto

# nessun tunnel sul router: una rotta statica verso il node gateway lychee
# (nella fleet lychee deve avere un indirizzo LAN statico: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copia l’output sul router ed eseguilo lì:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Lo script installa il pacchetto WireGuard, se manca. Crea un’interfaccia
chiamata `kiwi`, un nome che puoi cambiare con `--name`. L’interfaccia usa come
MTU il valore `wg_mtu` della fleet e ha un solo peer, il master. Il peer viene
creato con `route_allowed_ips`, quindi le rotte le aggiunge OpenWrt. Lo script
crea anche una zona del firewall verso cui la LAN può inoltrare traffico, con
masquerading e MSS clamping. Infine aggiunge la regola di dnsmasq che inoltra
il dominio della fleet al master (`server=/home/10.8.0.1`). Con `--full`,
dnsmasq manda tutte le query DNS al Pi-hole del master. Ogni sezione scritta
dallo script ha un nome: se lo esegui di nuovo, sostituisce ciò che aveva
scritto la volta precedente.

## FritzBox { #fritzbox }

Fritz!OS ha un client WireGuard e le rotte statiche, ma non sa inoltrare le
query DNS di un singolo dominio. Della regola DNS deve quindi occuparsi un
node:

1. **Tunnel:** vai in Internet → Abilitazioni → VPN (WireGuard) → Aggiungere
   connessione, scegli di collegarti a un altro servizio WireGuard e importa la
   configurazione emessa dal master. È la riga `AllowedIPs` di quella
   configurazione a decidere se il tunnel è split o full.
2. **Oppure una rotta statica:** vai in Rete domestica → Rete → Impostazioni di
   rete → Route IPv4. Inserisci `10.8.0.0` come destinazione, `255.255.0.0` come
   maschera di sottorete e l’indirizzo LAN del node gateway come gateway.
3. **DNS:** fai in modo che la LAN usi un Pi-hole come server DNS. Puoi
   impostare il node gateway come server DNS locale, oppure lasciare che il
   Pi-hole del node faccia da server DHCP per la LAN (le impostazioni
   `dns.dhcp_*` insieme al modulo dhcp-relay). Il Pi-hole del node conosce i
   nomi della fleet e inoltra tutte le altre query al master.

Puoi usare il tunnel e le rotte statiche contemporaneamente. In quel caso il
traffico per la mesh passa dal tunnel.

## Qualsiasi altro router { #any-other-router }

Per qualsiasi altro router bastano tre cose. Dai al router una configurazione
da client WireGuard, oppure aggiungi una rotta statica per `10.8.0.0/16` che
punti all’indirizzo LAN del node gateway. Poi fai in modo che la LAN usi come
server DNS un Pi-hole che conosce la fleet: lo è qualsiasi node su cui gira il
modulo `dns`. I router basati su dnsmasq (DD-WRT, Tomato, il forwarder di
pfSense) accettano anche la regola di inoltro su una sola riga
`server=/home/10.8.0.1`.
