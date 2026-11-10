# kiwi-proxy

Zapieczętowane wyjścia SOCKS5 i VPN w Podmanie bez roota, dla przeglądarek,
narzędzi testowych, aplikacji hosta i maszyn kiwi-server.

- Repozytorium: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Najnowsze wydanie: **v0.7.3**. Jest w [katalogu Kiwi](../desktop/catalogs.md), zakres użytkownika.
- CLI (`kiwi-proxy`), aplikacja GTK4 (**Kiwi Proxy**) i jednostki użytkownika
  systemd. To silnik proxy, który wcześniej był częścią kiwi-fox, wydzielony,
  żeby obsługiwał więcej niż jedną aplikację.

**Wyjście** (exit) to jeden upstream o nazwie: SOCKS5, który ci przekazano, albo
taki, który tworzy [moduł dostawcy](providers.md) (Tor, tunel VPN, 9proxy,
Mysterium). Wyjście to tylko dane. Uruchomienie go tworzy **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Cokolwiek dołącza do przestrzeni nazw gatewaya (przeglądarka kiwi-fox,
kontener kiwi-custodia, kontener z narzędziem), nie ma żadnej trasy poza tym
upstreamem. Jeśli gateway padnie, jego członkowie tracą trasę.

## Instalacja { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox i kiwi-custodia przynoszą go ze sobą
kiwi-proxy setup             # obraz gatewaya, dane DNS, obrazy modułów dostawców
```

Potrzebuje Podmana bez roota, Pythona 3.12+ z pydantic oraz GTK4 + libadwaita
dla aplikacji. Hasła trafiają do pęku kluczy pulpitu (`secret-tool`) albo do
plików 0600 na maszynie, która go nie ma.

## Użycie { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # wyjście; nic jeszcze nie działa
kiwi-proxy add tor-de --module tor --country de        # wyjście z modułu dostawcy
kiwi-proxy list
kiwi-proxy check client-a      # co świat przez nie widzi
kiwi-proxy up client-a         # uruchom jego gateway i utrzymuj go
kiwi-proxy down client-a       # zamknij go razem ze wszystkimi, którzy dołączyli
kiwi-proxy ps                  # działające gatewaye, niezależnie od tego, która aplikacja je uruchomiła
kiwi-proxy reap                # zamknij gatewaye, których nikt nie używa
kiwi-proxy-gui                 # "Kiwi Proxy" in the app grid
```

Punkty końcowe to `socks5://user:pass@host:port`, `http://…`, `https://…` lub
format dostawcy `host:port:user:pass`. `kiwi-proxy test ENDPOINT` sonduje
jeden, niczego nie tworząc.

### Wyjścia dla aplikacji hosta { #exits-for-host-applications }

Każdy program na hoście może używać wyjścia przez opublikowany port SOCKS5,
jeden port na wyjście:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Port domyślnie nasłuchuje na `127.0.0.1`. Inny adres wymaga nazwy użytkownika
(`--expose-user`) albo jawnego `--expose-open`.
`systemctl --user enable --now kiwi-proxy@NAME` utrzymuje wyjście od
zalogowania.

### DNS { #dns }

- **Tryb resolvera** (domyślny): dnscrypt-proxy rozwiązuje nazwy przez DoH
  przez wyjście (Google, Cloudflare, Quad9 lub Mullvad jako upstream), z
  listami blokującymi (OISD) odświeżanymi codziennie.
- **Tryb zdalny** (`--dns remote`): nazwy trafiają do samego upstreamu, dla
  Tora i nazw `.onion`. Listy blokujące nadal obowiązują.

### Zasady gatewaya { #rules-of-the-gateway }

- UDP nigdzie nie wychodzi: bez QUIC, bez mediów WebRTC, bez DNS w czystym
  tekście.
- Dla świata wyjście to IPv4. Nazwa bez adresu IPv4 jest odrzucana.
- Gateway uruchomiony przez konsumenta znika, gdy odejdzie jego ostatni
  członek. Uruchomiony przez `kiwi-proxy up` zostaje do `kiwi-proxy down`.
- Jedno wyjście, jeden gateway, dowolna liczba członków. Członkowie, którzy
  muszą pozostać osobno, używają różnych wyjść.

## Aplikacja { #the-app }

**Kiwi Proxy** dodaje i edytuje wyjścia (SOCKS5, który ci przekazano, albo moduł
dostawcy, z przeszukiwalną listą krajów lub wyborem węzłów), uruchamia je i
zatrzymuje, udostępnia jedno jako port SOCKS5 na tym komputerze i kopiuje jego
adres, sprawdza, co widzi świat, pokazuje, kto dołączył do gatewaya, i jego
logi, a także instaluje i konfiguruje moduły dostawców.

## Na maszynie kiwi-server { #on-a-kiwi-server-machine }

kiwi-proxy zawiera też moduł kiwi-server, który hostuje wyjścia dla całej
sieci mesh (jeden gateway na wyjście, opublikowany pod adresem hosta w sieci
mesh). Nie ma go jeszcze w drzewie kiwi-server i nie działał na żadnej
maszynie, jak mówi jego dokumentacja. Moduły dostawców to mechanizm
desktopowy i tam nie działają.

Dalsza lektura: [architektura](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[konsumenci](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[system wtyczek](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
