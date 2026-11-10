# DNS, Namen & Zertifikate

## Eine Resolver-Kette { #one-resolver-chain }

DNS ist eine einzige Kette für das ganze Netzwerk:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **VPN-Clients** (Laptops, Telefone) fragen das Pi-hole des Masters unter
  `10.8.0.1`.
- **Das Pi-hole eines Nodes** fragt zuerst das Pi-hole des Masters, sodass das
  Netzwerk eine Blockliste teilt und jede Anfrage über den Ausgang des Masters
  hinausgeht. Quad9 (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) folgt in strikter
  Reihenfolge und antwortet nur, solange der Master nicht erreichbar ist.
- **Das Pi-hole des Masters** leitet an den DNS-over-TLS-Resolver seines VPN-Clients
  weiter (standardmäßig Quad9, `dot_providers`).
- **Namen unter der Domain der Fleet** werden an den Master weitergeleitet und
  verlassen ihn nie. Der Master markiert die Domain als lokal.

Jeder Stack-Host trägt die Namen der Fleet außerdem in `/etc/hosts` (seine eigenen
Namen zeigen auf ihn selbst), sodass Backups und Zertifikatserneuerungen ohne ein
Pi-hole auflösen. Unter Fedora CoreOS und uCore löst der Host selbst über das
Pi-hole seines eigenen Stacks auf.

**Nachbarn im selben LAN.** Das Pi-hole und die Hosts-Datei eines Nodes antworten
mit der **LAN-Adresse** von Fleet-Nodes, die eine statische Adresse im eigenen
Subnetz haben, sodass Verkehr zwischen zwei Maschinen im selben Raum im Raum bleibt.
Der Master antwortet weiterhin mit Mesh-Adressen.

## Namen: `service.hostname.home` { #names-servicehostnamehome }

Jeder Host ist `<host>.<domain>` (`papaya.home`), und jeder Dienst, den er
betreibt, ist ein Name darunter: `cloud.papaya.home`, `vault.papaya.home`,
`portainer.papaya.home`, `dl.lychee.home` und auf dem Master `wg.sorbet.home`,
`pihole.sorbet.home`, `hub.sorbet.home`, `relay.sorbet.home`. Jeder Name, den ein
Modul ankündigt, kommt mit der **Mesh-Adresse** des Hosts in die DNS-Einträge der
Fleet. Jedes Pi-hole in der Fleet löst jeden Host- und Dienstnamen auf
(Split-Horizon, `fleet_records`). Eigene fügst du mit `extra_records` hinzu.

Die Standard-Domain ist **`.home`**, weil ICANN sie nicht als öffentliche
Top-Level-Domain delegieren wird. Ein Fleet-Name kann nie in ein öffentliches
Register gelangen, und niemand sonst kann ihn registrieren oder ein von Browsern
anerkanntes Zertifikat dafür bekommen. `.kiwi` ist eine echte TLD, weshalb die Fleet davon
weggezogen ist. kiwi-server prüft deine Wahl: `home`, `corp`, `mail`, `internal`,
`arpa` und `test` gehen stillschweigend durch, `.local` wird abgelehnt (es gehört
mDNS), `.lan` bekommt eine Warnung (Router beantworten es selbst), und öffentliche
TLDs bekommen eine Warnung.

Namen *außerhalb* der Domain der Fleet, für einen öffentlichen Hub oder ein
öffentliches Relay, bekommen Zertifikate von Let's Encrypt, wenn der Reverse Proxy
des Masters öffentlich ist.

## Mullvad-SOCKS5-Proxys per Name { #mullvad-socks5-proxies-by-name }

Seit kiwi-server 2.2.0 antwortet das Pi-hole des Masters für jeden
**Mullvad-SOCKS5-Proxy**, sowohl als `de-fra-wg-socks5-001.relays.mullvad.net` als
auch in der Kurzform `de-fra-001.mullvad.home`. gluetun verwirft diese Antworten aus
privaten Adressbereichen (Schutz vor DNS-Rebinding), sodass die Namen ohne die
Einträge nur über die Fallback-Resolver auflösen würden. Ein Host-Timer
(`km-mullvad-socks.timer`, alle 6 Stunden) aktualisiert die Liste aus
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5). Daraus
werden nur Namen `*.relays.mullvad.net` mit `10.x`-Adressen übernommen, sodass die
Liste nie einen anderen Namen umleiten kann.

Im Master-Preset, dessen Ausgang Mullvad ist, ist es eingeschaltet. Schalte es mit
`mullvad_socks: false` im Block `dns:` des Masters aus.

## Eine CA für die Fleet { #one-ca-for-the-fleet }

Mit `tls.auto: true` (dem Standard) führt kiwi-server **eine
Zertifizierungsstelle** für die Fleet in `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`,
RSA-4096, 3650 Tage gültig), angelegt, wenn ein Host zum ersten Mal ein Zertifikat
braucht. Jeder Host, auf dem der Reverse Proxy läuft, bekommt ein Zertifikat für
`<hostname>` und `*.<hostname>` (825 Tage, die längste Laufzeit, die Browser noch
akzeptieren, erneuert, wenn weniger als 30 Tage übrig sind), und jede Maschine, die
kiwi-server baut, installiert die CA in ihrem Trust Store.

Setz **Name Constraints**, und die CA kann nur Namen unter der Domain der Fleet
signieren: `tls: { name_constraints: [home] }`. Die Beispiel-Fleet tut das; der
eingebaute Standard ist keine Einschränkung. Ein gestohlener `kiwiCA.key` ist dann
für alles andere wertlos, und das zählt, weil jede Maschine ihm vertraut.

```bash
kiwi-server ca fleet.yaml        # die CA der Fleet anzeigen
```

Importiere `kiwiCA.pem` auf deinen eigenen Geräten (Browser, Telefone), damit
`https://cloud.papaya.home` vertraut wird. Um stattdessen eigene Zertifikate zu
benutzen, setz `tls_fullchain` und `tls_privkey` im Modul reverse-proxy.

!!! warning "`secrets/` privat halten"
    `kiwiCA.key` signiert Zertifikate, denen jede deiner Maschinen vertraut. Halte
    `secrets/` und `output/` aus git heraus (`output/` steht bereits in der
    `.gitignore` von kiwi-server).
