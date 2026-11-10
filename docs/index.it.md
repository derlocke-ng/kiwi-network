---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">La tua rete privata: un master al cancello, i node dietro di lui, ogni macchina è tua. Costruita da un solo file, con una sola porta verso Internet.</p>

[Come funziona](network/index.md){ .md-button .md-button--primary }
[Costruiscine una](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>La rete</strong>
<span>Un master, molti node, una mesh WireGuard. Gruppi di client, un'uscita a doppio hop, DNS e certificati tutti tuoi.</span>
<em>Come funziona →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Il file fleet, ISO di installazione, apply via SSH, registrazione, backup, sblocco. CLI e app GTK.</span>
<em>Costruisci una rete →</em>
</a>

<a href="server/modules/">
<strong>Moduli</strong>
<span>Tutti e 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, backup, Tang, Immich, Paperless-ngx e altri.</span>
<em>Cosa può essere un node →</em>
</a>

<a href="people/">
<strong>Hub</strong>
<span>kiwi-framework: mercati aperti, feed, chat e condivisione su nostr, sigillati nel browser. Armory è il primo.</span>
<em>Hub, non piattaforme →</em>
</a>

<a href="desktop/">
<strong>Il desktop</strong>
<span>kiwi-updater e le app per Fedora Atomic: kill switch, uscite sigillate per le reti dei clienti, configurazione, sincronizzazione.</span>
<em>App da git →</em>
</a>

<a href="project/status/">
<strong>Stato</strong>
<span>Ogni repository, la sua release e le sue lacune note, descritti per come sono.</span>
<em>A che punto siamo →</em>
</a>

</div>

## L'idea { #the-idea }

Kiwi Network è un ambiente Linux completamente automatizzato in cui vivere e
lavorare: sicuro, solido e protetto per una dura vita online. Le tue macchine si
prendono cura di sé.

- **Si installano da sole.** Una ISO automatica per ogni macchina, oppure
  direttamente su un server in affitto tramite l'API del provider (oggi netcup,
  altri [previsti](server/roadmap.md#more-hosters-and-network-boot)).
- **Si tengono aggiornate da sole.** Gli aggiornamenti si installano di continuo,
  e i riavvii aspettano la finestra che imposti tu.
- **Si fanno il backup da sole.** Ogni notte, cifrato e in sola aggiunta, su node
  di backup tutti tuoi. Anche il file fleet e i suoi segreti finiscono nel backup.
- **Si rimettono in piedi.** I dischi cifrati si sbloccano tramite Tang, o da
  remoto quando qualcosa non va, e una macchina ricostruita torna a partire dal
  file fleet e dal suo backup.

## Le macchine { #the-machines }

| Ruolo | Cosa diventa la macchina |
|---|---|
| `master` | il cancello: WireGuard, un'uscita a doppio hop o diretta, Pi-hole, Tor, le pagine di amministrazione e, se vuoi, un relay nostr e un hub |
| `node` · `gateway` | una LAN attraverso la VPN, con Pi-hole come DNS e DHCP, una stazione di download e SFTP |
| `node` · `cloud` | Nextcloud con Collabora, e Vaultwarden |
| `node` · `minimal` | il tunnel e nginx, per i moduli che scegli tu: backup, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | solo il sistema di base |

I master prendono il nome da piatti a base di frutta (sorbet, crumble, compote), i node
da frutti (papaya, lychee, quince). Il master è l'unica macchina che deve essere
raggiungibile da Internet, e di default pubblica una sola porta: WireGuard,
UDP 51820.

```bash
kiwi install kiwi-server            # oppure da un clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # una ISO automatica per ogni macchina
kiwi-server apply fleet.yaml papaya # il ruolo, via SSH
```
