# Gestione

Questa pagina riguarda il lavoro che viene dopo, quando le macchine sono
installate e in funzione: controllarne lo stato, custodire i segreti, fare il
backup della fleet e dei dati delle macchine, sbloccare i dischi cifrati,
regolare la MTU del tunnel e installare su un server netcup. Fai tutto con
kiwi-server dal tuo computer, la *postazione di amministrazione*, cioè il
computer su cui si trovano il file fleet e i segreti.

## Stato { #status }

`kiwi-server status` mostra come stanno le macchine della fleet, tutte oppure
quella che indichi:

```bash
kiwi-server status fleet.yaml            # tutti gli host
kiwi-server status fleet.yaml papaya        # uno solo
```

kiwi-server si collega a ogni macchina via SSH e si limita a leggere. Ogni
macchina riporta il suo ruolo e il suo stack (l’insieme dei container e dei
servizi che esegue), gli eventuali problemi, come un ruolo fallito o un
container fermo, i suoi dischi e se sono cifrati o bloccati, i suoi backup e
per quanto tempo i suoi certificati sono ancora validi. Un node di backup
riporta anche lo spazio disponibile. L’app Kiwi Server mostra le stesse
informazioni nella scheda *Overview* di ogni host.

## Segreti { #secrets }

Tutto ciò che è segreto si trova in `secrets/`, la cartella accanto al file
fleet. Contiene il seed da cui deriva ogni password generata, l’autorità di
certificazione (CA) della fleet, le configurazioni WireGuard, le chiavi LUKS
dei dischi cifrati e le chiavi host SSH. kiwi-server può tenere questa
cartella cifrata e aprirla solo mentre ci lavori:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ diventa un unico file cifrato con age
kiwi-server secrets unlock fleet.yaml    # la apre in memoria (--for 8h; 0 la lascia aperta)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # le password generate di un host
```

`secrets init` crea l’archivio cifrato. Salva una chiave nel portachiavi di
GNOME e ti mostra una **chiave di recupero**, che viene mostrata una sola
volta. Finché l’archivio è aperto, qualsiasi programma che gira con il tuo
account utente può leggerlo.

## Il backup della fleet { #backing-up-the-fleet-itself }

La cartella della fleet contiene il file fleet e `secrets/`, e kiwi-server ne
fa il backup da solo. Dopo ogni `render` o `build` riuscito (i due passaggi
che generano la configurazione degli host e le loro ISO di installazione),
cifra la cartella della fleet (AES-256 con PBKDF2, 600.000 iterazioni) e la
copia sui node elencati in `backup.hosts`. Ognuno di questi node conserva le
dieci copie più recenti. Su un computer nuovo recuperi la cartella della fleet
da uno di quei node. In qualsiasi momento puoi anche scriverne una copia in
una cartella a tua scelta:

```bash
kiwi-server restore --from core@lychee.home  # recupera la cartella della fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # oppure una copia in una cartella, in qualsiasi momento
```

## Il backup dei dati delle macchine { #backing-up-the-machines-data }

Il backup dei dati delle macchine si fa con restic, un programma di backup. I
backup vengono conservati su un node, a cui dai il modulo `backup-server`, che
esegue un server REST di restic. Ogni macchina di cui vuoi il backup riceve il
modulo `backup`, con un’impostazione che punta a quel server:

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

Ogni notte alle 03:00, o fino a 15 minuti dopo, restic invia al server di
backup, cifrati, i dati che ogni modulo vuole conservare. Una macchina
raggiunge soltanto il proprio repository sul server, e può solo aggiungervi
dati: lì non può cancellare nulla. Per questo il comando che elimina i vecchi
snapshot si esegue sul tuo computer. Uno snapshot è il nome che restic dà allo
stato salvato da un singolo backup. Il primo comando qui sotto è per la
macchina stessa, il secondo per il tuo computer:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # sulla macchina
kiwi-server prune fleet.yaml            # ne conserva 7 giornalieri, 4 settimanali, 6 mensili
```

Il ripristino è stato testato tra due node, ripristinando su lychee i backup di
papaya.

### In arrivo nella prossima release { #coming-in-the-next-release }

!!! info "Nel branch `several-servers`"
    Questo lavoro si trova nei branch `several-servers` di kiwi-modules e di
    kiwi-server, ma non è ancora stato unito né rilasciato. L’uso di più
    server di backup e il ripristino automatico sono stati testati su
    hardware. L’health check della VPN no.

- **Più server di backup.** `backup.servers` accetta un elenco di server, e
  ogni server riceve una copia completa tutta sua. Se un server si guasta, è
  colpita solo la sua copia. Un ripristino prende la copia più recente dal
  server che ce l’ha, e `kiwi-stack snapshots` elenca gli snapshot server per
  server. L’impostazione singola `server` funziona ancora.
- **Una macchina ricostruita si ripristina da sola.** Una macchina appena
  ricostruita trova sul server dei backup di sé stessa, anche se non ne ha
  fatto nessuno. In quel caso, prima di fare il suo primo backup, ripristina da
  sola tutti i moduli, e poi continua a fare i backup come prima. È il
  comportamento predefinito, `backup.restore: auto`. Con `hold` la macchina
  aspetta che tu esegua `kiwi-stack restore` oppure `kiwi-stack backup --new`.
- **Eliminazione dei vecchi snapshot a orari fissi.**
  `kiwi-server prune fleet.yaml --every week` (oppure `day`) installa sul tuo
  computer un timer utente di systemd. Il tuo computer è l’unico posto che
  custodisce le chiavi autorizzate a cancellare. Se un’esecuzione salta, viene
  recuperata al login successivo. `kiwi-server status` mostra ogni copia di
  backup e ti avvisa quando da tre settimane non sono stati eliminati i
  vecchi snapshot di un node di backup.
- **Una connessione bloccata con il provider VPN commerciale si ripristina da
  sola.** gluetun, il container del client VPN, riceve un health check, cioè
  un controllo periodico che verifica se la connessione funziona ancora.
  Quando il controllo fallisce per cinque minuti, il container viene terminato,
  e al riavvio successivo sceglie un altro server.

## Dischi cifrati e sblocco { #encrypted-disks-and-unlocking }

Un disco cifrato va sbloccato a ogni avvio della macchina. Questa sezione
descrive come ogni sistema di destinazione (il sistema operativo con cui è
installata una macchina) cifra il disco, e come il disco si può sbloccare con o
senza una persona presente.

- **Debian** (`debian.encrypt: true`) viene installato con una chiave monouso,
  che digiti al primo avvio. La trovi in `secrets/luks/<host>.once`. Il primo
  `apply` la sostituisce con `secrets/luks/<host>.key`, e in quel momento un
  master riceve anche una nuova chiave del volume. Se perdi quel file di
  chiave, il disco resta bloccato: tieni quindi sempre un backup della fleet.
- **CoreOS / uCore** cifrano il disco durante l’installazione tramite Ignition,
  lo strumento che configura una macchina CoreOS al primo avvio. Per farlo, al
  primo avvio la macchina ha bisogno di circa 4 GiB di RAM.
- **Gli anelli Tang** permettono alle macchine cifrate di sbloccare i dischi
  all’avvio senza che ci sia una persona. Tang è un piccolo server a cui una
  macchina chiede aiuto, attraverso la rete, per sbloccare il proprio disco.
  Su un node gira il modulo `tang`, e ogni anello è un server Tang con le
  proprie chiavi. Per impostazione predefinita c’è un solo anello, `infra`,
  sulla porta 7500. Il blocco `unlock:` di un host lega il suo disco a uno o
  più anelli e imposta una soglia, cioè il numero di anelli che devono
  rispondere.
- **SSH nell’initramfs** (`unlock.ssh: true`) ti permette di raggiungere una
  macchina che aspetta lo sblocco del disco. L’initramfs è il piccolo sistema
  che gira prima che il disco sia aperto. Il server SSH al suo interno è
  dropbear su Debian e dracut-sshd su CoreOS. Accetta una chiave propria e
  limitata, `secrets/unlock_ed25519`, che può soltanto eseguire lo sblocco.
- `kiwi-server unlock fleet.yaml <host>` inoltra un anello a una macchina che
  aspetta all’avvio, così la macchina può usare un anello che da sola non
  raggiunge. Con `--manual` consegna direttamente la chiave. Un anello chiamato
  `operator` viene servito dal tuo computer per il tempo necessario.
  `vpn-server.unlock_relay` rende un anello raggiungibile attraverso il master
  per le macchine dietro NAT.

## MTU del tunnel { #tunnel-mtu }

La MTU è la dimensione massima di un pacchetto che un collegamento di rete
trasporta in un unico pezzo. WireGuard aggiunge le proprie intestazioni a ogni
pacchetto, quindi un tunnel trasporta pacchetti più piccoli della connessione
sottostante, e una connessione mobile ancora più piccoli. Un pacchetto troppo
grande per uno dei collegamenti lungo il percorso viene scartato o spezzato, e
le connessioni si bloccano. Kiwi affronta il problema in tre modi:

- **Due impostazioni.** `wg_mtu` è la MTU di gluetun (il client VPN), delle
  configurazioni client emesse da wg-easy (il server WireGuard) e
  dell’interfaccia WireGuard `wg0`. Il valore predefinito è **1376**, un
  multiplo di 16, perché WireGuard riempie ogni pacchetto fino al multiplo di
  16 byte successivo. `bridge_mtu` è la MTU della rete dello stack, che collega
  i container di una macchina. Il valore predefinito è **1500**. `validate`
  rifiuta un `wg_mtu` se il pacchetto riempito, più 80 byte di intestazioni,
  non entra nel bridge. Rifiuta anche qualsiasi valore sotto 1280, la MTU
  minima con cui funziona IPv6.
- **La MSS viene limitata in entrambe le direzioni.** La MSS è la quantità
  massima di dati che TCP mette in un pacchetto. wg-easy e il client VPN la
  limitano entrambi a `wg_mtu - 40`, così TCP non prova mai un segmento che
  non può passare.
- **TCP trova da solo una dimensione che funziona.** Il client VPN gira con
  `net.ipv4.tcp_mtu_probing=1` e `tcp_base_mss=1024`. Quando una connessione
  passa per un percorso che scarta in silenzio i pacchetti grandi, TCP prova
  pacchetti più piccoli finché non trova una dimensione che funziona, invece
  di restare bloccato.

### Misurare un percorso: `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Per sapere che cosa trasporta davvero il percorso verso un node o un
dispositivo, misuralo:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # un node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # un dispositivo da secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # e scrive wg_mtu nel file fleet
```

La misurazione manda dei ping attraverso il tunnel con il flag don’t-fragment
attivo, così non possono essere spezzati lungo il percorso. Li manda
dall’interno del namespace di rete che contiene il tunnel. Un namespace di rete
è un ambiente di rete separato su una macchina, come quello che ha un
container. Un node viene misurato dal suo client VPN, perché il firewall del
client scarta i ping in arrivo. Un dispositivo viene misurato dal server
WireGuard. La misurazione parte con un ping normale, poi prova tutti i
multipli di 16 a partire da 1280 e riporta la dimensione più grande che arriva
**intera**. Mentre manda i ping, legge i contatori di riassemblaggio del
kernel: così una risposta spezzata lungo il percorso e poi ricomposta non
viene contata come se fosse passata.

La misurazione ti dice anche che cosa impostare. Per un **dispositivo** è la
riga `MTU =` nella configurazione WireGuard del dispositivo stesso, e nessun
altro ne risente. Per un **node** è `wg_mtu` su quel node e sul suo master. Con
`--write` la misurazione scrive il valore nel file fleet e modifica solo
quelle righe. C’è una cosa che da questo lato non si vede: un pacchetto
spezzato solo all’andata e ricomposto dall’altra parte.

I valori predefiniti sono stati misurati sulla fleet di test. Un telefono con
i dati mobili ha bisogno di una misurazione tutta sua, perché i percorsi mobili
sono spesso solo IPv6 dietro 464XLAT, con incapsulamenti annidati. Misura il
telefono stesso, e abbassa il suo `MTU =` se la misurazione lo indica.

## VPS netcup { #netcup-vpses }

netcup è un provider di hosting, e oggi è l’unico su cui kiwi-server sa
installare da solo un server a noleggio (un VPS). Lo fa tramite l’API del
Server Control Panel di netcup. Altri provider di hosting sono
[previsti](roadmap.md#more-hosters-and-network-boot) sotto forma di plugin.

```bash
kiwi-server vps login fleet.yaml         # login con device flow; il token finisce in secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # cancella il server e installa la ISO dell’host
```

`vps install` cancella il server, quindi prima chiede conferma, a meno che tu
non passi `--yes`. Si rifiuta di installare in tre casi: quando la ISO
contiene segreti del ruolo, quando `disk:` indica il disco sbagliato e quando
un disco CoreOS dovrebbe essere cifrato su un server con meno di 3500 MiB di
RAM.
