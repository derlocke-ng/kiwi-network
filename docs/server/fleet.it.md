# Il file fleet

`fleet.yaml` descrive ogni macchina che kiwi-server costruisce. Ha due chiavi:
`defaults`, che vale per ogni host, e `hosts`, con una voce per ogni
macchina. Tutto ciò che un host imposta sovrascrive i default. `kiwi-server init` scrive
un punto di partenza commentato, e il riferimento completo è
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Un host ha un **target** (cosa viene installato) e un **ruolo** (cosa diventa):

- `target`: `coreos`, `ucore` (il default) o `debian`. Vedi [Macchine](machines.md).
- `role`: `bare` (il default), `master` o `node`. Vedi [Ruoli](roles.md).

## Esempio { #example }

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
  sorbet:                              # il master, una VPS Debian
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
        wg_host: vpn.example.org     # dove si collegano client e node

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

Non contiene password dei servizi. Ogni password che ometti viene
generata da `secrets/seed`, e `kiwi-server secrets show fleet.yaml papaya`
le stampa. Nemmeno le configurazioni WireGuard dei node vi compaiono:
`kiwi-server enroll` scrive `secrets/<hostname>.conf`, che ogni node trova da
solo, e l'indirizzo mesh del node viene letto da lì.

## Default { #defaults }

| Chiave | Default |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | nessuno; obbligatorio per `build`, deve iniziare con `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; indica un `password_hash` per la console |
| `network` | `dhcp: true`; statico con `address` (CIDR), `gateway`, `dns`, oppure un `iprange` che assegna gli indirizzi nell'ordine del file |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (o `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | gli anelli Tang a cui legare il disco (vedi [Operazioni](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | dove viene salvato il backup della directory della fleet (`hosts: []`, `keep: 10`) |
| `vps` | `server:` id, nome o nickname di un server netcup |

## Come si combinano le impostazioni { #how-settings-combine }

- Gli host sovrascrivono i default **chiave per chiave**. Le liste `admin.ssh_keys`,
  `debian.packages`, `debian.kernel_arguments` e le liste `coreos.*` invece si *aggiungono*
  ai default.
- Un ruolo a moduli tiene le sue impostazioni in un blocco che porta il nome del ruolo (`master:`,
  `node:`): prima le **impostazioni dello stack**, poi **un blocco per modulo**.
- `modules:` in quel blocco **sostituisce** l'elenco dei moduli del preset. I moduli
  richiesti si aggiungono da soli.
- Le **impostazioni di tipo file** (certificati, configurazioni) sono percorsi relativi al file
  fleet. Il loro contenuto viene incorporato nello script di ruolo dell'host.
- Un'impostazione indicata senza valore significa il default. Una chiave scritta male è un errore
  con un suggerimento.

## Impostazioni dello stack { #stack-settings }

| Impostazione | Default | Note |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` o `minimal` |
| `runtime` | `podman` | podman quadlet; `docker` esegue docker compose |
| `auto_update` | `registry` | `podman auto-update` settimanale; `off`: le immagini cambiano con un apply |
| `docker_dir` | `/home/user/docker` | lo stack e i suoi dati |
| `service_user` | l'utente amministratore | proprietario delle directory dei dati |
| `vpn_ip` | dalla configurazione WireGuard | l'indirizzo mesh della macchina |
| `master_ip` | dalla fleet | l'indirizzo mesh del master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | misura con `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | dalla route predefinita | l'interfaccia LAN |
| `daily_vpn_restart` | `07:00` | vuoto: mai |
| `weekly_update` | `Sun *-*-* 00:00` | vuoto: mai |

`kiwi-server roles -v` e `kiwi-server modules -v` elencano ogni impostazione con il suo
default.

## Controllare ciò che hai scritto { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # errori e avvisi
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server controlla anche il dominio: `.local` viene rifiutato, `.lan` e i domini
di primo livello pubblici ricevono un avviso (vedi [DNS](../network/dns.md#names-servicehostnamehome)).

## Prendere in carico una macchina v1 { #taking-over-a-v1-machine }

Una macchina che eseguiva uno dei vecchi stack v1 può essere presa in carico senza perdere
dati. Il runtime predefinito ora è podman, e lo script di ruolo non ferma i
container docker. Quindi imposta `runtime: docker`, oppure ferma prima il vecchio stack.
Poi imposta `docker_subnet` su quello che usava il vecchio stack, e rinomina le directory
dei dati con i nomi dei moduli (`kmvpn-server` → `km-vpn-server`, `knvault` →
`kn-vault`, …). I container mantengono i loro indirizzi e wg-easy mantiene i suoi peer.
