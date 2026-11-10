# Moduły

Moduł to jedna usługa maszyny Kiwi Network. [Rola](roles.md) wybiera zestaw
modułów, a renderer zamienia je w **stack** dla jednego hosta. Rendererem jest
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), dołączony do
kiwi-server (vendored). Stack to plik compose, **quadlety podmana** (jedna
jednostka systemd na kontener), konfiguracje i jednostki hosta oraz
`stack.sh`, manifest, który je wszystkie wymienia. [kiwi-stack](single.md)
umieszcza go na maszynie. Całe szablonowanie odbywa się na maszynie, która
renderuje. Target potrzebuje tylko podmana 4.4 lub nowszego (albo dockera z
wtyczką compose, przy `runtime: docker`).

```bash
kiwi-server modules -v      # każdy moduł i każde ustawienie z wartością domyślną
```

## Sieć { #the-network }

| Moduł | Co to jest | Działa na | Wymaga | Na hoście |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: punkt wejścia dla każdego klienta i node'a; jego trasą domyślną jest klient VPN (podwójny skok) | master | nic | `51820/udp`; interfejs na `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: tunel, na którym wisi każda maszyna: do mastera na nodzie, do komercyjnego VPN-a na masterze | oba | nic | nic |
| `dns` | **Pi-hole 6**: blokuje reklamy w sieci mesh lub w LAN, serwuje nazwy floty i opcjonalnie proxy SOCKS5 Mullvad po nazwie | oba | nic | `53` na nodzie |
| `tor` | proxy **Tor SOCKS5** dla klientów sieci mesh, przypięte do krajów | oba | nic | `127.0.0.1:9050` na nodzie; adres mesh `:9050` na masterze |
| `reverse-proxy` | **nginx** z TLS: jeden blok server na usługę; strony administracyjne odpowiadają tylko sieci mesh; opcjonalne nazwy publiczne z Let's Encrypt | oba | nic | `80`, `443` na nodzie lub na publicznym masterze |
| `gateway` | routing oparty na politykach na hoście: klienci w LAN, którzy używają tej maszyny jako bramy, wychodzą przez VPN | node | vpn-client | jednostka hosta |
| `dhcp-relay` | przekazuje DHCP z LAN do Pi-hole, żeby Pi-hole mógł być serwerem DHCP w LAN | node | dns | `67/udp` |

## Usługi { #services }

| Moduł | Co to jest | Działa na | Wymaga |
|---|---|---|---|
| `cloud` | **Nextcloud** z kontenerów projektu AIO, *bez* kontenera AIO master (bez gniazda dockera, działa na podmanie). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, wyszukiwanie pełnotekstowe i Whiteboard to przełączniki | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, menedżer haseł zgodny z Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** i **JDownloader** wewnątrz przestrzeni nazw sieciowych klienta VPN: bez tunelu nie ma ruchu | node | vpn-client |
| `sftp` | serwer SFTP na własnym porcie (`2224`), do pobierania ściągniętych plików | node | nic |
| `portainer` | **Portainer CE**, interfejs WWW dla kontenerów (`127.0.0.1:9443` i `portainer.<host>`) | oba | nic |
| `opencloud` | **OpenCloud**: pliki i udostępnianie w jednym pliku binarnym Go (do wypróbowania) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**: zdjęcia i filmy (do wypróbowania) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: zeskanowane dokumenty z OCR i wyszukiwaniem pełnotekstowym (do wypróbowania) | node | vpn-client, reverse-proxy |

Ostatnich trzech nie ma w żadnym presecie; dodaj je do `modules:`.

## Ludzie { #people }

| Moduł | Co to jest | Działa na | Wymaga |
|---|---|---|---|
| `nostr-relay` | **strfry**, przekaźnik, na którym hub trzyma swoje zdarzenia (pod `relay.<host>`). Z Internetu członkowie mogą publikować po udowodnieniu swojego klucza (NIP-42): klucze `approved` z podpisanej listy administratorów albo każdy `registered` z kontem. Sieć mesh może publikować zawsze | master | reverse-proxy |
| `hub` | **hub kiwi-framework** jako kontener (domyślnie Armory, pod `hub.<host>`), prywatny, półpubliczny lub publiczny | master | reverse-proxy |

Zobacz [Własny hub](../people/hubs.md).

## Kopie zapasowe i dyski { #backups-and-disks }

| Moduł | Co to jest | Działa na | Wymaga |
|---|---|---|---|
| `backup` | dane tej maszyny przez **restic**, zaszyfrowane, na node'a z backup-server: co noc o `03:00` (w ciągu 15 minut po tej godzinie) i przez `kiwi-stack backup`. Każdy moduł określa, co z niego jest zachowywane. Następne wydanie: kilka serwerów i odbudowana maszyna, która sama się odtwarza ([szczegóły](operations.md#coming-in-the-next-release)) | oba | nic |
| `backup-server` | **serwer restic REST**; każda maszyna ma dostęp tylko do własnego repozytorium, w trybie tylko do dopisywania | node | vpn-client, reverse-proxy |
| `tang` | serwery **Tang**, żeby zaszyfrowane maszyny odblokowywały się przy starcie; jeden pierścień to jeden serwer z własnymi kluczami (domyślnie `infra` na `7500`) | node | nic |

Zobacz [Eksploatacja](operations.md).

## Ważne ustawienia { #important-settings }

| Moduł | Ustawienie | Domyślnie | Uwagi |
|---|---|---|---|
| vpn-server | `wg_host` | (wymagane) | nazwa lub IP, z którym łączą się klienci |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | zobacz [grupy klientów](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | porty Tang dla maszyn za NAT-em |
| vpn-client | `vpn_provider` | `custom` | `custom`: konfiguracja WireGuard wydana przez mastera (node); albo dostawca gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | gdzie jest komercyjne wyjście |
| | `dot_providers` | `quad9` | DNS-over-TLS gluetuna |
| | `extra_dnat_rules` | `[]` | np. SSH z sieci mesh do hosta |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | tylko gdy master jest nieosiągalny |
| | `dhcp_enabled` | `false` | z `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` na masterze | [proxy Mullvad po nazwie](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | węzły wejściowe i wyjściowe, `StrictNodes` |
| reverse-proxy | `public` | `false` | tylko master: 80/443 z Let's Encrypt dla nazw spoza domeny floty |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | wskaż duży dysk |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | włącz dla pierwszego konta, potem wyłącz |
| downloader | `download_dir` | (wymagane) | |
| nostr-relay | `members` | `approved` | albo `registered` |
| | `write_pubkeys` | `[]` | administratorzy: mogą zawsze publikować i liczą się tylko ich listy członków i banów |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | dowolny hub kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | hub półpubliczny |
| backup | `server` | (wymagane) | `https://…` node'a z backup-server, który ma tę maszynę na liście |
| tang | `rings` | `{ infra: "7500" }` | nazwa i port |

Pominięte hasła i klucze są generowane z seeda floty.

## Nazwy { #names }

Każdy moduł ogłasza swoje nazwy reverse proxy i DNS floty, pod nazwą hosta:

| Usługa | Nazwa |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (każdy host z `dns` i reverse proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| przekaźnik / hub | `relay.<host>` / `hub.<host>` |
| serwer kopii zapasowych | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Kontenery { #containers }

- Pod podmanem każda usługa to quadlet w `/etc/containers/systemd`,
  uruchamiany przez `kiwi-stack.target`, z logiem w journalu. Kontener, który
  żyje w przestrzeni nazw sieciowych innego, jest z nim związany i wraca razem
  z nim.
- Sekrety trafiają do plików `kiwi/env/<service>.env` dostępnych tylko dla
  roota, nigdy do jednostek.
- Stałe adresy są zgodne z planem v1, więc zmigrowana maszyna je zachowuje:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Pozostałe moduły liczą w górę od `.100`. Kontenery bez stałego
  adresu używają trzeciej ćwiartki sieci (`.128/26`).
- Fedora CoreOS i uCore działają z włączonym SELinuksem, więc montowania bind
  mają etykietę `:z`. Montowania gniazda kontenerów i `/lib/modules` nigdy nie
  są etykietowane.

## Pisanie modułu { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` deklaruje metadane modułu i typy node'ów, jego zależności, porty
hosta, które otwiera, jego szablony i miejsce, do którego trafia ich wynik,
przechowywanie danych, co z niego trafia do kopii zapasowej, integrację z
hostem (sysctl, moduły jądra), bloki server nginx, które ogłasza, adresy URL
wypisywane po zakończeniu roli, swoje reguły walidacji i swoje `settings`.
Schemat ustawień waliduje plik fleet i buduje formularz aplikacji. Szablony to
Jinja2 i widzą kontekst hosta: nazwę i typ hosta, adres każdego modułu, sieć
mesh, nazwy floty, każdy włączony moduł i ustawienia każdego modułu.

Pod podmanem plik compose jest tłumaczony na quadlety. Tłumaczony jest tylko
znany zestaw kluczy compose, a wszystko inne jest błędem w czasie
renderowania.

Moduły są rozwijane i wydawane w
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Pełna
dokumentacja formatu to
[docs/modules.md w kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
