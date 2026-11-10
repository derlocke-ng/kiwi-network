# DNS, nazwy i certyfikaty

Każda maszyna i każda usługa w Kiwi Network ma nazwę, na przykład
`cloud.papaya.home`, i otwierasz ją przez HTTPS z certyfikatem, któremu ufają
twoje urządzenia. Na tej stronie znajdziesz opis tego, jak w sieci
rozwiązywane są nazwy, jak są zbudowane i skąd biorą się certyfikaty. Serwerami
DNS są Pi-hole’e, które przy okazji blokują niechciane domeny według wspólnej
listy blokowania.

## Jeden łańcuch serwerów DNS { #one-resolver-chain }

Wszystkie zapytania DNS w sieci przechodzą przez ten sam łańcuch serwerów DNS:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Klienci VPN** (laptopy, telefony) wysyłają zapytania do Pi-hole’a mastera
  pod adresem `10.8.0.1`.
- **Pi-hole node’a** pyta najpierw Pi-hole’a mastera. Dzięki temu cała sieć
  korzysta z jednej listy blokowania, a każde zapytanie trafia do internetu
  przez wyjście mastera, czyli jego połączenie z internetem. Następny w ściśle
  ustalonej kolejności jest Quad9 (`9.9.9.9`, `149.112.112.112`, ustawiany
  przez `fallback_dns`), więc odpowiada tylko wtedy, gdy master jest
  niedostępny.
- **Pi-hole mastera** przekazuje zapytania do serwera DNS-over-TLS swojego
  klienta VPN. Domyślnie jest nim Quad9 (`dot_providers`).
- **Nazwy w domenie twojej sieci** trafiają do mastera i nie są przekazywane
  dalej. Master oznacza tę domenę jako lokalną.

Każda maszyna, na której działa stack, ma też nazwy z całej sieci w pliku
`/etc/hosts`, przy czym jej własne nazwy wskazują na nią samą. Kopie zapasowe
i odnawianie certyfikatów działają więc także bez Pi-hole’a. Na Fedora CoreOS
i uCore sama maszyna używa do rozwiązywania nazw Pi-hole’a z własnego stacku.

**Sąsiedzi w tej samej sieci lokalnej.** Jeśli inne node’y z pliku fleet mają
stały adres w podsieci danego node’a, Pi-hole i plik hosts tego node’a podają
ich **adres w sieci lokalnej**. Ruch między dwiema maszynami w tej samej sieci
lokalnej nie opuszcza jej wtedy. Master nadal odpowiada adresami w sieci mesh.

## Nazwy: `service.hostname.home` { #names-servicehostnamehome }

Każdy host ma nazwę `<host>.<domain>`, na przykład `papaya.home`. Każda
usługa, która na nim działa, dostaje nazwę pod nazwą hosta: `cloud.papaya.home`,
`vault.papaya.home`, `portainer.papaya.home`, `dl.lychee.home`, a na masterze
`wg.sorbet.home`, `pihole.sorbet.home`, `hub.sorbet.home`,
`relay.sorbet.home`. Każda nazwa zgłoszona przez moduł trafia do rekordów DNS
sieci z **adresem hosta w sieci mesh** (mesh to prywatna sieć WireGuard,
do której należą wszystkie twoje maszyny). Każdy Pi-hole w sieci rozwiązuje
każdą nazwę hosta i każdą nazwę usługi. Odpowiada za to ustawienie
`fleet_records`, a sama technika nazywa się split-horizon DNS, bo na te nazwy
odpowiada się tylko wewnątrz twojej sieci. Własne rekordy dodasz w
`extra_records`.

Domyślna domena to **`.home`**. Wybrano ją, bo ICANN nie przydzieli jej jako
publicznej domeny najwyższego poziomu (TLD). Nazwa z twojej sieci nie trafi
więc nigdy do publicznego rejestru i nikt inny nie zarejestruje jej ani nie
dostanie dla niej certyfikatu, któremu ufałyby przeglądarki. `.kiwi` to
natomiast prawdziwa domena TLD i dlatego Kiwi Network już jej nie używa.
kiwi-server sprawdza wybraną przez ciebie domenę. `home`, `corp`, `mail`,
`internal`, `arpa` i `test` przyjmuje bez uwag. `.local` odrzuca, bo należy do
mDNS. Przy `.lan` wyświetla ostrzeżenie, bo routery same odpowiadają na tę
domenę, i tak samo ostrzega przy publicznych domenach TLD.

Nazwy *spoza* domeny twojej sieci, potrzebne dla publicznego huba albo
przekaźnika, dostają certyfikaty Let’s Encrypt, jeśli reverse proxy mastera
jest publiczne.

## Proxy SOCKS5 Mullvada po nazwie { #mullvad-socks5-proxies-by-name }

Proxy SOCKS5 Mullvada mają adresy z prywatnego zakresu, a ta funkcja pozwala
korzystać z nich po nazwie. Od wersji kiwi-server 2.2.0 Pi-hole mastera zna
każde **proxy SOCKS5 Mullvada**, zarówno pod pełną nazwą, np.
`de-fra-wg-socks5-001.relays.mullvad.net`, jak i pod krótką, np.
`de-fra-001.mullvad.home`. gluetun odrzuca odpowiedzi DNS wskazujące na adresy
prywatne, bo tak chroni się przed atakiem DNS rebinding. Bez tych rekordów
nazwy dałoby się więc rozwiązać tylko przez zapasowe serwery DNS. Timer na
hoście (`km-mullvad-socks.timer`, co 6 godzin) odświeża listę z
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Z tej listy przyjmowane są wyłącznie nazwy `*.relays.mullvad.net` z adresami
`10.x`, więc lista nie może przekierować żadnej innej nazwy.

Funkcja jest włączona w presecie mastera, bo wyjście w tym presecie prowadzi
przez Mullvada. Żeby ją wyłączyć, ustaw `mullvad_socks: false` w bloku `dns:`
mastera.

## Jeden urząd certyfikacji dla całej sieci { #one-ca-for-the-fleet }

Urząd certyfikacji (CA) podpisuje certyfikaty, których twoje usługi używają do
HTTPS. Przy `tls.auto: true`, czyli domyślnie, kiwi-server prowadzi **jeden
urząd certyfikacji** dla całej sieci w `secrets/ca/`. CA składa się z plików
`kiwiCA.key` i `kiwiCA.pem`, używa RSA-4096 i jest ważny przez 3650 dni.
kiwi-server tworzy go wtedy, gdy któryś host po raz pierwszy potrzebuje
certyfikatu. Każdy host z reverse proxy dostaje certyfikat dla `<hostname>`
i `*.<hostname>`. Taki certyfikat jest ważny 825 dni, bo to najdłuższy okres,
jaki przeglądarki jeszcze akceptują, i jest odnawiany, gdy do końca zostaje
mniej niż 30 dni. Każda maszyna zbudowana przez kiwi-server instaluje CA
w swoim magazynie zaufanych certyfikatów.

Jeśli ustawisz **ograniczenia nazw** (name constraints), CA może podpisywać
tylko nazwy w domenie twojej sieci: `tls: { name_constraints: [home] }`.
Przykładowy plik fleet to ustawia, ale wbudowana wartość domyślna nie ma
żadnego ograniczenia. Z ograniczeniem skradziony `kiwiCA.key` jest
bezużyteczny dla wszystkich innych nazw. Ma to znaczenie, bo CA ufa każda
twoja maszyna.

```bash
kiwi-server ca fleet.yaml        # pokaż CA sieci
```

Zaimportuj `kiwiCA.pem` na swoich urządzeniach (w przeglądarkach, na
telefonach), żeby ufały `https://cloud.papaya.home`. Jeśli wolisz własne
certyfikaty, ustaw `tls_fullchain` i `tls_privkey` w module reverse-proxy.

!!! warning "Nie udostępniaj nikomu `secrets/`"
    `kiwiCA.key` podpisuje certyfikaty, którym ufa każda twoja maszyna.
    Nie wrzucaj `secrets/` ani `output/` do gita (`output/` jest już w pliku
    `.gitignore` narzędzia kiwi-server).
