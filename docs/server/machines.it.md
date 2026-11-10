# Macchine: installazione, apply, aggiornamenti

Questa pagina segue una macchina dalla sua voce nel file fleet fino a un
sistema in funzione che si aggiorna da solo. kiwi-server crea un’immagine di
installazione che installa il sistema operativo senza nessuno alla tastiera.
Poi, con il comando `apply`, prepara la macchina per il suo ruolo via SSH. Da
quel momento la macchina installa da sola i propri aggiornamenti e si riavvia
soltanto negli orari che hai autorizzato.

## Sistemi di destinazione { #targets }

Il sistema di destinazione (`target`) è il sistema operativo che kiwi-server
installa su una macchina.

| Sistema di destinazione | Che cosa viene installato | Supporto di installazione |
|---|---|---|
| `coreos` | Fedora CoreOS, canale stable | La ISO live ufficiale, personalizzata con la configurazione Ignition dell’host (Butane `fcos` 1.6.0). L’installazione non richiede una connessione di rete |
| `ucore` | Fedora CoreOS, che poi passa da sé (rebase) a un’immagine `ghcr.io/ublue-os/ucore*`. Le immagini sono `ucore-minimal`, `ucore` e `ucore-hci`, anche nelle varianti `-nvidia` / `-zfs`. Il rebase funziona come l’esempio di autorebase di uCore | Lo stesso di CoreOS, più le unità di autorebase |
| `debian` | Debian stable (trixie), amd64 | L’immagine netinst ufficiale con il preseed (il file con le risposte per l’installer) nel suo initrd, così l’installer conosce le risposte fin dalla prima domanda. I file dell’host si trovano sull’immagine in `/kiwi-server`. L’immagine si avvia ancora sia con BIOS sia con UEFI |

Su tutti i sistemi di destinazione l’utente amministratore può usare sudo
senza password. SSH accetta soltanto chiavi, a meno che tu non imposti
`ssh_password_auth: true`.

## Supporti di installazione { #install-media }

Il primo comando crea l’immagine di installazione (ISO) per un host. Il secondo
la copia su una chiavetta USB.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- La ISO installa sul disco indicato in `disk:` **senza chiedere nulla**, e
  quindi cancella quel disco. A installazione finita **spegne la macchina**
  (`install.on_done: poweroff`, oppure `reboot` se vuoi che si riavvii). Metti
  un’etichetta alle tue chiavette USB.
- Per impostazione predefinita i supporti di installazione contengono
  **soltanto il sistema di base**: il nome host, le impostazioni di rete,
  l’utente amministratore con le chiavi SSH e le regole per gli aggiornamenti.
  Non contengono nessuno dei segreti dello stack. La macchina riceve il suo
  ruolo dopo, quando esegui `apply`.
- Con `--offline` sulla ISO finiscono l’intero ruolo e i suoi segreti. È
  pensato per una macchina che non è raggiungibile via SSH. Chiunque abbia
  quella ISO ha anche quei segreti.
- L’installer live elenca i dischi della macchina (`lsblk`) e offre una shell,
  che accetta la password di console e le chiavi SSH della fleet.

## Apply { #apply }

`apply` prepara una macchina per il suo ruolo, via SSH.

```bash
kiwi-server apply fleet.yaml papaya                         # per nome, indirizzo o indirizzo nella mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # la prima volta, per indirizzo
```

Per prima cosa `apply` genera di nuovo la configurazione dell’host, cioè
ricrea i file dell’host a partire dal file fleet. Poi copia via SSH lo script
del ruolo in `/var/lib/kiwi-server/role.sh`. Lo script del ruolo è lo script
che prepara la macchina per il suo ruolo, e `apply` lo esegue come root. Dopodiché
`apply` lega il disco ai suoi anelli Tang, cioè ai server che
permettono a una macchina cifrata di sbloccare il disco all’avvio. Su un
master salva inoltre lo stato di WireGuard insieme ai segreti della fleet. Su
una macchina Debian cifrata, il primo `apply` sostituisce la chiave monouso
usata per l’installazione.

La connessione SSH usa la chiave della fleet e confronta la chiave host della
macchina con quella registrata in `secrets/known_hosts`. `apply` e `status`
possono raggiungere una macchina tramite il suo nome, il suo indirizzo
statico, l’indirizzo pubblico del master o il suo indirizzo nella mesh, cioè
l’indirizzo che la macchina ha nella rete WireGuard privata. Usano soltanto
indirizzi la cui chiave host è già registrata.

Per un ruolo costruito con i moduli, lo script del ruolo passa lo stack a
`kiwi-stack`. Lo stack è l’insieme dei container che la macchina esegue per i
suoi moduli. `kiwi-stack` esegue poi questi passaggi:

1. Installa o attiva podman 4.4+ o docker, e si assicura che l’utente dei
   servizi esista. Su Debian, podman viene installato insieme a `netavark`,
   `aardvark-dns` e `catatonit`.
2. Carica i moduli del kernel e imposta i sysctl. Se lo stack contiene
   Pi-hole, aardvark-dns di podman viene spostato sulla porta 5533 e l’host
   stesso risolve i nomi attraverso il Pi-hole dello stack. Aggiunge inoltre
   la mesh alle reti considerate attendibili da firewalld.
3. Rifiuta uno stack generato con un seed diverso. Il seed è il segreto da cui
   vengono generate le password della fleet. Altrimenti estrae lo stack in
   `docker_dir`. Installa i quadlet, cioè le unità systemd per i container, in
   `/etc/containers/systemd`, e installa le unità dell’host. Rimuove anche
   tutto ciò che aveva installato un modulo non più presente nello stack.
4. Apre le porte dello stack in firewalld o in ufw, se uno dei due è attivo.
5. Scarica tutte le immagini dei container e poi avvia `kiwi-stack.service`,
   che a sua volta avvia `kiwi-stack.target`.
6. Esegue `kiwi-stack verify`, che controlla che tutti i container siano in
   esecuzione. Se uno non lo è, l’`apply` fallisce e indica il passaggio non
   riuscito.

Se applichi di nuovo la stessa configurazione generata, sulla macchina non
cambia nulla. Se applichi una configurazione nuova, viene sostituito ciò che è
cambiato. Tieni presente che ogni `apply` riavvia tutti i container dello
stack, anche quando non è cambiato nulla.

## Primo avvio { #first-boot }

Al primo avvio `kiwi-role.service` esegue una volta lo script del ruolo
`/var/lib/kiwi-server/role.sh`. Parte quando la rete è attiva e aspetta fino a
120 secondi che il DNS risponda. Il file `role.done` indica che il ruolo è
completato, e viene scritto solo quando tutti i container sono in esecuzione.
Se lo script fallisce, lascia il file `/var/lib/kiwi-server/role.failed`, che
indica il passaggio e il comando non riusciti, e lo script viene eseguito di
nuovo all’avvio successivo. Il log è `/var/log/kiwi-server-role.log`. Su uCore
lo script del ruolo aspetta che la macchina esegua l’immagine uCore firmata.
Per eseguire di nuovo lo script a mano, usa
`sudo bash /var/lib/kiwi-server/role.sh --force`.

## Aggiornamenti { #updates }

Le macchine installano di continuo gli aggiornamenti del sistema operativo. Il
**riavvio** che li rende effettivi avviene però solo all’interno della
finestra di manutenzione che imposti con `updates.days`, `time` e
`length_minutes`, secondo l’ora locale.

| Sistema di destinazione | Installa gli aggiornamenti | Si riavvia |
|---|---|---|
| `coreos` | Zincati, di continuo | solo nella finestra (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` li scarica e li prepara (staging) | `kiwi-staged-reboot.timer` nella finestra |
| `debian` | unattended-upgrades, ogni giorno | `kiwi-reboot-if-required.timer` nella finestra, se un aggiornamento richiede un riavvio |

`updates.days: []` permette il riavvio in qualsiasi giorno, e
`updates.enabled: false` disattiva sia gli aggiornamenti sia i riavvii. Una
macchina cifrata non si riavvia da sola se ha bisogno di un anello Tang che
qualcuno deve inoltrarle a mano: altrimenti resterebbe ferma all’avvio finché
qualcuno non la sblocca.

I container si aggiornano con un calendario tutto loro. Una volta alla
settimana, la domenica alle 00:00, `kiwi-stack update` esegue
`podman auto-update`, purché sia impostato `auto_update: registry`. Il client
VPN viene riavviato ogni giorno alle 07:00, e così riceve un nuovo indirizzo di
uscita. L’indirizzo di uscita è l’indirizzo pubblico che i siti web vedono
quando il traffico esce dalla VPN.

## Sulla macchina: `kiwi-stack` { #on-the-machine-kiwi-stack }

`kiwi-stack` è il comando che esegui direttamente sulla macchina per
controllare lo stato dello stack e gestirlo.

```bash
sudo kiwi-stack status          # container, unità dell’host, verify
sudo kiwi-stack verify          # tutti i container sono in esecuzione?
sudo kiwi-stack logs [service]  # dal journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # il client VPN e tutti i container nel suo namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # con il modulo backup
sudo kiwi-stack apply DIR       # un bundle dello stack, senza script del ruolo
```

I file dello stack si trovano in `docker_dir` (per impostazione predefinita
`/home/user/docker`), e le sue impostazioni in `/etc/kiwi-server/stack.env`. Le
unità systemd sono `kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` e
`kiwi-stack-update.timer`, più le eventuali unità aggiunte da un modulo.

## Che cosa contiene una configurazione generata { #what-a-render-produces }

La configurazione generata è ciò che kiwi-server produce dal file fleet per un
host. Viene scritta in `output/<host>/`, che contiene poi questi file.

| File | Che cosa |
|---|---|
| `<host>.role.sh` | Il ruolo in un unico script. Contiene le impostazioni, lo stack incorporato, il comando e la libreria di kiwi-stack e il corpo del ruolo. Il file ha i permessi 0600 |
| `<host>.stack/` | Il bundle dello stack, così puoi esaminarlo. Contiene `docker-compose.yml`, `quadlets/`, i file di configurazione dei moduli, le unità dell’host e `stack.sh`. Puoi anche installarlo a mano con `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | Su CoreOS e uCore, la configurazione Butane e Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Su Debian, il file di preseed e i file che copia sulla macchina |
| `<host>.iso` | L’immagine di installazione, che installa senza nessuno alla tastiera |
