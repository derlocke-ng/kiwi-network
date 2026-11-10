# Moduły dostawców

W [kiwi-proxy](kiwi-proxy.md) exit to zapisane pod nazwą połączenie
z upstreamem, przez które twoje boxy i przeglądarki wysyłają ruch. Zwykle jest
to połączenie, które ci przekazano, np. proxy SOCKS5 prowadzące do sieci
klienta. Moduł dostawcy służy do drugiej sytuacji: tworzy exit samodzielnie,
korzystając z Tora, subskrypcji VPN, 9proxy albo Mysterium. Zwłaszcza Tor i Mysterium służą do
tego, żeby mieć więcej adresów IP do testów.

Każdy moduł ma własne repozytorium. kiwi-updater instaluje go do folderu
modułów kiwi-proxy, a od tej chwili zarządza nim kiwi-proxy. kiwi-proxy buduje
obraz kontenera modułu, uruchamia moduł, gdy potrzebuje go jakiś exit,
i zatrzymuje go, gdy nie korzysta z niego już żaden gateway. Gateway to
kontener, który kiwi-proxy uruchamia dla exitu, dopóki exit działa.

| Moduł | Repozytorium | Wydanie | Exit | Wymaga |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | sieć Tor, z jednym obwodem na każdy exit i dowolnym krajem węzła wyjściowego | niczego (jest bezpłatny) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | tunel WireGuard albo OpenVPN przez [gluetun](https://github.com/qdm12/gluetun) | subskrypcji VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | adres domowy (residential) z [9proxy](https://9proxy.com/) | konta 9proxy i własnościowego klienta 9proxy, który nie jest rozpowszechniany |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | dVPN [Mysterium](https://mysterium.network/) (zdecentralizowany VPN), z listą węzłów do wyboru według kraju i rodzaju adresu IP | zarejestrowanej tożsamości konsumenta z saldem MYST |

Wszystkie cztery moduły są na licencji GPL-3.0-or-later i znajdują się
w [katalogu Kiwi](../desktop/catalogs.md). Każdy deklaruje
`DEPENDS=kiwi-proxy`, więc kiwi-updater najpierw instaluje kiwi-proxy. Tor
i Mysterium to szybki sposób na zdobycie dodatkowych adresów IP exitów, np. do
testów.

## Instalacja i używanie { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # buduje jego obraz (kiwi-proxy setup buduje wszystkie)
kiwi-proxy module list
kiwi-proxy module countries tor                  # w jakich krajach Tor może wychodzić
kiwi-proxy add tor-de --module tor --country de  # exit z tego modułu
kiwi-custodia new test --exit tor-de             # box na nim albo:
kiwi-fox new test --exit tor-de                  # profil przeglądarki na nim
```

W przypadku exitu przez Tor kraj jest wymuszany opcją Tora `StrictNodes`.
Jeśli nie da się zbudować obwodu z węzłem wyjściowym w tym kraju, połączenie
kończy się błędem. Ruch nigdy nie wychodzi przez inny kraj. Exity z modułu tor przekazują dalej dane logowania
SOCKS, które Tor Browser wysyła osobno dla każdej strony. Takie jest ich
ustawienie domyślne (`--socks-auth passthrough`).

## Jak dostawca łączy się z gatewayem { #how-it-is-wired }

**Każdy dostawca oferuje SOCKS5 i nic poza tym.** Kontener dostawcy potrzebuje
własnego połączenia z internetem. Nie może więc działać w sieciowej
przestrzeni nazw (network namespace) gatewaya, bo tam odrzucany jest cały ruch
poza ruchem do jednego celu. Zamiast tego dostawca i gateway są połączone
przez sieć mostkową rootless Podmana, `kf-providers`, w której każdy moduł ma
stały adres:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** sam oferuje SOCKS5. kiwi-proxy wysyła osobne dane logowania dla
  każdego exitu, a opcja Tora `IsolateSOCKSAuth` daje wtedy każdemu exitowi
  własny obwód, czyli własną drogę przez sieć Tor.
- **VPN i Mysterium** korzystają z tunelu, a tunel nie oferuje SOCKS5. Dlatego
  do sieciowej przestrzeni nazw tunelu dołącza mały adapter, microsocks.
  Oferuje on SOCKS5 i wysyła ruch przez tunel.
- **9proxy** uruchamia klienta 9proxy, który otwiera port SOCKS5 prowadzący do
  adresu domowego.

Jeden kontener dostawcy obsługuje wszystkie exity korzystające z tego samego
modułu i tej samej dzierżawy (lease). Dzierżawa to jeden z exitów do wyboru,
które oferuje moduł, np. kraj serwera VPN albo węzeł Mysterium. Jeśli tunel
straci sesję, obowiązuje zasada fail-closed: żaden ruch nie wychodzi, a tunel
jest uruchamiany ponownie.

## Konfiguracja { #configuration }

Stan każdego modułu jest przechowywany w
`~/.local/share/kiwi-proxy/modules-state/<module>/`, poza jakimkolwiek
repozytorium:

- **vpn**: Plik `vpn.json` zawiera ustawienia gluetun, np.
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` i `WIREGUARD_ADDRESSES`. Każdy klucz
  zapisany wielkimi literami jest przekazywany do gluetun bez zmian. Plik może
  też zawierać listę `leases`. Opcjonalny folder `gluetun/` zawiera dodatkowe
  pliki, np. `wireguard.conf` dla dostawcy `custom` w gluetun. Na maszynę
  przypada jedna taka konfiguracja, a exity na niej różnią się krajem serwera.
- **9proxy**: Plik konfiguracyjny to `config/account.conf`. Własnościowy
  klient nie jest dołączony. Zanim uruchomisz
  `kiwi-proxy module setup 9proxy`, umieść klienta w folderze
  `module/containers/vendor/` wtyczki i dopisz `COPY vendor/ /opt/9proxy/` do
  jej pliku `Containerfile`. Bez klienta obraz i tak się zbuduje, ale dostawca
  odmówi uruchomienia i nie otworzy portu.
- **mysterium**: Uruchom `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase` albo użyj opcji *Configure…* w aplikacji Kiwi Proxy. Fraza
  dostępu jest przechowywana jako sekret Podmana. Jedna tożsamość może mieć
  naraz tylko jedno połączenie.

## Stan { #status }

Tor nie wymaga konta. Moduł Mysterium został sprawdzony w pełnym przebiegu,
od początku do końca, 7 listopada 2026 roku. Według ich plików README moduły
VPN i 9proxy są kompletne i mają testy jednostkowe, ale nie były jeszcze
uruchamiane w pełnym przebiegu z prawdziwą subskrypcją lub kontem.
