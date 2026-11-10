---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Een opensource Linux-omgeving die je zelf beheert: je servers, je apparaten en je desktop samen in één privénetwerk. Ze installeert zichzelf, houdt zichzelf up-to-date, maakt elke nacht een back-up en is opnieuw op te bouwen als er iets kapotgaat.</p>

[Zo werkt het](network/index.md){ .md-button .md-button--primary }
[Zelf opzetten](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Het netwerk</strong>
<span>Je servers en apparaten in één privé WireGuard-netwerk. Eén server is bereikbaar vanaf internet, de andere blijven thuis.</span>
<em>Zo werkt het →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Het programma waarmee je het netwerk opbouwt en beheert: één bestand voor al je machines, automatische installatie, back-ups en ontgrendelen.</span>
<em>Een netwerk opzetten →</em>
</a>

<a href="server/modules/">
<strong>Modules</strong>
<span>De 20 diensten die een machine kan draaien, van WireGuard en Pi-hole tot Nextcloud, Vaultwarden, back-ups en Immich.</span>
<em>Wat een node kan draaien →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>Met kiwi-framework heeft een community haar eigen hub, met een open markt, een feed en chat, en zonder centraal platform.</span>
<em>Hubs voor community’s →</em>
</a>

<a href="desktop/">
<strong>De desktop</strong>
<span>Een werkstation met Fedora Atomic en apps uit git: een VPN-killswitch, afgeschermde verbindingen voor klantnetwerken, inrichting en synchronisatie.</span>
<em>Desktop-apps →</em>
</a>

<a href="project/status/">
<strong>Status</strong>
<span>Alle repository’s met hun huidige release en wat er nog ontbreekt.</span>
<em>Hoe het ervoor staat →</em>
</a>

</div>

## Het idee { #the-idea }

Op internet moet je op alles voorbereid zijn, en eigen servers onderhouden is
werk dat nooit af is. Kiwi Network neemt dat werk van je over. Je beschrijft je
machines in één bestand, en het routinewerk gaat vanzelf. Met inbraken, kapotte
schijven en kwijtgeraakte machines is vanaf het begin rekening gehouden.

- **Automatische installatie.** Elke machine wordt geïnstalleerd zonder dat er
  iemand achter het toetsenbord zit: vanaf een eigen installatie-image, of
  rechtstreeks op een gehuurde server via de API van de hostingprovider. Op dit
  moment wordt netcup ondersteund, meer providers zijn
  [gepland](server/roadmap.md#more-hosters-and-network-boot).
- **Automatische updates.** Updates worden automatisch geïnstalleerd. Een
  machine herstart alleen in de uren die je daarvoor hebt vrijgegeven.
- **Elke nacht een back-up.** Elke machine stuurt een versleutelde back-up naar
  een back-upserver van jezelf. Ze kan back-ups alleen toevoegen, niet
  verwijderen, dus een indringer kan ze niet wissen. Ook van het fleetbestand
  en de secrets wordt een back-up gemaakt.
- **Herstel als het erop aankomt.** De schijven zijn versleuteld. Bij het
  opstarten ontgrendelen de machines ze zelf, of je ontgrendelt ze op afstand.
  Moet een machine opnieuw worden opgebouwd, dan komt de configuratie uit het
  fleetbestand en komen de gegevens uit de back-up.

## De machines { #the-machines }

Elke machine heeft een rol. Die bepaalt wat de machine in het netwerk doet.

| Rol | Wat de machine doet |
|---|---|
| `master` | De enige machine die bereikbaar is vanaf internet. Ze draait de WireGuard-server, stuurt uitgaand verkeer via een VPN-provider of rechtstreeks naar internet, en levert DNS met Pi-hole, Tor en de beheerpagina’s. Daarnaast kan ze een nostr-relay en een hub draaien. |
| `node` · `gateway` | Stuurt een thuis- of kantoornetwerk door de VPN, met Pi-hole als DNS- en DHCP-server, een downloadstation en SFTP. |
| `node` · `cloud` | Draait Nextcloud met Collabora, en Vaultwarden. |
| `node` · `minimal` | Heeft alleen de verbinding met het netwerk en nginx. De modules kies je zelf, bijvoorbeeld back-ups, Tang, Immich, Paperless-ngx of OpenCloud. |
| `bare` | Heeft alleen het basissysteem. |

Masters zijn vernoemd naar fruitgerechten (sorbet, crumble, compote), nodes naar
vruchten (papaya, lychee, quince). De master is de enige machine die bereikbaar
moet zijn vanaf internet. Standaard staat er precies één poort open: WireGuard,
op UDP 51820.

```bash
kiwi install kiwi-server            # of vanuit een kloon: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # per machine een ISO die zonder toezicht installeert
kiwi-server apply fleet.yaml papaya # de rol, via SSH
```
