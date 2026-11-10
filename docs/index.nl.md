---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Je eigen privénetwerk: een master aan de poort, nodes erachter, elke machine van jou. Gebouwd uit één bestand, met één deur naar het internet.</p>

[Hoe het werkt](network/index.md){ .md-button .md-button--primary }
[Bouw er een](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Het netwerk</strong>
<span>Eén master, veel nodes, één WireGuard-mesh. Clientgroepen, een double-hop-exit, DNS en certificaten van jezelf.</span>
<em>Hoe het werkt →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Het fleet-bestand, installatie-ISO's, toepassen via SSH, aanmelden, back-ups, ontgrendelen. CLI en GTK-app.</span>
<em>Bouw een netwerk →</em>
</a>

<a href="server/modules/">
<strong>Modules</strong>
<span>Alle 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, back-ups, Tang, Immich, Paperless-ngx en meer.</span>
<em>Wat een node kan zijn →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>kiwi-framework: open markten, feeds, chat en delen op nostr, verzegeld in de browser. Armory is de eerste.</span>
<em>Hubs, geen platforms →</em>
</a>

<a href="desktop/">
<strong>De desktop</strong>
<span>kiwi-updater en de apps voor Fedora Atomic: killswitch, verzegelde exits voor klantnetwerken, inrichting, synchronisatie.</span>
<em>Apps uit git →</em>
</a>

<a href="project/status/">
<strong>Status</strong>
<span>Elke repository, de release ervan en de bekende hiaten, beschreven zoals ze zijn.</span>
<em>Hoe het ervoor staat →</em>
</a>

</div>

## De machines { #the-machines }

| Rol | Wat de machine wordt |
|---|---|
| `master` | de poort: WireGuard, een double-hop- of directe exit, Pi-hole, Tor, de beheerpagina's, en optioneel een nostr-relay en een hub |
| `node` · `gateway` | een LAN via de VPN, met Pi-hole als DNS en DHCP, een downloadstation en SFTP |
| `node` · `cloud` | Nextcloud met Collabora, en Vaultwarden |
| `node` · `minimal` | de tunnel en nginx, voor modules naar keuze: back-ups, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | alleen het basissysteem |

Masters zijn vernoemd naar fruitgerechten (sorbet, crumble, compote), nodes naar
vruchten (papaya, lychee, quince). De master is de enige machine die vanaf het
internet bereikbaar moet zijn, en standaard publiceert hij één poort: WireGuard,
UDP 51820.

```bash
kiwi install kiwi-server            # of vanuit een clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # per machine een ISO die zonder tussenkomst installeert
kiwi-server apply fleet.yaml papaya # de rol, via SSH
```
