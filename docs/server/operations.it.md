# Operazioni

Il lavoro quotidiano su una fleet in funzione, tutto dalla macchina dell'operatore.

## Stato { #status }

```bash
kiwi-server status fleet.yaml            # ogni host
kiwi-server status fleet.yaml papaya        # uno solo
```

Ogni macchina riporta via SSH (in sola lettura): il suo ruolo, il suo stack, i problemi (un
ruolo fallito, un container fermo), i suoi dischi e se sono cifrati o
bloccati, i suoi backup, e quanto manca alla scadenza dei suoi certificati. Un node di backup riporta
anche la sua capacità. L'app Kiwi Server mostra le stesse cose nella *Overview*
di ogni host.

## Segreti { #secrets }

Tutto ciò che è segreto si trova in `secrets/` accanto al file fleet: il seed da cui derivano
tutte le password generate, la CA della fleet, le configurazioni WireGuard, le chiavi LUKS e
le chiavi host SSH.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ diventa un unico file cifrato con age
kiwi-server secrets unlock fleet.yaml    # lo apre in memoria (--for 8h; 0 lo tiene aperto)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` conserva una chiave nel portachiavi di GNOME (GNOME Keyring) e mostra una **chiave di recupero**
una sola volta. Mentre l'archivio è aperto, qualsiasi cosa giri con il tuo utente può leggerlo.

## Backup della fleet stessa { #backing-up-the-fleet-itself }

Dopo ogni render o build riuscito, la directory della fleet viene cifrata
(AES-256 con PBKDF2, 600.000 iterazioni) e copiata sui node elencati in
`backup.hosts`, che conservano le dieci copie più recenti. Su una macchina nuova:

```bash
kiwi-server restore --from core@lychee.home  # di nuovo la directory della fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # oppure una copia in una directory, in qualsiasi momento
```

## Backup dei dati delle macchine { #backing-up-the-machines-data }

Dai a un node il modulo `backup-server` (un server REST di restic), e a ogni
macchina di cui vuoi il backup il modulo `backup`, che punta a quel node:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Ogni notte alle 03:00 (entro i 15 minuti successivi) restic invia, cifrato, ciò che ogni modulo chiede di conservare.
Ogni macchina può raggiungere solo il proprio repository, e può solo aggiungervi dati.
Per questo la rimozione dei vecchi snapshot parte dalla macchina dell'operatore:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # sulla macchina
kiwi-server prune fleet.yaml            # conserva 7 giornalieri, 4 settimanali, 6 mensili
```

Un ripristino è stato provato da node a node: i backup di papaya su lychee.

### In arrivo nella prossima release { #coming-in-the-next-release }

!!! info "Sul branch `several-servers`"
    Questo lavoro è stato pubblicato nei branch `several-servers` di kiwi-modules e
    kiwi-server, ma non è ancora stato unito né rilasciato. I server multipli e il
    ripristino automatico sono stati provati su hardware. Il controllo di salute della VPN no.

- **Più server di backup.** `backup.servers` accetta una lista, e ogni server
  riceve una copia completa tutta sua. Se un server si guasta, manca solo la sua copia.
  Un ripristino prende la copia più recente da qualunque server la abbia, e
  `kiwi-stack snapshots` le elenca server per server. Il singolo `server`
  funziona ancora.
- **Una macchina ricostruita si ripristina da sola.** Se una macchina trova sé stessa nei
  backup ma non ne ha fatto nessuno (una ricostruzione), ripristina ogni modulo da
  sola prima del suo primo backup, poi fa i backup come prima (`backup.restore:
  auto`, il default). Con `hold` aspetta `kiwi-stack restore` o
  `kiwi-stack backup --new`.
- **Pulizia con un timer.** `kiwi-server prune fleet.yaml --every week` (o
  `day`) installa un timer utente systemd sul tuo computer, l'unico posto che
  ha le chiavi che possono cancellare. Un'esecuzione saltata avviene al login successivo.
  `kiwi-server status` mostra ogni copia di backup, e avvisa quando un node di backup
  non viene ripulito da tre settimane.
- **Un'uscita commerciale bloccata riparte da capo.** gluetun riceve un controllo di salute. Dopo
  cinque minuti in cattivo stato il container viene terminato, e al riavvio successivo sceglie
  un altro server.

## Dischi cifrati e sblocco { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) si installa con una chiave monouso che digiti al
  primo avvio (`secrets/luks/<host>.once`). Il primo `apply` la sostituisce
  con `secrets/luks/<host>.key`, e un master riceve anche una nuova chiave di volume.
  Perdere quel file di chiave blocca il disco, quindi tieni un backup della fleet.
- **CoreOS / uCore** cifrano durante l'installazione tramite Ignition (con circa 4 GiB di
  RAM al primo avvio).
- **Gli anelli Tang** permettono alle macchine cifrate di sbloccarsi all'avvio senza che ci sia
  una persona presente. Un node esegue il modulo `tang` (ogni anello è un server Tang con le
  proprie chiavi, `infra` sulla porta 7500 di default), e il blocco `unlock:` di un host lega
  il suo disco agli anelli con una soglia.
- **SSH nell'initramfs** (`unlock.ssh: true`: dropbear su Debian, dracut-sshd
  su CoreOS) usa una propria chiave limitata, `secrets/unlock_ed25519`, che può
  solo eseguire lo sblocco.
- `kiwi-server unlock fleet.yaml <host>` inoltra un anello a una macchina in attesa
  all'avvio, e `--manual` consegna direttamente la chiave. Un anello `operator` viene
  servito dalla tua macchina finché serve. `vpn-server.unlock_relay`
  raggiunge le macchine dietro NAT.

## MTU del tunnel { #tunnel-mtu }

WireGuard aggiunge le proprie intestazioni, quindi un tunnel trasporta pacchetti più piccoli della
linea sottostante, e un percorso mobile ancora più piccoli. Un pacchetto
troppo grande per qualche collegamento lungo il percorso viene scartato o frammentato, e le connessioni si bloccano.
Kiwi gestisce questo problema su tre livelli:

- **Due impostazioni.** `wg_mtu` (default **1376**, un multiplo di 16 perché
  WireGuard riempie fino a multipli di 16) è l'MTU di gluetun, delle configurazioni client di wg-easy e di
  `wg0`. `bridge_mtu` (default **1500**) è l'MTU della rete dello stack.
  `validate` rifiuta un `wg_mtu` il cui pacchetto riempito più 80 byte di intestazioni
  non entra nel bridge, e qualsiasi valore sotto 1280, il minimo con cui funziona IPv6.
- **L'MSS viene limitato in entrambe le direzioni** a `wg_mtu - 40`, in wg-easy e nel client
  VPN, così TCP non prova mai un segmento che non può passare.
- **TCP sonda da solo.** Il client VPN gira con
  `net.ipv4.tcp_mtu_probing=1` e `tcp_base_mss=1024`, così una connessione che
  incontra un percorso che scarta in silenzio i pacchetti grandi trova una dimensione che funziona invece di
  bloccarsi.

### Misurare un percorso: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # un node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # un dispositivo da secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # e scrive wg_mtu nel file fleet
```

La sonda invia ping con il flag don't-fragment attraverso il tunnel, dall'interno del
namespace che lo contiene. Misura un node dal suo client VPN (il cui
firewall scarta i ping in entrata), e un dispositivo dal server WireGuard. Inizia
con un ping normale, poi prova ogni multiplo di 16 a partire da 1280 e
riporta il più grande che arriva **intero**. Mentre invia i ping legge i
contatori di riassemblaggio del kernel, così una risposta frammentata lungo il percorso e poi
ricomposta non conta come adatta.

Dice anche cosa impostare. Per un **dispositivo**, è il suo `MTU =` nella
sua configurazione WireGuard, e nessun altro ne è toccato. Per un **node**, è
`wg_mtu` su quel node e sul suo master, che `--write` scrive nel file fleet
(cambiando solo quelle righe). Un pacchetto frammentato solo in uscita e ricomposto
dall'altra estremità non si può vedere da questa parte.

I default sono stati misurati sulla fleet di test. Per un telefono con dati mobili, dove
i percorsi sono spesso solo IPv6 dietro 464XLAT con incapsulamento annidato, misura il
telefono stesso e abbassa il suo `MTU =` se la sonda lo indica.

## VPS netcup { #netcup-vpses }

netcup è il provider su cui oggi kiwi-server sa installare da solo, tramite
l'API del suo Server Control Panel. Altri provider sono
[previsti](roadmap.md#more-hosters-and-network-boot) come plugin.

```bash
kiwi-server vps login fleet.yaml         # login con device flow; il token va in secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wipe the server and install the host's ISO
```

`vps install` chiede prima di procedere, a meno che tu non passi `--yes`. Rifiuta una ISO che
contiene segreti del ruolo, un `disk:` sbagliato e la cifratura del disco di CoreOS con meno di
3500 MiB di RAM.
