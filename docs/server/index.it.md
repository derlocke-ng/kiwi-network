# kiwi-server

kiwi-server è lo strumento con cui crei e gestisci una Kiwi Network. Descrivi
tutte le macchine in un solo file, `fleet.yaml`, e kiwi-server le prepara a
partire da quel file: non devi installarle e configurarle a mano una per una.

Per ogni host kiwi-server crea una **ISO di installazione automatica**, cioè
un’immagine di installazione che installa Fedora CoreOS, uCore o Debian senza
fare domande e poi spegne la macchina. Dopodiché kiwi-server **applica** il
ruolo della macchina via SSH, e la macchina diventa un `kiwi-master` o un
`kiwi-node`. Da quel momento kiwi-server continua a occuparsi della fleet: registra i
client WireGuard, legge lo stato di ogni macchina, custodisce i segreti, fa il
backup della fleet e sblocca i dischi cifrati.

kiwi-server esiste come strumento a riga di comando (CLI), `kiwi-server`, e
come app GTK4, **Kiwi Server**. Entrambi si installano in `~/.local` e non
richiedono i permessi di root.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Ultima release: **v2.42.0**. È disponibile nel [catalogo Kiwi](../desktop/catalogs.md).
- kiwi-server si basa su [kiwi-modules](single.md) v0.23.0, che contiene i
  moduli e il programma che li genera, e su [kiwi-stack](single.md) v0.5.0, la
  parte che gira su ogni macchina. Una copia di entrambi è inclusa in
  kiwi-server, fissata a un tag preciso.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Installazione { #install }

```bash
kiwi install kiwi-server        # con kiwi-updater
```

In alternativa puoi installarlo da un clone del repository: esegui
`./install.sh install` e poi `kiwi-server doctor`.

kiwi-server richiede Python 3.9+ con PyYAML e Jinja2, e i programmi `openssl` e
`ssh`. Per l’archivio dei segreti serve `age`. Per creare le ISO ti servono
`butane`, `coreos-installer` e `xorriso`, e per Debian anche `cpio`, `gzip` e
`curl`. Su Silverblue o Bluefin non aggiungere questi pacchetti al sistema con
il layering: crea invece un’unica immagine container con tutti gli strumenti
per le ISO:

```bash
kiwi-server toolchain build     # usata automaticamente quando mancano gli strumenti
```

`qrencode` (per `enroll --qr`), `shellcheck` e `docker compose` sono
facoltativi.

## Da zero a una rete funzionante { #from-nothing-to-a-running-network }

Con i comandi qui sotto passi da una cartella vuota a una rete funzionante, con
un master, un node e i tuoi dispositivi:

```bash
kiwi-server init                          # un fleet.yaml commentato
$EDITOR fleet.yaml                        # host, ruoli, la tua chiave SSH, il disco di installazione
kiwi-server secrets init fleet.yaml       # facoltativo: secrets/ come unico archivio cifrato con age
kiwi-server validate fleet.yaml

# il master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   avvia la macchina dalla ISO: si installa e si spegne; poi riaccendila
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# ogni node: prima il suo client WireGuard, poi il supporto di installazione, poi il ruolo
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# i tuoi dispositivi
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # che cosa riporta ogni macchina
```

Per impostazione predefinita una ISO di installazione **non contiene nessuno
dei segreti dello stack**. Contiene soltanto il sistema di base: il ruolo e il
suo stack arrivano sulla macchina dopo, con `apply`. Se una macchina non è
raggiungibile via SSH, `build --offline` mette invece sulla ISO l’intero ruolo
con i suoi segreti. Una ISO del genere non va caricata nell’archivio ISO di un
provider di hosting, e dopo l’installazione va cancellata.

**Se non vuoi usare nessuna ISO,** `kiwi-server script fleet.yaml papaya`
stampa lo script per una macchina che hai installato tu. Con `--offline` lo
script contiene l’intero ruolo.

Su un VPS di netcup, `kiwi-server vps install fleet.yaml sorbet` cancella il
server e installa la ISO tramite l’API di netcup, così nessuno deve stare
davanti a una console. Finora netcup è l’unico provider di hosting con cui
funziona. Altri sono [previsti](roadmap.md#more-hosters-and-network-boot).

## Comandi { #commands }

| Comando | Che cosa fa |
|---|---|
| `init [fleet.yaml]` | Scrive il file fleet di esempio. `--domain` imposta il dominio; quello predefinito è `home`. |
| `validate fleet.yaml [host…]` | Controlla il file fleet. Genera tutti gli stack, così trova anche gli errori nei moduli. |
| `list` / `show fleet.yaml <host>` | Il primo elenca gli host e ciò che è stato generato per ciascuno. Il secondo mostra la configurazione effettiva di un host, con i segreti oscurati. |
| `render fleet.yaml [host…]` | Scrive in `output/<host>/` gli script dei ruoli, gli stack e le configurazioni di installazione. |
| `build fleet.yaml [host…]` | Genera la configurazione e poi crea la ISO. Per impostazione predefinita la ISO contiene solo il sistema di base; con `--offline` contiene l’intero ruolo. |
| `script fleet.yaml <host>` | Stampa lo script per una macchina qualsiasi. Con `--offline` lo script contiene l’intero ruolo. |
| `apply fleet.yaml <host…>` | Genera di nuovo la configurazione, manda il ruolo alla macchina via SSH e lo esegue lì (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Mostra che cosa riportano le macchine: ruolo, stack, problemi, dischi, backup e certificati. |
| `enroll fleet.yaml <host\|name>` | Crea un client WireGuard sul master, oppure ne recupera uno che esiste già (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Gestisce `secrets/` come un unico file cifrato con age, che quando lo sblocchi viene aperto in memoria (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Mostra le password generate di un host. |
| `ca fleet.yaml` | Mostra la CA della fleet. |
| `mtu fleet.yaml <node\|device\|address>` | Misura la MTU reale di un tunnel e ti dice quale valore impostare (`--write`). |
| `openwrt fleet.yaml` | Scrive uno script che collega un router OpenWrt alla mesh ([Router](../network/routers.md)). |
| `backup` / `restore` / `prune` | Fanno il backup della cartella della fleet sui node, la ripristinano da lì ed eliminano i vecchi backup delle macchine ([Gestione](operations.md)). |
| `unlock fleet.yaml <host>` | Inoltra un anello Tang a una macchina che all’avvio aspetta lo sblocco del suo disco cifrato ([Gestione](operations.md)). |
| `vps login\|list\|probe\|install` | Lavorano con l’API del Server Control Panel di netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Mostrano che cosa è disponibile, con ogni impostazione e il suo valore predefinito. |
| `toolchain [status\|build]`, `doctor` | Gestiscono gli strumenti per le ISO e controllano questo computer. |

Tutti i comandi accettano `--porcelain` (output in JSON), `-o/--output-dir`,
`--quiet` e `-v`. `kiwi-server <command> -h` spiega un singolo comando.

## L’app { #the-app }

L’app **Kiwi Server** apre la fleet su cui hai lavorato l’ultima volta. Nella
barra laterale trovi una panoramica, una riga per ogni host e i valori
predefiniti. La scheda *Overview* di un host mostra le informazioni aggiornate
di `kiwi-server status`: l’app le recupera una volta al minuto, finché la
finestra è in primo piano, via SSH e in sola lettura. La scheda *Settings* di
un host è un form costruito a partire dai ruoli e dai moduli. *Apply*,
*Build* e *Render* eseguono lo strumento a riga di comando e ne mostrano
l’output man mano che arriva. Prima di partire, *Build* elenca i dischi che
cancellerà. *Unlock* e *Lock* aprono e chiudono l’archivio dei segreti. L’app
scrive YAML semplice: se salva un file fleet che avevi scritto a mano, i
commenti vanno persi.

## Da tenere a mente { #mind }

!!! danger "Le ISO cancellano il disco indicato, senza chiedere"
    Una ISO di installazione cancella il disco per cui è stata creata appena
    una macchina viene avviata da quella ISO, senza chiedere nulla. Metti un’etichetta alle
    tue ISO. È proprio per questo che `build` pretende l’impostazione `disk:`.

- **L’output contiene segreti**: hash delle password, chiavi WireGuard, chiavi
  TLS e chiavi LUKS. I file vengono scritti con i permessi 0600, e git ignora
  `output/`. Tratta con la stessa cura le ISO create con `--offline`.
- **Le password dei servizi vengono generate** a partire da `secrets/seed`, se
  non le scrivi nel file fleet. `validate` ti avvisa se nel file fleet ci sono
  password scritte in chiaro, e `kiwi-server secrets show` stampa quelle
  generate. Una macchina rifiuta un `apply` preparato con un seed diverso.
- **Le chiavi host SSH** vengono registrate in `secrets/known_hosts` la prima
  volta che kiwi-server si collega a una macchina. Se in seguito la chiave di
  una macchina cambia, la connessione viene rifiutata. Dopo aver reinstallato
  una macchina, cancella la sua riga da quel file.
- **Lo script di un ruolo gira come root.** Prima di fidarti di un ruolo che
  non hai scritto tu, leggi l’output di `kiwi-server script fleet.yaml <host>
  --offline`.
- **Un ruolo fallito viene segnalato.** La macchina conserva il file
  `/var/lib/kiwi-server/role.failed`, che indica il passaggio e il comando non
  riusciti, e `status` lo mostra.

## Stato { #status }

L’intero processo, dal file fleet a una macchina in funzione, è stato testato
su hardware reale tra ottobre e novembre 2026. Debian, uCore e Fedora CoreOS lo
hanno completato su due VPS, un mini PC e una VM. In una prova che simulava un
node guasto, una macchina Debian cifrata è stata ricostruita in circa 14
minuti. I backup dei node sono stati ripristinati da un node all’altro (da
papaya a lychee). La MTU del tunnel è stata misurata e regolata su connessioni
reali, comprese quelle mobili. I test automatici (CI) generano tutti i ruoli,
passano ogni script a shellcheck e validano ogni configurazione Butane.
Confrontano inoltre byte per byte quattro stack di riferimento, detti golden
stack, con l’output salvato.

La federazione tra reti non è ancora stata testata. Tutto funziona su IPv4. La ISO di
Debian esiste solo per amd64. Un control plane (`kiwi-server serve`) è previsto
e progettato, ma non ancora realizzato.

Continua con: [Il file fleet](fleet.md) · [Ruoli](roles.md) · [Moduli](modules.md) ·
[Macchine](machines.md) · [Gestione](operations.md) ·
[Una macchina senza fleet](single.md)
