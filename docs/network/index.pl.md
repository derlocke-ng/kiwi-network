# Jak działa sieć

Kiwi Network łączy twoje maszyny w jedną prywatną sieć, niezależnie od tego,
gdzie stoją: serwery w domu albo w biurze, laptopy, telefony, a nawet całe
sieci domowe za routerem. Maszyny łączą się ze sobą tak, jakby były w tej samej
sieci lokalnej, a dostępna z internetu musi być tylko jedna z nich. Z tej
strony dowiesz się, jak ta sieć jest zbudowana i do czego służy każda jej
część.

Ta prywatna sieć to **sieć mesh oparta na WireGuard**. WireGuard to
oprogramowanie VPN, które szyfruje połączenia, a *siecią mesh* nazywamy w tej
dokumentacji prywatną sieć, do której należą wszystkie twoje maszyny. W jej
centrum jest jedna maszyna, *kiwi-master*. Każda inna maszyna (node’y w domu
albo w biurze, laptopy, telefony, routery) sama nawiązuje połączenie
z masterem i dzięki temu może przez sieć mesh połączyć się z pozostałymi. Całą
sieć opisuje jeden plik, plik fleet (`fleet.yaml`), a narzędzie
[kiwi-server](../server/index.md) buduje ją na jego podstawie.

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

Master to maszyna, z którą łączą się wszystkie pozostałe. Jego rola, `master`,
uruchamia pięć modułów opisanych poniżej. Pi-hole, Tor i nginx współdzielą
z serwerem WireGuard sieciową przestrzeń nazw (network namespace), czyli osobny
zestaw interfejsów, adresów i tras, jaki ma każdy kontener. Te trzy usługi nie mają
więc własnej sieci, tylko korzystają z sieci serwera WireGuard. Z tego powodu
są restartowane razem z nim.

- **vpn-server** (wg-easy) to serwer WireGuard. Łączy się z nim każdy klient
  i każdy node i to on wystawia im konfiguracje WireGuard. Może je dla ciebie
  utworzyć kiwi-server (`kiwi-server enroll`).
- **vpn-client** (gluetun) łączy mastera z komercyjnym dostawcą VPN. Preset
  używa usługi Mullvad, ale zadziała każdy dostawca obsługiwany przez gluetun.
  Trasa domyślna serwera WireGuard prowadzi do tego klienta VPN, więc ruch
  z sieci mesh do internetu przechodzi przez dostawcę, a strony internetowe
  widzą adres dostawcy, nie adres mastera. To połączenie jest *wyjściem*
  mastera, czyli drogą, którą ruch z sieci mesh trafia do internetu. Ruch
  przechodzi kolejno przez dwa VPN-y, najpierw twój, potem dostawcy, dlatego
  taki układ nazywa się **podwójnym przeskokiem** (double hop). Master bez
  modułu vpn-client wysyła ruch do internetu bezpośrednio, ze swojego adresu.
- **dns** (Pi-hole 6) to serwer DNS sieci mesh. Odpowiada pod adresem mastera
  w sieci mesh, `10.8.0.1`. Zobacz [DNS, nazwy i certyfikaty](dns.md).
- **tor** udostępnia klientom w sieci mesh proxy SOCKS5 pod adresem
  `10.8.0.1:9050`. Węzły wejściowe i wyjściowe Tora są ograniczone do wybranych
  krajów (domyślnie `de,ch,at,nl,fr`, co wymusza opcja `StrictNodes`).
- **reverse-proxy** (nginx) udostępnia strony administracyjne, czyli interfejsy
  WWW wg-easy i Pi-hole: `wg.<master>` i `pihole.<master>`. Można je otworzyć
  tylko z sieci mesh i tylko z klientów, którym wolno z nich korzystać (zobacz
  „Grupy klientów” niżej).

Na masterze mogą też działać **przekaźnik nostr** i **hub** dla
[ludzi z twojej sieci](../people/hubs.md#on-a-kiwi-network). Hub to strona
społeczności, która działa w przeglądarce, a przekaźnik nostr to serwer, przez
który huby synchronizują dane. Do mastera można również dodać Portainer i kopie
zapasowe.

### Co jest dostępne z internetu { #what-is-reachable-from-the-internet }

Domyślnie master ma otwarty do internetu **jeden port**: WireGuard na UDP
51820. Strony administracyjne da się otworzyć tylko z sieci mesh. Kolejne
porty otwierają dwa ustawienia:

- `reverse-proxy.public: true` otwiera porty 80 i 443 i pobiera certyfikaty
  Let’s Encrypt dla nazw spoza domeny twojej sieci. Cała reszta nadal jest
  dostępna wyłącznie z sieci mesh, a strony administracyjne odpowiadają na
  zapytania z zewnątrz błędem 403. To ustawienie jest przeznaczone dla
  publicznego huba albo przekaźnika.
- `vpn-server.unlock_relay` otwiera porty TCP
  [pierścieni Tang](../server/operations.md#encrypted-disks-and-unlocking) dla
  maszyn za NAT-em. Tang to serwer, dzięki któremu maszyna z zaszyfrowanym
  dyskiem może odblokować ten dysk przy starcie, a pierścień to jeden serwer
  Tang z własnymi kluczami.

kiwi-server nie zmienia konfiguracji SSH, którą ustawił system operacyjny,
więc domyślnie można się logować wyłącznie kluczem. Sam kiwi-server używa SSH
do poleceń `apply` i `status`.

## Grupy klientów { #client-groups }

Klienci serwera WireGuard (wg-easy) są przydzielani do **grup** według adresu.
Grupa określa, z czym jej członkowie mogą się łączyć:

| Grupa | Podsieć | Ma dostęp do | Widzi innych klientów | Strony administracyjne |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | node’ów | nie | nie |
| `pentest` | `10.8.2.0/24` | niczego w sieci mesh | nie | nie |
| `devices` | `10.8.3.0/24` | wszystkiego | tak | tak |
| `routers` | `10.8.4.0/24` | wszystkiego | tak | nie |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # kod QR dla aplikacji WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # przez tunel idzie tylko ruch do sieci mesh
```

Członkowie każdej grupy mają też dostęp do internetu przez wyjście mastera,
chyba że ustawisz dla grupy `internet: false`. Klient, którego adres nie należy
do żadnej grupy (`10.8.0.x`), jest zwykłym uczestnikiem sieci mesh. Ma dostęp
do wszystkiego, a strony administracyjne otworzy, o ile włączone jest
ustawienie `admin_from_mesh`.

Grupy są ustawieniem modułu vpn-server (`groups`), możesz więc je zmieniać
i dodawać własne. Ustawienie `reach` grupy przyjmuje wartości `all` i `nodes`,
nazwy hostów, adresy albo podsieci. Starsze ustawienie `isolated_subnet`, które
definiowało jedną odizolowaną grupę, nadal istnieje, ale domyślnie jest
wyłączone.

## Node’y { #nodes }

Node to maszyna w domu albo w biurze, na której działają twoje usługi. Node też
ma moduł vpn-client, ale tu nie łączy się on z komercyjnym dostawcą VPN,
tylko z masterem. Używa do tego konfiguracji WireGuard, którą master
wystawił dla tego node’a. Polecenie `kiwi-server enroll` zapisuje ją w pliku
`secrets/<hostname>.conf`, a node korzysta z niej bez żadnych dodatkowych
ustawień. Node nie potrzebuje portu otwartego do internetu, bo sam nawiązuje
połączenie z masterem. Dlatego działa także za NAT-em domowego routera.

Rola `node` ma trzy presety, czyli gotowe listy modułów:

| Preset | Czym staje się maszyna |
|---|---|
| `gateway` (domyślny) | Bramą dla sieci lokalnej (LAN). Urządzenia w sieci lokalnej, które mają tę maszynę ustawioną jako bramę domyślną, wychodzą do internetu przez VPN i mają dostęp do sieci mesh. Pi-hole jest serwerem DNS sieci lokalnej, a opcjonalnie także jej serwerem DHCP. Programy do pobierania plików, Transmission i JDownloader, działają *wewnątrz* sieciowej przestrzeni nazw klienta VPN, więc gdy tunel nie działa, nie mają żadnej trasy. Preset zawiera też nginx, Portainer i SFTP. |
| `cloud` | Twoją własną chmurą: Nextcloud z pakietem Collabora obsługuje pliki, kalendarze i dokumenty, a Vaultwarden hasła. Usługi te stoją za nginx, w zestawie jest też Portainer. Nextcloud jest zbudowany z kontenerów projektu AIO, ale bez jego kontenera głównego (master container). |
| `minimal` | Tylko klient VPN i nginx. Potrzebne moduły dodajesz samodzielnie. |

Node’y mogą też robić kopie zapasowe, służyć jako serwer kopii zapasowych
i uruchamiać Tang. OpenCloud, Immich i Paperless-ngx są dołączone do
wypróbowania. Zobacz [listę modułów](../server/modules.md).

Usługi node’a są dostępne w jego sieci lokalnej oraz pod jego **adresem
w sieci mesh** (na przykład `10.8.0.25`). Ruch z sieci mesh na porty 80 i 443
pod tym adresem jest przekazywany do reverse proxy node’a.

## Nazwy { #names }

Nazwy maszyn trzymają się pewnej konwencji. **Mastery noszą nazwy potraw
z owoców** (`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`,
`trifle`, `cider`), a **node’y nazwy owoców** (`papaya`, `lychee`, `guava`,
`quince`, `damson`). Dzięki temu w każdej linii logu od razu widać, o jaki
rodzaj maszyny chodzi. To tylko konwencja i zadziała każda nazwa. Nazwa
usługi powstaje z nazwy maszyny, na której usługa działa: `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. Zobacz
[DNS, nazwy i certyfikaty](dns.md).

## Jak sieć mesh łączy się z internetem { #ways-out }

Master to serwer WireGuard z wyjściem, czyli drogą, którą ruch z sieci mesh
trafia do internetu. Wyjście ma trzy tryby:

| Tryb | Jak sieć mesh łączy się z internetem | Stan |
|---|---|---|
| **provider** | Przez komercyjnego dostawcę VPN (gluetun). To właśnie podwójny przeskok i tak konfiguruje mastera jego preset. | zrealizowane |
| **direct** | Bezpośrednio przez łącze internetowe mastera. Żeby uzyskać ten tryb, wypisz moduły mastera bez `vpn-client`. | zrealizowane |
| **master** | Przez *mastera innej sieci*. Twój master jest tam klientem w jednej z grup, które mają dostęp do internetu i do niczego więcej. Nazywa się to multi-hop. | zaprojektowane; wymaga dodawania maszyn między sieciami, czyli federacji |

Niezależnie od trybu wyjścia każdy master udostępnia sieci mesh także proxy
SOCKS5 Tora.

## Każda sieć Kiwi ma własną sieć mesh { #one-mesh-per-network }

Każda sieć Kiwi ma własną sieć mesh z osobnym zakresem adresów. Domyślny zakres to
`10.8.0.0/16`. Mastery i node’y mają adresy z `10.8.0.0/24`, a dalej idą grupy:
guests w `.1`, pentest w `.2`, devices w `.3` i routers w `.4`. Druga sieć Kiwi
używa innego zakresu, na przykład `10.9.0.0/16`, żeby urządzenie należące do
obu sieci mogło je odróżnić. Na razie zakresu nie ustawia się w jednym miejscu,
tylko w kilku ustawieniach: `mesh_subnet`, w module vpn-server `server_ip`,
`wg_subnet`, `wg_default_address` i `groups`, a w module tor
`socks_policy_accept`. Wszystkie ustawia plik fleet.

## Adresacja { #addressing }

| Co | Wartość domyślna |
|---|---|
| Cała sieć mesh (trasowana na każdym hoście) | domyślnie `10.8.0.0/16` (`mesh_subnet`) |
| Klienci wg-easy | `10.8.0.0/24`; serwer ma adres `10.8.0.1` |
| Grupy klientów | `10.8.1.0/24` … `10.8.4.0/24` |
| Sieć stacku | `172.64.0.0/24` na masterze, `172.128.0.0/24` na nodzie |
| MTU WireGuard | `1376` (`wg_mtu`), zmierzone poleceniem [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU mostu stacku | `1500` (`bridge_mtu`) |

Stack maszyny to wszystkie kontenery, które uruchamiają jej moduły. Każda
maszyna ze stackiem kieruje ruch do całego zakresu adresów sieci mesh przez
swojego klienta VPN, a master przez serwer WireGuard. Dzięki temu zarówno sama
maszyna, jak i jej kontenery mają dostęp do każdego node’a.

## Automatyczne restarty i aktualizacje { #keeping-it-fresh }

Każda maszyna dostaje dwa timery systemd, które konfiguruje się w ustawieniach
jej stacku. Pierwszy to **codzienny restart VPN** o `07:00`, po którym maszyna
ma nowy adres wyjściowy. Drugi to **cotygodniowa aktualizacja** w niedzielę
o 00:00, która uruchamia `podman auto-update`, o ile ustawione jest
`auto_update: registry`. System operacyjny też aktualizuje się sam, a ponownie
uruchamia się tylko w
[oknie czasowym, które wyznaczysz](../server/machines.md#updates).

## Cała sieć lokalna w sieci mesh { #a-whole-lan-in-the-mesh }

Router może dołączyć do sieci mesh jako klient WireGuard w grupie `routers`.
Router może też mieć trasę statyczną, która kieruje ruch przeznaczony dla
podsieci mesh do node’a `gateway`. W obu przypadkach każde urządzenie w sieci lokalnej tego
routera ma dostęp do każdego node’a, choć samo nie uruchamia WireGuard. Zobacz
[Routery](routers.md).
