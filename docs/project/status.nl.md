# Repository's en status

Elke repository staat onder [github.com/derlocke-ng](https://github.com/derlocke-ng).
"Uitgebracht" betekent een versietag, en dat is wat kiwi-updater installeert. De
versies zijn die van november 2026.

## Het netwerk { #the-network }

| Repository | Wat het is | Release | Catalogus | Licentie |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | het netwerk bouwen en draaien: fleet-bestand → installatie-ISO's → toepassen via SSH | v2.42.0 | ja | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | de 20 modules en hun renderer: één machinebestand → een stackbundel | v0.23.0 | nee | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | de kant van de machine: zet een bundel op een machine en houdt hem draaiende | v0.5.0 | nee | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | de SOCKS5-proxy's van Mullvad als lijsten en DNS-records, elke 6 uur opnieuw opgebouwd | de branch `list` | nee | MIT (README) |

## Mensen { #people }

| Repository | Wat het is | Release | Licentie |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | de motor van gefedereerde gemeenschapshubs op nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | de eerste hub: tien peer-to-peer-webtools ([live](https://derlocke-ng.github.io/armory/)) | volgt `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | een catalogus van hubs en hun apps | (een lijst) | CC0 (README) |

## De desktop { #the-desktop }

| Repository | Wat het is | Release | Catalogus | Licentie |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installeert en werkt apps bij vanuit git-catalogi | v2.4.0 | ja | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | de Kiwi-appcatalogus | (een lijst) | n.v.t. | niet vermeld |
| [ensconce](https://github.com/derlocke-ng/ensconce) | inrichting na de installatie voor Bluefin-DX | v2.5.0 | ja | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | fail-closed VPN-killswitch voor GNOME | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | verzegelde SOCKS5/VPN-exits in rootless Podman | v0.7.3 | ja | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | distroboxen waarvan het verkeer alleen via een exit vertrekt | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | geïsoleerde browseridentiteiten op kiwi-proxy-exits | v0.7.1 | ja | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | kiwi-proxy-provider: Tor | v0.3.0 | ja | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | kiwi-proxy-provider: een VPN via gluetun | v0.2.2 | ja | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | kiwi-proxy-provider: 9proxy | v0.2.0 | ja | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | kiwi-proxy-provider: Mysterium | v0.5.2 | ja | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | schermindelingen voor GNOME | v0.3.2 | ja | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | tweerichtings-mappensynchronisatie als gebruikersservices | v0.4.1 | ja | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | ja | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | SSH- en TLS-sleutels en -certificaten, offline in de browser ([live](https://derlocke-ng.github.io/kiwi-gen/)) | webpagina | nee | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | de app-iconen ([voorbeeld](https://derlocke-ng.github.io/kiwi-icons/)) | geen tags | nee | niet vermeld |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | deze website en documentatie | n.v.t. | n.v.t. | AGPL-3.0 |

## Bekende hiaten { #known-gaps }

Uit de repository's zelf:

- **kiwi-server**: in oktober–november 2026 op hardware bewezen, met back-ups
  van nodes die over nodes heen zijn teruggezet en de MTU van de tunnel
  afgestemd, mobiele paden inbegrepen. Meerdere back-upservers, het automatisch
  terugzetten van een opnieuw opgebouwde machine, een prune-timer en een
  gezondheidscontrole voor een vastgelopen commerciële exit staan op de
  branches `several-servers` van kiwi-server en kiwi-modules, nog niet
  uitgebracht. Federatie tussen netwerken is nog niet bewezen. Alleen IPv4, en
  de Debian-ISO is alleen amd64. Het control plane is ontworpen, niet gebouwd.
- **kiwi-modules**: OpenCloud, Immich en Paperless-ngx zijn "om uit te proberen".
  Een TURN-server voor gesprekken wacht op een merge.
- **kiwi-stack**: geen rollback behalve gegevens terugzetten en een oudere
  bundel opnieuw toepassen.
- **kiwi-framework**: de blog, goedkeuringen door moderators, spaces volgen die
  een hub niet meelevert, en NIP-07/NIP-46-signers moeten nog komen.
- **kiwi-updater**: een gehost register van vertrouwde catalogi is gepland. De
  release-tags van de andere apps zijn nog niet ondertekend, dus de root-helft
  van kiwi-killswitch vraagt om een wachtwoord om bij te werken.
- **kiwi-proxy**: de kiwi-server-module ervan heeft nog niet op een machine
  gedraaid. Exits zijn alleen TCP en IPv4. De VPN-module bevat één configuratie
  per machine.
- **Providermodules**: VPN en 9proxy zijn niet end-to-end gevalideerd tegen een
  echt account; Mysterium wel (7 november 2026).
- **kiwi-custodia**: sommige onderdelen moeten nog op een echte machine gemeten
  worden (tun2socks in een rootless gateway, andere compositors dan die van GNOME).
- **Licenties**: kiwi-icons, kiwi-catalog en mullvad-socks5 hebben geen
  LICENSE-bestand, en kiwi-killswitch vermeldt zijn licentie alleen in de README
  en het manifest.
