# kiwi-proxy

Versiegelte SOCKS5- und VPN-Ausgänge in rootless Podman, für Browser,
Testwerkzeuge, Host-Anwendungen und kiwi-server-Maschinen.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Aktuelles Release: **v0.7.3**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md), Benutzerbereich.
- Eine CLI (`kiwi-proxy`), eine GTK4-App (**Kiwi Proxy**) und systemd-Benutzer-Units.
  Es ist die Proxy-Engine, die früher in kiwi-fox steckte, herausgelöst, damit sie
  mehr als einer App dient.

Ein **Ausgang** ist ein Upstream mit Namen: ein SOCKS5, das du bekommen hast, oder
eines, das ein [Provider-Modul](providers.md) erzeugt (Tor, ein VPN-Tunnel, 9proxy,
Mysterium). Ein Ausgang ist nur Daten. Wird er hochgefahren, entsteht ein
**Gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Was auch immer dem Namespace des Gateways beitritt (ein kiwi-fox-Browser, eine
kiwi-custodia-Box, ein Werkzeug-Container), hat keine Route außer diesem Upstream.
Stirbt das Gateway, verlieren seine Mitglieder ihre Route.

## Installation { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox und kiwi-custodia bringen es mit
kiwi-proxy setup             # das Gateway-Image, DNS-Daten, Images der Provider-Module
```

Es braucht rootless Podman, Python 3.12+ mit pydantic und GTK4 + libadwaita für die
App. Passwörter landen im Schlüsselbund des Desktops (`secret-tool`) oder, auf einer
Maschine ohne Schlüsselbund, in Dateien mit 0600.

## Benutzung { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # an exit; nothing runs yet
kiwi-proxy add tor-de --module tor --country de        # an exit from a provider module
kiwi-proxy list
kiwi-proxy check client-a      # what the world sees through it
kiwi-proxy up client-a         # bring its gateway up and keep it up
kiwi-proxy down client-a       # tear it down, with whoever joined it
kiwi-proxy ps                  # running gateways, whichever app started them
kiwi-proxy reap                # tear down gateways nobody uses
kiwi-proxy-gui                 # "Kiwi Proxy" in the app grid
```

Endpunkte sind `socks5://user:pass@host:port`, `http://…`, `https://…` oder das
Herstellerformat `host:port:user:pass`. `kiwi-proxy test ENDPOINT` prüft einen,
ohne etwas anzulegen.

### Ausgänge für Host-Anwendungen { #exits-for-host-applications }

Jedes Programm auf dem Host kann einen Ausgang über einen veröffentlichten
SOCKS5-Port nutzen, ein Port pro Ausgang:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Der Port lauscht standardmäßig auf `127.0.0.1`. Eine andere Adresse braucht einen
Benutzernamen (`--expose-user`) oder ein ausdrückliches `--expose-open`.
`systemctl --user enable --now kiwi-proxy@NAME` hält einen Ausgang ab der Anmeldung
oben.

### DNS { #dns }

- **Resolver-Modus** (der Standard): dnscrypt-proxy löst per DoH über den Ausgang
  auf (Google, Cloudflare, Quad9 oder Mullvad als Upstream), mit Blocklisten (OISD),
  die täglich aktualisiert werden.
- **Remote-Modus** (`--dns remote`): Namen gehen an den Upstream selbst, für Tor und
  `.onion`-Namen. Die Blocklisten gelten weiterhin.

### Regeln des Gateways { #rules-of-the-gateway }

- UDP kommt nirgendwo hinaus: kein QUIC, keine WebRTC-Medien, kein DNS im Klartext.
- Nach außen ist ein Ausgang IPv4. Ein Name ohne IPv4-Adresse wird abgelehnt.
- Ein Gateway, das ein Nutzer hochgefahren hat, verschwindet, wenn sein letztes
  Mitglied geht. Eines, das mit `kiwi-proxy up` hochgefahren wurde, bleibt bis
  `kiwi-proxy down`.
- Ein Ausgang, ein Gateway, beliebig viele Mitglieder. Mitglieder, die getrennt
  bleiben müssen, nutzen verschiedene Ausgänge.

## Die App { #the-app }

**Kiwi Proxy** legt Ausgänge an und bearbeitet sie (ein SOCKS5, das du bekommen
hast, oder ein Provider-Modul, mit einer durchsuchbaren Länderliste oder
Node-Auswahl), fährt sie hoch und herunter, bietet einen als SOCKS5-Port auf diesem
Computer an und kopiert seine Adresse, prüft, was die Welt sieht, zeigt, wer einem
Gateway beigetreten ist, samt deren Logs, und richtet Provider-Module ein und
konfiguriert sie.

## Auf einer kiwi-server-Maschine { #on-a-kiwi-server-machine }

kiwi-proxy bringt außerdem ein kiwi-server-Modul mit, das Ausgänge für das ganze
Mesh bereitstellt (ein Gateway pro Ausgang, veröffentlicht auf der Mesh-Adresse des
Hosts). Es ist noch nicht im Baum von kiwi-server und ist noch auf keiner Maschine
gelaufen, wie seine Dokumentation sagt. Provider-Module sind ein Mechanismus für
den Desktop und laufen dort nicht.

Weiterlesen: [Architektur](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[Nutzer](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[Plugin-System](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
