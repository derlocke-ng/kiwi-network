# kiwi-server

kiwi-server crea e gestisce una Kiwi Network. Descrivi ogni macchina in
un unico `fleet.yaml`. kiwi-server crea una **ISO di installazione automatica** per ogni host,
che installa Fedora CoreOS, uCore o Debian e spegne la macchina. Poi
**applica** il ruolo via SSH, trasformando la macchina in un `kiwi-master` o
in un `kiwi-node`. Dopodiché continua a lavorare con la fleet: registra i client
WireGuard, legge lo stato di salute di ogni macchina, custodisce i segreti, fa il backup della fleet
e sblocca i dischi cifrati.

Ha una CLI, `kiwi-server`, e un'app GTK4, **Kiwi Server**. Entrambe si installano in
`~/.local` e non richiedono root.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Ultima release: **v2.42.0**. È nel [catalogo Kiwi](../desktop/catalogs.md).
- Costruito su [kiwi-modules](single.md) v0.23.0 (i moduli e il loro renderer)
  e [kiwi-stack](single.md) v0.5.0 (il lato macchina), inclusi nel repository e fissati per
  tag.

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

Oppure da un checkout: `./install.sh install`, poi `kiwi-server doctor`.

Richiede Python 3.9+ con PyYAML e Jinja2, `openssl` e `ssh`. L'archivio dei
segreti richiede `age`. Per costruire le ISO servono `butane`, `coreos-installer` e
`xorriso` (più `cpio`, `gzip` e `curl` per Debian). Su Silverblue o Bluefin,
costruiscili come un'unica immagine container invece di aggiungere pacchetti al sistema:

```bash
kiwi-server toolchain build     # usata in automatico quando mancano gli strumenti
```

`qrencode` (per `enroll --qr`), `shellcheck` e `docker compose` sono opzionali.

## Da zero a una rete funzionante { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # un fleet.yaml commentato
$EDITOR fleet.yaml                        # host, ruoli, la tua chiave SSH, il disco di installazione
kiwi-server secrets init fleet.yaml       # opzionale: secrets/ come un unico archivio cifrato con age
kiwi-server validate fleet.yaml

# il master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   avvialo; si installa e si spegne; riaccendilo
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# ogni node: prima il suo client WireGuard, poi il supporto, poi il ruolo
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# i tuoi dispositivi
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # cosa riporta ogni macchina
```

Di default i supporti di installazione non contengono **nessuno dei segreti dello stack**: solo il sistema di base.
Il ruolo e il suo stack arrivano con `apply`. Se una macchina non è raggiungibile via
SSH, `build --offline` mette invece l'intero ruolo e i suoi segreti sulla ISO.
Non caricare una ISO del genere nell'archivio ISO di un provider ed eliminala dopo l'installazione.

**Niente ISO?** `kiwi-server script fleet.yaml papaya` stampa lo script per una
macchina che hai installato tu (`--offline` per l'intero ruolo).

Su una VPS netcup, `kiwi-server vps install fleet.yaml sorbet` cancella il server e
installa la ISO tramite l'API di netcup.

## Comandi { #commands }

| Comando | Cosa fa |
|---|---|
| `init [fleet.yaml]` | scrive il file fleet di esempio (`--domain`, default `home`) |
| `validate fleet.yaml [host…]` | lo controlla, eseguendo il render di ogni stack per intercettare gli errori dei moduli |
| `list` / `show fleet.yaml <host>` | gli host e ciò che è stato generato / la configurazione effettiva di un host, con i segreti mascherati |
| `render fleet.yaml [host…]` | script dei ruoli, stack e configurazioni di installazione in `output/<host>/` |
| `build fleet.yaml [host…]` | render, poi la ISO: di default solo il sistema di base, `--offline` per l'intero ruolo |
| `script fleet.yaml <host>` | lo script per qualsiasi macchina (`--offline` per l'intero ruolo) |
| `apply fleet.yaml <host…>` | rifà il render, invia il ruolo via SSH e lo esegue (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | cosa riportano le macchine: ruolo, stack, problemi, dischi, backup, certificati |
| `enroll fleet.yaml <host\|name>` | crea o recupera un client WireGuard sul master (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` come un unico file cifrato con age, aperto in memoria (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | le password generate di un host |
| `ca fleet.yaml` | la CA della fleet |
| `mtu fleet.yaml <node\|device\|address>` | misura l'MTU reale di un tunnel e dice cosa impostare (`--write`) |
| `openwrt fleet.yaml` | uno script che collega un router OpenWrt alla mesh ([Router](../network/routers.md)) |
| `backup` / `restore` / `prune` | la directory della fleet verso i node e ritorno; rimozione dei vecchi backup delle macchine ([Operazioni](operations.md)) |
| `unlock fleet.yaml <host>` | inoltra un anello Tang a una macchina in attesa all'avvio ([Operazioni](operations.md)) |
| `vps login\|list\|probe\|install` | l'API del Server Control Panel di netcup |
| `roles [-v]`, `modules [-v]`, `targets` | cosa è disponibile, con ogni impostazione e il suo default |
| `toolchain [status\|build]`, `doctor` | gli strumenti per le ISO; controlla questa macchina |

Ogni comando accetta `--porcelain` (JSON), `-o/--output-dir`, `--quiet` e
`-v`. `kiwi-server <command> -h` spiega un singolo comando.

## L'app { #the-app }

**Kiwi Server** apre la tua ultima fleet. La barra laterale ha una panoramica, una riga per
host e i default. La *Overview* di un host mostra dati in tempo reale da
`kiwi-server status` (interrogato una volta al minuto mentre la finestra ha il focus,
in sola lettura via SSH). Le sue *Settings* sono un modulo costruito dai ruoli e dai moduli.
*Apply*, *Build* e *Render* eseguono la CLI e ne mostrano l'output in diretta, e *Build*
elenca i dischi che cancellerà prima di partire. *Unlock* e *Lock* aprono e
chiudono l'archivio dei segreti. L'app scrive YAML semplice, quindi i commenti in un
file fleet scritto a mano vanno persi quando salva.

## Attenzione { #mind }

!!! danger "Le ISO cancellano il disco che viene loro indicato"
    All'avvio, senza chiedere. Etichettale. `disk:` è obbligatorio per `build`
    proprio per questo motivo.

- **L'output contiene segreti**: hash delle password, chiavi WireGuard, chiavi TLS, chiavi
  LUKS. I file vengono scritti con permessi 0600 e `output/` è ignorato da git. Tratta allo stesso modo le ISO create
  con `--offline`.
- **Le password dei servizi vengono generate** da `secrets/seed` quando le ometti
  dal file fleet. `validate` avvisa se ci sono password scritte nel file.
  `kiwi-server secrets show` le stampa. Una macchina rifiuta un apply fatto con un
  seed diverso.
- **Le chiavi host SSH** vengono registrate in `secrets/known_hosts` al primo contatto, e
  una chiave cambiata viene rifiutata (dopo una reinstallazione, elimina la riga).
- **Uno script di ruolo gira come root.** Leggi `kiwi-server script fleet.yaml <host>
  --offline` prima di fidarti di un ruolo che non hai scritto tu.
- **Un ruolo fallito lo dice.** La macchina conserva `/var/lib/kiwi-server/role.failed`
  (il passo e il comando), e `status` lo mostra.

## Stato { #status }

La pipeline è stata provata su hardware reale a ottobre e novembre 2026. Debian,
uCore e Fedora CoreOS sono stati avviati dall'inizio alla fine su due VPS, un mini PC e una
VM, e un'esercitazione con un node guasto ha ricostruito una macchina Debian cifrata in circa 14
minuti. I backup dei node sono stati ripristinati da un node su un altro (da papaya a
lychee), e l'MTU del tunnel è stato misurato e regolato su percorsi reali, compresi
quelli mobili. La CI esegue il render di ogni ruolo, passa ogni script a shellcheck, valida ogni
configurazione Butane e fissa quattro stack di riferimento byte per byte.

Non ancora provato: la federazione tra reti. Tutto è IPv4. La ISO Debian è solo amd64. Un
control plane pianificato (`kiwi-server serve`) è progettato ma non realizzato.

Continua a leggere: [Il file fleet](fleet.md) · [Ruoli](roles.md) · [Moduli](modules.md) ·
[Macchine](machines.md) · [Operazioni](operations.md) ·
[Una macchina senza fleet](single.md)
