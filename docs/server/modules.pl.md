# Moduły

Moduł to jedna usługa, którą może uruchamiać maszyna w twojej Kiwi Network,
na przykład serwer VPN, serwer DNS blokujący reklamy, Nextcloud albo kopia
zapasowa co noc. Za pomocą modułów decydujesz, co robi każda maszyna.
[Rola](roles.md) przynosi ze sobą zestaw modułów, a ten zestaw możesz zmienić
w pliku fleet.

Program generujący konfigurację zamienia moduły jednego hosta w **stack**,
czyli wszystko, czego maszyna potrzebuje do uruchomienia tych usług. Tym
programem jest [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules),
a jego kopia jest dołączona do kiwi-server. Stack składa się z pliku compose,
**podman quadlets** (po jednej jednostce systemd na kontener), plików
konfiguracyjnych, jednostek systemd dla hosta i pliku `stack.sh`, który je
wszystkie wymienia. Na maszynie stack instaluje [kiwi-stack](single.md).
Wszystkie szablony są wypełniane na komputerze, który generuje stack. Maszyna,
na której stack działa, potrzebuje tylko podmana 4.4 lub nowszego albo, jeśli
ustawisz `runtime: docker`, dockera z wtyczką compose.

To polecenie wypisuje wszystkie moduły z ich ustawieniami.

```bash
kiwi-server modules -v      # każdy moduł i każde ustawienie z wartością domyślną
```

## Sieć { #the-network }

Te moduły budują sieć mesh, czyli prywatną sieć WireGuard, która łączy
wszystkie twoje maszyny, i decydują o tym, którędy jej ruch trafia do
internetu.

| Moduł | Co to jest | Działa na | Wymaga | Na hoście |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, serwer WireGuard, z którym łączy się każdy klient i każdy node. Jego trasa domyślna prowadzi do klienta VPN, więc ruch do internetu idzie dalej przez komercyjny VPN mastera (podwójny przeskok, double hop) | master | nic | `51820/udp` oraz interfejs WWW na `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, tunel VPN, przez który idzie ruch maszyny. Na nodzie tunel prowadzi do mastera, a na masterze do komercyjnego VPN | obu | nic | nic |
| `dns` | **Pi-hole 6**, serwer DNS blokujący reklamy w sieci mesh albo w sieci lokalnej. Odpowiada na nazwy z twojej sieci i może też podawać nazwy proxy SOCKS5 Mullvada | obu | nic | `53` na nodzie |
| `tor` | Proxy **Tor SOCKS5** dla klientów w sieci mesh. Korzysta tylko z węzłów Tora w wybranych przez ciebie krajach | obu | nic | `127.0.0.1:9050` na nodzie, a na masterze adres w sieci mesh `:9050` |
| `reverse-proxy` | **nginx** z TLS. Ma po jednym bloku server na usługę, więc każda usługa jest dostępna pod własną nazwą. Strony administracyjne są dostępne tylko z sieci mesh. Opcjonalnie dochodzą publiczne nazwy z certyfikatami Let’s Encrypt | obu | nic | `80`, `443` na nodzie albo na masterze z włączonym `public` |
| `gateway` | Routing według reguł (policy routing) na hoście. Urządzenia w sieci lokalnej, które mają tę maszynę ustawioną jako bramę, wysyłają ruch do internetu przez VPN | node | vpn-client | jednostka systemd na hoście |
| `dhcp-relay` | Przekazuje zapytania DHCP z sieci lokalnej do Pi-hole’a, dzięki czemu Pi-hole może być serwerem DHCP tej sieci | node | dns | `67/udp` |

## Usługi { #services }

| Moduł | Co to jest | Działa na | Wymaga |
|---|---|---|---|
| `cloud` | **Nextcloud** zbudowany z kontenerów projektu AIO, ale *bez* jego kontenera głównego (master container). Dzięki temu nie potrzebuje gniazda dockera i działa na podmanie. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, wyszukiwanie pełnotekstowe i Whiteboard można włączać i wyłączać osobno | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, menedżer haseł zgodny z Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** i **JDownloader**. Oba działają w sieciowej przestrzeni nazw klienta VPN, czyli korzystają z jego połączenia sieciowego i nie mają własnego. Gdy tunel nie działa, niczego nie przesyłają | node | vpn-client |
| `sftp` | Serwer SFTP na osobnym porcie (`2224`), z którego pobierzesz ściągnięte pliki | node | nic |
| `portainer` | **Portainer CE**, interfejs WWW do zarządzania kontenerami. Jest dostępny pod `127.0.0.1:9443` i pod `portainer.<host>` | obu | nic |
| `opencloud` | **OpenCloud**, do plików i ich udostępniania, w postaci jednego pliku binarnego Go (do wypróbowania) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, do zdjęć i filmów (do wypróbowania) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, do zeskanowanych dokumentów, z OCR i wyszukiwaniem pełnotekstowym (do wypróbowania) | node | vpn-client, reverse-proxy |

Trzech ostatnich modułów nie ma w żadnym presecie. Żeby użyć któregoś z nich,
dodaj go do `modules:`.

## Ludzie { #people }

Hub to własna strona społeczności, działająca w przeglądarce. Te dwa moduły
uruchamiają hub i przekaźnik, na którym hub przechowuje swoje zdarzenia.

| Moduł | Co to jest | Działa na | Wymaga |
|---|---|---|---|
| `nostr-relay` | **strfry**, przekaźnik, na którym hub przechowuje swoje zdarzenia. Jest dostępny pod `relay.<host>`. Osoby łączące się z internetu mogą publikować tylko wtedy, gdy są członkami i udowodnią, że są właścicielami swojego klucza (NIP-42). Przy `approved` członkami są klucze z listy podpisanej przez administratorów. Przy `registered` członkiem jest każdy, kto ma konto. Połączenia z sieci mesh mogą publikować zawsze | master | reverse-proxy |
| `hub` | **Hub zbudowany na kiwi-framework**, działający jako kontener. Domyślnie jest to Armory, dostępne pod `hub.<host>`. Hub może być prywatny, półpubliczny albo publiczny | master | reverse-proxy |

Zobacz [Własny hub](../people/hubs.md).

## Kopie zapasowe i dyski { #backups-and-disks }

| Moduł | Co to jest | Działa na | Wymaga |
|---|---|---|---|
| `backup` | Robi kopię zapasową danych tej maszyny programem **restic**, w postaci zaszyfrowanej, na node’a z modułem backup-server. Kopia powstaje co noc o `03:00` lub do 15 minut później oraz za każdym razem, gdy uruchomisz `kiwi-stack backup`. Każdy moduł sam określa, które jego dane trafiają do kopii. Na następne wydanie zaplanowano kopie zapasowe na kilku serwerach i odbudowaną maszynę, która sama przywraca swoje dane ([szczegóły](operations.md#coming-in-the-next-release)) | obu | nic |
| `backup-server` | **Serwer REST restic**, który przechowuje kopie zapasowe. Każda maszyna ma dostęp tylko do własnego repozytorium i może tylko do niego dopisywać (append-only) | node | vpn-client, reverse-proxy |
| `tang` | Serwery **Tang**, dzięki którym maszyny z zaszyfrowanymi dyskami mogą je odblokować przy starcie bez udziału człowieka. Jeden pierścień to jeden serwer Tang z własnymi kluczami. Domyślnie jest jeden pierścień o nazwie `infra` na porcie `7500` | node | nic |

Więcej na stronie [Eksploatacja](operations.md).

## Najważniejsze ustawienia { #important-settings }

| Moduł | Ustawienie | Wartość domyślna | Uwagi |
|---|---|---|---|
| vpn-server | `wg_host` | (wymagane) | nazwa albo adres IP, z którym łączą się klienci |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | zobacz [grupy klientów](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | porty na masterze, przez które maszyny za NAT-em łączą się ze swoim pierścieniem Tang |
| vpn-client | `vpn_provider` | `custom` | `custom` używa konfiguracji WireGuard wystawionej przez mastera i tego właśnie potrzebuje node. W innym przypadku podaj dostawcę obsługiwanego przez gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | kraje i miasta serwerów komercyjnego VPN, z których ma korzystać |
| | `dot_providers` | `quad9` | dostawca DNS-over-TLS, z którego korzysta gluetun |
| | `extra_dnat_rules` | `[]` | dodatkowe reguły przekierowania, na przykład dla SSH z sieci mesh do hosta |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | używane tylko wtedy, gdy master jest niedostępny |
| | `dhcp_enabled` | `false` | razem z `dhcp_start`, `dhcp_end` i `dhcp_router` |
| | `mullvad_socks` | `true` na masterze | [proxy Mullvada po nazwie](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | kraje węzłów wejściowych i wyjściowych Tora, wymuszane opcją `StrictNodes` |
| reverse-proxy | `public` | `false` | tylko na masterze. Otwiera porty 80/443 i używa Let’s Encrypt dla nazw spoza domeny twojej sieci |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | ustaw katalog na dużym dysku |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | włącz, żeby założyć pierwsze konto, a potem znowu wyłącz |
| downloader | `download_dir` | (wymagane) | |
| nostr-relay | `members` | `approved` | albo `registered` |
| | `write_pubkeys` | `[]` | klucze administratorów. Administratorzy mogą zawsze publikować i tylko ich listy członków i listy zablokowanych są ważne |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | obraz dowolnego huba zbudowanego na kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | ustaw je dla huba półpublicznego |
| backup | `server` | (wymagane) | adres `https://…` node’a z modułem backup-server, na którego liście jest ta maszyna |
| tang | `rings` | `{ infra: "7500" }` | nazwa i port każdego pierścienia |

Jeśli pominiesz hasło albo klucz, zostanie wygenerowane z seeda twojej sieci.

## Nazwy { #names }

Każdy moduł rejestruje nazwy swoich usług w reverse proxy i w DNS twojej
sieci. Każda nazwa składa się z nazwy usługi i nazwy hosta.

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

- W podmanie każda usługa to quadlet w `/etc/containers/systemd`. Quadlets są
  uruchamiane przez `kiwi-stack.target`, a ich logi trafiają do dziennika
  systemd. Kontener, który współdzieli sieciową przestrzeń nazw innego
  kontenera, jest z nim powiązany, więc jest restartowany razem z nim.
- Sekrety są zapisywane w plikach `kiwi/env/<service>.env`, które może czytać
  tylko root. Nigdy nie trafiają do samych jednostek.
- Kontenery mają stałe adresy zgodne z planem adresacji z v1, dzięki czemu
  maszyna przeniesiona z v1 zachowuje swoje adresy. Są to: vpn-client `.2`,
  vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`, vault `.7`,
  tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` i sftp `.251`.
  Pozostałe moduły dostają kolejne adresy od `.100` w górę. Kontenery bez
  stałego adresu dostają adres z trzeciej ćwiartki sieci (`.128/26`).
- Fedora CoreOS i uCore działają z włączonym SELinuxem, więc montowania typu
  bind dostają etykietę `:z`. Gniazdo kontenerów i `/lib/modules` są montowane
  zawsze bez etykiety.

## Własny moduł { #writing-a-module }

Moduł to katalog z następującymi plikami.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` opisuje moduł. Deklaruje jego metadane i typy maszyn, na których
działa, jego zależności oraz porty, które otwiera na hoście. Wymienia szablony
modułu i miejsca, w które trafia ich wynik, jego przestrzeń na dane i to, które
z jego danych trafiają do kopii zapasowej. Deklaruje też integrację z hostem
(parametry sysctl i moduły jądra), bloki server nginx rejestrowane przez moduł,
adresy URL wypisywane po zakończeniu roli, reguły walidacji i ustawienia modułu
(`settings`).

Schemat ustawień ma dwa zastosowania. Służy do sprawdzania pliku fleet,
a aplikacja kiwi-server buduje na jego podstawie formularz ustawień. Szablony
są pisane w Jinja2 i mogą korzystać z kontekstu hosta. Ten kontekst zawiera
nazwę i typ hosta, adres każdego modułu, sieć mesh, nazwy z twojej sieci,
włączone moduły i ustawienia każdego modułu.

W podmanie plik compose jest tłumaczony na quadlets. To tłumaczenie obsługuje
ustalony zestaw kluczy compose, a każdy inny klucz powoduje błąd podczas
generowania stacku.

Moduły są rozwijane i wydawane w repozytorium
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Pełny opis
formatu znajdziesz w
[docs/modules.md w repozytorium kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
