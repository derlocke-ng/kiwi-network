# Router: un'intera LAN nella mesh

Un dispositivo nella mesh risolve ogni nome della fleet e raggiunge ogni node. Una LAN
dietro un router può fare lo stesso senza che ogni dispositivo esegua WireGuard, in uno
di due modi:

- **Il router è un client della mesh.** Esegue WireGuard con una configurazione rilasciata
  dal wg-easy del master (`kiwi-server enroll fleet.yaml router --group routers`) e
  instrada la subnet della mesh (`10.8.0.0/16`) nel tunnel.
  Questo è il tunnel *split*: ci passa solo il traffico della mesh. Il tunnel *full*
  manda tutto, così l'intera LAN raggiunge Internet attraverso
  l'uscita del master.
- **Una route statica verso un node gateway.** Il router non ha un tunnel. Manda la
  subnet della mesh a un node della LAN che esegue il modulo `gateway`, il quale
  la inoltra attraverso il suo client VPN.

In entrambi i casi, un'unica regola DNS sostituisce gli override per singolo host: il dominio della fleet
(`*.home`) viene inoltrato al Pi-hole del master, che conosce ogni nome di host e
di servizio. Nient'altro cambia nel DNS del router.

Quello che la LAN non può fare è raggiungere un dispositivo *dietro un altro router* tramite il suo
indirizzo LAN. La mesh trasporta solo indirizzi mesh, per scelta progettuale.

## OpenWrt { #openwrt }

kiwi-server scrive l'intera configurazione come script `uci`:

```bash
# il router come client della mesh, con la configurazione rilasciata dal wg-easy del master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: solo la mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: tutto

# nessun tunnel sul router: una route statica verso il node gateway lychee
# (lychee ha bisogno di un indirizzo LAN statico nella fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copia l'output sul router ed eseguilo:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Lo script installa il pacchetto WireGuard se manca. Crea un'interfaccia
`kiwi` (cambia il nome con `--name`), con il `wg_mtu` della fleet come
MTU e un peer per il master
e `route_allowed_ips`, una zona firewall verso cui la LAN può inoltrare (con
masquerading e MSS clamping), e l'inoltro dnsmasq per il dominio della fleet
(`server=/home/10.8.0.1`). Con `--full`, dnsmasq manda ogni risoluzione al
Pi-hole del master. Ogni sezione ha un nome, quindi eseguire di nuovo lo script sostituisce
ciò che aveva scritto prima.

## FritzBox { #fritzbox }

Fritz!OS ha un client WireGuard e le route statiche, ma non l'inoltro DNS per
dominio, quindi la regola DNS passa a un node:

1. **Tunnel:** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   connect to another WireGuard service → importa la configurazione rilasciata dal master.
   I suoi `AllowedIPs` decidono tra split e full.
2. **Oppure una route statica:** Home Network → Network → Network Settings → IPv4
   Routes. Destinazione `10.8.0.0`, subnet mask `255.255.0.0`, gateway l'indirizzo
   LAN del node gateway.
3. **DNS:** fai puntare la LAN a un Pi-hole. Imposta il node gateway come server DNS
   locale, oppure lascia che il Pi-hole del node sia il server DHCP della LAN (impostazioni
   `dns.dhcp_*` più il modulo dhcp-relay). Il Pi-hole del node contiene i nomi della
   fleet e inoltra il resto al master.

Il tunnel e le route statiche possono coesistere. Per la mesh vince il tunnel.

## Qualsiasi altro router { #any-other-router }

Bastano tre cose. Dai al router una configurazione client WireGuard, oppure
aggiungi una route statica per `10.8.0.0/16` verso l'indirizzo LAN del node gateway. Poi
fai puntare il DNS della LAN a un Pi-hole che conosce la fleet, cioè qualsiasi node che esegue
il modulo `dns`. I router con dnsmasq sotto (DD-WRT, Tomato, il forwarder di pfSense)
accettano anche l'inoltro di una riga `server=/home/10.8.0.1`.
