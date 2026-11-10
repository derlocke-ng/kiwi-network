# Praca z wieloma sieciami klientów

Dziesięciu zdalnych klientów to często dziesięć VPN-ów lub punktów końcowych
SOCKS, po jednym do sieci każdego klienta. Uruchamianie ich wszystkich na
hoście to bałagan: dziesięć tuneli naraz, trasy, które się gryzą, i jedna sieć
przeciekająca do następnej. Aplikacje desktopowe Kiwi dają zamiast tego
każdemu z nich **zapieczętowane wyjście**: kontener, którego jedyną trasą jest
ten jeden upstream. Twoje narzędzia dołączają do potrzebnego wyjścia, a poza
tym nic na hoście się nie zmienia.

| Aplikacja | Co robi |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Silnik. **Wyjście** (exit) to jeden upstream o nazwie: SOCKS5, który ci przekazano, albo taki, który tworzy moduł dostawcy. Uruchomienie go tworzy **gateway**, przestrzeń nazw sieciowych, której jedyną trasą jest ten upstream. Aplikacje hosta mogą go używać jako lokalnego portu SOCKS5 |
| [**kiwi-custodia**](kiwi-custodia.md) | **Kontenery dystrybucji na wyjściu**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky lub Alpine w kontenerze bez roota z własnym katalogiem domowym. *Wszystko* w kontenerze wychodzi przez wyjście: menedżery pakietów, gry, statyczne pliki binarne, które nigdy nie słyszały o proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Profile przeglądarki na wyjściu**: Camoufox, Firefox lub Tor Browser, każdy profil z własną pamięcią |
| [**Moduły dostawców**](providers.md) | Wyjścia z Tora, VPN-a (gluetun), 9proxy lub Mysterium. Tor i Mysterium to szybki sposób na więcej adresów IP wyjścia, przydatny do testów |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Jak zachowuje się czystość { #how-it-stays-clean }

- **Fail closed.** Zapora gatewaya odrzuca wszystko poza jego jednym
  upstreamem. Jeśli gateway padnie, to, co do niego dołączyło, traci trasę.
  Kill switch to brak trasy, a nie oprogramowanie, które musi coś zauważyć.
- **Nic nieużywanego nie działa.** Gateway uruchomiony przez kontener lub
  przeglądarkę znika, gdy odejdzie ostatni z nich. Działać zostają tylko
  wyjścia, które uruchomisz przez `kiwi-proxy up`.
- **Co osobne, zostaje osobne.** Rzeczy na tym samym wyjściu je dzielą (jeden
  IP, jedna przestrzeń nazw). Klienci, którzy nie mogą się spotkać, dostają
  różne wyjścia, a każdy kontener ma własny katalog domowy, więc klucze SSH i
  profile przeglądarki się nie mieszają.
- **Bez roota, bez tras na hoście.** Wszystko działa w Podmanie bez roota, a
  własna sieć hosta pozostaje nietknięta.
- **DNS też idzie przez wyjście.** Domyślnie nazwy są rozwiązywane przez DoH
  przez wyjście, z listami blokującymi reklamy. Dla **wewnętrznych nazw hostów**
  klienta przekaż zamiast tego nazwy stronie klienta przez `--dns remote`
  (to także tryb dla Tora i nazw `.onion`).

## Ograniczenia { #limits }

Pochodzą z repozytoriów:

- **Tylko TCP, tylko IPv4.** UDP nigdzie nie wychodzi (bez QUIC, bez mediów
  WebRTC), a IPv6 nie dostaje trasy.
- **Jedna konfiguracja VPN na maszynę.** Moduł dostawcy VPN trzyma jedną
  konfigurację gluetun (jeden `vpn.json`, jedną własną konfigurację
  WireGuard), a jego wyjścia różnią się tylko krajem serwera. Dla własnych
  VPN-ów kilku klientów obok siebie drogą jest dziś punkt końcowy SOCKS5 dla
  każdego klienta.
- **Kontener to areszt sieciowy, a nie piaskownica.** Dzieli twój ekran,
  magistralę sesji i schowek, jak distrobox. Nie może natomiast dotrzeć do
  sieci inaczej niż przez swoje wyjście.
- **Mysterium:** jedna tożsamość utrzymuje jedno połączenie naraz.

## Pierwsze kroki { #get-started }

```bash
kiwi install kiwi-custodia            # przynosi ze sobą kiwi-proxy
kiwi-custodia setup                   # obrazy i dane DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
