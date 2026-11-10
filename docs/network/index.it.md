# Come funziona la rete

Una Kiwi Network è una **mesh WireGuard con un solo hub**, il *kiwi-master*. Ogni
altra macchina (node a casa o in ufficio, portatili, telefoni, router) si collega
al master e incontra le altre nella mesh. Tutto è descritto in
un unico file fleet e costruito da [kiwi-server](../server/index.md).

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## Il master { #the-master }

Il ruolo `master` esegue cinque moduli. Pi-hole, Tor e nginx vivono dentro il
namespace di rete del server WireGuard e ripartono insieme a lui.

- **vpn-server** (wg-easy) è il punto d'ingresso per ogni client e ogni node, e
  rilascia le loro configurazioni WireGuard. kiwi-server può crearle per te
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) si collega a un provider VPN commerciale: Mullvad nel
  preset, in generale qualsiasi provider supportato da gluetun. La route predefinita
  del server WireGuard punta a lui, quindi il traffico della mesh esce attraverso il
  provider, non dall'indirizzo del master. Questo è il **doppio hop**. Un master senza
  vpn-client esce direttamente.
- **dns** (Pi-hole 6) risponde all'indirizzo mesh del master, `10.8.0.1`. Vedi
  [DNS, nomi e certificati](dns.md).
- **tor** offre SOCKS5 su `10.8.0.1:9050` ai client della mesh, con nodi di entrata
  e di uscita fissati su un insieme di paesi (default `de,ch,at,nl,fr`, `StrictNodes`).
- **reverse-proxy** (nginx) serve le pagine di amministrazione, `wg.<master>` e
  `pihole.<master>`, ai gruppi di amministrazione nella mesh.

Un master può anche ospitare un **relay nostr** e un **hub** per
[le persone della tua rete](../people/hubs.md#on-a-kiwi-network), oltre a Portainer
e ai backup.

### Cosa è raggiungibile da Internet { #what-is-reachable-from-the-internet }

Di default il master pubblica **una sola porta**: WireGuard, UDP 51820. Le pagine
di amministrazione rispondono solo alla mesh. Due impostazioni aggiungono altro:

- `reverse-proxy.public: true` pubblica la 80 e la 443, con certificati Let's Encrypt
  per i nomi fuori dal dominio della fleet. Tutto il resto continua a rispondere
  solo alla mesh, e le pagine di amministrazione rispondono 403 dall'esterno. Serve
  per un hub o un relay pubblico.
- `vpn-server.unlock_relay` apre le porte TCP degli
  [anelli Tang](../server/operations.md#encrypted-disks-and-unlocking) per le
  macchine dietro NAT.

SSH resta come lo configura il sistema operativo (di default solo chiavi). kiwi-server
lo usa per `apply` e `status`.

## Gruppi di client { #client-groups }

I client di wg-easy sono divisi in **gruppi** in base all'indirizzo. Ogni gruppo decide
cosa possono raggiungere i suoi membri:

| Gruppo | Subnet | Raggiunge | Vede gli altri client | Pagine di amministrazione |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | i node | no | no |
| `pentest` | `10.8.2.0/24` | niente nella mesh | no | no |
| `devices` | `10.8.3.0/24` | tutto | sì | sì |
| `routers` | `10.8.4.0/24` | tutto | sì | no |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # un codice QR per il client WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # solo la mesh passa nel tunnel
```

Ogni gruppo può uscire verso Internet attraverso l'uscita, a meno che tu non imposti
`internet: false`. I client fuori da ogni gruppo (`10.8.0.x`) sono la mesh
semplice: raggiungono tutto e vedono le pagine di amministrazione finché `admin_from_mesh` è
attivo. I gruppi sono un'impostazione del modulo vpn-server (`groups`), quindi puoi cambiarli
o aggiungerne di tuoi (`reach` accetta `all`, `nodes`, nomi host, indirizzi o
subnet). Il vecchio `isolated_subnet` singolo esiste ancora, ma è disattivato di
default.

## Node { #nodes }

Il vpn-client di un node non parla con una VPN commerciale. Usa la configurazione
WireGuard che il master ha rilasciato per lui (`kiwi-server enroll` scrive
`secrets/<hostname>.conf`, e il node la prende da solo). Un node non ha bisogno di
porte aperte su Internet: si collega lui al master, quindi funziona dietro il NAT
di un router di casa.

Il ruolo `node` ha tre preset:

| Preset | Cosa diventa la macchina |
|---|---|
| `gateway` (default) | Un gateway per la LAN. I client della LAN che lo usano come gateway predefinito escono attraverso la VPN e possono raggiungere la mesh. Pi-hole serve la LAN (se vuoi anche come suo server DHCP). Transmission e JDownloader girano *dentro* il namespace di rete del client VPN, quindi non hanno alcuna route quando il tunnel è giù. Con nginx, Portainer e SFTP. |
| `cloud` | Nextcloud (dai container del progetto AIO, senza il container master di AIO) con Collabora, più Vaultwarden, dietro nginx, più Portainer |
| `minimal` | Solo il client VPN e nginx, per i moduli che scegli tu |

I node possono anche eseguire backup, un server di backup, Tang e (in prova) OpenCloud,
Immich e Paperless-ngx. Vedi l'[elenco dei moduli](../server/modules.md).

I servizi di un node sono raggiungibili sulla sua LAN e al suo **indirizzo mesh** (ad es.
`10.8.0.25`). Il traffico della mesh verso quell'indirizzo sulla 80 e sulla 443 viene inoltrato al
reverse proxy.

## Nomi { #names }

Le macchine prendono il nome dal frutteto: **i master da piatti a base di frutta** (`crumble`,
`sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`, `cider`) e
**i node da frutti** (`papaya`, `lychee`, `guava`, `quince`, `damson`), così
il tipo di una macchina si legge in ogni riga di log. È una convenzione, e
qualsiasi nome funziona. I servizi stanno sotto il loro host: `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. Vedi [DNS, nomi e certificati](dns.md).

## Vie d'uscita { #ways-out }

Un master è un server WireGuard con un'uscita, e l'uscita ha tre modalità:

| Modalità | Come la mesh raggiunge Internet | Stato |
|---|---|---|
| **provider** | attraverso una VPN commerciale (gluetun): il doppio hop, e il preset del master | realizzata |
| **direct** | direttamente dall'uplink del master. Elenca i moduli del master senza `vpn-client` | realizzata |
| **master** | attraverso *il master di un'altra rete*, come client in uno dei suoi gruppi che può raggiungere Internet e nient'altro: multi-hop | progettata; richiede la registrazione tra reti diverse, cioè la federazione |

Ogni master offre inoltre alla mesh il SOCKS5 di Tor, qualunque sia la sua uscita.

## Una mesh per rete { #one-mesh-per-network }

Ogni rete ha la sua mesh. Il default è `10.8.0.0/16`: master e node
in `10.8.0.0/24`, poi guests `.1`, pentest `.2`, devices `.3` e routers
`.4`. Una seconda rete prende un altro intervallo, per esempio `10.9.0.0/16`, così un
dispositivo che sta in entrambe le distingue. Oggi l'intervallo è distribuito su
diverse impostazioni (`mesh_subnet`, `server_ip` del vpn-server, `wg_subnet`,
`wg_default_address` e `groups`, e `socks_policy_accept` di Tor), e il
file fleet le imposta tutte.

## Indirizzi { #addressing }

| Cosa | Default |
|---|---|
| L'intera mesh (instradata su ogni host) | `10.8.0.0/16` di default (`mesh_subnet`) |
| Client di wg-easy | `10.8.0.0/24`; il server è `10.8.0.1` |
| Gruppi di client | `10.8.1.0/24` … `10.8.4.0/24` |
| Rete dello stack | `172.64.0.0/24` su un master, `172.128.0.0/24` su un node |
| MTU di WireGuard | `1376` (`wg_mtu`), misurato con [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU del bridge dello stack | `1500` (`bridge_mtu`) |

Ogni host con uno stack instrada la mesh attraverso il suo client VPN (sul master, attraverso
il server WireGuard), così l'host e i suoi container raggiungono ogni node.

## Tenerla fresca { #keeping-it-fresh }

Ogni macchina riceve due timer dalle impostazioni del suo stack: un **riavvio quotidiano della VPN**
(`07:00`, per un indirizzo d'uscita nuovo) e un **aggiornamento settimanale** (domenica 00:00, che
esegue `podman auto-update` finché è impostato `auto_update: registry`). Il sistema
operativo si aggiorna da solo e si riavvia solo nella [tua finestra](../server/machines.md#updates).

## Un'intera LAN nella mesh { #a-whole-lan-in-the-mesh }

Un router può entrare nella mesh come client WireGuard nel gruppo `routers`, oppure inviare
la subnet della mesh a un node gateway con una route statica. A quel punto ogni dispositivo di quella
LAN raggiunge ogni node senza eseguire WireGuard. Vedi [Router](routers.md).
