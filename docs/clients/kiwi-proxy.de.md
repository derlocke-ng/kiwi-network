# kiwi-proxy

kiwi-proxy ist für Leute gedacht, die in vielen Kundennetzen arbeiten und
jedes davon über eine eigene VPN- oder SOCKS-Verbindung erreichen. Jede
Verbindung speicherst du als **Exit** unter einem Namen und startest sie nur,
wenn du sie brauchst. Die Exits sind voneinander abgeschottet, und ein
Programm, das einen Exit nutzt, erreicht das Netzwerk nur über diesen Exit.
Zehn Kunden bedeuten deshalb nicht zehn VPN-Verbindungen, die gleichzeitig auf
dem Host laufen. Browser, Testwerkzeuge, Programme auf dem Host und Maschinen,
die du mit kiwi-server betreibst, können einen Exit nutzen. kiwi-proxy läuft in rootless Podman,
also in Containern, die unter deinem eigenen Benutzer ohne Root-Rechte laufen.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Aktuelles Release: **v0.7.3**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md), Scope user.
- Es besteht aus einem Kommandozeilenwerkzeug (`kiwi-proxy`), einer GTK4-App
  (**Kiwi Proxy**) und systemd-Benutzer-Units. Die Proxy-Technik war früher
  Teil von kiwi-fox. Sie wurde in ein eigenes Projekt ausgelagert, damit mehr
  als eine App sie nutzen kann.

Ein **Exit** ist eine Verbindung zu einem Upstream, die einen Namen hat. Der
Upstream ist der Proxy, an den der Verkehr geschickt wird. Das ist entweder ein
SOCKS5-Proxy, den du bekommen hast, oder einer, den ein
[Provider-Modul](providers.md) für dich über Tor, einen VPN-Tunnel, 9proxy oder
Mysterium anlegt. Ein Exit allein ist nur ein gespeicherter Eintrag, für ihn
läuft noch nichts. Erst wenn du einen Exit startest, fährt kiwi-proxy dafür
einen **Gateway-Container** hoch:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Zum Gateway gehört ein Netzwerk-Namespace, also ein eigener Netzwerk-Stack mit
eigenen Routen und Firewall-Regeln. Ein Browser von kiwi-fox, eine Box von
kiwi-custodia oder ein Werkzeug-Container teilt sich diesen Namespace und hängt
damit als Mitglied am Gateway. Von da an führt seine einzige Route zum Upstream
des Exits. Fällt das Gateway aus, haben seine Mitglieder keine Route mehr. Das
heißt fail-closed: Ein Ausfall kappt die Verbindung und öffnet nie einen
anderen Weg.

## Installation { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox und kiwi-custodia bringen es mit
kiwi-proxy setup             # das Gateway-Image, DNS-Daten, Images der Provider-Module
```

kiwi-proxy braucht rootless Podman und Python 3.12+ mit pydantic. Die App
braucht außerdem GTK4 und libadwaita. Passwörter werden über `secret-tool` im
Schlüsselbund des Desktops gespeichert. Auf einem Rechner ohne Schlüsselbund
landen sie in Dateien mit den Rechten 0600, die nur dein Benutzer lesen kann.

## Bedienung { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # ein Exit; noch läuft nichts
kiwi-proxy add tor-de --module tor --country de        # ein Exit aus einem Provider-Modul
kiwi-proxy list
kiwi-proxy check client-a      # was die Welt darüber sieht
kiwi-proxy up client-a         # sein Gateway starten und laufen lassen
kiwi-proxy down client-a       # es beenden, samt allem, was daran hängt
kiwi-proxy ps                  # laufende Gateways, egal welche App sie gestartet hat
kiwi-proxy reap                # Gateways beenden, die niemand nutzt
kiwi-proxy-gui                 # "Kiwi Proxy" in der Anwendungsübersicht
```

Ein Endpunkt ist die Adresse eines Upstream. Du kannst ihn als
`socks5://user:pass@host:port`, `http://…` oder `https://…` schreiben oder im
Format der Anbieter, `host:port:user:pass`. `kiwi-proxy test ENDPOINT` testet
einen Endpunkt, ohne einen Exit anzulegen.

### Exits für Programme auf dem Host { #exits-for-host-applications }

Ein Programm auf dem Host muss nicht in einem Container laufen, um einen Exit
zu nutzen. kiwi-proxy kann einen Exit als SOCKS5-Port auf dem Host anbieten,
mit einem eigenen Port pro Exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Standardmäßig lauscht der Port nur auf `127.0.0.1`. Soll er auf einer anderen
Adresse lauschen, musst du entweder mit `--expose-user` einen Benutzernamen
setzen oder mit `--expose-open` ausdrücklich offenen Zugang erlauben. Soll ein
Exit ab der Anmeldung laufen, führe
`systemctl --user enable --now kiwi-proxy@NAME` aus.

### DNS { #dns }

- Der **Resolver-Modus** ist voreingestellt. dnscrypt-proxy löst Namen per DNS
  over HTTPS (DoH) auf und schickt diese Anfragen über den Exit. Als
  DoH-Resolver lassen sich Google, Cloudflare, Quad9 oder Mullvad verwenden.
  Blocklisten (OISD) werden angewendet und täglich aktualisiert.
- Der **Remote-Modus** (`--dns remote`) reicht die Namen an den Upstream
  weiter, der sie selbst auflöst. Dieser Modus ist für Tor und `.onion`-Namen
  gedacht. Die Blocklisten gelten auch hier.

### Regeln des Gateways { #rules-of-the-gateway }

- UDP wird nicht weitergeleitet. Es gibt also kein QUIC, keine WebRTC-Medien
  und kein unverschlüsseltes DNS.
- Ein Exit erreicht die Außenwelt nur über IPv4. Ein Name ohne IPv4-Adresse
  wird abgewiesen.
- Ein Gateway, das eine andere App gestartet hat, etwa kiwi-fox oder
  kiwi-custodia, wird entfernt, sobald sein letztes Mitglied weg ist. Ein
  Gateway, das du mit `kiwi-proxy up` gestartet hast, läuft weiter, bis du
  `kiwi-proxy down` ausführst.
- Jeder Exit hat genau ein Gateway, und beliebig viele Mitglieder können daran
  hängen. Mitglieder, die voneinander getrennt bleiben müssen, nutzen
  verschiedene Exits.

## Die App { #the-app }

In der App **Kiwi Proxy** legst du Exits an und bearbeitest sie, entweder aus
einem SOCKS5-Proxy, den du bekommen hast, oder aus einem Provider-Modul. Bei
einem Exit aus einem Modul wählst du aus einer durchsuchbaren Länderliste oder
aus einer Liste von Knoten. Du kannst Exits starten und stoppen, einen Exit als
SOCKS5-Port auf diesem Rechner anbieten und dessen Adresse kopieren. Außerdem
prüfst du dort, was die Außenwelt sieht, wenn du dich über einen Exit
verbindest. Die App zeigt auch,
welche Mitglieder an einem Gateway hängen, samt ihren Logs, und sie richtet
Provider-Module ein und konfiguriert sie.

## Auf einer Maschine mit kiwi-server { #on-a-kiwi-server-machine }

Das Repository von kiwi-proxy enthält auch ein Modul für kiwi-server. Damit
stellt eine Maschine, die du mit kiwi-server betreibst, Exits für das ganze
Mesh bereit, also für
das private WireGuard-Netzwerk, in dem deine Maschinen hängen. Das Modul
betreibt ein Gateway pro Exit und bietet es auf der Mesh-Adresse des Hosts an.
Laut seiner Dokumentation ist das Modul noch nicht im Quellbaum von kiwi-server
und wurde noch auf keiner Maschine ausgeführt. Provider-Module funktionieren
nur auf dem Desktop und laufen nicht auf einer solchen Maschine.

Weiterlesen: [Architektur](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[Nutzer eines Exits](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[Plugin-System](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
