# Wohin es geht

!!! info "Entworfen, nicht gebaut"
    Diese Seite fasst den
    [Control-Plane-Entwurf](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    von kiwi-server zusammen, beschlossen im Oktober 2026. Sofern eine Zeile nicht
    *gebaut* sagt, existiert nichts davon bisher.
    Die [Roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    hält die Reihenfolge fest.

Heute ist kiwi-server ein Desktop-Werkzeug: Die Fleet-Datei, die Secrets und die CA
liegen auf der Maschine des Betreibers. Der Plan ist, daraus einen **Dienst** zu
machen, der auf einem Node laufen kann, sodass sich ein Netzwerk ohne Linux-Desktop
anlegen und verwalten lässt, vom Telefon aus und von mehr als einer Person.
Maschinen bleiben aus der Fleet-Datei reproduzierbar. Die Control Plane ist einfach
das, was diese Datei hält und den Renderer ausführt.

## Die Schichten { #the-layers }

1. **kiwi-modules**: die Module und der Render-Vertrag für eine Maschine. *Gebaut.*
2. **kiwi-stack**: die Maschinenseite, ab `kiwi-stack apply`. *Gebaut.*
3. **kiwi-server-Kern**: die Fleet, Hosts, Ziele, ISOs, die CA, Aufnahme und
   Anwenden, ohne Oberfläche wie heute. *Gebaut.*
4. **Das Steuerungsmodul**: der Kern als Container, mit einer API und einer
   Web-Oberfläche, als Modul auf einem Node wie jedes andere.
5. **Clients**: zuerst die Web-Oberfläche. Die GTK-App bleibt und spricht mit der
   lokalen CLI oder über das Mesh mit einem Controller, und die CLI bleibt auch. Kein
   Frontend bekommt eigene Logik.

## Der Control-Node { #the-control-node }

Der Controller läuft auf einem Node zu Hause (dem *Control-Node*), aus dem Mesh nur
für Admins erreichbar, auf einer verschlüsselten Festplatte. Er hält den Seed, den
CA-Schlüssel, die Fleet-Datei und jede Konfiguration.

Der gemietete **Master wird zu austauschbarer Relay-Infrastruktur**. Er hält nur,
was er zum Laufen braucht: seine WireGuard-Schlüssel und Peers, seine eigenen
Passwörter und sein Zertifikat. Ihn zu verlieren kostet ein erneutes Anwenden vom
Control-Node aus. Den Control-Node zu verlieren kostet eine Wiederherstellung des
Fleet-Backups.

## Benutzer { #users }

Ein Block `users:` mit zwei Rollen: ein **Fleet-Admin**, der alles kann, und
**Node-Admins**, die an ihre eigenen Hosts gebunden sind. Ein Node-Admin sieht
Status, Logs, Workloads und Backups dieser Hosts und nimmt Geräte in die Gruppen
auf, die der Fleet-Admin erlaubt, sieht aber nichts vom Master, von der CA oder von
den anderen Nodes. Die Anmeldung ist ein Passwort plus ein Client-Zertifikat der
Fleet-CA oder WebAuthn, und jede Änderung geht in ein Audit-Log.

## Eine Maschine aufnehmen { #joining-a-machine }

Beide Wege bleiben:

- **Eine ISO pro Host** mit ihrer Rolle (das heutige `build --offline`), für
  Offline-Installationen.
- **Eine generische Bootstrap-ISO** pro Ziel, einmal von der CI gebaut und ohne
  Secrets. Beim ersten Booten holt sie sich ihre Rolle mit einem einmaligen
  **Join-Token** vom Controller. Eine von Hand installierte Maschine oder ein VPS
  tritt mit einer Zeile bei:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Jede Maschine aus der CoreOS-Linie soll **ein bootc-Image** betreiben, wobei die
Rolle beim ersten Booten ankommt.

## Föderation und Multi-Hop { #federation-and-multi-hop }

Netzwerke, die gegenseitig ihrer CA vertrauen und einander Namen delegieren, werden
zu Clients voneinander. Mit dem dritten Ausgangsmodus kann der Master eines Netzwerks
das Internet über den eines anderen erreichen: **Multi-Hop**, bei dem der zweite
Master nur den ersten sieht. Mehrere Master eines Betreibers ergeben dann einen
eigenen VPN-Dienst: Eingangs-Master in einem Land, Ausgangs-Master in anderen, Tor
darin.

## Der Obstgarten { #the-orchard }

Der Obstgarten (orchard) ist für Leute, die viele Master für andere betreiben. Er ist
eine eigene App oder ein kiwi-server-Plugin, das VPSes über Provider-APIs anlegt,
jedem Master seine Installation und ein Registrierungs-Token gibt, von jedem Master
einen Heartbeat einsammelt (Version, Zustand, Festplatte, letztes Update) und Updates
ausrollt, indem es Image-Tags pro Kanal verschiebt.

Er kann sich nicht an einem Master anmelden, keine Fleet lesen und keinen Node
anfassen. Der Control-Node jedes Mandanten zu Hause behält dessen Netzwerk. Der
Hoster des Masters kann es nicht lesen und betreibt eine VM pro Mandant. Die
netcup-Unterstützung von kiwi-server (`kiwi-server
vps`, *gebaut*) ist das erste Stück seines Provider-Treibers.

## Mehr Hoster und Netzwerk-Boot { #more-hosters-and-network-boot }

*Geplant.* Das Ziel ist eine vollautomatische Installation, wo auch immer eine
Maschine steht.

- **Hoster als Plugins.** netcup ist heute eingebaut. Der Plan ist ein eigenes
  Repository für Hoster-APIs, damit jeder AWS, Hetzner und den Rest so ergänzen
  kann, wie netcup jetzt funktioniert: einen Server anlegen oder löschen, die
  Installation darauf bringen und ihn booten.
- **Wake-on-LAN und PXE-Boot** für Maschinen zu Hause: Ein Node wacht auf und
  installiert sich über das Netzwerk, ohne USB-Stick.

## Außerdem auf der Liste { #also-on-the-list }

Ein Standby-Master, rootless podman, IPv6 Ende-zu-Ende, ARM-Boards, Portbereiche und
ein Spiele-Modul sowie eine Wiederherstellung der Daten eines Nodes beim ersten
Booten.
