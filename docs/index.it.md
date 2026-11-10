---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Un ambiente Linux open source che gestisci tu: i tuoi server, i tuoi dispositivi e il tuo desktop, collegati in un’unica rete privata. Si installa da solo, si tiene aggiornato, fa un backup ogni notte e, quando qualcosa si rompe, si può ricostruire.</p>

[Come funziona](network/index.md){ .md-button .md-button--primary }
[Crea la tua rete](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>La rete</strong>
<span>I tuoi server e i tuoi dispositivi in un’unica rete WireGuard privata. Un solo server è raggiungibile da Internet, tutti gli altri restano a casa.</span>
<em>Come funziona →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Lo strumento con cui costruisci e gestisci la rete: un solo file per tutte le macchine, installazione automatica, backup e sblocco dei dischi.</span>
<em>Crea la tua rete →</em>
</a>

<a href="server/modules/">
<strong>Moduli</strong>
<span>I 20 servizi che una macchina può eseguire: da WireGuard e Pi-hole a Nextcloud, Vaultwarden, i backup e Immich.</span>
<em>Che cosa può fare un node →</em>
</a>

<a href="people/">
<strong>Hub</strong>
<span>Con kiwi-framework una comunità gestisce il proprio hub, con un mercato aperto, un feed e una chat, senza nessuna piattaforma centrale.</span>
<em>Hub per le comunità →</em>
</a>

<a href="desktop/">
<strong>Il desktop</strong>
<span>Una postazione di lavoro con Fedora Atomic e app installate da git: un kill switch per la VPN, connessioni isolate per le reti dei clienti, configurazione iniziale e sincronizzazione.</span>
<em>Le app per il desktop →</em>
</a>

<a href="project/status/">
<strong>Stato</strong>
<span>Tutti i repository, ciascuno con la sua release attuale e con quello che ancora manca.</span>
<em>Stato attuale →</em>
</a>

</div>

## L’idea { #the-idea }

Internet non è un posto tranquillo, e badare ai propri server è un lavoro che
non finisce mai. Kiwi Network questo lavoro lo fa al posto tuo. Descrivi le tue macchine in un
solo file, e le operazioni di routine vengono eseguite in automatico.
Intrusioni, dischi guasti e macchine perse sono messi in conto fin dall’inizio.

- **Installazione automatica.** Ogni macchina viene installata senza nessuno
  alla tastiera: dalla propria immagine di installazione, oppure direttamente su
  un server a noleggio, tramite l’API del provider di hosting. Oggi funziona con
  netcup, e altri provider sono
  [previsti](server/roadmap.md#more-hosters-and-network-boot).
- **Aggiornamenti automatici.** Gli aggiornamenti vengono installati senza che
  tu debba fare nulla. Una macchina si riavvia soltanto nelle ore che hai
  autorizzato.
- **Un backup ogni notte.** Ogni macchina invia un backup cifrato a un server di
  backup che appartiene a te. Può aggiungere ai propri backup, ma non può
  cancellarli: chi riuscisse a entrare in una macchina non potrebbe farli
  sparire. Nel backup finiscono anche il file fleet (`fleet.yaml`) e i suoi
  segreti, cioè password e chiavi.
- **Ripristino quando serve davvero.** I dischi sono cifrati. All’avvio le
  macchine li sbloccano da sole, oppure li sblocchi tu da remoto. Se una
  macchina va ricostruita, la configurazione arriva dal file fleet e i dati dal
  backup.

## Le macchine { #the-machines }

Ogni macchina ha un ruolo, che stabilisce che cosa fa nella rete.

| Ruolo | Che cosa fa la macchina |
|---|---|
| `master` | È l’unica macchina raggiungibile da Internet. Esegue il server WireGuard, manda il traffico in uscita attraverso un provider VPN oppure direttamente a Internet, e offre il DNS con Pi-hole, Tor e le pagine di amministrazione. Può ospitare anche un relay nostr e un hub. |
| `node` · `gateway` | Fa passare un’intera rete domestica o d’ufficio attraverso la VPN, con Pi-hole come server DNS e DHCP, un gestore di download e SFTP. |
| `node` · `cloud` | Esegue Nextcloud con Collabora, e Vaultwarden. |
| `node` · `minimal` | Ha soltanto la connessione alla rete e nginx. I moduli li aggiungi tu: per esempio i backup, Tang, Immich, Paperless-ngx oppure OpenCloud. |
| `bare` | Ha soltanto il sistema di base. |

I master prendono il nome da dolci a base di frutta (sorbet, crumble, compote),
i node da frutti (papaya, lychee, quince). Il master è l’unica macchina che deve
essere raggiungibile da Internet. Per impostazione predefinita ha una sola porta
aperta: WireGuard, sulla UDP 51820.

```bash
kiwi install kiwi-server            # oppure da un clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # una ISO per ogni macchina, che si installa da sola
kiwi-server apply fleet.yaml papaya # il ruolo, via SSH
```
