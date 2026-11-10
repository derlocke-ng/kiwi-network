# Jak działa sieć

Kiwi Network to **sieć mesh WireGuard z jednym hubem**, *kiwi-master*. Każda
inna maszyna (node'y w domu lub w biurze, laptopy, telefony, routery) łączy się
z masterem i spotyka pozostałe w sieci mesh. Całość jest opisana w jednym pliku
fleet i budowana przez [kiwi-server](../server/index.md).

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## Master { #the-master }

Rola `master` uruchamia pięć modułów. Pi-hole, Tor i nginx działają w
przestrzeni nazw sieciowych serwera WireGuard i wracają razem z nim.

- **vpn-server** (wg-easy) to punkt wejścia dla każdego klienta i node'a; wydaje
  też ich konfiguracje WireGuard. kiwi-server może je dla ciebie utworzyć
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) łączy się z komercyjnym dostawcą VPN: w presecie z
  Mullvad, ogólnie z dowolnym dostawcą obsługiwanym przez gluetun. Domyślna
  trasa serwera WireGuard prowadzi do niego, więc ruch z sieci mesh wychodzi
  przez dostawcę, a nie z własnego adresu mastera. To jest **podwójny skok**
  (double hop). Master bez vpn-client wychodzi bezpośrednio.
- **dns** (Pi-hole 6) odpowiada pod adresem mastera w sieci mesh, `10.8.0.1`.
  Zobacz [DNS, nazwy i certyfikaty](dns.md).
- **tor** udostępnia klientom sieci mesh SOCKS5 pod `10.8.0.1:9050`, z węzłami
  wejściowymi i wyjściowymi przypiętymi do zestawu krajów (domyślnie
  `de,ch,at,nl,fr`, `StrictNodes`).
- **reverse-proxy** (nginx) serwuje strony administracyjne, `wg.<master>` i
  `pihole.<master>`, grupom administracyjnym w sieci mesh.

Master może też obsługiwać **przekaźnik nostr** i **hub** dla
[ludzi w twojej sieci](../people/hubs.md#on-a-kiwi-network), a także Portainer
i kopie zapasowe.

### Co jest osiągalne z Internetu { #what-is-reachable-from-the-internet }

Domyślnie master publikuje **jeden port**: WireGuard, UDP 51820. Strony
administracyjne odpowiadają tylko sieci mesh. Dwa ustawienia dodają więcej:

- `reverse-proxy.public: true` publikuje porty 80 i 443, z certyfikatami Let's
  Encrypt dla nazw spoza domeny floty. Wszystko inne nadal odpowiada tylko
  sieci mesh, a strony administracyjne odpowiadają z zewnątrz kodem 403. To
  opcja dla publicznego huba lub przekaźnika.
- `vpn-server.unlock_relay` otwiera porty TCP
  [pierścieni Tang](../server/operations.md#encrypted-disks-and-unlocking) dla
  maszyn za NAT-em.

SSH pozostaje takie, jak ustawił je system operacyjny (domyślnie tylko klucze).
kiwi-server używa go do `apply` i `status`.

## Grupy klientów { #client-groups }

Klienci wg-easy są dzieleni na **grupy** według adresu. Każda grupa decyduje,
do czego mają dostęp jej członkowie:

| Grupa | Podsieć | Ma dostęp do | Widzi innych klientów | Strony administracyjne |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | node'ów | nie | nie |
| `pentest` | `10.8.2.0/24` | niczego w sieci mesh | nie | nie |
| `devices` | `10.8.3.0/24` | wszystkiego | tak | tak |
| `routers` | `10.8.4.0/24` | wszystkiego | tak | nie |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # kod QR dla aplikacji WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # przez tunel idzie tylko sieć mesh
```

Każda grupa może wychodzić do Internetu przez wyjście, chyba że ustawisz
`internet: false`. Klienci spoza wszystkich grup (`10.8.0.x`) to zwykła sieć
mesh: mają dostęp do wszystkiego i widzą strony administracyjne, dopóki
`admin_from_mesh` jest włączone. Grupy są ustawieniem modułu vpn-server
(`groups`), więc możesz je zmieniać lub dodawać własne (`reach` przyjmuje
`all`, `nodes`, nazwy hostów, adresy lub podsieci). Stare pojedyncze
`isolated_subnet` nadal istnieje, ale domyślnie jest wyłączone.

## Node'y { #nodes }

vpn-client node'a nie rozmawia z komercyjnym VPN-em. Używa konfiguracji
WireGuard, którą master dla niego wydał (`kiwi-server enroll` zapisuje
`secrets/<hostname>.conf`, a node sam ją pobiera). Node nie potrzebuje
otwartego portu w Internecie: sam łączy się z masterem, więc działa za NAT-em
domowego routera.

Rola `node` ma trzy presety:

| Preset | Czym staje się maszyna |
|---|---|
| `gateway` (domyślny) | Bramą LAN. Klienci w LAN, którzy używają jej jako bramy domyślnej, wychodzą przez VPN i mają dostęp do sieci mesh. Pi-hole obsługuje LAN (opcjonalnie jako jego serwer DHCP). Transmission i JDownloader działają *wewnątrz* przestrzeni nazw sieciowych klienta VPN, więc gdy tunel nie działa, nie mają żadnej trasy. Z nginx, Portainer i SFTP. |
| `cloud` | Nextcloud (z kontenerów projektu AIO, bez kontenera AIO master) z Collabora, do tego Vaultwarden, za nginx, do tego Portainer |
| `minimal` | Tylko klient VPN i nginx, a moduły wybierasz sam |

Node'y mogą też uruchamiać kopie zapasowe, serwer kopii zapasowych, Tang oraz
(do wypróbowania) OpenCloud, Immich i Paperless-ngx. Zobacz
[listę modułów](../server/modules.md).

Usługi na nodzie są osiągalne w jego LAN i pod jego **adresem w sieci mesh**
(np. `10.8.0.25`). Ruch z sieci mesh na ten adres na portach 80 i 443 trafia
do reverse proxy.

## Nazwy { #names }

Nazwy maszyn pochodzą z sadu: **mastery od deserów i potraw z owoców**
(`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`,
`cider`), a **node'y od owoców** (`papaya`, `lychee`, `guava`, `quince`,
`damson`), dzięki czemu rodzaj maszyny widać w każdej linii logu. To konwencja;
każda nazwa działa. Usługi leżą pod swoim hostem: `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. Zobacz [DNS, nazwy i certyfikaty](dns.md).

## Drogi wyjścia { #ways-out }

Master to serwer WireGuard z wyjściem, a wyjście ma trzy tryby:

| Tryb | Jak sieć mesh dociera do Internetu | Stan |
|---|---|---|
| **provider** | przez komercyjny VPN (gluetun): podwójny skok i preset mastera | zbudowany |
| **direct** | prosto przez własne łącze mastera. Wypisz moduły mastera bez `vpn-client` | zbudowany |
| **master** | przez *mastera innej sieci*, jako klient w jednej z jego grup, który może dotrzeć do Internetu i do niczego więcej: multi-hop | zaprojektowany; wymaga rejestracji między sieciami, czyli federacji |

Każdy master udostępnia też sieci mesh SOCKS5 Tora, niezależnie od swojego
wyjścia.

## Jedna sieć mesh na sieć { #one-mesh-per-network }

Każda sieć ma własną sieć mesh. Domyślnie jest to `10.8.0.0/16`: mastery i
node'y w `10.8.0.0/24`, potem guests `.1`, pentest `.2`, devices `.3` i
routers `.4`. Druga sieć bierze inny zakres, na przykład `10.9.0.0/16`, żeby
urządzenie należące do obu mogło je rozróżnić. Dziś zakres jest rozłożony na
kilka ustawień (`mesh_subnet`, `server_ip` modułu vpn-server, `wg_subnet`,
`wg_default_address` i `groups` oraz `socks_policy_accept` Tora), a plik fleet
ustawia je wszystkie.

## Adresacja { #addressing }

| Co | Domyślnie |
|---|---|
| Cała sieć mesh (trasowana na każdym hoście) | domyślnie `10.8.0.0/16` (`mesh_subnet`) |
| Klienci wg-easy | `10.8.0.0/24`; serwer to `10.8.0.1` |
| Grupy klientów | `10.8.1.0/24` … `10.8.4.0/24` |
| Sieć stacka | `172.64.0.0/24` na masterze, `172.128.0.0/24` na nodzie |
| MTU WireGuard | `1376` (`wg_mtu`), zmierzone przez [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU mostka stacka | `1500` (`bridge_mtu`) |

Każdy host stacka trasuje sieć mesh przez swojego klienta VPN (na masterze
przez serwer WireGuard), więc host i jego kontenery docierają do każdego
node'a.

## Świeżość { #keeping-it-fresh }

Każda maszyna dostaje ze swoich ustawień stacka dwa timery: **codzienny
restart VPN** (`07:00`, dla świeżego adresu wyjściowego) i **cotygodniową
aktualizację** (niedziela 00:00; uruchamia `podman auto-update`, dopóki
ustawione jest `auto_update: registry`). System operacyjny aktualizuje się sam
i uruchamia ponownie tylko w [twoim oknie](../server/machines.md#updates).

## Cały LAN w sieci mesh { #a-whole-lan-in-the-mesh }

Router może dołączyć do sieci mesh jako klient WireGuard w grupie `routers`
albo wysyłać podsieć mesh do node'a gateway przez trasę statyczną. Wtedy każde
urządzenie w tym LAN dociera do każdego node'a bez uruchamiania WireGuard.
Zobacz [Routery](routers.md).
