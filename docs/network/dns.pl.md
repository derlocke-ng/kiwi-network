# DNS, nazwy i certyfikaty

## Jeden łańcuch resolverów { #one-resolver-chain }

DNS to jeden łańcuch dla całej sieci:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Klienci VPN** (laptopy, telefony) pytają Pi-hole mastera pod `10.8.0.1`.
- **Pi-hole node'a** pyta najpierw Pi-hole mastera, więc sieć dzieli jedną
  listę blokowanych domen, a każde zapytanie wychodzi przez wyjście mastera.
  Quad9 (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) jest następny w ścisłej
  kolejności i odpowiada tylko wtedy, gdy master jest nieosiągalny.
- **Pi-hole mastera** przekazuje zapytania do resolvera DNS-over-TLS swojego
  klienta VPN (domyślnie Quad9, `dot_providers`).
- **Nazwy w domenie floty** są przekazywane do mastera i nigdy go nie
  opuszczają. Master oznacza domenę jako lokalną.

Każdy host stacka ma też nazwy floty w `/etc/hosts` (własne nazwy wskazują na
niego samego), więc kopie zapasowe i odnawianie certyfikatów działają bez
Pi-hole. Na Fedora CoreOS i uCore sam host rozwiązuje nazwy przez Pi-hole
własnego stacka.

**Sąsiedzi w tym samym LAN.** Pi-hole node'a i jego plik hosts odpowiadają
**adresem LAN** tych node'ów floty, które mają statyczny adres w jego własnej
podsieci, więc ruch między dwiema maszynami w tym samym pokoju zostaje w
pokoju. Master nadal odpowiada adresami w sieci mesh.

## Nazwy: `service.hostname.home` { #names-servicehostnamehome }

Każdy host to `<host>.<domain>` (`papaya.home`), a każda usługa, którą
uruchamia, to nazwa pod nim: `cloud.papaya.home`, `vault.papaya.home`,
`portainer.papaya.home`, `dl.lychee.home`, a na masterze `wg.sorbet.home`,
`pihole.sorbet.home`, `hub.sorbet.home`, `relay.sorbet.home`. Każda nazwa
ogłaszana przez moduł trafia do rekordów DNS floty pod **adresem hosta w sieci
mesh**. Każdy Pi-hole we flocie rozwiązuje każdą nazwę hosta i usługi
(split-horizon, `fleet_records`). Własne dodasz przez `extra_records`.

Domyślna domena to **`.home`**, bo ICANN nie przydzieli jej jako publicznej
domeny najwyższego poziomu. Nazwa z floty nigdy nie wycieknie do publicznego
rejestru i nikt inny nie może jej zarejestrować ani uzyskać dla niej
certyfikatu zaufanego przez przeglądarki. `.kiwi` to prawdziwa TLD i dlatego
flota od niej odeszła. kiwi-server sprawdza twój wybór: `home`, `corp`,
`mail`, `internal`, `arpa` i `test` przechodzą bez komentarza, `.local` jest
odrzucana (należy do mDNS), `.lan` daje ostrzeżenie (routery same na nią
odpowiadają), a publiczne TLD też dają ostrzeżenie.

Nazwy *spoza* domeny floty, dla publicznego huba lub przekaźnika, dostają
certyfikaty Let's Encrypt, gdy reverse proxy mastera jest publiczne.

## Proxy SOCKS5 Mullvad po nazwie { #mullvad-socks5-proxies-by-name }

Od kiwi-server 2.2.0 Pi-hole mastera odpowiada za każde **proxy SOCKS5
Mullvad**, zarówno jako `de-fra-wg-socks5-001.relays.mullvad.net`, jak i w
krótkiej formie `de-fra-001.mullvad.home`. gluetun odrzuca takie odpowiedzi z
prywatnych zakresów (ochrona przed DNS rebinding), więc bez tych rekordów nazwy
rozwiązywałyby się tylko przez resolvery zapasowe. Timer hosta
(`km-mullvad-socks.timer`, co 6 godzin) odświeża listę z
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Przyjmowane są z niej tylko nazwy `*.relays.mullvad.net` z adresami `10.x`,
więc lista nigdy nie może przekierować żadnej innej nazwy.

Jest to włączone w presecie mastera, którego wyjściem jest Mullvad. Wyłączysz
to przez `mullvad_socks: false` w bloku `dns:` mastera.

## Jeden CA dla floty { #one-ca-for-the-fleet }

Z `tls.auto: true` (domyślnie) kiwi-server prowadzi **jeden urząd
certyfikacji** dla floty w `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`,
RSA-4096, ważny 3650 dni), tworzony przy pierwszej potrzebie certyfikatu dla
hosta. Każdy host z reverse proxy dostaje certyfikat dla `<hostname>` i
`*.<hostname>` (825 dni, najdłuższy okres ważności, jaki przeglądarki jeszcze
akceptują, odnawiany, gdy zostaje mniej niż 30 dni), a każda maszyna zbudowana
przez kiwi-server instaluje CA w swoim magazynie zaufanych certyfikatów.

Ustaw **ograniczenia nazw** (name constraints), a CA będzie mógł podpisywać
tylko nazwy w domenie floty: `tls: { name_constraints: [home] }`. Przykładowa
flota to robi; wbudowane ustawienie domyślne to brak ograniczeń. Skradziony
`kiwiCA.key` jest wtedy bezwartościowy do czegokolwiek innego, co ma
znaczenie, bo ufa mu każda maszyna.

```bash
kiwi-server ca fleet.yaml        # pokaż CA floty
```

Zaimportuj `kiwiCA.pem` na swoich urządzeniach (przeglądarki, telefony), żeby
`https://cloud.papaya.home` był zaufany. Jeśli wolisz własne certyfikaty,
ustaw `tls_fullchain` i `tls_privkey` w module reverse-proxy.

!!! warning "Zachowaj `secrets/` w tajemnicy"
    `kiwiCA.key` podpisuje certyfikaty, którym ufa każda twoja maszyna. Trzymaj
    `secrets/` i `output/` poza gitem (`output/` jest już w `.gitignore`
    kiwi-server).
