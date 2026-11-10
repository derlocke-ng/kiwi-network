---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Dein eigenes privates Netzwerk: ein Master am Tor, Nodes dahinter, jede Maschine gehört dir. Gebaut aus einer Datei, mit einer Tür ins Internet.</p>

[So funktioniert es](network/index.md){ .md-button .md-button--primary }
[Selbst bauen](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Das Netzwerk</strong>
<span>Ein Master, viele Nodes, ein WireGuard-Mesh. Client-Gruppen, ein Double-Hop-Ausgang, eigenes DNS und eigene Zertifikate.</span>
<em>So funktioniert es →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Die Fleet-Datei, Installations-ISOs, Anwenden über SSH, Aufnahme neuer Maschinen, Backups, Entsperren. CLI und GTK-App.</span>
<em>Ein Netzwerk bauen →</em>
</a>

<a href="server/modules/">
<strong>Module</strong>
<span>Alle 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, Backups, Tang, Immich, Paperless-ngx und mehr.</span>
<em>Was ein Node sein kann →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>kiwi-framework: offene Marktplätze, Feeds, Chat und Teilen auf nostr, im Browser versiegelt. Armory ist der erste.</span>
<em>Hubs statt Plattformen →</em>
</a>

<a href="desktop/">
<strong>Der Desktop</strong>
<span>kiwi-updater und die Apps für Fedora Atomic: Kill Switch, versiegelte Ausgänge für Kundennetze, Einrichtung, Sync.</span>
<em>Apps aus Git →</em>
</a>

<a href="project/status/">
<strong>Status</strong>
<span>Jedes Repository, sein Release und seine bekannten Lücken, so beschrieben, wie sie sind.</span>
<em>Wo die Dinge stehen →</em>
</a>

</div>

## Die Maschinen { #the-machines }

| Rolle | Was aus der Maschine wird |
|---|---|
| `master` | das Tor: WireGuard, ein Double-Hop- oder direkter Ausgang, Pi-hole, Tor, die Admin-Seiten und optional ein nostr-Relay und ein Hub |
| `node` · `gateway` | ein LAN durch das VPN, mit Pi-hole als DNS und DHCP, einer Download-Station und SFTP |
| `node` · `cloud` | Nextcloud mit Collabora, und Vaultwarden |
| `node` · `minimal` | der Tunnel und nginx, für Module deiner Wahl: Backups, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | nur das Basissystem |

Master sind nach Obstgerichten benannt (sorbet, crumble, compote), Nodes nach
Früchten (papaya, lychee, quince). Der Master ist die einzige Maschine, die aus
dem Internet erreichbar sein muss, und standardmäßig veröffentlicht er einen Port:
WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # oder aus einem Klon: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # eine unbeaufsichtigte ISO pro Maschine
kiwi-server apply fleet.yaml papaya # die Rolle, über SSH
```
