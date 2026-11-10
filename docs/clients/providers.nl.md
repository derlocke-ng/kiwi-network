# Providermodules

In [kiwi-proxy](kiwi-proxy.md) is een exit een opgeslagen verbinding naar een
upstream, met een eigen naam, waarlangs je boxen en browsers hun verkeer sturen.
Meestal is dat een verbinding die je hebt gekregen, zoals de SOCKS5-proxy die
naar het netwerk van een klant leidt. Een providermodule is voor het andere
geval: die maakt de exit zelf aan, via Tor, een VPN-abonnement, 9proxy of
Mysterium. Vooral Tor en Mysterium zijn er om je extra IP-adressen te geven om
mee te testen.

Elke module staat in een eigen repository. kiwi-updater installeert haar in de
map met modules van kiwi-proxy, en vanaf dan beheert kiwi-proxy haar. kiwi-proxy
bouwt het container-image van de module, start de module als een exit haar nodig
heeft, en stopt haar als geen enkele gateway haar nog gebruikt. Een gateway is
de container die kiwi-proxy voor een exit laat draaien zolang de exit actief is.

| Module | Repository | Release | Exit | Nodig |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | het Tor-netwerk, met één circuit per exit en elk land voor de Tor-exitnode | niets (het is gratis) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | een WireGuard- of OpenVPN-tunnel via [gluetun](https://github.com/qdm12/gluetun) | een VPN-abonnement |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | een residential exit van [9proxy](https://9proxy.com/), dus via een gewone thuisaansluiting | een account bij 9proxy en de propriëtaire client van 9proxy, die niet wordt meegeleverd |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | de dVPN van [Mysterium](https://mysterium.network/) (een gedecentraliseerde VPN), met een lijst nodes waaruit je kiest op land en type IP-adres | een geregistreerde consumer-identiteit met een tegoed in MYST |

Alle vier de modules vallen onder GPL-3.0-or-later en staan in de
[Kiwi-catalogus](../desktop/catalogs.md). Elke module geeft `DEPENDS=kiwi-proxy`
op, dus kiwi-updater installeert eerst kiwi-proxy. Met Tor en Mysterium kom je
het snelst aan extra IP-adressen voor een exit, bijvoorbeeld om te testen.

## Installeren en gebruiken { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # het image bouwen (kiwi-proxy setup doet ze allemaal)
kiwi-proxy module list
kiwi-proxy module countries tor                  # in welke landen Tor naar buiten kan
kiwi-proxy add tor-de --module tor --country de  # een exit eruit
kiwi-custodia new test --exit tor-de             # een box erop, of:
kiwi-fox new test --exit tor-de                  # een browserprofiel erop
```

Bij een Tor-exit wordt het land afgedwongen met de Tor-optie `StrictNodes`. Een
circuit dat niet via dit land naar buiten kan, mislukt, en gaat nooit via een
ander land naar buiten. Exits op de module tor geven de SOCKS-inloggegevens door
die Tor Browser voor elke site meestuurt. Dat is hun standaardinstelling
(`--socks-auth passthrough`).

## Hoe een provider op een gateway aansluit { #how-it-is-wired }

**Elke provider biedt SOCKS5 aan, en verder niets.** Een providercontainer
heeft een eigen verbinding met internet nodig. Hij kan dus niet in de
netwerk-namespace van een gateway draaien, want daar wordt alles weggegooid
behalve verkeer naar één bestemming. In plaats daarvan zijn provider en gateway
verbonden via een bridge-netwerk in rootless Podman, `kf-providers`, waarop elke
module een vast adres heeft:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** biedt zelf SOCKS5 aan. kiwi-proxy stuurt voor elke exit andere
  inloggegevens mee, en de Tor-optie `IsolateSOCKSAuth` geeft elke exit dan een
  eigen circuit, een eigen pad door het Tor-netwerk.
- **VPN en Mysterium** gebruiken een tunnel, en een tunnel biedt geen SOCKS5
  aan. Daarom sluit een kleine adapter, microsocks, zich aan bij de
  netwerk-namespace van de tunnel. Die biedt SOCKS5 aan en stuurt het verkeer
  door de tunnel.
- **9proxy** draait de client van 9proxy, die een SOCKS5-poort opent die naar
  een residential exit leidt.

Eén providercontainer bedient elke exit die dezelfde module en dezelfde lease
gebruikt. Een lease is een van de exits die een module aanbiedt en waaruit je
kunt kiezen, bijvoorbeeld een land van een VPN-server of een node van
Mysterium. Verliest een tunnel zijn sessie, dan is hij fail-closed: er gaat
geen verkeer meer naar buiten, en de tunnel wordt herstart.

## Configuratie { #configuration }

De toestand van elke module staat in
`~/.local/share/kiwi-proxy/modules-state/<module>/`, buiten elke repository:

- **vpn**: Het bestand `vpn.json` bevat de instellingen van gluetun, zoals
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` en `WIREGUARD_ADDRESSES`. Elke sleutel in
  hoofdletters wordt ongewijzigd aan gluetun doorgegeven. Het bestand kan ook
  een lijst `leases` bevatten. In een optionele map `gluetun/` staan nog andere
  bestanden, bijvoorbeeld een `wireguard.conf` voor de provider `custom` van
  gluetun. Er is één zo’n configuratie per machine, en de exits erop verschillen
  alleen in het land van de server.
- **9proxy**: Het configuratiebestand is `config/account.conf`. De
  propriëtaire client wordt niet meegeleverd. Zet de client, voordat je
  `kiwi-proxy module setup 9proxy` uitvoert, in de map
  `module/containers/vendor/` van de plugin, en voeg `COPY vendor/ /opt/9proxy/`
  toe aan de `Containerfile` van de plugin. Zonder de client wordt het image
  wel gebouwd, maar weigert de provider te starten en opent hij geen poort.
- **mysterium**: Voer `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase` uit, of gebruik *Configure…* in de app Kiwi Proxy. De
  wachtzin wordt als Podman-secret opgeslagen. Eén identiteit kan maar één
  verbinding tegelijk hebben.

## Status { #status }

Voor Tor heb je geen account nodig. De module voor Mysterium is op 2026-11-07
van begin tot eind getest. Volgens hun README’s zijn de modules voor VPN en
9proxy af en hebben ze unittests, maar ze zijn nog niet van begin tot eind
gedraaid met een echt abonnement of account.
