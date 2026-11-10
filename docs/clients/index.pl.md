# Praca w sieciach wielu klientów

Jeśli pracujesz zdalnie dla wielu klientów, do sieci każdego z nich zwykle
łączysz się przez osobne połączenie VPN lub SOCKS. Dziesięciu klientów to
wtedy dziesięć połączeń. Uruchomienie ich wszystkich na hoście sprawia
kłopoty: dziesięć tuneli działa jednocześnie, ich trasy wchodzą sobie
w drogę, a ruch przeznaczony do sieci jednego klienta może trafić do sieci
innego.

Aplikacje desktopowe Kiwi pozwalają pracować w sieci każdego klienta
w izolacji. Host nie jest zaśmiecany tunelami i trasami, a ty nie masz
dziesięciu połączeń VPN działających naraz. Każde połączenie trafia do
osobnego kontenera, a jedyna trasa wychodząca z tego kontenera prowadzi do
tego jednego klienta. Takie połączenie nazywa się **exitem**. Swoje narzędzia
uruchamiasz w kontenerze albo w profilu przeglądarki, który korzysta
z potrzebnego exitu. Poza tym nic na hoście się nie zmienia.

| Aplikacja | Co robi |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Silnik, na którym opierają się pozostałe aplikacje. **Exit** to jedno połączenie z upstreamem, zapisane pod wybraną nazwą. Upstream to proxy, do którego wysyłany jest twój ruch: albo proxy SOCKS5, które ci przekazano, albo takie, które tworzy moduł dostawcy. Gdy uruchamiasz exit, kiwi-proxy tworzy dla niego **gateway**. Gateway to sieciowa przestrzeń nazw (network namespace), czyli osobny stos sieciowy z własnymi trasami i zaporą. Jedyna trasa z gatewaya prowadzi do tego upstreamu. Programy na hoście mogą korzystać z exitu przez lokalny port SOCKS5 |
| [**kiwi-custodia**](kiwi-custodia.md) | **Dystrybucje Linuksa w boxach, które korzystają z exitu.** Box to kontener rootless (działający bez uprawnień roota) z Fedorą, Ubuntu, Debianem, Kali, Archem, openSUSE, Rocky albo Alpine i z własnym folderem domowym. *Cały* ruch sieciowy z boxa przechodzi przez exit. Dotyczy to także menedżerów pakietów, gier i programów linkowanych statycznie, które ignorują ustawienia proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Profile przeglądarki, które korzystają z exitu.** Każdy profil uruchamia Camoufox, Firefoksa albo Tor Browser i ma własne dane |
| [**Moduły dostawców**](providers.md) | Moduły, które tworzą exity przez Tor, VPN (z gluetun), 9proxy albo Mysterium. Tor i Mysterium to szybki sposób na zdobycie dodatkowych adresów IP, przydatnych przy testach |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Jak exity pozostają rozdzielone { #how-it-stays-clean }

- **Gateway działa w trybie fail-closed.** Oznacza to, że awaria przerywa
  połączenie i nigdy nie otwiera ruchowi innej drogi. Zapora w gatewayu
  odrzuca wszystko, co nie jest adresowane do jego jedynego upstreamu. Jeśli
  gateway przestanie działać, wszystko, co z niego korzysta, traci połączenie.
  Żaden program nie musi zauważyć awarii i na nią zareagować, bo bez gatewaya
  po prostu nie ma trasy.
- **Działa tylko to, czego używasz.** Gateway uruchomiony przez box albo
  przeglądarkę jest usuwany, gdy tylko zatrzyma się ostatni box lub ostatnia
  przeglądarka, która z niego korzystała. Działać pozostają tylko exity, które
  uruchomisz samodzielnie poleceniem `kiwi-proxy up`.
- **Klienci są od siebie oddzieleni.** Boxy i przeglądarki korzystające z tego
  samego exitu współdzielą go, więc mają ten sam adres IP i tę samą sieciową
  przestrzeń nazw. Klienci, którzy nie mogą się nawzajem widzieć, dostają
  różne exity. Każdy box ma też własny folder domowy, więc klucze SSH i profile
  przeglądarki jednego klienta nie są dostępne w boxie innego klienta.
- **Bez uprawnień roota i bez tras na hoście.** Wszystko działa w rootless
  Podmanie, który uruchamia kontenery jako twój własny użytkownik. Sieć samego
  hosta pozostaje bez zmian.
- **Zapytania DNS też idą przez exit.** Domyślnie nazwy są rozwiązywane przez
  DNS over HTTPS (DoH) przez exit, a domeny reklamowe z list blokowania są odrzucane.
  Żeby rozwiązywać **wewnętrzne nazwy hostów** klienta, użyj zamiast tego
  `--dns remote`. Nazwy są wtedy przekazywane dalej i rozwiązywane
  po stronie klienta. Tego trybu wymagają też Tor i nazwy `.onion`.

## Ograniczenia { #limits }

Te ograniczenia podają same repozytoria:

- **Tylko TCP i tylko IPv4.** UDP nie jest przekazywane, więc QUIC i media
  WebRTC nie działają. Dla IPv6 nie ma trasy.
- **Jedna konfiguracja VPN na maszynę.** Moduł dostawcy VPN ma jedną
  konfigurację gluetun, z jednym plikiem `vpn.json` i jedną własną
  konfiguracją WireGuard. Jego exity różnią się tylko krajem serwera. Jeśli
  potrzebujesz jednocześnie własnych VPN-ów kilku klientów, obecnie da się to
  zrobić tylko przez osobny punkt końcowy SOCKS5 dla każdego klienta.
- **Box ogranicza sieć, ale nie jest piaskownicą.** Tak jak kontener
  distrobox, współdzieli twój ekran, magistralę sesji i schowek. Nie może
  jedynie łączyć się z siecią inaczej niż przez swój exit.
- **Mysterium:** jedna tożsamość może mieć naraz tylko jedno połączenie.

## Pierwsze kroki { #get-started }

Poniższe polecenia instalują aplikacje, zapisują proxy SOCKS5 jednego klienta
jako exit i otwierają powłokę w boxie z Fedorą, który korzysta z tego exitu:

```bash
kiwi install kiwi-custodia            # instaluje przy okazji kiwi-proxy
kiwi-custodia setup                   # obrazy i dane DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # powłoka, której jedyną drogą na zewnątrz jest SOCKS5 klienta A
```
