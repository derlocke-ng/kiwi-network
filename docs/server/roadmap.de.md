# Wohin es geht

Diese Seite beschreibt, was aus kiwi-server werden soll und welche Teile dieses
Plans es schon gibt.

!!! info "Entworfen, noch nicht umgesetzt"
    Diese Seite fasst den [Entwurf der Control
    Plane](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    von kiwi-server zusammen, auf den man sich im Oktober 2026 geeinigt hat.
    Nichts davon gibt es bisher, außer wo eine Zeile *umgesetzt* sagt. In
    welcher Reihenfolge die Arbeit erledigt wird, steht in der
    [Roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md).

Heute ist kiwi-server ein Werkzeug für den Desktop. Die Fleet-Datei, die Secrets
und die CA (die Zertifizierungsstelle der Fleet) liegen auf dem Admin-Rechner.
Geplant ist, daraus einen **Dienst** zu machen, der auf einem Node laufen kann.
Ein Netzwerk lässt sich dann auch ohne Linux-Desktop anlegen und verwalten, vom
Handy aus und von mehr als einer Person. Die Maschinen bleiben dabei aus der
Fleet-Datei reproduzierbar. Die Control Plane ist der Teil, der diese Datei
verwahrt und den Renderer ausführt, also das Programm, das aus der Fleet-Datei
die Konfiguration jeder Maschine erzeugt.

## Die Schichten { #the-layers }

Der Entwurf teilt die Software in fünf Schichten.

1. **kiwi-modules** enthält die Module und den Render-Vertrag, der festlegt, wie
   die Konfiguration einer Maschine erzeugt wird. *Umgesetzt.*
2. **kiwi-stack** ist der Teil, der auf der Maschine läuft. Er beginnt mit
   `kiwi-stack apply`, das eine erzeugte Konfiguration auf die Maschine bringt.
   *Umgesetzt.*
3. **Der Kern von kiwi-server** kümmert sich um die Fleet, die Hosts, die
   Zielsysteme, die ISOs, die CA, das Aufnehmen von Geräten und `apply`. Er ist
   headless, hat also wie heute keine eigene grafische Oberfläche. *Umgesetzt.*
4. **Das Control-Modul** ist der Kern als Container, mit einer API und einer
   Weboberfläche. Es läuft auf einem Node wie jedes andere Modul.
5. **Clients** sind die Programme, mit denen du das Control-Modul bedienst. Die
   Weboberfläche kommt zuerst. Die GTK-App bleibt und spricht entweder mit der
   lokalen CLI oder über das Mesh, das private WireGuard-Netzwerk, mit einem
   Controller (einem laufenden Control-Modul). Auch die CLI bleibt. Die gesamte
   Logik bleibt im Kern, kein Client bekommt eine eigene.

## Der Control-Node { #the-control-node }

Der Controller läuft auf einem Node zu Hause, dem *Control-Node*. Nur Admins
können ihn erreichen, und zwar nur aus dem Mesh, und seine Festplatte ist
verschlüsselt. Auf ihm liegen der Seed, der Schlüssel der CA, die Fleet-Datei
und jede Konfiguration.

Der gemietete **Master wird zu einem Relay, das sich ersetzen lässt**. Er leitet
den Verkehr des Netzwerks weiter und hat nur, was er für den Betrieb braucht:
seine WireGuard-Schlüssel und Peers, seine eigenen Passwörter und sein
Zertifikat. Geht der Master verloren, richtest du ihn vom Control-Node aus neu
ein. Geht der Control-Node verloren, stellst du das Backup der Fleet wieder her.

## Benutzer { #users }

Ein `users:`-Block legt Benutzer mit einer von zwei Rollen an. Ein
**Fleet-Admin** darf alles. Ein **Node-Admin** ist an seine eigenen Hosts
gebunden. Er sieht Status, Logs, laufende Dienste und Backups dieser Hosts und
kann Geräte in die Gruppen aufnehmen, die der Fleet-Admin freigibt. Vom Master,
von der CA und von den anderen Nodes sieht ein Node-Admin nichts. Zum Anmelden
braucht ein Benutzer ein Passwort und zusätzlich entweder ein Client-Zertifikat
der Fleet-CA oder WebAuthn. Jede Änderung wird in einem Audit-Log festgehalten.

## Wie eine Maschine dazukommt { #joining-a-machine }

Eine Maschine kann auf zwei Wegen ins Netzwerk kommen, und beide bleiben
erhalten:

- **Ein ISO pro Host**, das die Rolle der Maschine enthält, so wie heute
  `build --offline`. Es ist für Installationen ohne Netzwerk gedacht.
- **Ein allgemeines Bootstrap-ISO** pro Zielsystem, das einmal von der CI gebaut
  wird und keine Secrets enthält. Beim ersten Start holt sich die Maschine ihre
  Rolle mit einem einmaligen **Join-Token** vom Controller. Eine Maschine, die
  von Hand installiert wurde, oder ein VPS kommt mit einer einzigen Zeile dazu:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Jede Maschine aus der CoreOS-Familie soll **ein einziges bootc-Image** nutzen,
also ein bootfähiges Container-Image, das für alle gleich ist. Ihre Rolle
bekommt die Maschine beim ersten Start.

## Föderation und Multi-Hop { #federation-and-multi-hop }

Die Föderation verbindet getrennte Kiwi Networks miteinander. Netzwerke, die der
CA des jeweils anderen vertrauen und einander Namen delegieren, werden
gegenseitig zu Clients. Ein Master hat drei Ausgangsarten, die bestimmen, wie
sein Verkehr ins Internet gelangt. Bei der dritten schickt der Master eines
Netzwerks seinen Internetverkehr über den Master eines anderen Netzwerks. Das
nennt sich **Multi-Hop**, und der zweite Master sieht nur den ersten. Wer auf
diese Weise mehrere Master betreibt, hat einen eigenen VPN-Dienst, mit
Eingangs-Mastern in einem Land, Ausgangs-Mastern in anderen Ländern und Tor
innerhalb des Netzwerks.

## Der Orchard { #the-orchard }

Der Orchard (englisch für Obstgarten) ist der geplante Dienst für Leute, die
viele Master für andere betreiben. Er ist eine eigene App oder ein Plugin für
kiwi-server. Er legt VPS über die APIs der Hoster an und gibt jedem Master seine
Installation und ein Registrierungs-Token. Von jedem Master sammelt er einen
Heartbeat ein, also eine regelmäßige Statusmeldung (Version, Zustand,
Festplatte, letztes Update). Updates verteilt er, indem er das Image-Tag des
jeweiligen Update-Kanals weitersetzt.

Der Orchard kann sich nicht auf einem Master anmelden, keine Fleet lesen und
keinen Node verändern. Jeder Kunde, also jeder, dessen Master für ihn betrieben
wird, verwaltet sein Netzwerk auf seinem eigenen Control-Node zu Hause. Die
Fleet und die Schlüssel bleiben dort. Der Hoster, auf dessen Infrastruktur die
VM des Masters läuft, kann die Netzwerkdaten des Kunden deshalb nicht lesen. Der
Master jedes Kunden läuft in einer eigenen VM. Der Orchard braucht einen Treiber
für die APIs der Hoster, und die netcup-Unterstützung von kiwi-server
(`kiwi-server vps`, *umgesetzt*) ist das erste Stück davon.

## Mehr Hoster und Start über das Netzwerk { #more-hosters-and-network-boot }

*Geplant.* Ziel ist, dass sich eine Maschine vollautomatisch installieren lässt,
egal wo sie steht.

- **Hoster als Plugins.** Die Unterstützung für netcup ist heute fest eingebaut.
  Geplant ist ein eigenes Repository für die APIs der Hoster, sodass jeder AWS,
  Hetzner und weitere Hoster ergänzen kann. Ein Plugin würde so arbeiten wie
  heute die netcup-Unterstützung: Es legt einen Server an oder löscht ihn,
  spielt die Installation auf und bootet ihn.
- **Wake-on-LAN und PXE-Boot** sind für Maschinen zu Hause geplant. Wake-on-LAN
  schaltet eine Maschine über das Netzwerk ein, und mit PXE bootet sie über das
  Netzwerk. Ein Node wacht dann auf und installiert sich über das Netzwerk, ganz
  ohne USB-Stick.

## Außerdem auf der Liste { #also-on-the-list }

In der Roadmap stehen außerdem ein Ersatz-Master in Bereitschaft, rootless
podman, IPv6 durchgängig von Ende zu Ende, ARM-Boards, Portbereiche und ein
Modul für Spiele sowie das Wiederherstellen der Daten eines Nodes beim ersten
Start.
