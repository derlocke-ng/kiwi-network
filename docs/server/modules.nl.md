# Modules

Een module is een dienst die een machine in je Kiwi Network draait,
bijvoorbeeld de VPN-server, de DNS-server die reclame blokkeert, Nextcloud of
de nachtelijke back-up. Met modules bepaal je wat elke machine doet. Een
[rol](roles.md) brengt een set modules mee, en die set kun je in het
fleetbestand aanpassen.

Uit de modules van één host genereert een programma een **stack**: alles wat
de machine nodig heeft om deze diensten te draaien. Dat programma is
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), en kiwi-server
bevat er een kopie van. Een stack bestaat uit een compose-bestand,
**podman-quadlets** (een systemd-unit per container), de configuratiebestanden,
de systemd-units voor de host en `stack.sh`, een manifest waarin dat allemaal
staat opgesomd. [kiwi-stack](single.md) installeert de stack op de machine.
Alle templates worden ingevuld op de computer die de stack genereert. De
machine die de stack draait, heeft alleen podman 4.4 of nieuwer nodig, of
docker met de compose-plug-in als je `runtime: docker` instelt.

Dit commando toont elke module met haar instellingen.

```bash
kiwi-server modules -v      # elke module en elke instelling met de standaardwaarde
```

## Het netwerk { #the-network }

Deze modules bouwen de mesh op, het besloten WireGuard-netwerk waarin al je
machines zitten, en bepalen hoe het verkeer uit de mesh op internet komt.

| Module | Wat het is | Draait op | Vereist | Op de host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, de WireGuard-server waarmee elke client en elke node verbinding maakt. De standaardroute is de VPN-client, dus verkeer naar internet gaat verder via de commerciële VPN van de master (de double hop) | master | niets | `51820/udp`, en de webinterface op `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, de VPN-tunnel waar het verkeer van een machine doorheen gaat. Op een node leidt de tunnel naar de master, op de master naar een commerciële VPN | beide | niets | niets |
| `dns` | **Pi-hole 6**, een DNS-server die reclame blokkeert, voor de mesh of het LAN. Hij beantwoordt de namen van de fleet en kan ook namen leveren voor de SOCKS5-proxy’s van Mullvad | beide | niets | `53` op een node |
| `tor` | Een **Tor-SOCKS5**-proxy voor clients in de mesh. Hij gebruikt alleen Tor-nodes in de landen die je instelt | beide | niets | `127.0.0.1:9050` op een node, en het mesh-adres `:9050` op een master |
| `reverse-proxy` | **nginx** met TLS. Er is een serverblok per dienst, zodat elke dienst onder een eigen naam bereikbaar is. Beheerpagina’s zijn alleen vanuit de mesh bereikbaar. Openbare namen met Let’s Encrypt-certificaten zijn optioneel | beide | niets | `80`, `443` op een node, of op een master met `public` ingeschakeld |
| `gateway` | Policy routing op de host. Apparaten in het LAN die deze machine als gateway gebruiken, krijgen hun internetverkeer door de VPN gestuurd | node | vpn-client | een systemd-unit op de host |
| `dhcp-relay` | Geeft de DHCP-verzoeken uit het LAN door aan Pi-hole, zodat Pi-hole de DHCP-server van het LAN kan zijn | node | dns | `67/udp` |

## Diensten { #services }

| Module | Wat het is | Draait op | Vereist |
|---|---|---|---|
| `cloud` | **Nextcloud**, opgebouwd uit de containers van het AIO-project, maar *zonder* de AIO-mastercontainer. Daardoor is er geen docker-socket nodig en draait het op podman. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, zoeken in volledige tekst en Whiteboard kun je elk afzonderlijk aan- of uitzetten | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, een wachtwoordbeheerder die compatibel is met Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** en **JDownloader**. Beide draaien in de netwerk-namespace van de VPN-client: ze gebruiken diens netwerkverbinding en hebben er zelf geen. Ligt de tunnel plat, dan wordt er niets overgedragen | node | vpn-client |
| `sftp` | Een SFTP-server op een eigen poort (`2224`), waar je de downloads kunt ophalen | node | niets |
| `portainer` | **Portainer CE**, een webinterface voor de containers. Bereikbaar op `127.0.0.1:9443` en op `portainer.<host>` | beide | niets |
| `opencloud` | **OpenCloud**, voor bestanden en bestanden delen, in één Go-binary (om uit te proberen) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, voor foto’s en video’s (om uit te proberen) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, voor gescande documenten, met OCR en zoeken in volledige tekst (om uit te proberen) | node | vpn-client, reverse-proxy |

De laatste drie modules zitten in geen enkele preset. Wil je er een gebruiken,
zet hem dan in `modules:`.

## Mensen { #people }

Een hub is de eigen site van een community, in de browser. Deze twee modules
draaien een hub en de relay waarop de hub zijn events opslaat.

| Module | Wat het is | Draait op | Vereist |
|---|---|---|---|
| `nostr-relay` | **strfry**, de relay waarop een hub zijn events bewaart. Bereikbaar op `relay.<host>`. Wie vanaf internet verbinding maakt, mag alleen berichten plaatsen als hij lid is en heeft bewezen dat de sleutel van hem is (NIP-42). Met `approved` zijn de leden de sleutels op een lijst die de beheerders ondertekenen. Met `registered` is iedereen met een account lid. Verbindingen vanuit de mesh mogen altijd berichten plaatsen | master | reverse-proxy |
| `hub` | Een **hub van kiwi-framework** die als container draait. Standaard is dat Armory, bereikbaar op `hub.<host>`. Een hub kan privé, half openbaar of openbaar zijn | master | reverse-proxy |

Zie [Je eigen hub draaien](../people/hubs.md).

## Back-ups en schijven { #backups-and-disks }

| Module | Wat het is | Draait op | Vereist |
|---|---|---|---|
| `backup` | Maakt met **restic** een versleutelde back-up van de gegevens van deze machine, op een node waarop de module backup-server draait. De back-up start elke nacht om `03:00`, of tot 15 minuten later, en telkens als je `kiwi-stack backup` uitvoert. Elke module bepaalt van welke van haar gegevens een back-up wordt gemaakt. Gepland voor de volgende release: back-ups naar meerdere servers, en een opnieuw opgebouwde machine die haar eigen gegevens terugzet ([details](operations.md#coming-in-the-next-release)) | beide | niets |
| `backup-server` | Een **restic REST-server** die de back-ups opslaat. Elke machine kan alleen bij haar eigen repository, en kan daar alleen back-ups aan toevoegen, niet verwijderen (append-only) | node | vpn-client, reverse-proxy |
| `tang` | **Tang**-servers, waarmee machines met een versleutelde schijf die bij het opstarten kunnen ontgrendelen zonder dat er iemand bij is. Een ring is één Tang-server met eigen sleutels. Standaard is er een ring met de naam `infra` op poort `7500` | node | niets |

Zie [Beheer](operations.md).

## Belangrijke instellingen { #important-settings }

| Module | Instelling | Standaard | Opmerkingen |
|---|---|---|---|
| vpn-server | `wg_host` | (verplicht) | de naam of het IP-adres waarmee clients verbinding maken |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | zie [clientgroepen](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | doorgestuurde poorten op de master waarlangs machines achter NAT hun Tang-ring bereiken |
| vpn-client | `vpn_provider` | `custom` | `custom` gebruikt de WireGuard-configuratie die de master heeft uitgegeven; dat is wat een node nodig heeft. Noem anders een provider van gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | de landen en steden van de commerciële VPN-servers die worden gebruikt |
| | `dot_providers` | `quad9` | de DNS-over-TLS-provider die gluetun gebruikt |
| | `extra_dnat_rules` | `[]` | extra doorstuurregels, bijvoorbeeld voor SSH vanuit de mesh naar de host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | alleen gebruikt zolang de master onbereikbaar is |
| | `dhcp_enabled` | `false` | samen met `dhcp_start`, `dhcp_end` en `dhcp_router` |
| | `mullvad_socks` | `true` op een master | [de proxy’s van Mullvad op naam](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | de landen van de entrynodes en Tor-exitnodes, afgedwongen met `StrictNodes` |
| reverse-proxy | `public` | `false` | alleen op de master. Zet 80/443 open en gebruikt Let’s Encrypt voor namen buiten het domein van de fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | kies een map op een grote schijf |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | zet dit aan om het eerste account aan te maken en daarna weer uit |
| downloader | `download_dir` | (verplicht) | |
| nostr-relay | `members` | `approved` | of `registered` |
| | `write_pubkeys` | `[]` | de sleutels van de beheerders. Beheerders mogen altijd berichten plaatsen, en alleen hun ledenlijsten en banlijsten gelden |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | het image van elke hub die met kiwi-framework is gebouwd |
| | `public_relays`, `public_mounts` | `[]` | stel deze in voor een half openbare hub |
| backup | `server` | (verplicht) | het `https://…`-adres van een node met backup-server waarop deze machine vermeld staat |
| tang | `rings` | `{ infra: "7500" }` | naam en poort van elke ring |

Laat je een wachtwoord of sleutel weg, dan wordt die gegenereerd uit de seed
van de fleet.

## Namen { #names }

Elke module meldt de namen van haar diensten aan bij de reverse proxy en bij de
DNS van de fleet. Elke naam bestaat uit de naam van de dienst en de naam van de
host.

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

- Onder podman is elke dienst een quadlet in `/etc/containers/systemd`. De
  quadlets worden gestart via `kiwi-stack.target`, en hun logs gaan naar het
  systemd-journal. Een container die de netwerk-namespace van een andere
  container deelt, is aan die container gekoppeld en wordt dus samen met haar
  herstart.
- Secrets worden geschreven naar bestanden `kiwi/env/<service>.env` die alleen
  root kan lezen. Ze komen nooit in de units te staan.
- De containers hebben vaste adressen volgens het adresplan van v1, zodat een
  machine die van v1 is overgezet haar adressen houdt. Het gaat om vpn-client
  `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`, vault `.7`,
  tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` en sftp `.251`.
  Andere modules krijgen adressen die vanaf `.100` oplopen. Containers zonder
  vast adres krijgen er een uit het derde kwart van het netwerk (`.128/26`).
- Fedora CoreOS en uCore draaien met SELinux ingeschakeld, dus bind mounts
  krijgen het label `:z`. De mounts van de containersocket en van
  `/lib/modules` krijgen nooit een label.

## Een module schrijven { #writing-a-module }

Een module is een map met de volgende bestanden.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` beschrijft de module. Het legt de metadata vast, de typen nodes
waarop de module draait, haar afhankelijkheden en de poorten die ze op de host
openzet. Het noemt de templates van de module en waar hun uitvoer terechtkomt,
de opslag, en van welke gegevens een back-up wordt gemaakt. Verder staan erin:
de integratie met de host (sysctls en kernelmodules), de nginx-serverblokken
die de module aanmeldt, de URL’s die worden getoond als de rol klaar is, de
validatieregels en de `settings` van de module.

Het schema van de instellingen wordt voor twee dingen gebruikt. Het valideert
het fleetbestand, en de app van kiwi-server bouwt er het formulier voor de
instellingen mee op. De templates zijn geschreven in Jinja2 en kunnen de
context van de host gebruiken. Daarin staan de naam en het type van de host,
het adres van elke module, de mesh, de namen van de fleet, de ingeschakelde
modules en de instellingen van elke module.

Onder podman wordt het compose-bestand vertaald naar quadlets. Die vertaling
ondersteunt een vaste set compose-sleutels. Elke andere sleutel geeft een fout
bij het genereren van de stack.

Modules worden ontwikkeld en uitgebracht in
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). De volledige
beschrijving van het formaat staat in
[docs/modules.md van kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
