# Dove sta andando

Questa pagina descrive che cosa dovrà diventare kiwi-server, e quali parti di
questo progetto esistono già.

!!! info "Progettato, non ancora realizzato"
    Questa pagina riassume il
    [progetto del control plane](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    di kiwi-server, concordato nell’ottobre 2026. Niente di ciò che è descritto
    qui esiste ancora, a meno che una riga non dica *realizzato*. La
    [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    tiene traccia dell’ordine dei lavori.

Oggi kiwi-server è uno strumento per il desktop. Il file fleet, i segreti e la
CA (l’autorità di certificazione della fleet) si trovano sul tuo computer.
L’obiettivo è farne un **servizio** che possa girare su un node. A quel punto
una rete si potrà creare e gestire senza un desktop Linux, da un telefono e in
più di una persona. Le macchine resteranno riproducibili a partire dal file
fleet. Il control plane è la parte che custodisce quel file ed esegue il
generatore, cioè il programma che trasforma il file fleet nella configurazione
di ogni macchina.

## I livelli { #the-layers }

Il progetto divide il software in cinque livelli.

1. **kiwi-modules** contiene i moduli e il contratto di generazione, che
   stabilisce come viene generata la configurazione di una macchina.
   *Realizzato.*
2. **kiwi-stack** è la parte che gira sulla macchina. Il suo punto di
   partenza è `kiwi-stack apply`, che installa sulla macchina una configurazione
   generata. *Realizzato.*
3. **Il nucleo di kiwi-server** si occupa di fleet, host, sistemi di
   destinazione, ISO, CA, registrazione dei dispositivi e `apply`. Come oggi,
   è headless, cioè non ha un’interfaccia grafica propria. *Realizzato.*
4. **Il modulo di controllo** è il nucleo confezionato come container, con
   un’API e un’interfaccia web. Gira su un node come qualsiasi altro modulo.
5. **I client** sono i programmi con cui lavori con il modulo di controllo. Per
   prima arriva l’interfaccia web. L’app GTK resta, e comunica con la CLI
   locale oppure con un controller (un modulo di controllo in funzione)
   attraverso la mesh, la rete WireGuard privata. Anche la CLI resta. Tutta la
   logica rimane nel nucleo, quindi nessun client ha una logica propria.

## Il node di controllo { #the-control-node }

Il controller gira su un node di casa, chiamato *node di controllo*. Solo gli
amministratori possono raggiungerlo, e solo dalla mesh, e il suo disco è
cifrato. Custodisce il seed, la chiave della CA, il file fleet e tutte le
configurazioni.

Il master a noleggio **diventa un semplice punto di passaggio, sostituibile**.
Inoltra il traffico della rete e conserva solo ciò che gli serve per
funzionare, cioè le sue chiavi e i suoi peer WireGuard, le sue password e il
suo certificato. Se perdi il master, lo applichi di nuovo dal node di
controllo. Se perdi il node di controllo, ripristini il backup della fleet.

## Utenti { #users }

Un blocco `users:` definisce gli utenti, ciascuno con uno di due ruoli. Un
**amministratore della fleet** può fare tutto. Un **amministratore di node** è
legato ai propri host: ne vede lo stato, i log, i carichi di lavoro e i backup,
e può registrare dispositivi nei gruppi che l’amministratore della fleet gli
consente. Non vede nulla del master, della CA o degli altri node. Per
accedere, un utente ha bisogno di una password più un certificato client
emesso dalla CA della fleet oppure WebAuthn. Ogni modifica viene scritta in un
registro di controllo (audit log).

## Aggiungere una macchina { #joining-a-machine }

Una macchina può entrare nella rete in due modi, e restano entrambi:

- **Una ISO per ogni host** che contiene il ruolo della macchina, cioè l’attuale
  `build --offline`. Serve per le installazioni offline.
- **Una ISO di avvio generica** per ogni sistema di destinazione, creata una
  volta sola dalla CI e senza segreti. Al primo avvio la macchina scarica il
  suo ruolo dal controller con un **token di adesione** monouso. Una macchina
  installata a mano, o un VPS, entra nella rete con una sola riga:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

L’idea è che ogni macchina della famiglia CoreOS esegua **un’unica immagine
bootc**, cioè un’immagine container avviabile, uguale per tutte. La macchina
riceve il suo ruolo al primo avvio.

## Federazione e multi-hop { #federation-and-multi-hop }

La federazione collega tra loro Kiwi Network separate. Reti che si fidano
reciprocamente delle proprie CA e si delegano a vicenda dei nomi diventano
client l’una dell’altra. Un master ha tre modalità di uscita, che stabiliscono come
il suo traffico arriva a Internet. Con la terza, il master di una rete manda
il proprio traffico Internet attraverso il master di un’altra rete. Questo si
chiama **multi-hop**, e il secondo master vede soltanto il primo. Chi gestisce
più master in questo modo ha un proprio servizio VPN, con master di ingresso
in un paese, master di uscita in altri paesi e Tor all’interno della rete.

## L’orchard { #the-orchard }

L’orchard (“frutteto” in inglese) è il servizio previsto per chi gestisce molti
master per conto di altre persone. Sarà un’app separata oppure un plugin di
kiwi-server. Crea VPS tramite le API dei provider di hosting e consegna a ogni
master la sua installazione e un token di registrazione. Raccoglie da ogni
master un heartbeat, cioè un rapporto di stato periodico (versione, stato di
salute, disco, ultimo aggiornamento). Distribuisce gli aggiornamenti spostando il tag
dell’immagine di ciascun canale di aggiornamento.

L’orchard non può accedere a un master, leggere una fleet o modificare un
node. Ogni tenant, cioè ogni persona il cui master è gestito da qualcun altro,
tiene la propria rete sul proprio node di controllo, a casa. La fleet e le
chiavi restano lì, quindi il provider di hosting su cui gira la VM del master
non può leggere i dati di rete del tenant. Il master di ogni tenant gira in una
VM tutta sua. L’orchard ha bisogno di un driver per le API dei provider, e il
supporto di kiwi-server per netcup (`kiwi-server vps`, *realizzato*) ne è il
primo pezzo.

## Altri provider di hosting e avvio da rete { #more-hosters-and-network-boot }

*Previsto.* L’obiettivo è che una macchina si possa installare in modo
completamente automatico, ovunque si trovi.

- **I provider di hosting come plugin.** Il supporto per netcup oggi è
  integrato. L’idea è un repository separato per le API dei provider, così
  chiunque può aggiungere AWS, Hetzner e altri provider. Un plugin
  funzionerebbe come funziona oggi il supporto per netcup: crea o cancella un
  server, ci mette sopra l’installazione e lo avvia.
- **Wake-on-LAN e avvio PXE** sono previsti per le macchine di casa.
  Wake-on-LAN accende una macchina attraverso la rete, e PXE le permette di
  avviarsi dalla rete. Un node si sveglia allora da solo e si installa
  attraverso la rete, senza bisogno di una chiavetta USB.

## Anche in programma { #also-on-the-list }

La roadmap elenca inoltre un master di riserva, podman rootless, IPv6 da un
capo all’altro, le schede ARM, gli intervalli di porte e un modulo per i
giochi, e il ripristino dei dati di un node al primo avvio.
