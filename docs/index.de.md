---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Eine quelloffene Linux-Umgebung, die du selbst betreibst: deine Server, deine Geräte und dein Desktop in einem gemeinsamen privaten Netzwerk. Sie installiert sich selbst, hält sich aktuell, sichert jede Nacht ihre Daten und lässt sich wiederherstellen, wenn etwas kaputtgeht.</p>

[So funktioniert es](network/index.md){ .md-button .md-button--primary }
[Netzwerk aufsetzen](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Das Netzwerk</strong>
<span>Deine Server und Geräte in einem privaten WireGuard-Netzwerk. Nur ein Server ist aus dem Internet erreichbar, alle anderen bleiben zu Hause.</span>
<em>So funktioniert es →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Das Werkzeug, mit dem du das Netzwerk aufbaust und betreibst: eine Datei für alle Maschinen, automatische Installation, Backups und Entsperren.</span>
<em>Netzwerk aufsetzen →</em>
</a>

<a href="server/modules/">
<strong>Module</strong>
<span>Die 20 Dienste, die eine Maschine übernehmen kann – von WireGuard und Pi-hole bis Nextcloud, Vaultwarden, Backups und Immich.</span>
<em>Was ein Node kann →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>Mit kiwi-framework betreibt eine Community ihren eigenen Hub – mit offenem Marktplatz, Feed und Chat, ganz ohne zentrale Plattform.</span>
<em>Community-Hubs →</em>
</a>

<a href="desktop/">
<strong>Der Desktop</strong>
<span>Ein Arbeitsplatz mit Fedora Atomic und Apps direkt aus git: VPN-Kill-Switch, getrennte Verbindungen für Kundennetze, Einrichtung und Synchronisation.</span>
<em>Desktop-Apps →</em>
</a>

<a href="project/status/">
<strong>Status</strong>
<span>Alle Repositories mit ihrem aktuellen Release und dem, was noch fehlt.</span>
<em>Aktueller Stand →</em>
</a>

</div>

## Die Idee { #the-idea }

Das Internet ist ein raues Pflaster, und eigene Server zu pflegen ist Arbeit,
die nie aufhört. Kiwi Network nimmt dir diese Arbeit ab. Du beschreibst deine
Maschinen in einer einzigen Datei, und die Routineaufgaben laufen von selbst.
Einbrüche, defekte Festplatten und verlorene Geräte sind von Anfang an
eingeplant.

- **Automatische Installation.** Jede Maschine wird installiert, ohne dass
  jemand an der Tastatur sitzt: von ihrem eigenen Installations-Image oder
  direkt auf einem gemieteten Server über die API des Hosters. Heute wird netcup
  unterstützt, weitere Hoster sind
  [geplant](server/roadmap.md#more-hosters-and-network-boot).
- **Automatische Updates.** Updates werden automatisch eingespielt. Neu
  gestartet wird eine Maschine nur in den Stunden, die du dafür freigegeben
  hast.
- **Jede Nacht ein Backup.** Jede Maschine schickt ein verschlüsseltes Backup an
  einen Backup-Server, der dir gehört. Sie kann ihren Backups nur etwas
  hinzufügen, aber nichts löschen. Ein Angreifer kann sie also nicht vernichten.
  Auch die Fleet-Datei und ihre Secrets werden gesichert.
- **Wiederherstellung im Ernstfall.** Die Festplatten sind verschlüsselt. Beim
  Start entsperren die Maschinen sie selbst, oder du entsperrst sie aus der
  Ferne. Muss eine Maschine neu aufgesetzt werden, kommt ihre Konfiguration aus
  der Fleet-Datei und ihre Daten kommen aus dem Backup.

## Die Maschinen { #the-machines }

Jede Maschine hat eine Rolle. Sie legt fest, welche Aufgabe die Maschine im
Netzwerk übernimmt.

| Rolle | Aufgabe der Maschine |
|---|---|
| `master` | Die einzige Maschine, die aus dem Internet erreichbar ist. Auf ihr läuft der WireGuard-Server. Ausgehenden Verkehr schickt sie über einen VPN-Anbieter oder direkt ins Internet, und sie stellt DNS mit Pi-hole, Tor und die Admin-Seiten bereit. Auf Wunsch laufen dort auch ein nostr-Relay und ein Hub. |
| `node` · `gateway` | Leitet ein Heim- oder Büronetz durch das VPN, mit Pi-hole als DNS- und DHCP-Server, einer Download-Station und SFTP. |
| `node` · `cloud` | Betreibt Nextcloud mit Collabora sowie Vaultwarden. |
| `node` · `minimal` | Hat nur die Verbindung zum Netzwerk und nginx. Die Module wählst du selbst, zum Beispiel Backups, Tang, Immich, Paperless-ngx oder OpenCloud. |
| `bare` | Enthält nur das Grundsystem. |

Master heißen nach Obstgerichten (sorbet, crumble, compote), Nodes nach Früchten
(papaya, lychee, quince). Der Master ist die einzige Maschine, die aus dem
Internet erreichbar sein muss. Standardmäßig ist dort genau ein Port offen:
WireGuard auf UDP 51820.

```bash
kiwi install kiwi-server            # oder aus einem Klon: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # pro Maschine ein ISO, das ohne Zutun installiert
kiwi-server apply fleet.yaml papaya # die Rolle, per SSH
```
