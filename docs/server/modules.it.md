# Moduli

Un modulo è un servizio che una macchina della tua Kiwi Network può eseguire:
per esempio il server VPN, il server DNS che blocca la pubblicità, Nextcloud o
il backup notturno. Con i moduli decidi che cosa fa ogni macchina. Un
[ruolo](roles.md) porta con sé un insieme di moduli, che puoi modificare nel
file fleet.

Un generatore trasforma i moduli di un host in uno **stack**, cioè tutto ciò di
cui la macchina ha bisogno per eseguire quei servizi. Il generatore è
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), e kiwi-server ne
include una copia. Uno stack è composto da un file compose, dai **quadlet di
podman** (un’unità systemd per ogni container), dai file di configurazione,
dalle unità systemd per l’host e da `stack.sh`, un manifest che li elenca
tutti. Sulla macchina lo stack viene installato da [kiwi-stack](single.md).
I template vengono completati con i valori sul computer che genera lo
stack. Alla
macchina che lo esegue basta podman 4.4 o successivo, oppure docker con il
plugin compose se imposti `runtime: docker`.

Questo comando elenca tutti i moduli con le loro impostazioni.

```bash
kiwi-server modules -v      # tutti i moduli e tutte le impostazioni, con i valori predefiniti
```

## La rete { #the-network }

Questi moduli costruiscono la mesh, cioè la rete WireGuard privata che collega
tutte le tue macchine, e stabiliscono come il suo traffico arriva a Internet.

| Modulo | Che cos’è | Gira su | Richiede | Sull’host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, il server WireGuard a cui si collegano tutti i client e tutti i node. La sua rotta predefinita è il client VPN, quindi il traffico verso Internet prosegue attraverso la VPN commerciale del master (il doppio hop) | master | nessuno | `51820/udp`, e l’interfaccia web su `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, il tunnel VPN attraverso cui passa il traffico di una macchina. Su un node il tunnel porta al master, sul master porta a una VPN commerciale | entrambi | nessuno | nessuno |
| `dns` | **Pi-hole 6**, un server DNS che blocca la pubblicità per la mesh o per la LAN. Risponde per i nomi della fleet e può fornire anche i nomi dei proxy SOCKS5 di Mullvad | entrambi | nessuno | `53` su un node |
| `tor` | Un proxy **SOCKS5 di Tor** per i client della mesh. Usa soltanto nodi Tor nei paesi che imposti | entrambi | nessuno | `127.0.0.1:9050` su un node, e l’indirizzo nella mesh `:9050` su un master |
| `reverse-proxy` | **nginx** con TLS. Ha un blocco server per ogni servizio, così ogni servizio è raggiungibile con un nome tutto suo. Le pagine di amministrazione sono raggiungibili solo dalla mesh. I nomi pubblici con certificati Let’s Encrypt sono facoltativi | entrambi | nessuno | `80`, `443` su un node, oppure su un master con `public` attivo |
| `gateway` | Policy routing sull’host. I dispositivi della LAN che usano questa macchina come gateway mandano il loro traffico Internet attraverso la VPN | node | vpn-client | un’unità systemd sull’host |
| `dhcp-relay` | Inoltra a Pi-hole le richieste DHCP della LAN, così Pi-hole può fare da server DHCP per la LAN | node | dns | `67/udp` |

## Servizi { #services }

| Modulo | Che cos’è | Gira su | Richiede |
|---|---|---|---|
| `cloud` | **Nextcloud**, composto dai container del progetto AIO ma *senza* il container master di AIO. Per questo non ha bisogno del socket di docker e funziona con podman. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, la ricerca full-text e Whiteboard si possono attivare o disattivare uno per uno | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, un gestore di password compatibile con Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** e **JDownloader**. Entrambi girano nel namespace di rete del client VPN: usano la sua connessione e non ne hanno una propria. Quando il tunnel non è attivo non trasferiscono nulla | node | vpn-client |
| `sftp` | Un server SFTP su una porta dedicata (`2224`), da cui puoi recuperare i file scaricati | node | nessuno |
| `portainer` | **Portainer CE**, un’interfaccia web per i container. È raggiungibile su `127.0.0.1:9443` e su `portainer.<host>` | entrambi | nessuno |
| `opencloud` | **OpenCloud**, per i file e la loro condivisione, in un unico binario Go (da provare) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, per foto e video (da provare) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, per i documenti scansionati, con OCR e ricerca full-text (da provare) | node | vpn-client, reverse-proxy |

Gli ultimi tre moduli non fanno parte di nessun preset. Per usarne uno,
aggiungilo a `modules:`.

## Persone { #people }

Un hub è il sito di una comunità, nel browser. Questi due moduli eseguono un
hub e il relay su cui l’hub salva i suoi eventi.

| Modulo | Che cos’è | Gira su | Richiede |
|---|---|---|---|
| `nostr-relay` | **strfry**, il relay su cui un hub conserva i suoi eventi. È raggiungibile su `relay.<host>`. Chi si collega da Internet può pubblicare solo se è membro e ha dimostrato di possedere la propria chiave (NIP-42). Con `approved` i membri sono le chiavi di una lista firmata dagli amministratori. Con `registered` è membro chiunque abbia un account. Le connessioni dalla mesh possono sempre pubblicare | master | reverse-proxy |
| `hub` | Un **hub kiwi-framework** che gira come container. Per impostazione predefinita è Armory, ed è raggiungibile su `hub.<host>`. Un hub può essere privato, semipubblico o pubblico | master | reverse-proxy |

Vedi [Gestire il tuo hub](../people/hubs.md).

## Backup e dischi { #backups-and-disks }

| Modulo | Che cos’è | Gira su | Richiede |
|---|---|---|---|
| `backup` | Fa il backup cifrato dei dati di questa macchina con **restic**, su un node su cui gira il modulo backup-server. Il backup parte ogni notte alle `03:00`, o fino a 15 minuti dopo, e ogni volta che esegui `kiwi-stack backup`. Ogni modulo stabilisce quali dei suoi dati finiscono nel backup. Per la prossima release sono previsti i backup su più server e una macchina ricostruita che ripristina da sé i propri dati ([dettagli](operations.md#coming-in-the-next-release)) | entrambi | nessuno |
| `backup-server` | Un **server REST di restic** che conserva i backup. Ogni macchina raggiunge soltanto il proprio repository, e può solo aggiungervi dati (sola aggiunta, append-only) | node | vpn-client, reverse-proxy |
| `tang` | Server **Tang**, che permettono alle macchine con dischi cifrati di sbloccarli all’avvio senza che qualcuno sia presente. Un anello è un server Tang con le proprie chiavi. Il valore predefinito è un anello chiamato `infra` sulla porta `7500` | node | nessuno |

Vedi [Gestione](operations.md).

## Impostazioni importanti { #important-settings }

| Modulo | Impostazione | Valore predefinito | Note |
|---|---|---|---|
| vpn-server | `wg_host` | (obbligatoria) | il nome o l’indirizzo IP a cui si collegano i client |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | vedi [gruppi di client](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | porte del master attraverso cui le macchine dietro NAT raggiungono il loro anello Tang |
| vpn-client | `vpn_provider` | `custom` | `custom` usa la configurazione WireGuard emessa dal master, ed è ciò che serve a un node. Altrimenti indica un provider di gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | i paesi e le città dei server della VPN commerciale da usare |
| | `dot_providers` | `quad9` | il provider DNS-over-TLS usato da gluetun |
| | `extra_dnat_rules` | `[]` | regole di inoltro aggiuntive, per esempio per SSH dalla mesh verso l’host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | usati solo quando il master non è raggiungibile |
| | `dhcp_enabled` | `false` | si usa insieme a `dhcp_start`, `dhcp_end` e `dhcp_router` |
| | `mullvad_socks` | `true` su un master | [i proxy di Mullvad per nome](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | i paesi dei nodi di ingresso e di uscita di Tor, imposti con `StrictNodes` |
| reverse-proxy | `public` | `false` | solo sul master. Apre 80/443 e usa Let’s Encrypt per i nomi fuori dal dominio della fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | indica una cartella su un disco capiente |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | attivala per creare il primo account, poi disattivala di nuovo |
| downloader | `download_dir` | (obbligatoria) | |
| nostr-relay | `members` | `approved` | oppure `registered` |
| | `write_pubkeys` | `[]` | le chiavi degli amministratori. Gli amministratori possono sempre pubblicare, e valgono solo le liste dei membri e le liste di ban pubblicate da loro |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | l’immagine di un qualsiasi hub costruito con kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | da impostare per un hub semipubblico |
| backup | `server` | (obbligatoria) | l’indirizzo `https://…` di un node backup-server che elenca questa macchina |
| tang | `rings` | `{ infra: "7500" }` | nome e porta di ogni anello |

Se ometti una password o una chiave, viene generata a partire dal seed della
fleet.

## Nomi { #names }

Ogni modulo registra i nomi dei suoi servizi nel reverse proxy e nel DNS della
fleet. Ogni nome è composto dal nome del servizio e dal nome dell’host.

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

- Con podman ogni servizio è un quadlet in `/etc/containers/systemd`. I quadlet
  vengono avviati tramite `kiwi-stack.target`, e i loro log finiscono nel
  journal di systemd. Un container che condivide il namespace di rete di un
  altro container è legato a quel container, e quindi viene riavviato insieme
  a quello.
- I segreti vengono scritti in file `kiwi/env/<service>.env` leggibili solo da
  root. Non finiscono mai nelle unità.
- I container hanno indirizzi fissi che seguono lo schema di indirizzamento
  della v1, così una macchina migrata dalla v1 mantiene i suoi indirizzi. Sono
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` e sftp
  `.251`. Gli altri moduli ricevono indirizzi a salire da `.100`. I container
  senza indirizzo fisso ne ricevono uno dal terzo quarto della rete
  (`.128/26`).
- Fedora CoreOS e uCore funzionano con SELinux attivo, quindi i bind mount
  ricevono l’etichetta `:z`. I mount del socket dei container e di
  `/lib/modules` non vengono mai etichettati.

## Scrivere un modulo { #writing-a-module }

Un modulo è una cartella con i file seguenti.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` descrive il modulo. Dichiara i metadati del modulo e i tipi di
node su cui gira, le sue dipendenze e le porte che apre sull’host. Indica i
template del modulo e dove viene scritto il loro output, lo spazio di
archiviazione e quali dei suoi dati finiscono nel backup. Dichiara inoltre
l’integrazione con l’host (sysctl e moduli del kernel), i blocchi server di
nginx che il modulo registra, gli URL stampati quando il ruolo ha finito, le
regole di validazione e le impostazioni del modulo (`settings`).

Lo schema delle impostazioni serve a due cose: convalida il file fleet, e l’app
kiwi-server lo usa per costruire il form delle impostazioni. I template sono
scritti in Jinja2 e possono usare il contesto dell’host, che contiene il nome e
il tipo dell’host, l’indirizzo di ogni modulo, la mesh, i nomi della fleet, i
moduli attivi e le impostazioni di tutti i moduli.

Con podman il file compose viene tradotto in quadlet. La traduzione supporta un
insieme fisso di chiavi compose, e qualsiasi altra chiave provoca un errore
quando lo stack viene generato.

I moduli vengono sviluppati e pubblicati in
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Il riferimento
completo del formato è
[docs/modules.md di kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
