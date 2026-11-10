# Modules

Een module is één dienst van een machine in een Kiwi Network. Een [rol](roles.md)
kiest een set modules, en de renderer maakt daar een **stack** voor één host van.
De renderer is [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), dat
kiwi-server in zich opneemt. De stack is een compose-bestand, **podman-quadlets**
(één systemd-unit per container), de configuraties en host-units, en `stack.sh`,
het manifest dat ze allemaal noemt. [kiwi-stack](single.md) zet hem op de
machine. Alle templating gebeurt op de machine die rendert. Het target heeft
alleen podman 4.4 of later nodig (of docker met de compose-plugin, met
`runtime: docker`).

```bash
kiwi-server modules -v      # elke module en elke instelling met haar standaardwaarde
```

## Het netwerk { #the-network }

| Module | Wat het is | Draait op | Vereist | Op de host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: het toegangspunt voor elke client en node; de standaardroute is de VPN-client (de double hop) | master | geen | `51820/udp`; de interface op `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: de tunnel waar elke machine aan hangt: naar de master op een node, naar een commerciële VPN op de master | beide | geen | geen |
| `dns` | **Pi-hole 6**: blokkeert advertenties voor de mesh of het LAN, serveert de namen van de fleet en, optioneel, de SOCKS5-proxy's van Mullvad op naam | beide | geen | `53` op een node |
| `tor` | een **Tor-SOCKS5**-proxy voor mesh-clients, vastgezet op landen | beide | geen | `127.0.0.1:9050` op een node; het mesh-adres `:9050` op een master |
| `reverse-proxy` | **nginx** met TLS: één serverblok per dienst; beheerpagina's antwoorden alleen de mesh; optioneel publieke namen met Let's Encrypt | beide | geen | `80`, `443` op een node, of op een publieke master |
| `gateway` | policy routing op de host: LAN-clients die deze machine als gateway gebruiken, vertrekken via de VPN | node | vpn-client | een host-unit |
| `dhcp-relay` | stuurt de DHCP van het LAN door naar Pi-hole, zodat Pi-hole de DHCP-server van het LAN kan zijn | node | dns | `67/udp` |

## Diensten { #services }

| Module | Wat het is | Draait op | Vereist |
|---|---|---|---|
| `cloud` | **Nextcloud** uit de containers van het AIO-project, *zonder* de AIO-mastercontainer (geen docker-socket, draait op podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, volledige-tekstzoeken en Whiteboard zijn schakelaars | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, de met Bitwarden compatibele wachtwoordbeheerder | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** en **JDownloader** binnen de netwerknamespace van de VPN-client: geen tunnel, geen verkeer | node | vpn-client |
| `sftp` | een SFTP-server op een eigen poort (`2224`), om downloads op te halen | node | geen |
| `portainer` | **Portainer CE**, een webinterface voor de containers (`127.0.0.1:9443`, en `portainer.<host>`) | beide | geen |
| `opencloud` | **OpenCloud**: bestanden en delen in één Go-binary (om uit te proberen) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**: foto's en video's (om uit te proberen) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: gescande documenten met OCR en volledige-tekstzoeken (om uit te proberen) | node | vpn-client, reverse-proxy |

De laatste drie zitten in geen enkele preset; voeg ze toe aan `modules:`.

## Mensen { #people }

| Module | Wat het is | Draait op | Vereist |
|---|---|---|---|
| `nostr-relay` | **strfry**, de relay waarop een hub zijn events bewaart (op `relay.<host>`). Vanaf het internet mogen leden posten nadat ze hun sleutel hebben bewezen (NIP-42): `approved`-sleutels op de ondertekende lijst van de beheerders, of iedereen die `registered` is met een account. De mesh mag altijd posten | master | reverse-proxy |
| `hub` | een **kiwi-framework-hub** als container (standaard Armory, op `hub.<host>`), privé, semipubliek of publiek | master | reverse-proxy |

Zie [Je eigen hub draaien](../people/hubs.md).

## Back-ups en schijven { #backups-and-disks }

| Module | Wat het is | Draait op | Vereist |
|---|---|---|---|
| `backup` | de gegevens van deze machine met **restic**, versleuteld, naar een backup-server-node: elke nacht om `03:00` (binnen 15 minuten daarna) en met `kiwi-stack backup`. Elke module zegt wat ervan bewaard wordt. Volgende release: meerdere servers en een opnieuw opgebouwde machine die zichzelf terugzet ([details](operations.md#coming-in-the-next-release)) | beide | geen |
| `backup-server` | een **restic-REST-server**; elke machine bereikt alleen haar eigen repository, alleen toevoegen | node | vpn-client, reverse-proxy |
| `tang` | **Tang**-servers zodat versleutelde machines bij het opstarten ontgrendelen; één ring is één server met eigen sleutels (standaard `infra` op `7500`) | node | geen |

Zie [Beheer](operations.md).

## Belangrijke instellingen { #important-settings }

| Module | Instelling | Standaard | Opmerkingen |
|---|---|---|---|
| vpn-server | `wg_host` | (verplicht) | de naam of het IP waarmee clients verbinden |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | zie [clientgroepen](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | Tang-poorten voor machines achter NAT |
| vpn-client | `vpn_provider` | `custom` | `custom`: de WireGuard-configuratie die de master heeft uitgegeven (een node); of een gluetun-provider (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | waar een commerciële exit is |
| | `dot_providers` | `quad9` | DNS-over-TLS van gluetun |
| | `extra_dnat_rules` | `[]` | bijv. SSH vanuit de mesh naar de host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | alleen zolang de master onbereikbaar is |
| | `dhcp_enabled` | `false` | met `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` op een master | [de proxy's van Mullvad op naam](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | ingangs- en exit-nodes, `StrictNodes` |
| reverse-proxy | `public` | `false` | alleen master: 80/443 met Let's Encrypt voor namen buiten het domein van de fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | laat het naar een grote schijf wijzen |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | aanzetten voor het eerste account, daarna uit |
| downloader | `download_dir` | (verplicht) | |
| nostr-relay | `members` | `approved` | of `registered` |
| | `write_pubkeys` | `[]` | de beheerders: zij mogen altijd posten, en alleen hun leden- en banlijsten tellen |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | elke kiwi-framework-hub |
| | `public_relays`, `public_mounts` | `[]` | een semipublieke hub |
| backup | `server` | (verplicht) | `https://…` van een backup-server-node die deze machine vermeldt |
| tang | `rings` | `{ infra: "7500" }` | naam en poort |

Wachtwoorden en sleutels die je weglaat, worden gegenereerd uit de seed van de
fleet.

## Namen { #names }

Elke module kondigt haar namen aan bij de reverse proxy en bij de DNS van de
fleet, onder de naam van de host:

| Dienst | Naam |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (elke host met `dns` en de reverse proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relay / hub | `relay.<host>` / `hub.<host>` |
| back-upserver | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Containers { #containers }

- Onder podman is elke dienst een quadlet in `/etc/containers/systemd`, gestart
  via `kiwi-stack.target`, met zijn log in de journal. Een container die in de
  netwerknamespace van een andere leeft, is daaraan gebonden en komt samen met
  hem terug.
- Geheimen gaan naar `kiwi/env/<service>.env`-bestanden die alleen root kan
  lezen, nooit naar de units.
- Vaste adressen volgen het v1-plan, zodat een gemigreerde machine ze houdt:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Andere modules tellen op vanaf `.100`. Containers zonder vast adres
  gebruiken het derde kwart van het netwerk (`.128/26`).
- Fedora CoreOS en uCore draaien met SELinux ingeschakeld, dus bind mounts
  krijgen het label `:z`. Mounts van de containersocket en `/lib/modules` krijgen
  nooit een label.

## Een module schrijven { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` declareert de metadata en node-types van de module, haar
afhankelijkheden, de hostpoorten die ze opent, haar sjablonen en waar hun
uitvoer heen gaat, opslag, wat ervan geback-upt wordt, integratie met de host
(sysctls, kernelmodules), de nginx-serverblokken die ze aankondigt, de URL's die
worden getoond als de rol klaar is, haar validatieregels, en haar `settings`. Het
settings-schema valideert het fleet-bestand en bouwt het formulier van de app.
Sjablonen zijn Jinja2 en zien de hostcontext: de naam en het type van de host,
het adres van elke module, de mesh, de namen van de fleet, elke ingeschakelde
module, en de instellingen van elke module.

Onder podman wordt het compose-bestand vertaald naar quadlets. Alleen een bekende
set compose-sleutels wordt vertaald, en al het andere is een fout tijdens het
renderen.

Modules worden ontwikkeld en uitgebracht in
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). De volledige
referentie van het formaat is
[docs/modules.md van kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
