# Providermodules

Een providermodule geeft [kiwi-proxy](kiwi-proxy.md) een exit die hij zelf
maakt, in plaats van een SOCKS5 die je hebt gekregen. Elke module staat in een
eigen repository, wordt via kiwi-updater geïnstalleerd in de modulemap van
kiwi-proxy, en wordt beheerd door kiwi-proxy: die bouwt de image van de module,
start haar wanneer een exit haar nodig heeft, en breekt haar af wanneer geen
gateway haar meer gebruikt.

| Module | Repository | Release | Exit | Vereist |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | het Tor-netwerk, één circuit per exit, elk exit-land | niets (gratis) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | een WireGuard- of OpenVPN-tunnel via [gluetun](https://github.com/qdm12/gluetun) | een VPN-abonnement |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | een residentiële exit van [9proxy](https://9proxy.com/) | een 9proxy-account en de propriëtaire client ervan (niet herverspreid) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | de dVPN van [Mysterium](https://mysterium.network/), met een keuzelijst van nodes op land en IP-type | een geregistreerde consumentenidentiteit met een MYST-saldo |

Alle vier zijn GPL-3.0-or-later, staan in de [Kiwi-catalogus](../desktop/catalogs.md),
en declareren `DEPENDS=kiwi-proxy`, zodat kiwi eerst kiwi-proxy installeert. Tor
en Mysterium zijn de snelle weg naar meer exit-IP's, bijvoorbeeld om te testen.

## Installeren en gebruiken { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # de image bouwen (kiwi-proxy setup doet ze allemaal)
kiwi-proxy module list
kiwi-proxy module countries tor                  # waar Tor naar buiten kan
kiwi-proxy add tor-de --module tor --country de  # een exit ervan
kiwi-custodia new test --exit tor-de             # een box erop, of:
kiwi-fox new test --exit tor-de                  # een browserprofiel erop
```

Bij Tor wordt het land vastgehouden met `StrictNodes`, zodat het circuit eerder
faalt dan elders naar buiten te gaan. Exits op de tor-module geven de
SOCKS-inloggegevens per site van Tor Browser standaard door
(`--socks-auth passthrough`).

## Hoe het is aangesloten { #how-it-is-wired }

**Elke provider biedt SOCKS5 aan en verder niets.** Een providercontainer heeft
een eigen weg naar buiten nodig, dus hij kan niet in de namespace van een gateway
leven, waar alles behalve één bestemming wordt weggegooid. De twee ontmoeten
elkaar op een rootless Podman-bridge, `kf-providers`, waar elke module een vast
adres krijgt:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** spreekt al SOCKS5. kiwi-proxy stuurt inloggegevens per exit, en
  `IsolateSOCKSAuth` van Tor geeft elke exit een eigen circuit.
- **VPN en Mysterium** lopen over een tunnel die geen SOCKS5 spreekt, dus een
  kleine microsocks-adapter sluit aan op de netwerknamespace van de tunnel en
  biedt SOCKS5 aan dat over de tunnel loopt.
- **9proxy** draait de 9proxy-client, die een SOCKS5-poort opent op een
  residentiële exit.

Eén providercontainer bedient elke exit op dezelfde module en lease. Een tunnel
die zijn sessie verliest, faalt gesloten en wordt opnieuw gestart.

## Configuratie { #configuration }

De status van elke module staat in `~/.local/share/kiwi-proxy/modules-state/<module>/`,
buiten elke repository:

- **vpn**: `vpn.json` met de instellingen van gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; elke sleutel in hoofdletters gaat
  ongewijzigd naar gluetun), een optionele lijst `leases`, en een optionele map
  `gluetun/` (bijvoorbeeld een `wireguard.conf` voor de `custom`-provider van
  gluetun). Dit is één configuratie per machine: exits erop verschillen in
  serverland.
- **9proxy**: `config/account.conf`. Zet de propriëtaire client in
  `module/containers/vendor/` van de plugin en voeg `COPY vendor/ /opt/9proxy/`
  toe aan zijn `Containerfile` vóór `kiwi-proxy module setup 9proxy`. Zonder de
  client wordt de image gebouwd, maar weigert de provider op te starten in plaats
  van een poort te openen.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, of *Configure…* in de app Kiwi Proxy. De wachtzin wordt een
  Podman-secret. Eén identiteit heeft één verbinding tegelijk.

## Status { #status }

Tor heeft geen account nodig. Mysterium is op 2026-11-07 end-to-end gecontroleerd.
De VPN- en 9proxy-modules zijn af en hebben unittests, maar zijn nog niet
end-to-end gedraaid tegen een echt abonnement of account, zoals hun README's
zeggen.
