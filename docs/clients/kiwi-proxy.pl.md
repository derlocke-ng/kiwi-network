# kiwi-proxy

kiwi-proxy jest dla osób, które pracują w sieciach wielu klientów i łączą się
z każdą z nich przez osobne połączenie VPN lub SOCKS. Każde połączenie
zapisujesz jako **exit** z własną nazwą i uruchamiasz je tylko wtedy, gdy go
potrzebujesz. Exity są od siebie odizolowane, a program, który korzysta
z exitu, może łączyć się z siecią wyłącznie przez niego. Dziesięciu klientów
nie oznacza więc dziesięciu połączeń VPN działających naraz na hoście.
Z exitu mogą korzystać przeglądarki, narzędzia do testów, programy na hoście
i maszyny z kiwi-server. kiwi-proxy działa w rootless Podmanie, czyli
w kontenerach uruchamianych jako twój własny użytkownik, bez uprawnień roota.

- Repozytorium: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Najnowsze wydanie: **v0.7.3**. Jest w [katalogu Kiwi](../desktop/catalogs.md), zakres użytkownika.
- Składa się z narzędzia wiersza poleceń (`kiwi-proxy`), aplikacji GTK4
  (**Kiwi Proxy**) i jednostek użytkownika systemd. To silnik proxy, który
  wcześniej był częścią kiwi-fox. Został wydzielony do osobnego projektu, żeby
  mogło z niego korzystać więcej niż jedna aplikacja.

**Exit** to jedno połączenie z upstreamem, zapisane pod własną nazwą. Upstream
to proxy, do którego wysyłany jest ruch. Jest to albo proxy SOCKS5, które ci
przekazano, albo proxy, które [moduł dostawcy](providers.md) tworzy dla ciebie
przez Tor, tunel VPN, 9proxy albo Mysterium. Sam exit to tylko zapisany wpis
i nic dla niego nie działa. Gdy uruchamiasz exit, kiwi-proxy uruchamia dla
niego kontener **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Gateway tworzy sieciową przestrzeń nazw (network namespace), czyli osobny stos
sieciowy z własnymi trasami i regułami zapory. Przeglądarka z kiwi-fox, box
z kiwi-custodia albo kontener z narzędziem dołącza do tej przestrzeni i staje
się członkiem gatewaya. Od tej chwili jego jedyna trasa prowadzi do upstreamu
exitu. Jeśli gateway przestanie działać, jego członkowie nie mają już żadnej
trasy. Takie zachowanie nazywa się fail-closed: awaria przerywa połączenie
i nigdy nie otwiera innej drogi.

## Instalacja { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox i kiwi-custodia instalują go przy okazji
kiwi-proxy setup             # obraz gatewaya, dane DNS, obrazy modułów dostawców
```

kiwi-proxy wymaga rootless Podmana oraz Pythona 3.12+ z pydantic. Aplikacja
potrzebuje dodatkowo GTK4 i libadwaita. Hasła są przechowywane w pęku kluczy
desktopu przez `secret-tool`. Na maszynie bez pęku kluczy trafiają do plików
z uprawnieniami 0600, które może odczytać tylko twój użytkownik.

## Używanie { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # exit; nic jeszcze nie działa
kiwi-proxy add tor-de --module tor --country de        # exit z modułu dostawcy
kiwi-proxy list
kiwi-proxy check client-a      # co widzi przez niego świat
kiwi-proxy up client-a         # uruchamia jego gateway i utrzymuje go
kiwi-proxy down client-a       # zatrzymuje go razem ze wszystkimi, którzy z niego korzystają
kiwi-proxy ps                  # działające gatewaye, niezależnie od tego, która aplikacja je uruchomiła
kiwi-proxy reap                # zatrzymuje gatewaye, z których nikt nie korzysta
kiwi-proxy-gui                 # „Kiwi Proxy” w siatce aplikacji
```

Punkt końcowy to adres upstreamu. Możesz go zapisać jako
`socks5://user:pass@host:port`, `http://…` albo `https://…` albo w formacie
dostawcy `host:port:user:pass`. `kiwi-proxy test ENDPOINT` testuje punkt
końcowy bez tworzenia exitu.

### Exity dla programów na hoście { #exits-for-host-applications }

Program na hoście nie musi działać w kontenerze, żeby korzystać z exitu.
kiwi-proxy może udostępnić exit jako port SOCKS5 na hoście, osobny port dla
każdego exitu:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Domyślnie port nasłuchuje tylko na `127.0.0.1`. Jeśli pozwolisz mu nasłuchiwać
na innym adresie, musisz albo ustawić nazwę użytkownika opcją `--expose-user`,
albo wprost zezwolić na otwarty dostęp opcją `--expose-open`. Żeby exit działał
od chwili zalogowania, uruchom `systemctl --user enable --now kiwi-proxy@NAME`.

### DNS { #dns }

- **Tryb resolvera** jest domyślny. dnscrypt-proxy rozwiązuje nazwy przez DNS
  over HTTPS (DoH) i wysyła te zapytania przez exit. Serwerem DoH może być
  Google, Cloudflare, Quad9 albo Mullvad. Stosowane są listy blokowania (OISD),
  odświeżane codziennie.
- **Tryb zdalny** (`--dns remote`) przekazuje nazwy do upstreamu, który sam je
  rozwiązuje. Ten tryb jest przeznaczony dla Tora i nazw `.onion`. Listy
  blokowania obowiązują także w nim.

### Zasady gatewaya { #rules-of-the-gateway }

- UDP nie jest przekazywane. Oznacza to brak QUIC, brak mediów WebRTC i brak
  DNS w postaci niezaszyfrowanej.
- Exit łączy się ze światem zewnętrznym wyłącznie przez IPv4. Nazwa, która nie
  ma adresu IPv4, jest odrzucana.
- Gateway uruchomiony przez inną aplikację, np. kiwi-fox albo kiwi-custodia,
  jest usuwany, gdy odłączy się od niego ostatni członek. Gateway uruchomiony
  poleceniem `kiwi-proxy up` działa, dopóki nie wydasz polecenia
  `kiwi-proxy down`.
- Każdy exit ma dokładnie jeden gateway, z którego może korzystać dowolna
  liczba członków. Członkowie, którzy muszą być od siebie oddzieleni, korzystają
  z różnych exitów.

## Aplikacja { #the-app }

W aplikacji **Kiwi Proxy** dodajesz i edytujesz exity, albo z przekazanego ci
proxy SOCKS5, albo z modułu dostawcy. Dla exitu z modułu wybierasz kraj
z listy z wyszukiwarką albo konkretny węzeł z listy. Możesz uruchamiać
i zatrzymywać exity, udostępnić exit jako port SOCKS5 na tym komputerze
i skopiować jego adres oraz sprawdzić, co widzi świat zewnętrzny, gdy łączysz
się przez ten exit. Aplikacja pokazuje też, którzy członkowie korzystają
z gatewaya, wraz z ich logami, a także instaluje i konfiguruje moduły
dostawców.

## Na maszynie z kiwi-server { #on-a-kiwi-server-machine }

Repozytorium kiwi-proxy zawiera też moduł dla kiwi-server. Dzięki niemu
maszyna z kiwi-server udostępnia exity całej sieci mesh, czyli prywatnej
sieci WireGuard, która łączy twoje maszyny z kiwi-server. Moduł uruchamia
jeden gateway dla każdego exitu i udostępnia go pod adresem hosta w sieci
mesh. Według jego dokumentacji modułu nie ma jeszcze w drzewie źródeł
kiwi-server i nie był jeszcze uruchamiany na żadnej maszynie. Moduły dostawców
działają tylko na desktopie i nie działają na maszynie z kiwi-server.

Więcej informacji: [architektura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[programy korzystające z exitów](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[system wtyczek](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
