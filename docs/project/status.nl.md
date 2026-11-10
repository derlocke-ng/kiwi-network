# Repository’s en status

Op deze pagina staan alle repository’s van het project Kiwi Network: wat erin
zit, wat de nieuwste release is en welke licentie ervoor geldt. Onderaan staat
wat er voor zover bekend nog ontbreekt of niet is getest.

Alle repository’s staan op
[github.com/derlocke-ng](https://github.com/derlocke-ng). Een repository geldt
als uitgebracht zodra hij een versietag heeft, want kiwi-updater installeert
versietags. De versies zijn die van november 2026.

## Het netwerk { #the-network }

| Repository | Wat het is | Release | Catalogus | Licentie |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | bouwt en beheert het netwerk: maakt van het fleetbestand installatie-ISO’s en past via SSH op elke machine de bijbehorende rol toe | v2.42.0 | ja | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | de 20 modules en het programma dat van één machinebestand een stackbundel genereert | v0.23.0 | nee | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | het deel dat op de machine zelf draait: het zet een bundel op de machine en houdt die in de lucht | v0.5.0 | nee | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | lijsten en DNS-records van de SOCKS5-proxy’s van Mullvad, elke 6 uur opnieuw opgebouwd | de branch `list` | nee | MIT (README) |

## Mensen { #people }

| Repository | Wat het is | Release | Licentie |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | het framework waarmee gefedereerde communityhubs op nostr worden gebouwd | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | de eerste hub die met kiwi-framework is gebouwd, met tien peer-to-peer-webtools ([live](https://derlocke-ng.github.io/armory/)) | volgt `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | een catalogus van hubs en hun apps | (een lijst) | CC0 (README) |

## De desktop { #the-desktop }

| Repository | Wat het is | Release | Catalogus | Licentie |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installeert apps uit git-catalogi en werkt ze bij | v2.4.0 | ja | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | de catalogus met Kiwi-apps | (een lijst) | n.v.t. | niet vermeld |
| [ensconce](https://github.com/derlocke-ng/ensconce) | richt Bluefin-DX in nadat het is geïnstalleerd | v2.5.0 | ja | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | een VPN-killswitch voor GNOME die fail-closed werkt: valt de VPN-verbinding weg, dan wordt het verkeer geblokkeerd | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | SOCKS5- en VPN-exits in rootless Podman, elk afgesloten in een container die als enige route die verbinding heeft | v0.7.3 | ja | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | boxen (Linux-distributies in containers) waarvan het verkeer alleen via een exit van kiwi-proxy op internet kan komen | v0.2.3 | ja | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | gescheiden browseridentiteiten die via exits van kiwi-proxy verbinding maken | v0.7.1 | ja | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | provider voor kiwi-proxy: Tor | v0.3.0 | ja | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | provider voor kiwi-proxy: een VPN via gluetun | v0.2.2 | ja | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | provider voor kiwi-proxy: 9proxy | v0.2.0 | ja | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | provider voor kiwi-proxy: Mysterium | v0.5.2 | ja | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | schermindelingen voor GNOME | v0.3.2 | ja | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | synchroniseert mappen in twee richtingen, als systemd-services voor je eigen gebruiker | v0.4.1 | ja | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | ja | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | maakt offline in de browser SSH- en TLS-sleutels en certificaten aan ([live](https://derlocke-ng.github.io/kiwi-gen/)) | webpagina | nee | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | de iconen van de apps ([voorbeeld](https://derlocke-ng.github.io/kiwi-icons/)) | geen tags | nee | niet vermeld |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | deze website en documentatie | n.v.t. | n.v.t. | AGPL-3.0 |

## Bekende hiaten { #known-gaps }

Deze hiaten noemen de repository’s zelf:

- **kiwi-server**: dat het op echte hardware werkt, is in oktober en november
  2026 aangetoond. Bij die tests zijn back-ups van de ene node op een andere node
  teruggezet en is de tunnel-MTU afgesteld, ook voor mobiele verbindingen. Vier
  uitbreidingen staan op de branches `several-servers` van kiwi-server en
  kiwi-modules en zijn nog niet uitgebracht: meerdere back-upservers, het
  automatisch terugzetten van de gegevens op een machine die opnieuw is
  opgebouwd, een timer die oude snapshots opruimt, en een healthcheck die een
  vastgelopen verbinding met de commerciële VPN-provider herstart. Dat federatie
  tussen netwerken werkt, is nog niet aangetoond. Alles werkt alleen met
  IPv4, en de Debian-ISO is er alleen voor amd64. De control plane is
  ontworpen, nog niet gebouwd.
- **kiwi-modules**: de modules OpenCloud, Immich en Paperless-ngx zijn
  gemarkeerd als “om uit te proberen”. Een TURN-server voor gesprekken moet nog
  worden gemerged.
- **kiwi-stack**: er is geen rollback. Je kunt alleen gegevens terugzetten en
  een oudere bundel opnieuw toepassen.
- **kiwi-framework**: een aantal onderdelen moet nog komen, namelijk het blog,
  goedkeuringen bij de moderatie, het volgen van spaces die een hub niet
  meelevert, en signers voor NIP-07 en NIP-46.
- **kiwi-updater**: een gehost register van vertrouwde catalogi is gepland. De
  releasetags van de andere apps zijn nog niet ondertekend. Daarom vraagt het
  deel van kiwi-killswitch dat als root draait om een wachtwoord wanneer het
  wordt bijgewerkt.
- **kiwi-proxy**: de module voor kiwi-server heeft nog niet op een
  machine gedraaid. Exits verwerken alleen TCP en IPv4. De VPN-module bevat per
  machine maar één configuratie.
- **Providermodules**: de modules voor VPN en 9proxy zijn nog niet van begin
  tot eind gevalideerd met een echt account. De module voor Mysterium is dat
  wel, op 7 november 2026.
- **kiwi-custodia**: sommige onderdelen moeten nog op een echte machine worden
  gemeten, namelijk tun2socks in een rootless gateway, en andere compositors dan GNOME.
- **Licenties**: kiwi-icons, kiwi-catalog en mullvad-socks5 hebben geen
  LICENSE-bestand, en kiwi-killswitch vermeldt zijn licentie alleen in de
  README en het manifest.
