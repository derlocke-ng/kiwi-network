# Moduli

Un modulo è un servizio di una macchina della Kiwi Network. Un [ruolo](roles.md) sceglie un
insieme di moduli, e il renderer li trasforma in uno **stack** per un host. Il
renderer è [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), che
kiwi-server include nel suo repository. Lo stack è un file compose, i **podman quadlet** (una
unità systemd per container), le configurazioni e le unità host, e `stack.sh`, il
manifest che li elenca tutti. [kiwi-stack](single.md) lo mette sulla macchina.
Tutto il templating avviene sulla macchina che esegue il render. Al target basta
podman 4.4 o successivo (oppure docker con il plugin compose, con `runtime: docker`).

```bash
kiwi-server modules -v      # ogni modulo e ogni impostazione con il suo default
```

## La rete { #the-network }

| Modulo | Cos'è | Gira su | Richiede | Sull'host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: il punto d'ingresso per ogni client e ogni node; la sua route predefinita è il client VPN (il doppio hop) | master | niente | `51820/udp`; la UI su `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: il tunnel a cui si appoggia ogni macchina: verso il master su un node, verso una VPN commerciale sul master | entrambi | niente | niente |
| `dns` | **Pi-hole 6**: blocca la pubblicità per la mesh o la LAN, serve i nomi della fleet e, se vuoi, i proxy SOCKS5 di Mullvad per nome | entrambi | niente | `53` su un node |
| `tor` | un proxy **Tor SOCKS5** per i client della mesh, fissato su alcuni paesi | entrambi | niente | `127.0.0.1:9050` su un node; l'indirizzo mesh `:9050` su un master |
| `reverse-proxy` | **nginx** con TLS: un server block per servizio; le pagine di amministrazione rispondono solo alla mesh; nomi pubblici opzionali con Let's Encrypt | entrambi | niente | `80`, `443` su un node, o su un master pubblico |
| `gateway` | policy routing sull'host: i client della LAN che usano questa macchina come gateway escono attraverso la VPN | node | vpn-client | un'unità host |
| `dhcp-relay` | inoltra il DHCP della LAN a Pi-hole, così Pi-hole può essere il server DHCP della LAN | node | dns | `67/udp` |

## Servizi { #services }

| Modulo | Cos'è | Gira su | Richiede |
|---|---|---|---|
| `cloud` | **Nextcloud** dai container del progetto AIO, *senza* il container master di AIO (niente socket docker, gira su podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, ricerca full-text e Whiteboard si attivano con un interruttore | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, il gestore di password compatibile con Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** e **JDownloader** dentro il namespace di rete del client VPN: niente tunnel, niente traffico | node | vpn-client |
| `sftp` | un server SFTP su una porta propria (`2224`), per prelevare i download | node | niente |
| `portainer` | **Portainer CE**, una UI web per i container (`127.0.0.1:9443`, e `portainer.<host>`) | entrambi | niente |
| `opencloud` | **OpenCloud**: file e condivisione in un unico binario Go (in prova) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**: foto e video (in prova) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: documenti scansionati con OCR e ricerca full-text (in prova) | node | vpn-client, reverse-proxy |

Gli ultimi tre non sono in nessun preset; aggiungili a `modules:`.

## Persone { #people }

| Modulo | Cos'è | Gira su | Richiede |
|---|---|---|---|
| `nostr-relay` | **strfry**, il relay su cui un hub tiene i suoi eventi (su `relay.<host>`). Da Internet, i membri possono pubblicare dopo aver dimostrato la loro chiave (NIP-42): chiavi `approved` nell'elenco firmato degli amministratori, oppure chiunque sia `registered` con un account. La mesh può sempre pubblicare | master | reverse-proxy |
| `hub` | un **hub kiwi-framework** come container (Armory di default, su `hub.<host>`), privato, semi-pubblico o pubblico | master | reverse-proxy |

Vedi [Gestire un proprio hub](../people/hubs.md).

## Backup e dischi { #backups-and-disks }

| Modulo | Cos'è | Gira su | Richiede |
|---|---|---|---|
| `backup` | i dati di questa macchina con **restic**, cifrati, verso un node backup-server: ogni notte alle `03:00` (entro i 15 minuti successivi) e con `kiwi-stack backup`. Ogni modulo dice cosa conservare di sé. Prossima release: più server e una macchina ricostruita che si ripristina da sola ([dettagli](operations.md#coming-in-the-next-release)) | entrambi | niente |
| `backup-server` | un **server REST di restic**; ogni macchina raggiunge solo il proprio repository, in sola aggiunta | node | vpn-client, reverse-proxy |
| `tang` | server **Tang** perché le macchine cifrate si sblocchino all'avvio; un anello è un server con le proprie chiavi (default `infra` sulla `7500`) | node | niente |

Vedi [Operazioni](operations.md).

## Impostazioni importanti { #important-settings }

| Modulo | Impostazione | Default | Note |
|---|---|---|---|
| vpn-server | `wg_host` | (obbligatoria) | il nome o l'IP a cui si collegano i client |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | vedi [gruppi di client](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | porte Tang per le macchine dietro NAT |
| vpn-client | `vpn_provider` | `custom` | `custom`: la configurazione WireGuard rilasciata dal master (un node); oppure un provider gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | dove si trova un'uscita commerciale |
| | `dot_providers` | `quad9` | il DNS-over-TLS di gluetun |
| | `extra_dnat_rules` | `[]` | ad es. SSH dalla mesh all'host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | solo mentre il master non è raggiungibile |
| | `dhcp_enabled` | `false` | con `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` su un master | [i proxy di Mullvad per nome](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | nodi di entrata e di uscita, `StrictNodes` |
| reverse-proxy | `public` | `false` | solo master: 80/443 con Let's Encrypt per i nomi fuori dal dominio della fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | fallo puntare a un disco grande |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | attivalo per il primo account, poi disattivalo |
| downloader | `download_dir` | (obbligatoria) | |
| nostr-relay | `members` | `approved` | oppure `registered` |
| | `write_pubkeys` | `[]` | gli amministratori: possono sempre pubblicare, e contano solo i loro elenchi di membri e di ban |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | qualsiasi hub kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | un hub semi-pubblico |
| backup | `server` | (obbligatoria) | `https://…` di un node backup-server che elenca questa macchina |
| tang | `rings` | `{ infra: "7500" }` | nome e porta |

Le password e le chiavi che ometti vengono generate dal seed della fleet.

## Nomi { #names }

Ogni modulo annuncia i suoi nomi al reverse proxy e al DNS della fleet,
sotto il nome dell'host:

| Servizio | Nome |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (qualsiasi host con `dns` e il reverse proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relay / hub | `relay.<host>` / `hub.<host>` |
| server di backup | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Container { #containers }

- Con podman, ogni servizio è un quadlet in `/etc/containers/systemd`, avviato
  tramite `kiwi-stack.target`, con il suo log nel journal. Un container che
  vive nel namespace di rete di un altro è legato a quello e riparte insieme a lui.
- I segreti vanno in file `kiwi/env/<service>.env` leggibili solo da root, mai nelle unità.
- Gli indirizzi fissi seguono lo schema della v1, così una macchina migrata li mantiene:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Gli altri moduli contano a partire da `.100`. I container senza indirizzo fisso
  usano il terzo quarto della rete (`.128/26`).
- Fedora CoreOS e uCore girano con SELinux attivo, quindi i bind mount hanno l'etichetta
  `:z`. I mount del socket dei container e di `/lib/modules` non vengono mai
  etichettati.

## Scrivere un modulo { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` dichiara i metadati del modulo e i tipi di node, le sue dipendenze,
le porte che apre sull'host, i suoi template e dove finisce il loro output, lo storage,
cosa di esso viene salvato nei backup, l'integrazione con l'host (sysctl, moduli del kernel), i server
block nginx che annuncia, gli URL stampati quando il ruolo ha finito, le sue
regole di validazione e le sue `settings`. Lo schema delle impostazioni valida il file
fleet e costruisce il modulo dell'app. I template sono Jinja2 e vedono il contesto dell'host:
il nome e il tipo dell'host, l'indirizzo di ogni modulo, la mesh, i nomi della fleet,
ogni modulo attivo e le impostazioni di ogni modulo.

Con podman, il file compose viene tradotto in quadlet. Viene tradotto solo un insieme noto di
chiavi compose, e qualsiasi altra cosa è un errore al momento del render.

I moduli vengono sviluppati e rilasciati in
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Il riferimento completo
del formato è
[docs/modules.md di kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
