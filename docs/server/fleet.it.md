# Il file fleet

Il file fleet, `fleet.yaml`, è il posto in cui descrivi tutte le macchine della
tua Kiwi Network. Per ogni macchina indica quale sistema operativo riceve, a che
cosa serve e come sono configurati i suoi servizi. kiwi-server costruisce ogni
macchina a partire da questa descrizione: scrivi una volta sola ciò che vuoi, e
non devi configurare a mano nessuna macchina.

Il file ha due chiavi. `defaults` contiene le impostazioni valide per tutti gli
host, mentre `hosts` ha una voce per ogni macchina. Un’impostazione scritta
nella voce di un host prende il posto della stessa impostazione in `defaults`.
`kiwi-server init` scrive un file commentato da cui puoi partire, e il
riferimento completo è
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Ogni host ha un **sistema di destinazione** (`target`), cioè il sistema
operativo che viene installato, e un **ruolo** (`role`), cioè il compito che la
macchina svolge dopo l’installazione.

- `target` è `coreos`, `ucore` (il valore predefinito) oppure `debian`. Vedi [Macchine](machines.md).
- `role` è `bare` (il valore predefinito), `master` oppure `node`. Vedi [Ruoli](roles.md).

## Esempio { #example }

Questo file fleet descrive tre macchine. La prima è il master, cioè la macchina
a cui si collegano tutte le altre, su un VPS Debian (un server virtuale a
noleggio). La seconda è un node gateway, che fa passare attraverso la VPN il
traffico di una rete locale. La terza è un node cloud, su cui girano Nextcloud
e Vaultwarden.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya diventa papaya.home; i servizi sono cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # CANCELLATO dalla ISO senza chiedere
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # il master, un VPS Debian
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # l’indirizzo a cui si collegano client e node

  lychee:                                # un node gateway
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # il lato LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # un node cloud su uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # per il primo account; poi disattivalo
```

Nell’esempio non c’è nessuna password dei servizi. Ogni password che non
scrivi viene generata da kiwi-server a partire dal seed in `secrets/seed`, e
`kiwi-server secrets show fleet.yaml papaya` stampa le password di quell’host.

L’esempio non indica nemmeno i file di configurazione WireGuard dei node.
`kiwi-server enroll` scrive la configurazione di un node in
`secrets/<hostname>.conf`, e il client VPN del node la trova lì senza bisogno
di una voce nel file fleet. Dallo stesso file viene letto anche l’indirizzo del
node nella mesh. La mesh è la rete WireGuard privata che collega tutte le tue
macchine, e l’indirizzo nella mesh è l’indirizzo che una macchina ha in quella
rete.

## Valori predefiniti { #defaults }

Se una chiave non è impostata né nel blocco `defaults` né nell’host,
kiwi-server usa il valore integrato indicato in questa tabella.

| Chiave | Valore predefinito |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Nessun valore predefinito. `build` ne ha bisogno, e il valore deve iniziare con `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Imposta un `password_hash` se vuoi accedere dalla console |
| `network` | `dhcp: true`. Per un indirizzo statico imposta `address` (in notazione CIDR), `gateway` e `dns`. In alternativa imposta un `iprange`, da cui gli host ricevono gli indirizzi nell’ordine in cui compaiono nel file |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (oppure `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Gli anelli Tang a cui è legato il disco. Un anello è un server Tang, che permette a una macchina cifrata di sbloccare il disco all’avvio (vedi [Gestione](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | Gli host su cui viene salvato il backup della cartella della fleet, e quanti backup vengono conservati (`hosts: []`, `keep: 10`) |
| `vps` | `server:` l’id, il nome o il nickname di un server netcup |

## Come si combinano le impostazioni { #how-settings-combine }

- Un host sostituisce i valori predefiniti **chiave per chiave**, quindi deve
  indicare soltanto le chiavi che cambiano. Fanno eccezione le liste
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` e le liste
  `coreos.*`: le voci che un host scrive in queste liste si *aggiungono* a
  quelle predefinite, invece di sostituirle.
- I ruoli costruiti con i moduli, `master` e `node`, tengono le loro
  impostazioni in un blocco che porta il nome del ruolo (`master:` o `node:`).
  Il blocco contiene prima le **impostazioni dello stack** e poi **un blocco
  per ogni modulo**. Lo stack è l’insieme dei container che una macchina
  esegue per i suoi moduli, e le impostazioni dello stack valgono per tutti.
- Una lista `modules:` in quel blocco **sostituisce** l’elenco dei moduli del
  preset. Un preset è un elenco di moduli già pronto. I moduli richiesti da
  quelli elencati vengono aggiunti automaticamente.
- Le **impostazioni che indicano file**, come certificati e file di
  configurazione, si scrivono come percorsi relativi al file fleet.
  kiwi-server copia il contenuto di questi file nello script del ruolo
  dell’host, cioè lo script che prepara la macchina per il suo ruolo.
- Un’impostazione scritta senza valore riceve il valore predefinito. Se scrivi
  male una chiave, kiwi-server segnala un errore e ti suggerisce la chiave che
  probabilmente intendevi.

## Impostazioni dello stack { #stack-settings }

Le impostazioni dello stack valgono per l’intero stack di una macchina. Si
scrivono direttamente nel blocco del ruolo.

| Impostazione | Valore predefinito | Note |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` oppure `minimal` |
| `runtime` | `podman` | `podman` esegue i container come quadlet di podman, cioè unità systemd per i container. `docker` usa docker compose |
| `auto_update` | `registry` | `registry` esegue `podman auto-update` una volta alla settimana. Con `off` le immagini dei container cambiano solo quando applichi di nuovo l’host |
| `docker_dir` | `/home/user/docker` | la cartella che contiene lo stack e i suoi dati |
| `service_user` | l’utente amministratore | l’utente proprietario delle cartelle dei dati |
| `vpn_ip` | dalla configurazione WireGuard | l’indirizzo della macchina nella mesh |
| `master_ip` | dalla fleet | l’indirizzo del master nella mesh |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | puoi misurarle con `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` sul master, `172.128.0.0/24` sui node | |
| `pub_iface` | dalla rotta predefinita | l’interfaccia di rete sul lato LAN |
| `daily_vpn_restart` | `07:00` | con un valore vuoto il riavvio giornaliero è disattivato |
| `weekly_update` | `Sun *-*-* 00:00` | con un valore vuoto l’aggiornamento settimanale è disattivato |

`kiwi-server roles -v` e `kiwi-server modules -v` elencano tutte le
impostazioni con il loro valore predefinito.

## Controllare quello che hai scritto { #checking-what-you-wrote }

kiwi-server può controllare il file fleet al posto tuo e mostrarti come
interpreta un host.

```bash
kiwi-server validate fleet.yaml          # errori e avvisi
kiwi-server show fleet.yaml papaya          # la configurazione effettiva di un host, con i segreti oscurati
```

kiwi-server controlla anche il dominio. Rifiuta `.local` e dà un avviso per
`.lan` e per i domini di primo livello pubblici (vedi
[DNS](../network/dns.md#names-servicehostnamehome)).

## Riprendere una macchina v1 { #taking-over-a-v1-machine }

Una macchina su cui girava uno dei vecchi stack v1 può entrare nella fleet
senza perdere i suoi dati. Il runtime predefinito ora è podman, e lo script del
ruolo non ferma i container docker ancora in esecuzione. Quindi imposta
`runtime: docker`, oppure ferma prima il vecchio stack. Poi imposta
`docker_subnet` sulla sottorete usata dal vecchio stack e rinomina le cartelle
dei dati con i nomi dei nuovi moduli (`kmvpn-server` → `km-vpn-server`,
`knvault` → `kn-vault`, …). In questo modo i container mantengono i loro
indirizzi, e wg-easy mantiene i suoi peer.
