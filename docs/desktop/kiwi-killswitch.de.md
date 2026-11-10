# kiwi-killswitch

kiwi-killswitch ist ein **VPN-Kill-Switch** für GNOME auf Fedora Silverblue und
Bluefin. Ein Kill-Switch sorgt dafür, dass dein Rechner keinen Verkehr an
deinem VPN vorbei schickt, zum Beispiel wenn die VPN-Verbindung abbricht oder
wenn du in ein anderes Netz wechselst. Dieser hier ist **fail-closed**: Die
Firewall sperrt alles, was nicht ausdrücklich erlaubt ist. Wenn etwas ausfällt,
wird der Verkehr also blockiert und nicht durchgelassen.

Die Firewall wird allein von einem Daemon mit Root-Rechten verwaltet. Bedienen
kannst du ihn über einen Schalter in den GNOME-Schnelleinstellungen, über eine
GTK4-App oder über ein Kommandozeilenwerkzeug (CLI). Alle drei schicken ihre
Anfragen über den D-Bus-Systembus an den Daemon und fragen nie nach einem
Passwort.

kiwi-killswitch schützt immer **eine** VPN-Verbindung, WireGuard oder OpenVPN.
Die Verbindung zum VPN baut es nicht selbst auf. Deine Verbindungen startest du
in den GNOME-Einstellungen, und der Kill-Switch richtet seine Firewall-Regeln
für die Verbindung ein, die tatsächlich steht. So kann kein Verkehr den Rechner
an dieser Verbindung vorbei verlassen.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Aktuelles Release: **v0.2.3**. Es steht im [Kiwi-Katalog](catalogs.md) und
  hat zwei Scopes, user + system: Ein Teil wird in deinem Home-Verzeichnis
  installiert, der andere gehört root.
- Es funktioniert mit GNOME Shell 45 bis 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Eine GNOME-Erweiterung läuft ohne Root-Rechte. Sie kann die Firewall nicht
ändern und soll es auch nicht können. Deshalb übernimmt der Daemon das gesamte
Sperren, und die Oberfläche schickt ihm nur Anfragen.

## Was es macht { #what-it-does }

- **Es ist fail-closed.** Die Firewall verwendet `policy drop` für ausgehenden,
  eingehenden und weitergeleiteten Verkehr, für IPv4 und IPv6. Jedes Paket wird
  also verworfen, sofern keine Regel es erlaubt. Ein neuer Regelsatz ersetzt
  den alten in einem einzigen atomaren Schritt. Verkehr kann den Rechner nur
  durch den geschützten Tunnel verlassen. Bricht das VPN ab, startest du neu
  oder wechselst du vom WLAN zum Tethering, bleibt alles gesperrt, bis wieder
  ein erlaubter Weg zur Verfügung steht.
- **Neue Netzwerkschnittstellen sind gesperrt.** Steckst du USB-Tethering an
  oder schaltest du das WLAN ein, während der Kill-Switch scharf geschaltet,
  also aktiv ist, wird die neue Schnittstelle standardmäßig gesperrt. Sie wird
  nicht etwa deshalb durchgelassen, weil keine Regel sie erwähnt.
- **Es gibt drei Filterstufen.** *Standard* filtert ausgehenden und eingehenden
  Verkehr. *Strict* ist voreingestellt und filtert zusätzlich
  **weitergeleiteten** Verkehr. Das ist nötig, weil Container, VMs und Waydroid
  ihren Verkehr über den Host schicken und weitergeleitete Pakete nie durch den
  Output-Hook laufen. *Paranoid* fügt auf jeder Netzwerkkarte (NIC) eine
  **netdev-egress**-Kette hinzu. Nur auf dieser Ebene ist auch Verkehr aus Raw
  Sockets sichtbar.
- **DNS-Anfragen können den Tunnel nicht umgehen.** Du legst fest, welcher
  DNS-Resolver verwendet wird, solange der Kill-Switch scharf geschaltet ist.
  Du kannst DNS-Anfragen durch das VPN schicken, den Resolver des Netzes
  verwenden, in dem du gerade bist, oder einen Resolver, den du selbst
  auswählst. Den Resolver des Netzes kannst du nur im Netz eines
  vertrauenswürdigen kiwi-node verwenden. Umgesetzt wird deine Wahl über die
  Einstellungen, die systemd-resolved für jede Netzwerkschnittstelle einzeln
  hat (per-link). Als zweite
  Absicherung verwirft eine nftables-Regel jede andere Namensauflösung.
- **Bei einem VPN-Server mit Hostnamen verlässt sich der Daemon nicht auf
  gewöhnliches DNS.** Er löst den Hostnamen des VPN-Servers selbst auf. Dazu
  verwendet er DNS-over-HTTPS, verbindet sich mit einer fest eingetragenen
  IP-Adresse und prüft das Zertifikat. Jede Antwort speichert er zwischen.
- **Erst Verbindung wählen, dann anwenden.** Änderungen werden vorgemerkt, also
  gesammelt, und wirken erst, wenn du sie anwendest. Du kannst deshalb von
  „Heim-LAN + kiwi-node“ auf „Tethering + VPN“ umstellen, *während du schon
  über Tethering verbunden bist*. Beim Anwenden (*Apply*) werden dann alle
  Änderungen in einer einzigen atomaren Transaktion ausgeführt, und der
  Kill-Switch ist zu keinem Zeitpunkt dazwischen ausgeschaltet.
- **Vertrauenswürdige kiwi-nodes.** In deinem Netz gibt es vielleicht ein
  Gateway, das deinen Verkehr ohnehin schon durch einen Tunnel schickt. In
  einem Kiwi-Netzwerk ist das ein [Gateway-Node](../server/roles.md#node). In
  seinem eigenen Netz kann so ein Gateway die Rolle des VPN übernehmen. Der
  Kill-Switch erkennt es an seiner IP-Adresse **und** seiner MAC-Adresse. Das
  musst du selbst einschalten. Der Kill-Switch entscheidet nie von sich aus,
  dass ein Gateway vertrauenswürdig ist.
- **Es kann sich nur ein VPN verbinden.** Erreichbar ist nur der Server der
  ausgewählten Verbindung. Jeder andere Tunnel, den du startest, bekommt keine
  Verbindung, und die Oberfläche nennt ihn dir.
- **Die Regeln bleiben bestehen.** Sie gelten auch nach einem Neustart, nach
  dem Ab- und Wiederanmelden und nach einem Neustart des NetworkManager. Eine
  eigene Unit lädt sperrende Regeln, *bevor das Netzwerk hochkommt*.

## Installation { #install }

kiwi-killswitch braucht `nftables`, `NetworkManager` und `python3-gobject`,
für WireGuard außerdem `wireguard-tools`. Das alles ist auf Silverblue und
Bluefin vorhanden. Ins unveränderliche `/usr` wird nichts geschrieben. Dein
Benutzer muss in der Gruppe `wheel` sein.

```bash
kiwi install kiwi-killswitch   # beide Teile; richtet bei Bedarf den Scope system von kiwi ein
```

Du kannst es auch aus einem Klon des Repositorys installieren. Führe zuerst
`sudo ./install.sh install` aus. Das installiert den Daemon, die CLI, die
D-Bus-Policy und die systemd-Units. Danach installiert `./install.sh install`
die GNOME-Erweiterung und die Einstellungs-App. Melde dich ab und wieder an,
damit GNOME die Erweiterung lädt. Beim Deinstallieren wird der Kill-Switch
zuerst ausgeschaltet, damit du danach nicht vor einem gesperrten Netzwerk
sitzt.

## Bedienung { #use }

Über **Schnelleinstellungen → Kill Switch** schaltest du den Kill-Switch scharf
oder aus und wählst, welches VPN geschützt wird. Für alles andere öffnest du
**Kiwi Kill Switch** in der Anwendungsübersicht. Die CLI kennt diese Befehle:

```bash
kiwi-killswitch status                   # was gerade durchgesetzt wird
kiwi-killswitch list                     # VPN-Verbindungen, die NetworkManager kennt
kiwi-killswitch vpn <name>               # vormerken, welche geschützt wird
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # eine atomare Transaktion
kiwi-killswitch arm                      # oder: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # was vorgemerkt ist; revert verwirft es
```

!!! warning "Scharf schalten über SSH"
    Wenn du den Kill-Switch scharf schaltest, wird eine SSH-Sitzung aus einem
    Subnetz, das nicht in `mgmt_subnets` steht, getrennt. Genau so soll sich
    ein Kill-Switch verhalten. Wenn du über SSH arbeitest, setze vorher diese
    Werte:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Notfall.** Die CLI braucht kein Netzwerk. Eine Textkonsole (TTY) reicht also
immer, um `kiwi-killswitch disarm` auszuführen. Läuft der Daemon selbst nicht
mehr, löschst du seine Firewall-Tabellen mit
`sudo nft delete table inet kiwi_ks` und
`sudo nft delete table netdev kiwi_ks_egress`.

**Virtuelle Maschinen.** Eine VM im Bridge-Modus schickt ihren Verkehr nie über
den Host, der Kill-Switch wirkt sich also nicht auf sie aus. Verzichte in
diesem Fall auf `paranoid`, weil diese Stufe an der physischen Netzwerkkarte
filtert. Eine VM hinter NAT schickt ihren Verkehr über den Host. Mit `strict`
geht dieser Verkehr durch den Tunnel hinaus und wird gesperrt, wenn der Tunnel
nicht steht. Trag das Subnetz der VM in `mgmt_subnets` ein, damit ihre DHCP-
und DNS-Anfragen den Host erreichen. Die Tabelle zeigt, was jede Einstellung
erlaubt:

| Einstellung | Ausgehend | Eingehend | Am Tunnel vorbei |
|---|---|---|---|
| `allow_lan` | ja (automatisch) | nein | nein |
| `bypass_subnets` | ja | nein | nein |
| `mgmt_subnets` | ja | ja | ja |

**Prüfen, ob es funktioniert.** Schalte den Kill-Switch scharf und nimm dann
das VPN mit `nmcli connection down …` herunter. Jetzt muss
`curl --max-time 5 ifconfig.me` in eine **Zeitüberschreitung** laufen. Deine
echte IP-Adresse darf dabei nicht erscheinen. Beurteile das Ergebnis nicht
anhand der öffentlichen IP-Adressen, die du siehst. Ob der Verkehr wirklich
durch den Tunnel geht, zeigen `wg show <iface> transfer` oder
`ip route get 1.1.1.1`.

## Andere Firewalls und bekannte Grenzen { #coexistence-and-known-limits }

- **firewalld kann eingeschaltet bleiben.** Seine Ketten laufen mit Priorität
  10, die des Kill-Switch mit −10.
- Betreibe kiwi-killswitch **nicht** zusammen mit einem anderen Kill-Switch, der eine
  eigene Tabelle hat, die ausgehenden Verkehr verwirft.
- Lass `nftables.service` in Ruhe, wenn du es nicht benutzt. Wird dieser Dienst
  gestoppt, löscht er alle nftables-Tabellen. Der Daemon lädt seine Regeln zwar
  innerhalb von Sekunden wieder, aber für diese Sekunden fehlen sie, und dafür
  gibt es keinen Grund.
- Ein VPN, dessen Server als **Hostname** angegeben ist, kann sich nicht neu
  verbinden, solange der Kill-Switch scharf geschaltet ist, außer DNS steht auf
  *a resolver I choose* (ein selbst gewählter Resolver). Der Grund: NetworkManager
  und OpenVPN lösen den Namen über den Resolver des Systems auf, und der ist
  gesperrt, solange kein Tunnel steht. Verbindungen, deren Server als
  IP-Adresse angegeben ist, betrifft das nicht.
- **Ein selbst gewählter Resolver ist am Tunnel vorbei erreichbar**, solange
  der Tunnel nicht steht. Schalte für ihn DNS-over-TLS ein.
- **Ein vertrauenswürdiger Node, der ohne MAC-Adresse gespeichert wurde**, wird
  allein an seiner Gateway-Adresse erkannt.
- **Die Bedienung ohne Passwort** läuft über die D-Bus-Policy für die Gruppe
  `wheel`. Das heißt auch: Jedes Programm, das unter deinem Benutzer läuft,
  kann den Kill-Switch ausschalten, ohne dich zu fragen.
- kiwi-killswitch verhindert Lecks auf Netzwerkebene. Es ist kein Tails und kein Whonix.
  Gegen Browser-Fingerprinting, WebRTC oder eine App, die durch den Tunnel
  Daten an ihren Hersteller schickt, hilft es nicht.
- Es ist ein Werkzeug für den eigenen Gebrauch und wurde nicht unabhängig
  geprüft. `tests/run.sh` testet den echten Daemon mit echtem nftables. Jede
  Testgruppe läuft in einem eigenen Namespace, und die Tests brauchen kein
  root.
- Seine Release-Tags sind noch nicht signiert. Mit kiwi-updater 2.4 fragt sein
  root-Teil deshalb beim Update nach deinem Passwort.

kiwi-killswitch baut auf drei älteren Werkzeugen desselben Autors auf. Die
Reihenfolge beim Booten stammt aus `gnome-vpn-killswitch`, die Erkennung des
Gateways aus `kiwi-vpn-monitor` und die Architektur des Daemons aus
`nova-killswitch`.
