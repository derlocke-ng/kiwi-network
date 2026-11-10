# Dove sta andando

!!! info "Progettato, non realizzato"
    Questa pagina riassume il
    [progetto del control plane](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    di kiwi-server, concordato a ottobre 2026. A meno che una riga non dica *realizzato*, niente di tutto questo esiste ancora.
    La [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    tiene traccia dell'ordine.

Oggi kiwi-server è uno strumento desktop: il file fleet, i segreti e la CA si trovano
sulla macchina dell'operatore. Il piano è farne un **servizio** che possa girare
su un node, così che una rete possa essere creata e gestita senza un desktop Linux,
da un telefono, e da più di una persona. Le macchine restano riproducibili dal
file fleet. Il control plane è semplicemente ciò che conserva quel file ed esegue il
renderer.

## I livelli { #the-layers }

1. **kiwi-modules**: i moduli e il contratto di render per una macchina. *Realizzato.*
2. **kiwi-stack**: il lato macchina, da `kiwi-stack apply`. *Realizzato.*
3. **kiwi-server core**: la fleet, gli host, i target, le ISO, la CA, la registrazione e
   l'apply, senza interfaccia come oggi. *Realizzato.*
4. **Il modulo di controllo**: il core come container, con un'API e una UI web,
   che gira come modulo su un node come qualsiasi altro.
5. **Client**: prima la UI web. L'app GTK resta e parla con la CLI locale
   o con un controller attraverso la mesh, e anche la CLI resta. Nessun front end sviluppa
   una logica propria.

## Il node di controllo { #the-control-node }

Il controller gira su un node a casa (il *node di controllo*), raggiungibile dalla
mesh solo per gli amministratori, su un disco cifrato. Conserva il seed, la chiave della CA, il
file fleet e ogni configurazione.

Il **master in affitto diventa un'infrastruttura di relay sostituibile**. Conserva solo
ciò che gli serve per funzionare: le sue chiavi WireGuard e i suoi peer, le sue password e il suo
certificato. Perderlo costa un nuovo apply dal node di controllo. Perdere il
node di controllo costa un ripristino del backup della fleet.

## Utenti { #users }

Un blocco `users:` con due ruoli: un **amministratore della fleet** che può fare tutto, e
gli **amministratori di node** legati ai propri host. Un amministratore di node vede lo
stato, i log, i carichi di lavoro e i backup di quegli host, e registra dispositivi nei gruppi che
l'amministratore della fleet consente, ma non vede nulla del master, della CA o degli altri node.
L'accesso è una password più un certificato client dalla CA della fleet oppure WebAuthn,
e ogni modifica finisce in un log di audit.

## Aggiungere una macchina { #joining-a-machine }

Restano entrambe le strade:

- **Una ISO per host** con il suo ruolo (l'odierno `build --offline`), per installazioni
  offline.
- **Una ISO di bootstrap generica** per target, costruita una volta dalla CI e senza
  segreti. Al primo avvio recupera il suo ruolo dal controller con un
  **join token** monouso. Una macchina installata a mano o una VPS si unisce con una
  riga: `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Ogni macchina della linea CoreOS è pensata per eseguire **un'unica immagine bootc**, con il ruolo
che arriva al primo avvio.

## Federazione e multi-hop { #federation-and-multi-hop }

Le reti che si fidano l'una della CA dell'altra e si delegano i nomi a vicenda diventano
client l'una dell'altra. Con la terza modalità d'uscita, il master di una rete può
uscire su Internet attraverso quello di un'altra: **multi-hop**, dove il secondo master
vede solo il primo. Più master gestiti da un solo operatore diventano allora un proprio
servizio VPN: master d'ingresso in un paese, master d'uscita in altri,
Tor all'interno.

## Il frutteto { #the-orchard }

Il frutteto (orchard) è per chi gestisce molti master per altri. È un'app separata
o un plugin di kiwi-server che crea VPS tramite le API dei provider, consegna a ogni
master la sua installazione e un token di registrazione, raccoglie un heartbeat da ogni
master (versione, salute, disco, ultimo aggiornamento) e distribuisce gli aggiornamenti spostando
i tag delle immagini per canale.

Non può accedere a un master, leggere una fleet o toccare un node. Il node di controllo
che ogni tenant ha a casa custodisce la sua rete. Chi ospita il master non può leggerla,
e gestisce una VM per tenant. Il supporto netcup di kiwi-server (`kiwi-server
vps`, *realizzato*) è il primo pezzo del suo driver per i provider.

## Più provider, e avvio di rete { #more-hosters-and-network-boot }

*Previsto.* L'obiettivo è un'installazione completamente automatizzata ovunque si
trovi una macchina.

- **Provider come plugin.** Oggi netcup è integrato. Il piano è un repository a sé
  per le API dei provider, così che chiunque possa aggiungere AWS, Hetzner e gli
  altri nel modo in cui funziona netcup ora: creare o cancellare un server,
  metterci sopra l'installazione e avviarlo.
- **Wake-on-LAN e avvio PXE** per le macchine di casa: un node si sveglia e si
  installa via rete, senza chiavetta USB.

## Anche in lista { #also-on-the-list }

Un master di riserva, podman rootless, IPv6 end-to-end, schede ARM, intervalli di porte
e un modulo per i giochi, e un ripristino dei dati di un node al primo avvio.
