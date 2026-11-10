# kiwi-custodia

kiwi-custodia daje ci osobne środowisko linuksowe dla każdej sieci klienta,
w której pracujesz. Każde środowisko to kontener z wybraną przez ciebie
dystrybucją Linuksa, a cały jego ruch sieciowy przechodzi przez jeden exit
[kiwi-proxy](kiwi-proxy.md). Exit to zapisane pod nazwą połączenie
z upstreamem, np. proxy SOCKS5 prowadzące do sieci jednego klienta. W ten
sposób możesz pracować dla dziesięciu klientów bez dziesięciu połączeń VPN na
hoście, a narzędzia i klucze każdego klienta zostają w jego środowisku.
*Jeśli znasz distrobox: to ten sam pomysł, z tą różnicą, że kontener może
łączyć się z siecią wyłącznie przez swój exit.*

- Repozytorium: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Najnowsze wydanie: **v0.2.3**. Jest w [katalogu Kiwi](../desktop/catalogs.md), zakres użytkownika.
- Ma narzędzie wiersza poleceń (`kiwi-custodia`) i aplikację GTK4 (**Kiwi Custodia**).

**Box** to jedna dystrybucja Linuksa w kontenerze rootless Podmana, czyli
w kontenerze uruchamianym jako twój własny użytkownik, bez uprawnień roota.
Box ma własny folder domowy i jest podłączony do gatewaya exitu. Gateway to
kontener, który kiwi-proxy uruchamia dla exitu, a jedyna trasa wychodząca
z niego prowadzi do upstreamu tego exitu. W boxie możesz zainstalować
cokolwiek menedżerem pakietów danej dystrybucji. Jego aplikacje desktopowe
otwierają się na twoim pulpicie i możesz je dodać do siatki aplikacji. Box nie
ma żadnej trasy poza exitem. Dotyczy to każdego programu w nim: `dnf`, klienta
gier, a także programu linkowanego statycznie, który ignoruje `$ALL_PROXY`.
Jeśli exit przestanie działać, box nie ma żadnej trasy.

Dlatego dobrym sposobem pracy jest jeden box na każdą sieć klienta. Narzędzia,
klucze i historia powłoki klienta A są w jednym boxie, klienta B w innym,
a każdy box łączy się tylko ze swoim klientem.

## Instalacja { #install }

```bash
kiwi install kiwi-custodia   # instaluje przy okazji kiwi-proxy; albo ./install.sh install
kiwi-custodia setup          # obraz tunelu oraz obraz gatewaya i dane DNS kiwi-proxy
```

kiwi-custodia wymaga rootless Podmana z `catatonit`, kiwi-proxy, sesji Wayland
i Pythona 3.12+ z pydantic. Aplikacja potrzebuje GTK4 i libadwaita. Kontenery
rootless muszą też mieć dostęp do `/dev/net/tun`. Obrazy dystrybucji nie są
pobierane podczas konfiguracji. Obraz zostaje pobrany, gdy po raz pierwszy
uruchomi się box, który z niego korzysta. Po aktualizacji uruchom ponownie
`kiwi-custodia setup`.

## Używanie { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # exit, definiowany raz, w kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # box na nim; pierwsze uruchomienie instaluje zestaw podstawowy
kiwi-custodia enter work                                   # powłoka w boxie: sudo dnf install …
kiwi-custodia run work -- firefox                          # jedno polecenie w boxie
kiwi-custodia check work                                   # co widzi świat z wnętrza boxa
kiwi-custodia apps work                                    # aplikacje desktopowe w boxie
kiwi-custodia export work firefox                          # „Firefox (work)” w siatce aplikacji
kiwi-custodia stop work
kiwi-custodia reset work                                   # powrót do obrazu bazowego; folder domowy zostaje
kiwi-custodia-gui
```

Dostępne dystrybucje to `fedora` (domyślna), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky` i `alpine`. Możesz też wybrać `custom` i samodzielnie
wskazać obraz opcją `--image`.

## Jak zbudowany jest box { #how-a-box-is-built }

Działający box składa się z trzech kontenerów, które współdzielą jedną
sieciową przestrzeń nazw (network namespace), czyli te same interfejsy
sieciowe, trasy i reguły zapory. Pierwszy to **gateway** z kiwi-proxy. Drugi
to **kontener pomocniczy tunelu** (sidecar), w którym tun2socks działa na
urządzeniu TUN. Urządzenie TUN to wirtualny interfejs sieciowy, który staje się
tu trasą domyślną. Trzeci kontener to sam **box**. Cały ruch z boxa trafia do
urządzenia TUN, a stamtąd do proxy SOCKS5 exitu. Działa to przez trasę
domyślną, a nie przez ustawienia proxy, więc obejmuje także programy, które
ustawienia proxy ignorują.

- Box działa jako twój użytkownik, z tym samym uid, a `sudo` działa w nim bez
  hasła. Jego folder domowy to
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Każdy box ma własny folder
  domowy i nie korzysta z twojego prawdziwego, więc dwa boxy to dwie osobne
  tożsamości.
- Gdy box się zatrzymuje, zmiany wprowadzone w jego wnętrzu są zapisywane
  w snapshocie należącym do tego boxa. `reset` przywraca box do obrazu
  bazowego.
- Wayland, X11 (przez Xwayland), PipeWire, magistrala sesji i `/dev/dri` są
  udostępniane wewnątrz boxa, żeby działały aplikacje desktopowe i gry.
- Na zapytania DNS odpowiada serwer DNS gatewaya, który blokuje też domeny
  reklamowe. Na exicie ze zdalnym DNS nazwy rozwiązuje zamiast niego upstream.

## Czym nie jest { #what-it-is-not }

Box **ogranicza sieć. Nie jest piaskownicą, która chroni twój desktop przed
programami w boxie.** Tak jak kontener distrobox, box dostaje dostęp do
twojego ekranu i magistrali sesji. Program w boxie może więc wyświetlać okna,
czytać schowek i korzystać z portali desktopowych. Nie może jedynie łączyć się
z siecią inaczej niż przez swój exit. UDP nie jest przekazywane, więc QUIC
i media WebRTC nie działają, a dla IPv6 nie ma trasy.

Boxy na tym samym exicie współdzielą go. Boxy, które muszą być od siebie
oddzielone, potrzebują różnych exitów.
