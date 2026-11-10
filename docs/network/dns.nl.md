# DNS, namen en certificaten

## Eén resolverketen { #one-resolver-chain }

DNS is één keten voor het hele netwerk:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **VPN-clients** (laptops, telefoons) vragen het aan de Pi-hole van de master op
  `10.8.0.1`.
- **De Pi-hole van een node** vraagt het eerst aan de Pi-hole van de master,
  zodat het netwerk één blokkeerlijst deelt en elke opzoeking via de exit van de
  master vertrekt. Quad9 (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) volgt in
  strikte volgorde en antwoordt alleen zolang de master onbereikbaar is.
- **De Pi-hole van de master** stuurt door naar de DNS-over-TLS-resolver van zijn
  VPN-client (standaard Quad9, `dot_providers`).
- **Namen onder het domein van de fleet** worden naar de master doorgestuurd en
  verlaten hem nooit. De master markeert het domein als lokaal.

Elke stackhost heeft de namen van de fleet ook in `/etc/hosts` (zijn eigen namen
wijzen naar hemzelf), zodat back-ups en certificaatvernieuwingen zonder Pi-hole
kunnen opzoeken. Op Fedora CoreOS en uCore zoekt de host zelf op via de Pi-hole
van zijn eigen stack.

**Buren op hetzelfde LAN.** De Pi-hole en het hosts-bestand van een node
antwoorden met het **LAN-adres** van fleet-nodes die een statisch adres in het
eigen subnet hebben, zodat verkeer tussen twee machines in dezelfde kamer in de
kamer blijft. De master blijft antwoorden met mesh-adressen.

## Namen: `service.hostname.home` { #names-servicehostnamehome }

Elke host is `<host>.<domain>` (`papaya.home`), en elke dienst die hij draait is
een naam daaronder: `cloud.papaya.home`, `vault.papaya.home`,
`portainer.papaya.home`, `dl.lychee.home`, en op de master `wg.sorbet.home`,
`pihole.sorbet.home`, `hub.sorbet.home`, `relay.sorbet.home`. Elke naam die een
module aankondigt, komt in de DNS-records van de fleet op het **mesh-adres** van
de host. Elke Pi-hole in de fleet kan elke host- en dienstnaam opzoeken
(split-horizon, `fleet_records`). Voeg je eigen namen toe met `extra_records`.

Het standaarddomein is **`.home`**, omdat ICANN het niet als publiek topleveldomein
zal delegeren. Een fleet-naam kan nooit naar een publiek register lekken, en
niemand anders kan hem registreren of er een door browsers vertrouwd certificaat
voor krijgen. `.kiwi` is een echt TLD, en daarom is de fleet ervan weggegaan.
kiwi-server controleert je keuze: `home`, `corp`, `mail`, `internal`, `arpa` en
`test` gaan zonder melding door, `.local` wordt geweigerd (dat hoort bij mDNS),
`.lan` krijgt een waarschuwing (routers beantwoorden het zelf), en publieke TLD's
krijgen een waarschuwing.

Namen *buiten* het domein van de fleet, voor een publieke hub of relay, krijgen
Let's Encrypt-certificaten wanneer de reverse proxy van de master publiek is.

## Mullvad-SOCKS5-proxy's op naam { #mullvad-socks5-proxies-by-name }

Sinds kiwi-server 2.2.0 antwoordt de Pi-hole van de master voor elke
**Mullvad-SOCKS5-proxy**, zowel als `de-fra-wg-socks5-001.relays.mullvad.net` als
in de korte vorm `de-fra-001.mullvad.home`. gluetun weigert deze antwoorden in
een privébereik (bescherming tegen DNS-rebinding), dus zonder de records zouden
de namen alleen via de fallback-resolvers opgezocht kunnen worden. Een hosttimer
(`km-mullvad-socks.timer`, elke 6 uur) ververst de lijst vanuit
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Alleen namen `*.relays.mullvad.net` op `10.x`-adressen worden daaruit
geaccepteerd, zodat de lijst nooit een andere naam kan omleiden.

Het staat aan in de master-preset, waarvan de exit Mullvad is. Zet het uit met
`mullvad_socks: false` in het `dns:`-blok van de master.

## Eén CA voor de fleet { #one-ca-for-the-fleet }

Met `tls.auto: true` (de standaard) houdt kiwi-server **één
certificaatautoriteit** voor de fleet bij in `secrets/ca/` (`kiwiCA.key`,
`kiwiCA.pem`, RSA-4096, 3650 dagen geldig), aangemaakt de eerste keer dat een
host een certificaat nodig heeft. Elke host die de reverse proxy draait, krijgt
een certificaat voor `<hostname>` en `*.<hostname>` (825 dagen, de langste
looptijd die browsers nog accepteren, vernieuwd als er minder dan 30 dagen over
zijn), en elke machine die kiwi-server bouwt, installeert de CA in haar
trust store.

Stel **name constraints** in en de CA kan alleen namen onder het domein van de
fleet ondertekenen: `tls: { name_constraints: [home] }`. De voorbeeld-fleet doet
dit; de ingebouwde standaard is geen beperking. Een gestolen `kiwiCA.key` is dan
voor al het andere waardeloos, en dat is belangrijk, want elke machine vertrouwt
hem.

```bash
kiwi-server ca fleet.yaml        # de CA van de fleet tonen
```

Importeer `kiwiCA.pem` op je eigen apparaten (browsers, telefoons) zodat
`https://cloud.papaya.home` vertrouwd wordt. Wil je in plaats daarvan je eigen
certificaten gebruiken, stel dan `tls_fullchain` en `tls_privkey` in de module
reverse-proxy in.

!!! warning "Houd `secrets/` privé"
    `kiwiCA.key` ondertekent certificaten die al je machines vertrouwen. Houd
    `secrets/` en `output/` buiten git (`output/` staat al in de
    `.gitignore` van kiwi-server).
