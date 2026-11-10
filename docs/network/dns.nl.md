# DNS, namen en certificaten

Elke machine en elke dienst in een Kiwi Network heeft een naam, bijvoorbeeld
`cloud.papaya.home`, en je opent die via HTTPS met een certificaat dat je
apparaten vertrouwen. Op deze pagina lees je hoe namen in het netwerk worden
opgezocht, hoe ze zijn opgebouwd en waar de certificaten vandaan komen. De
DNS-servers zijn Pi-holes, die met een gedeelde blokkeerlijst ook ongewenste
domeinen blokkeren.

## Eén keten van DNS-servers { #one-resolver-chain }

Alle DNS-verzoeken in het netwerk gaan langs dezelfde keten van DNS-servers:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **VPN-clients** (laptops, telefoons) sturen hun verzoeken naar de Pi-hole van
  de master, op `10.8.0.1`.
- **De Pi-hole van een node** vraagt het eerst aan de Pi-hole van de master.
  Daardoor gebruikt het hele netwerk één blokkeerlijst en gaat elk verzoek naar
  internet via de uitgang van de master, de verbinding van de master met
  internet. Daarna komt Quad9 (`9.9.9.9`, `149.112.112.112`, ingesteld met
  `fallback_dns`). De volgorde is strikt, dus Quad9 antwoordt alleen zolang de
  master onbereikbaar is.
- **De Pi-hole van de master** stuurt verzoeken door naar de
  DNS-over-TLS-resolver van zijn VPN-client. Standaard is dat Quad9
  (`dot_providers`).
- **Namen onder het domein van de fleet** worden doorgestuurd naar de master en
  gaan van daaruit nooit verder. De master markeert het domein als lokaal.

Elke machine met een stack heeft de namen van de fleet bovendien in
`/etc/hosts` staan, waarbij haar eigen namen naar de machine zelf wijzen. Voor
back-ups en het vernieuwen van certificaten is dus geen Pi-hole nodig om namen
op te zoeken. Op Fedora CoreOS en uCore gebruikt de machine zelf de Pi-hole uit
haar eigen stack als resolver.

**Buren in hetzelfde LAN.** Hebben andere nodes van de fleet een vast adres in
het subnet van een node, dan antwoorden de Pi-hole en het hosts-bestand van die
node met hun **LAN-adres**. Verkeer tussen twee machines in hetzelfde LAN blijft
dan binnen dat LAN. De master blijft antwoorden met mesh-adressen.

## Namen: `service.hostname.home` { #names-servicehostnamehome }

Elke host heet `<host>.<domain>`, bijvoorbeeld `papaya.home`. Elke dienst die
erop draait, krijgt een naam onder de naam van de host: `cloud.papaya.home`,
`vault.papaya.home`, `portainer.papaya.home`, `dl.lychee.home`, en op de master
`wg.sorbet.home`, `pihole.sorbet.home`, `hub.sorbet.home`,
`relay.sorbet.home`. Elke naam die een module aanmeldt, komt met het
**mesh-adres** van de host in de DNS-records van de fleet te staan. Elke
Pi-hole in de fleet kent dus elke hostnaam en elke dienstnaam. De instelling
hiervoor is `fleet_records`. De techniek heet split-horizon DNS, omdat de namen
alleen binnen je eigen netwerk worden beantwoord. Eigen records voeg je toe met
`extra_records`.

Het standaarddomein is **`.home`**. Daarvoor is gekozen omdat ICANN het niet
als openbaar topleveldomein (TLD) zal uitgeven. Een naam in je fleet kan dus
nooit in een openbaar register terechtkomen, en niemand anders kan hem
registreren of er een certificaat voor krijgen dat browsers vertrouwen. `.kiwi`
is daarentegen een echt TLD, en daarom gebruikt Kiwi Network het niet meer.
kiwi-server controleert het domein dat je kiest. `home`, `corp`, `mail`,
`internal`, `arpa` en `test` worden zonder opmerking geaccepteerd. `.local`
wordt geweigerd, omdat het bij mDNS hoort. Bij `.lan` krijg je een
waarschuwing, omdat routers dat domein zelf beantwoorden, en bij openbare TLD’s
krijg je er ook een.

Namen *buiten* het domein van de fleet, die je nodig hebt voor een openbare hub
of relay, krijgen Let’s Encrypt-certificaten als de reverse proxy van de master
openbaar is.

## SOCKS5-proxy’s van Mullvad op naam { #mullvad-socks5-proxies-by-name }

De SOCKS5-proxy’s van Mullvad hebben adressen in een privébereik. Met deze
functie kun je ze toch bij naam gebruiken. Sinds kiwi-server 2.2.0 kent de
Pi-hole van de master elke **SOCKS5-proxy van Mullvad**, zowel onder de
volledige naam, zoals `de-fra-wg-socks5-001.relays.mullvad.net`, als onder een
korte naam, zoals `de-fra-001.mullvad.home`. gluetun weigert DNS-antwoorden die
naar privéadressen wijzen, als bescherming tegen DNS-rebinding. Zonder deze
records zouden de namen dus alleen via de fallback-resolvers te vinden zijn. Een
timer op de host (`km-mullvad-socks.timer`, elke 6 uur) haalt de lijst opnieuw
op bij
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Uit die lijst worden alleen namen onder `*.relays.mullvad.net` met een
`10.x`-adres overgenomen. De lijst kan dus nooit een andere naam omleiden.

In de preset voor de master staat de functie aan, omdat de uitgang van die
preset Mullvad is. Je zet haar uit met `mullvad_socks: false` in het blok
`dns:` van de master.

## Eén CA voor de hele fleet { #one-ca-for-the-fleet }

Een certificaatautoriteit (CA) ondertekent de certificaten die je diensten voor
HTTPS gebruiken. Met `tls.auto: true`, de standaardinstelling, beheert
kiwi-server in `secrets/ca/` **één certificaatautoriteit** voor de hele fleet.
De CA bestaat uit de bestanden `kiwiCA.key` en `kiwiCA.pem`, gebruikt RSA-4096
en is 3650 dagen geldig. kiwi-server maakt de CA aan zodra een host voor het
eerst een certificaat nodig heeft. Elke host waarop de reverse proxy draait,
krijgt een certificaat voor `<hostname>` en `*.<hostname>`. Dat certificaat is
825 dagen geldig, de langste looptijd die browsers nog accepteren, en het wordt
vernieuwd zodra er minder dan 30 dagen over zijn. Op elke machine die
kiwi-server opbouwt, wordt de CA in de trust store geïnstalleerd.

Stel je **naambeperkingen** (name constraints) in, dan kan de CA alleen namen
onder het domein van de fleet ondertekenen: `tls: { name_constraints: [home] }`.
In het voorbeeldfleetbestand staat die beperking, maar standaard is er geen. Met
de beperking heeft iemand die `kiwiCA.key` steelt er niets aan voor welke
andere naam dan ook. Dat is belangrijk, want elke machine vertrouwt de CA.

```bash
kiwi-server ca fleet.yaml        # de CA van de fleet tonen
```

Importeer `kiwiCA.pem` op je eigen apparaten (browsers, telefoons), zodat ze
`https://cloud.papaya.home` vertrouwen. Gebruik je liever je eigen
certificaten, stel dan `tls_fullchain` en `tls_privkey` in bij de module
reverse-proxy.

!!! warning "Houd `secrets/` privé"
    Met `kiwiCA.key` worden certificaten ondertekend die al je machines
    vertrouwen. Houd `secrets/` en `output/` buiten git (`output/` staat al in
    de `.gitignore` van kiwi-server).
