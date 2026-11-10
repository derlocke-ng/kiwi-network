# DNS, Namen & Zertifikate

Jede Maschine und jeder Dienst in einem Kiwi Network hat einen Namen, etwa
`cloud.papaya.home`, und du öffnest ihn per HTTPS mit einem Zertifikat, dem
deine Geräte vertrauen. Diese Seite erklärt, wie Namen im Netzwerk aufgelöst
werden, wie sie aufgebaut sind und woher die Zertifikate kommen. Die DNS-Server
sind Pi-holes, die außerdem unerwünschte Domains anhand einer gemeinsamen
Blockliste sperren.

## Eine Kette von Resolvern { #one-resolver-chain }

Alle DNS-Anfragen im Netzwerk laufen über dieselbe Kette von DNS-Servern:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **VPN-Clients** (Laptops, Handys) schicken ihre Anfragen an das Pi-hole des
  Masters unter `10.8.0.1`.
- **Das Pi-hole eines Nodes** fragt zuerst beim Pi-hole des Masters nach.
  Dadurch gilt im ganzen Netzwerk eine einzige Blockliste, und jede Anfrage
  gelangt über den Ausgang des Masters ins Internet, also über die
  Internetverbindung des Masters. An zweiter Stelle steht Quad9 (`9.9.9.9`,
  `149.112.112.112`, eingestellt mit `fallback_dns`). Die Reihenfolge wird
  strikt eingehalten, Quad9 antwortet also nur, solange der Master nicht
  erreichbar ist.
- **Das Pi-hole des Masters** leitet Anfragen an den DNS-over-TLS-Resolver
  seines VPN-Clients weiter. Standardmäßig ist das Quad9 (`dot_providers`).
- **Namen unter der Fleet-Domain** werden an den Master weitergeleitet und von
  dort nie weitergegeben, denn der Master behandelt die Domain als lokal.

Jede Maschine, auf der ein Stack läuft, hat die Namen der Fleet außerdem in
ihrer Datei `/etc/hosts`, wobei ihre eigenen Namen auf sie selbst zeigen. So
können Backups und Zertifikatserneuerungen Namen auch ohne Pi-hole auflösen.
Unter Fedora CoreOS und uCore nutzt die Maschine selbst das Pi-hole ihres
eigenen Stacks als Resolver.

**Nachbarn im selben LAN.** Haben andere Nodes der Fleet eine statische Adresse
im selben Subnetz wie ein Node, dann antworten das Pi-hole und die Hosts-Datei
dieses Nodes für sie mit ihrer **LAN-Adresse**. Verkehr zwischen zwei Maschinen
im selben LAN bleibt dann in diesem LAN. Der Master antwortet weiterhin mit
Mesh-Adressen.

## Namen: `service.hostname.home` { #names-servicehostnamehome }

Jeder Host heißt `<host>.<domain>`, zum Beispiel `papaya.home`. Jeder Dienst,
der auf ihm läuft, bekommt einen Namen unterhalb des Hostnamens:
`cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home` und auf dem Master `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Jeder Name, den ein Modul anmeldet, wird
mit der **Mesh-Adresse** des Hosts in die DNS-Einträge der Fleet aufgenommen.
Die Mesh-Adresse ist die Adresse einer Maschine im Mesh, dem privaten
WireGuard-Netzwerk, in dem alle deine Maschinen hängen. Jedes Pi-hole der Fleet
kann so jeden Host- und jeden Dienstnamen auflösen. Die Einstellung dafür heißt
`fleet_records`. Das Verfahren nennt sich Split-Horizon-DNS, weil die Namen nur
innerhalb deines Netzwerks beantwortet werden. Eigene Einträge ergänzt du mit
`extra_records`.

Die Standard-Domain ist **`.home`**. Sie wurde gewählt, weil die ICANN sie nicht
als öffentliche Top-Level-Domain (TLD) vergeben wird. Ein Name aus deiner Fleet
kann deshalb nie in einer öffentlichen Registry landen, und niemand sonst kann
ihn registrieren oder ein Zertifikat dafür bekommen, dem Browser vertrauen.
`.kiwi` dagegen ist eine echte TLD, und deshalb verwendet Kiwi Network sie nicht
mehr. kiwi-server prüft die Domain, die du wählst. `home`, `corp`, `mail`,
`internal`, `arpa` und `test` werden ohne Warnung akzeptiert. `.local` wird
abgelehnt, weil sie für mDNS reserviert ist. Bei `.lan` gibt es eine Warnung,
weil Router diese Domain selbst beantworten, und ebenso bei öffentlichen TLDs.

Namen *außerhalb* der Fleet-Domain, die du für einen öffentlichen Hub oder ein
öffentliches Relay brauchst, bekommen Zertifikate von Let's Encrypt, sofern der
Reverse-Proxy des Masters öffentlich ist.

## SOCKS5-Proxys von Mullvad per Namen { #mullvad-socks5-proxies-by-name }

Die SOCKS5-Proxys von Mullvad haben Adressen aus einem privaten Bereich. Mit
dieser Funktion kannst du sie über ihren Namen ansprechen. Seit kiwi-server
2.2.0 beantwortet das Pi-hole des Masters Anfragen nach jedem **SOCKS5-Proxy von
Mullvad**, sowohl unter seinem vollen Namen, etwa
`de-fra-wg-socks5-001.relays.mullvad.net`, als auch unter einem Kurznamen, etwa
`de-fra-001.mullvad.home`. gluetun verwirft DNS-Antworten, die auf private
Adressen zeigen, um sich gegen DNS-Rebinding zu schützen. Ohne diese Einträge
ließen sich die Namen deshalb nur über die Ausweich-Resolver auflösen. Ein Timer
auf dem Host (`km-mullvad-socks.timer`, alle 6 Stunden) holt die aktuelle Liste
von [derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Aus dieser Liste werden nur Namen unter `*.relays.mullvad.net` mit
`10.x`-Adressen übernommen. Die Liste kann also keinen anderen Namen umleiten.

Im Master-Preset ist die Funktion eingeschaltet, weil dessen Ausgang über
Mullvad läuft. Zum Ausschalten setzt du im `dns:`-Block des Masters
`mullvad_socks: false`.

## Eine CA für die ganze Fleet { #one-ca-for-the-fleet }

Eine Zertifizierungsstelle (CA) signiert die Zertifikate, die deine Dienste für
HTTPS verwenden. Mit `tls.auto: true`, der Standardeinstellung, verwaltet
kiwi-server in `secrets/ca/` **eine einzige Zertifizierungsstelle** für die
ganze Fleet. Die CA besteht aus den Dateien `kiwiCA.key` und `kiwiCA.pem`, nutzt
RSA-4096 und ist 3650 Tage gültig. kiwi-server legt sie an, sobald ein Host zum
ersten Mal ein Zertifikat braucht. Jeder Host, auf dem der Reverse-Proxy läuft,
bekommt ein Zertifikat für `<hostname>` und `*.<hostname>`. Es ist 825 Tage
gültig, das ist die längste Laufzeit, die Browser noch akzeptieren, und es wird
erneuert, wenn weniger als 30 Tage übrig sind. Jede Maschine, die kiwi-server
aufsetzt, nimmt die CA in ihren Zertifikatsspeicher auf.

Mit **Name Constraints** darf die CA nur Namen unter der Fleet-Domain signieren:
`tls: { name_constraints: [home] }`. Die Beispiel-Fleet setzt das. Ohne eigene
Angabe gilt aber keine Einschränkung. Mit der Einschränkung ist ein gestohlener
`kiwiCA.key` für jeden anderen Namen wertlos. Das ist wichtig, weil jede
Maschine der CA vertraut.

```bash
kiwi-server ca fleet.yaml        # die CA der Fleet anzeigen
```

Importiere `kiwiCA.pem` auf deinen eigenen Geräten (Browser, Handys), damit sie
`https://cloud.papaya.home` vertrauen. Wenn du lieber eigene Zertifikate
verwendest, setze `tls_fullchain` und `tls_privkey` im Modul reverse-proxy.

!!! warning "`secrets/` nicht aus der Hand geben"
    `kiwiCA.key` signiert Zertifikate, denen jede deiner Maschinen vertraut.
    Halte `secrets/` und `output/` aus git heraus (`output/` steht bereits in
    der `.gitignore` von kiwi-server).
