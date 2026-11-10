# Come funziona la rete

Una Kiwi Network riunisce le tue macchine in un’unica rete privata, ovunque si
trovino: server a casa o in ufficio, portatili, telefoni e intere reti
domestiche dietro un router. Le macchine si raggiungono tra loro come se
fossero sulla stessa rete locale, e una sola deve essere raggiungibile da
Internet. Questa pagina spiega com’è fatta la rete e a che cosa serve ogni sua
parte.

La rete privata è una **mesh WireGuard**. WireGuard è il software VPN che cifra
le connessioni, mentre *mesh* è il nome che queste pagine danno alla rete
privata condivisa da tutte le tue macchine. Al centro della mesh c’è una
macchina, il *kiwi-master*. Tutte le altre (i node a casa o in ufficio, i
portatili, i telefoni, i router) aprono da sé la connessione verso il master e
da lì raggiungono le altre attraverso la mesh. L’intera rete è descritta in un
solo file, il file fleet (`fleet.yaml`), ed è
[kiwi-server](../server/index.md) a costruirla a partire da quel file.

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

Il master è la macchina a cui si collegano tutte le altre. Il suo ruolo,
`master`, esegue i cinque moduli elencati qui sotto. Pi-hole, Tor e nginx
condividono il namespace di rete del server WireGuard. Un namespace di rete è
l’insieme di interfacce, indirizzi e rotte che appartiene a un container:
questi tre servizi, quindi, non hanno una rete propria ma usano quella del
server WireGuard. Per questo vengono riavviati insieme a lui.

- **vpn-server** (wg-easy) è il server WireGuard. Ogni client e ogni node si
  collega a lui e da lui riceve la propria configurazione WireGuard. Le
  configurazioni può crearle kiwi-server al posto tuo (`kiwi-server enroll`).
- **vpn-client** (gluetun) collega il master a un provider VPN commerciale. Il
  preset usa Mullvad, ma va bene qualsiasi provider compatibile con gluetun. La
  rotta predefinita del server WireGuard punta a questo client VPN: il traffico
  che dalla mesh va verso Internet passa quindi dal provider, e i siti web
  vedono l’indirizzo del provider e non quello del master. Questa connessione è
  l’*uscita* del master, cioè la strada per cui il traffico della mesh arriva a
  Internet. Poiché il traffico attraversa due VPN una dopo l’altra, prima la
  tua e poi quella del provider, questa configurazione si chiama **doppio
  hop**. Un master senza vpn-client manda il traffico direttamente a Internet,
  dal proprio indirizzo.
- **dns** (Pi-hole 6) è il server DNS della mesh. Risponde all’indirizzo del
  master nella mesh, `10.8.0.1`. Vedi [DNS, nomi e certificati](dns.md).
- **tor** mette a disposizione dei client della mesh un proxy SOCKS5 su
  `10.8.0.1:9050`. I nodi di ingresso e di uscita di Tor sono limitati a un
  elenco di paesi (il valore predefinito è `de,ch,at,nl,fr`, e viene imposto
  con `StrictNodes`).
- **reverse-proxy** (nginx) serve le pagine di amministrazione, cioè le
  interfacce web di wg-easy e Pi-hole: `wg.<master>` e `pihole.<master>`. Le
  serve soltanto all’interno della mesh, e soltanto ai client autorizzati a
  vederle (vedi «Gruppi di client» più sotto).

Su un master possono girare anche un **relay nostr** e un **hub** per le
[persone della tua rete](../people/hubs.md#on-a-kiwi-network). Un hub è il sito
di una comunità e funziona nel browser, mentre un relay nostr è il tipo di
server attraverso cui gli hub si sincronizzano. Al master puoi aggiungere anche
Portainer e i backup.

### Che cosa è raggiungibile da Internet { #what-is-reachable-from-the-internet }

Per impostazione predefinita il master ha **una sola porta** aperta verso
Internet: WireGuard, sulla UDP 51820. Le pagine di amministrazione si aprono
soltanto dall’interno della mesh. Due impostazioni aprono altre porte:

- `reverse-proxy.public: true` apre le porte 80 e 443 e richiede certificati
  Let’s Encrypt per i nomi che non appartengono al dominio della fleet. Tutto
  il resto rimane raggiungibile solo dalla mesh, e alle richieste che arrivano
  da fuori le pagine di amministrazione rispondono con l’errore 403. È
  un’impostazione pensata per un hub o un relay pubblico.
- `vpn-server.unlock_relay` apre le porte TCP degli
  [anelli Tang](../server/operations.md#encrypted-disks-and-unlocking) per le
  macchine dietro NAT. Tang è un server che permette a una macchina con il
  disco cifrato di sbloccarlo all’avvio, e un anello è un server Tang con le
  proprie chiavi.

kiwi-server non tocca SSH: resta come lo configura il sistema operativo, cioè,
per impostazione predefinita, con accesso solo tramite chiavi. Lo stesso
kiwi-server usa SSH per `apply` e `status`.

## Gruppi di client { #client-groups }

I client del server WireGuard (wg-easy) sono suddivisi in **gruppi** in base al
loro indirizzo. Il gruppo stabilisce che cosa i suoi membri possono
raggiungere:

| Gruppo | Sottorete | Raggiunge | Vede gli altri client | Pagine di amministrazione |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | i node | no | no |
| `pentest` | `10.8.2.0/24` | niente nella mesh | no | no |
| `devices` | `10.8.3.0/24` | tutto | sì | sì |
| `routers` | `10.8.4.0/24` | tutto | sì | no |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # un codice QR per l’app WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # dal tunnel passa solo la mesh
```

I membri di ogni gruppo raggiungono anche Internet attraverso l’uscita del
master, a meno che per quel gruppo tu non imposti `internet: false`. Un client
con un indirizzo fuori da tutti i gruppi (`10.8.0.x`) è un normale membro della
mesh: raggiunge tutto, e può aprire le pagine di amministrazione finché
`admin_from_mesh` è attivo.

I gruppi sono un’impostazione del modulo vpn-server (`groups`), quindi puoi
modificarli o aggiungerne di tuoi. L’impostazione `reach` di un gruppo accetta
`all`, `nodes`, nomi di host, indirizzi o sottoreti. Esiste ancora la vecchia
impostazione `isolated_subnet`, che definiva un unico gruppo isolato, ma per
impostazione predefinita è disattivata.

## I node { #nodes }

Un node è una macchina a casa o in ufficio su cui girano i tuoi servizi. Anche
un node ha un modulo vpn-client, che qui però non si collega a un provider VPN
commerciale ma al master, con la configurazione WireGuard che il master ha
emesso per quel node. `kiwi-server enroll` scrive questa configurazione in
`secrets/<hostname>.conf`, e il node la usa senza che tu debba impostare altro.
Un node non ha bisogno di porte aperte verso Internet, perché è lui ad aprire
la connessione verso il master. Ecco perché funziona anche dietro il NAT di un
router domestico.

Il ruolo `node` ha tre preset, cioè tre elenchi di moduli già pronti:

| Preset | Che cosa diventa la macchina |
|---|---|
| `gateway` (predefinito) | Un gateway per la rete locale (LAN). I dispositivi della LAN che usano questa macchina come gateway predefinito arrivano a Internet attraverso la VPN e possono raggiungere la mesh. Pi-hole fa da server DNS per la LAN e, se vuoi, anche da server DHCP. I programmi di download Transmission e JDownloader girano *dentro* il namespace di rete del client VPN: quando il tunnel non è attivo non hanno nessuna rotta. Il preset comprende anche nginx, Portainer e SFTP. |
| `cloud` | Il tuo cloud personale: Nextcloud con Collabora per file, calendari e documenti, e Vaultwarden per le password. Questi servizi stanno dietro nginx, e c’è anche Portainer. Nextcloud è composto dai container del progetto AIO, senza il container master di AIO. |
| `minimal` | Soltanto il client VPN e nginx. I moduli che ti servono li aggiungi tu. |

Su un node possono girare anche i backup, un server di backup e Tang.
OpenCloud, Immich e Paperless-ngx sono inclusi perché tu possa provarli. Vedi
l’[elenco dei moduli](../server/modules.md).

I servizi di un node si raggiungono dalla sua LAN e all’**indirizzo del node
nella mesh** (per esempio `10.8.0.25`). Il traffico che dalla mesh arriva a
quell’indirizzo sulle porte 80 e 443 viene inoltrato al reverse proxy del node.

## Nomi { #names }

I nomi delle macchine seguono una convenzione: **i master hanno nomi di piatti
a base di frutta** (`crumble`, `sorbet`, `compote`, `chutney`, `strudel`,
`cobbler`, `trifle`, `cider`) e **i node nomi di frutti** (`papaya`, `lychee`,
`guava`, `quince`, `damson`). Così, davanti a una qualsiasi riga di log, capisci
subito di che tipo di macchina si tratta. È soltanto una convenzione, e va bene
qualsiasi nome. Un servizio prende un nome sotto quello della macchina su cui
gira: `cloud.papaya.home`, `vault.papaya.home`, `wg.sorbet.home`. Vedi
[DNS, nomi e certificati](dns.md).

## Come la mesh arriva a Internet { #ways-out }

Un master è un server WireGuard con un’uscita, cioè la strada per cui il
traffico della mesh arriva a Internet. L’uscita ha tre modalità:

| Modalità | Come la mesh arriva a Internet | Stato |
|---|---|---|
| **provider** | Attraverso un provider VPN commerciale (gluetun). È il doppio hop, ed è ciò che configura il preset del master. | realizzato |
| **direct** | Direttamente dalla connessione a Internet del master. Per ottenere questa modalità, elenca i moduli del master senza `vpn-client`. | realizzato |
| **master** | Attraverso *il master di un’altra rete*. Il tuo master è un client di quella rete, in uno dei suoi gruppi che possono raggiungere Internet e nient’altro. Si chiama multi-hop. | progettato; richiede la registrazione tra reti diverse, cioè la federazione |

Qualunque sia la modalità di uscita, ogni master offre alla mesh anche il proxy
SOCKS5 di Tor.

## Una mesh per ogni rete { #one-mesh-per-network }

Ogni rete ha la propria mesh, con un intervallo di indirizzi tutto suo.
L’intervallo predefinito è `10.8.0.0/16`. Master e node stanno in `10.8.0.0/24`,
poi vengono i gruppi: guests in `.1`, pentest in `.2`, devices in `.3` e
routers in `.4`. Una seconda rete usa un altro intervallo, per esempio
`10.9.0.0/16`, così un dispositivo che appartiene a entrambe le reti riesce a
distinguerle. Oggi l’intervallo non si imposta in un punto solo, ma è
distribuito su più impostazioni (`mesh_subnet`, poi `server_ip`, `wg_subnet`,
`wg_default_address` e `groups` del vpn-server, e `socks_policy_accept` di Tor).
Il file fleet le imposta tutte.

## Indirizzi { #addressing }

| Che cosa | Valore predefinito |
|---|---|
| L’intera mesh (instradata su ogni host) | `10.8.0.0/16` per impostazione predefinita (`mesh_subnet`) |
| Client di wg-easy | `10.8.0.0/24`; il server è `10.8.0.1` |
| Gruppi di client | `10.8.1.0/24` … `10.8.4.0/24` |
| Rete dello stack | `172.64.0.0/24` su un master, `172.128.0.0/24` su un node |
| MTU di WireGuard | `1376` (`wg_mtu`), misurata con [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU del bridge dello stack | `1500` (`bridge_mtu`) |

Lo stack di una macchina è l’insieme dei container eseguiti dai suoi moduli.
Ogni macchina con uno stack instrada l’intervallo di indirizzi della mesh
attraverso il proprio client VPN oppure, sul master, attraverso il server
WireGuard. In questo modo la macchina e i suoi container raggiungono tutti i
node.

## Riavvii e aggiornamenti automatici { #keeping-it-fresh }

Ogni macchina riceve due timer, che si configurano nelle impostazioni del suo
stack. Il primo **riavvia la VPN ogni giorno** alle `07:00`, e così la macchina
ottiene un nuovo indirizzo di uscita. Il secondo è l’**aggiornamento
settimanale**, la domenica alle 00:00: esegue `podman auto-update`, purché sia
impostato `auto_update: registry`. Anche il sistema operativo si aggiorna da
solo, e si riavvia soltanto
[nella finestra oraria che hai stabilito](../server/machines.md#updates).

## Un’intera LAN nella mesh { #a-whole-lan-in-the-mesh }

Un router può entrare nella mesh come client WireGuard del gruppo `routers`. In
alternativa può mandare il traffico destinato alla sottorete della mesh a un
node gateway, con una rotta statica. In entrambi i casi tutti i dispositivi
della LAN di quel router raggiungono tutti i node senza dover usare WireGuard.
Vedi [Router](routers.md).
