# Aplikacje frameworka

kiwi-framework dostarcza swoje aplikacje pod prostymi nazwami. Dystrybucja je
**montuje**, w przestrzeni i pod własną nazwą. Jedną aplikację można zamontować
wiele razy: bank nasion i sklep z kamieniami to ten sam kod `market` w dwóch
przestrzeniach, każda z własnymi moderatorami i przekaźnikami, jako dwa
kafelki w jednym hubie.

| Aplikacja | Co to jest | Armory montuje ją jako |
|---|---|---|
| `market` | **Otwarty rynek** dla społeczności, której służy montowanie. Ogłoszenia mają zdjęcia, cenę, miejsce, skąd i dokąd jest wysyłka, albo odbiór osobisty. Kupujący znajdują je według kategorii i według tego, gdzie są, przez etykiety wyszukiwania, które przekaźniki mogą dopasować, ale nie mogą odczytać. Kupujący piszą do sprzedawcy na czacie, z gotowym szkicem wiadomości o ogłoszeniu. Ogłoszenia można rezerwować, oznaczać jako sprzedane, odnawiać i zgłaszać, a wygasają po 30 do 90 dniach. Montowanie może wymagać, żeby sprzedawcy najpierw pokazali się w feedzie albo zostali zatwierdzeni przez moderatora | Trading Post |
| `feed` | **Feed społeczności**: wpisy ze zdjęciami, hashtagami, polubieniami i komentarzami dla przestrzeni, dla znajomych, dla kręgu albo tylko dla ciebie, a także dzienniki (seria wpisów z okładką). Wpisy można oznaczyć jako 18+ lub jako reklamę | Outpost |
| `chat` | **Wiadomości**: prywatne wiadomości i pliki do znajomych (NIP-17), grupy, które trwają, dopóki ich gospodarz ich nie zamknie, pokoje na żywo, które znikają, gdy opustoszeją, odpowiedzi, reakcje, edycje, przypięcia, wyszukiwanie na urządzeniu, znikające wiadomości oraz rozmowy głosowe i wideo dla maksymalnie sześciu osób | Uplink |
| `notices` | **Tablica ogłoszeń** z podpisanymi, publicznymi notatkami z proof of work, głosami, zgłoszeniami i datą wygaśnięcia | DevBoard |
| `boards` | **Wspólne listy i notatki**: listy kontrolne, inwentarze z liczbami i notatki w Markdown, szyfrowane end-to-end, z linkami do edycji lub tylko do odczytu | Loadout |
| `payload` | **Udostępnianie plików**: link, który czeka zaszyfrowany na twoich serwerach multimediów; pliki do znajomych i grup; albo prosto z przeglądarki do przeglądarki | Payload |
| `vault` | **Menedżer haseł**: logowania, notatki, karty, kody dwuskładnikowe, generator i raport kondycji, klucze SSH, CA SSH, CA X.509 i certyfikaty TLS. Zapieczętowany własną frazą dostępu | Vault |
| `authenticator` | **Kody dwuskładnikowe** (TOTP), przechowywane w tym samym zapieczętowanym sejfie | Authenticator |
| `calendar` | **Twoje kalendarze** z Nextcloud lub dowolnego serwera CalDAV. Nic nie trafia do przekaźników | Calendar |
| `pong` | **Pong dla dwóch graczy** między przeglądarkami | pongjs |

Każdy hub ma też stronę startową, ustawienia (twoje konto i urządzenia,
znajomi i kręgi, zablokowane osoby, przekaźniki, przestrzenie, serwery
multimediów, kopie zapasowe) i stronę konta. Powiadomienia działają w samym
hubie.

## Przestrzenie i montowania { #spaces-and-mounts }

- **Przestrzeń** to nazwana społeczność z właścicielem: id, klucz
  właściciela, nazwa, moderatorzy, własne przekaźniki i flaga treści dla
  dorosłych. Jest wzorowana na moderowanych społecznościach nostr (NIP-72),
  więc inne klienty nostr mogą ją odczytać. Każdy post i każde ogłoszenie
  należy do dokładnie jednej przestrzeni.
- **Montowanie** to kod aplikacji w przestrzeni, z własnym id, nazwą i ikoną.
  Zaimportowanie sklepu innej społeczności to jedna linia montowania.
- **Linki wskazują aplikację, przestrzeń i element, nigdy hosta.** Hub
  otwiera link własnym montowaniem tej aplikacji i przestrzeni. Jeśli go nie
  ma, mówi, czyja to przestrzeń, i proponuje drogę powrotną.
- **Przestrzenie są sfederowane.** Dwa huby mogą serwować tę samą przestrzeń,
  a przekaźniki przestrzeni przenoszą tylko jej treść.

Zaplanowane: huby ogłaszające się podpisanym manifestem, żeby inni mogli je
znaleźć, zatwierdzenia moderacyjne i obserwowanie przestrzeni, których hub
danej osoby nie dostarcza.

## Pisanie aplikacji { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

To tworzy szkielet aplikacji React na zestawie UI frameworka, z powłoką,
stroną główną i stroną ustawień, tekstami w każdym języku, wpisem w rejestrze
i montowaniem. Aplikacje rozmawiają z frameworkiem tylko przez jego publiczne
API i nigdy nie dotykają bezpośrednio pamięci ani kluczy. Zobacz
[Własny hub](hubs.md).
