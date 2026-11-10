# Moduły dostawców

Moduł dostawcy daje [kiwi-proxy](kiwi-proxy.md) wyjście, które tworzy sam,
zamiast SOCKS5, który ci przekazano. Każdy żyje we własnym repozytorium, instaluje
się przez kiwi-updater do katalogu modułów kiwi-proxy i jest zarządzany przez
kiwi-proxy: ten buduje obraz modułu, uruchamia go, gdy potrzebuje go wyjście,
i zamyka, gdy nie używa go już żaden gateway.

| Moduł | Repozytorium | Wydanie | Wyjście | Wymaga |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | sieć Tor, jeden obwód na wyjście, dowolny kraj wyjścia | niczego (za darmo) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | tunel WireGuard lub OpenVPN przez [gluetun](https://github.com/qdm12/gluetun) | subskrypcji VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | wyjście rezydencjalne [9proxy](https://9proxy.com/) | konta 9proxy i jego własnościowego klienta (nieredystrybuowanego) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | dVPN [Mysterium](https://mysterium.network/), z wyborem węzłów według kraju i typu IP | zarejestrowanej tożsamości konsumenta z saldem MYST |

Wszystkie cztery są na licencji GPL-3.0-or-later, są w
[katalogu Kiwi](../desktop/catalogs.md) i deklarują `DEPENDS=kiwi-proxy`, więc
kiwi najpierw instaluje kiwi-proxy. Tor i Mysterium to szybki sposób na więcej
adresów IP wyjścia, na przykład do testów.

## Instalacja i użycie { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # zbuduj jego obraz (kiwi-proxy setup robi wszystkie)
kiwi-proxy module list
kiwi-proxy module countries tor                  # gdzie Tor może wychodzić
kiwi-proxy add tor-de --module tor --country de  # wyjście z niego
kiwi-custodia new test --exit tor-de             # kontener na nim, albo:
kiwi-fox new test --exit tor-de                  # profil przeglądarki na nim
```

W przypadku Tora kraj jest utrzymywany przez `StrictNodes`, więc obwód raczej
zawiedzie, niż wyjdzie gdzie indziej. Wyjścia na module tor domyślnie
przepuszczają dane uwierzytelniające SOCKS dla poszczególnych witryn z Tor
Browser (`--socks-auth passthrough`).

## Jak to jest połączone { #how-it-is-wired }

**Każdy dostawca udostępnia SOCKS5 i nic więcej.** Kontener dostawcy
potrzebuje własnej drogi na zewnątrz, więc nie może żyć w przestrzeni nazw
gatewaya, gdzie odrzucane jest wszystko poza jednym celem. Spotykają się na
mostku Podmana bez roota, `kf-providers`, gdzie każdy moduł dostaje stały
adres:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** już mówi SOCKS5. kiwi-proxy wysyła dane uwierzytelniające dla
  każdego wyjścia, a `IsolateSOCKSAuth` Tora daje każdemu wyjściu własny
  obwód.
- **VPN i Mysterium** jadą tunelem, który nie mówi SOCKS5, więc mały adapter
  microsocks dołącza do przestrzeni nazw sieciowych tunelu i oferuje SOCKS5,
  który jedzie tym tunelem.
- **9proxy** uruchamia klienta 9proxy, który otwiera port SOCKS5 na wyjściu
  rezydencjalnym.

Jeden kontener dostawcy obsługuje każde wyjście na tym samym module i tej
samej dzierżawie. Tunel, który traci sesję, zamyka się bezpiecznie (fail
closed) i jest restartowany.

## Konfiguracja { #configuration }

Stan każdego modułu leży w `~/.local/share/kiwi-proxy/modules-state/<module>/`,
poza jakimkolwiek repozytorium:

- **vpn**: `vpn.json` z ustawieniami gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; każdy klucz wielkimi literami trafia do
  gluetun bez zmian), opcjonalna lista `leases` i opcjonalny katalog
  `gluetun/` (na przykład `wireguard.conf` dla dostawcy `custom` w gluetun).
  To jedna konfiguracja na maszynę: wyjścia na niej różnią się krajem serwera.
- **9proxy**: `config/account.conf`. Umieść własnościowego klienta w
  `module/containers/vendor/` wtyczki i dodaj `COPY vendor/ /opt/9proxy/` do jej
  `Containerfile` przed `kiwi-proxy module setup 9proxy`. Bez niego obraz się
  buduje, ale dostawca odmawia uruchomienia, zamiast otworzyć port.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase` albo *Configure…* w aplikacji Kiwi Proxy. Fraza dostępu
  staje się sekretem Podmana. Jedna tożsamość utrzymuje jedno połączenie naraz.

## Stan { #status }

Tor nie wymaga konta. Mysterium zweryfikowano od początku do końca
2026-11-07. Moduły VPN i 9proxy są kompletne i mają testy jednostkowe, ale nie
zostały uruchomione od początku do końca z prawdziwą subskrypcją lub kontem,
jak mówią ich README.
