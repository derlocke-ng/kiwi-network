# kiwi-killswitch

Ein **Fail-Closed-VPN-Kill-Switch** für GNOME unter Fedora Silverblue und Bluefin.
Ein einziger Root-Daemon besitzt die Firewall. Ein Schalter in den
GNOME-Schnelleinstellungen, eine GTK4-App und eine CLI steuern ihn über den
D-Bus-Systembus, ohne je nach einem Passwort zu fragen.

Er schützt immer **eine** VPN-Verbindung, WireGuard oder OpenVPN. Er verbindet dein
VPN nicht für dich: Du baust Verbindungen in den GNOME-Einstellungen auf, und der
Kill Switch baut eine dichte Firewall um das, was tatsächlich aktiv ist.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Aktuelles Release: **v0.2.3**. Es steht im [Kiwi-Katalog](catalogs.md), Bereiche Benutzer + System.
- GNOME Shell 45 bis 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Eine GNOME-Erweiterung ist ein unprivilegierter Prozess. Sie kann und darf die
Firewall nicht anfassen, also liegt die Durchsetzung im Daemon, und die Oberfläche
fragt nur.

## Was er tut { #what-it-does }

- **Fail-closed.** `policy drop` auf Output, Input und Forward, IPv4 und IPv6,
  atomar ausgetauscht. Verkehr geht nur durch den geschützten Tunnel hinaus. Fällt
  das VPN weg, startest du neu oder wechselst du von WLAN zu Tethering, bleibt alles
  blockiert, bis ein erlaubter Weg wieder da ist.
- **Neue Schnittstellen können nicht lecken.** Steckst du im scharfen Zustand
  USB-Tethering ein oder schaltest WLAN ein, ist die neue Schnittstelle
  standardmäßig blockiert, nicht durch Auslassung erlaubt.
- **Drei Durchsetzungsstufen.** *Standard* filtert Output und Input. *Strict* (der
  Standard) filtert außerdem **weitergeleiteten** Verkehr, weil Container, VMs und
  Waydroid über den Host routen und weitergeleitete Pakete nie den Output-Hook
  passieren. *Paranoid* fügt auf jeder Netzwerkkarte eine **netdev-Egress**-Chain
  hinzu, die einzige Ebene, die Raw-Socket-Verkehr sieht.
- **DNS kann nicht abwandern.** Wähle: durch das VPN, das eigene des Netzwerks (nur
  vertrauenswürdige kiwi-nodes) oder einen Resolver, den du aussuchst. Angewendet
  wird es über die Einstellungen pro Link von systemd-resolved, mit einer
  nftables-Rückfallsicherung, die jede andere Anfrage verwirft.
- **Hostnamen-Endpunkte werden festgenagelt, nicht DNS anvertraut.** Der Daemon löst
  den Hostnamen eines VPN-Servers selbst auf, per DNS-over-HTTPS an eine fest
  hinterlegte IP mit geprüftem Zertifikat, und speichert jede Antwort zwischen.
- **Verbindung auswählen, dann Anwenden.** Änderungen werden vorgemerkt, sodass du von
  „Heim-LAN + kiwi-node“ zu „Tethering + VPN“ wechseln kannst, *während du schon im
  Tethering bist*, und es dann als eine atomare Transaktion anwendest, ohne
  ungeschütztes Zeitfenster dazwischen.
- **Vertrauenswürdige kiwi-nodes.** Ein Gateway, das schon für dich tunnelt (ein
  [Gateway-Node](../server/roles.md#node)), erkannt an IP **und** MAC, kann in
  seinem eigenen Netz an die Stelle des VPN treten. Das ist Opt-in und wird nie
  erraten.
- **Ein VPN, durchgesetzt.** Nur der Server der ausgewählten Verbindung ist
  erreichbar. Jeder andere Tunnel, den du startest, kann sich nicht verbinden, und
  die Oberfläche nennt ihn.
- **Übersteht alles.** Neustarts, Ab- und Anmelden, Neustarts von NetworkManager:
  Die Regeln bleiben. Eine eigene Unit setzt eine harte Sperre, *bevor das Netzwerk
  hochkommt*.

## Installation { #install }

Er braucht `nftables`, `NetworkManager`, `python3-gobject` und, für WireGuard,
`wireguard-tools`, alles auf Silverblue und Bluefin vorhanden. Nichts wird in das
unveränderliche `/usr` geschrieben. Dein Benutzer muss in `wheel` sein.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

Oder aus einem Klon: `sudo ./install.sh install` (Daemon, CLI, Bus-Richtlinie und
systemd-Units), dann `./install.sh install` (die GNOME-Erweiterung und die
Einstellungs-App). Melde dich ab und wieder an, damit GNOME die Erweiterung lädt.
Die Deinstallation entschärft zuerst, sodass sie dich nicht ausgesperrt
zurücklassen kann.

## Benutzung { #use }

Öffne **Schnelleinstellungen → Kill Switch**, um scharf zu schalten, zu entschärfen
und auszuwählen, welches VPN geschützt wird, oder **Kiwi Kill Switch** im App-Raster
für alles andere.

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
    Das Scharfschalten kappt eine Sitzung aus einem Subnetz, das nicht in
    `mgmt_subnets` steht. Das ist korrektes Kill-Switch-Verhalten. Setz es vorher:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Wiederherstellung.** Die CLI braucht kein Netzwerk, also reicht immer ein TTY:
`kiwi-killswitch disarm`. Ist der Daemon selbst weg:
`sudo nft delete table inet kiwi_ks` und `sudo nft delete table netdev kiwi_ks_egress`.

**Virtuelle Maschinen.** Eine VM im Bridge-Modus routet nie über den Host, also
lässt der Kill Switch sie in Ruhe (vermeide `paranoid`, das an der physischen Karte
filtert). Eine VM hinter NAT routet über den Host. `strict` schickt sie durch den
Tunnel hinaus und blockiert sie, wenn der Tunnel unten ist. Füge ihr Subnetz zu
`mgmt_subnets` hinzu, damit ihr DHCP und DNS den Host erreichen:

| Einstellung | Ausgehend | Eingehend | Am Tunnel vorbei festgelegt |
|---|---|---|---|
| `allow_lan` | ja (auto) | nein | nein |
| `bypass_subnets` | ja | nein | nein |
| `mgmt_subnets` | ja | ja | ja |

**Überprüfen.** Schalte ihn scharf, dann nimm das VPN herunter
(`nmcli connection down …`). `curl --max-time 5 ifconfig.me` muss in eine
**Zeitüberschreitung** laufen, nicht deine echte IP zeigen. Beurteile ihn nicht
durch den Vergleich von Ausgangs-IPs: Belege die Nutzung des Tunnels mit
`wg show <iface> transfer` oder `ip route get 1.1.1.1`.

## Koexistenz und bekannte Grenzen { #coexistence-and-known-limits }

- **firewalld kann an bleiben.** Seine Chains laufen mit Priorität 10, unsere mit −10.
- Betreibe ihn **nicht** neben einem anderen Kill Switch, dem eine
  Output-Drop-Tabelle gehört.
- Lass `nftables.service` in Ruhe, wenn du es nicht benutzt. Es zu stoppen leert
  jede Tabelle. Der Daemon setzt seine Regeln innerhalb von Sekunden wieder durch,
  aber es gibt keinen Grund, dieses Fenster zu öffnen.
- Ein VPN mit einem **Hostnamen** als Endpunkt kann sich im scharfen Zustand nicht
  neu verbinden, außer DNS steht auf *a resolver I choose* (einem Resolver, den du
  aussuchst). NetworkManager und OpenVPN schlagen den Namen über den
  System-Resolver nach, der blockiert ist, solange kein Tunnel steht. Verbindungen
  mit einer wörtlichen IP sind nicht betroffen.
- **Ein Resolver, den du aussuchst, ist außerhalb des Tunnels erreichbar**, solange
  der Tunnel unten ist. Schalte DNS-over-TLS für ihn ein.
- **Ein vertrauenswürdiger Node, der ohne MAC gespeichert ist**, wird allein an
  seiner Gateway-Adresse erkannt.
- **Steuerung ohne Passwort** ist die D-Bus-Bus-Richtlinie für die Gruppe `wheel`.
  Das bedeutet auch, dass jedes Programm, das als du läuft, den Schalter ohne
  Rückfrage ausschalten kann.
- Er stoppt Lecks auf Netzwerkebene. Er ist nicht Tails oder Whonix und tut nichts
  gegen Browser-Fingerprinting, WebRTC oder eine App, die durch den Tunnel nach
  Hause telefoniert.
- Er ist ein persönliches Werkzeug und wurde nicht unabhängig geprüft.
  `tests/run.sh` testet den echten Daemon mit echtem nftables, jede Testgruppe in
  ihrem eigenen Namespace, ohne root.
- Seine Release-Tags sind noch nicht signiert, daher fragt seine Root-Hälfte mit
  kiwi-updater 2.4 bei Updates nach deinem Passwort.

Er stammt ab von `gnome-vpn-killswitch` (Boot-Reihenfolge), `kiwi-vpn-monitor`
(Gateway-Erkennung) und `nova-killswitch` (die Daemon-Architektur) des Autors.
