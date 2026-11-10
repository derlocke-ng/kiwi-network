# Huby, nie platformy

**kiwi-framework** to oprogramowanie, dzięki któremu każda społeczność może
prowadzić własny **hub**. Hub to strona internetowa z zestawem aplikacji dla
członków społeczności: otwartym rynkiem, kanałem, czatem, udostępnianiem
plików, wspólnymi listami, menedżerem haseł i kalendarzem. Hub może uruchomić
każdy i dla dowolnej społeczności, a ta nie zależy wtedy od centralnej
platformy, która trzyma konta i dane wszystkich.

Aplikacje działają w całości w przeglądarce. Synchronizują się przez
przekaźniki [nostr](https://nostr.com), czyli serwery, które przechowują
podpisane wiadomości i przekazują je dalej. O tym, z których przekaźników
korzysta hub, decyduje społeczność. Między przeglądarką a przekaźnikami nie ma
serwera kont ani żadnego backendu, a wszystko, co prywatne, jest szyfrowane na
urządzeniu przed wysłaniem. Pozostałe części Kiwi Network łączą twoje maszyny.
Huby łączą ludzi. Poszczególne aplikacje opisuje strona
[Aplikacje frameworka](apps.md).

Armory to pierwszy hub zbudowany na tym frameworku. To jeden przykład, a zarazem
szablon, który inne społeczności kopiują, żeby zbudować własny hub.

Oprogramowanie mieści się w trzech repozytoriach:

| Repozytorium | Czym jest |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Ogólne oprogramowanie, z którego powstaje każdy hub. Zawiera tożsamość i konta, przekaźniki i synchronizację, znajomych i udostępnianie, moderację, zestaw komponentów interfejsu, strony huba oraz dziesięć aplikacji. Samego frameworka nie da się otworzyć jako strony internetowej. Hub powstaje z niego dopiero w dystrybucji. Aktualna wersja to v0.32.1, a licencja to GPL-3.0-or-later. |
| [**Armory**](armory.md) | Pierwsza **dystrybucja**, czyli konkretny hub zbudowany na frameworku. Dokłada nazwę, domyślne przekaźniki i wszystkie dziesięć aplikacji, każdą pod własną nazwą. To szablon, który forkujesz, żeby zrobić własny hub. Licencja: GPL-3.0-or-later. **Działa pod adresem:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Katalog, czyli repozytorium git z listą hubów i ich aplikacji. Ma ten sam format co [kiwi-catalog](../desktop/catalogs.md) dla desktopu. |

## Jak to się składa w całość { #how-it-fits-together }

Schemat pokazuje, jak z frameworka powstaje hub w twojej przeglądarce i z jakimi
serwerami przeglądarka potem się łączy.

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Pojęcia używane na tej stronie { #the-words }

- **Hub**: strona internetowa, z której korzysta społeczność. Hub powstaje,
  gdy zbudujesz dystrybucję. Składa się wyłącznie z plików statycznych, więc
  jego hosting sprowadza się do udostępnienia folderu z plikami. Każdy hub ma
  stronę startową, stronę ustawień i stronę konta.
- **Dystrybucja**: framework razem z decyzjami, które robią z niego jeden
  konkretny hub. Są to nazwa i wygląd, domyślne przekaźniki oraz wybrany zestaw
  aplikacji w wybranych przestrzeniach. Gdy forkujesz dystrybucję, wszystko, co
  zmieniasz, znajduje się w jednym pliku `distribution.js` i w jego
  tłumaczeniach.
- **Aplikacja**: folder z plikiem manifestu. Można ją dodać do dowolnej
  dystrybucji. Aplikacje korzystają wyłącznie z publicznego API frameworka
  i nigdy nie sięgają bezpośrednio do pamięci przeglądarki ani do kluczy.
- **Przestrzeń**: społeczność, która ma nazwę, właściciela, własnych
  moderatorów i, jeśli chce, własne przekaźniki. Wzorem są moderowane
  społeczności nostr (NIP-72). Inny hub może obsługiwać tę samą przestrzeń,
  jeśli poda jej adres.
- **Mount**: jedna aplikacja używana w jednej przestrzeni. Każdy mount ma
  własną nazwę, własną ścieżkę (adres wewnątrz huba) i własną ikonę. Tę samą
  aplikację można zamontować wiele razy. Na przykład *Trading Post* w Armory to
  aplikacja `market` z frameworka zamontowana w przestrzeni `tradingpost`
  należącej do Armory.

Dwie osoby, które korzystają z hubów z różnych dystrybucji, mogą być znajomymi,
udostępniać sobie rzeczy i rozmawiać na czacie dokładnie tak, jakby korzystały
z tego samego huba. Jest to możliwe, bo tożsamość i dane każdej osoby to
zdarzenia nostr, czyli podpisane wiadomości przechowywane na przekaźnikach,
i nie należą do żadnego huba.

## Konta i klucze { #accounts-and-keys }

- Gdy pierwszy raz otwierasz hub na jakimś urządzeniu, przeglądarka tworzy dla
  tego urządzenia klucz i go zapisuje.
- **Konto** to nazwa użytkownika i hasło. Opiera się na zwykłych zdarzeniach
  nostr i nie istnieje żaden rejestr kont. Twoje hasło jest przetwarzane
  funkcją scrypt, która celowo liczy się długo, a jej wynik odblokowuje twój
  klucz. Bez hasła nikt nie przejmie konta ani go nie nadpisze. **Hasła nie da
  się zresetować.**
- Możesz też zalogować się kluczem nostr, który już masz, podanym jako `nsec`,
  w zapisie szesnastkowym albo jako `ncryptsec`. Logowanie przez rozszerzenie
  przeglądarki (NIP-07) lub zdalny program podpisujący (NIP-46) jest planowane,
  ale jeszcze niezrealizowane.
- Jedno konto działa we wszystkich aplikacjach huba i na każdym urządzeniu, na
  którym się zalogujesz.

## Model prywatności { #privacy-model }

**Co jest szyfrowane.** Przeglądarka szyfruje treści, zanim je dokądkolwiek
wyśle. Używa do tego AES-256-GCM z kluczami wyprowadzanymi przez HKDF.
Wiadomości prywatne to wiadomości NIP-17 zapakowane w gift wrap NIP-59. Gift
wrap jest drugą warstwą szyfrowania, dzięki której przekaźnik widzi tylko tyle,
że jakiś klucz dostał zapakowaną wiadomość. Każdy plik jest przed wysłaniem na
serwer multimediów szyfrowany własnym, losowym kluczem AES-256-GCM. Zdjęcia są
najpierw kodowane na nowo, co usuwa metadane dodawane przez aparaty. Vault jest
szyfrowany osobną frazą dostępu (scrypt + AES-256-GCM). Rozmowy głosowe i wideo
biegną bezpośrednio z przeglądarki do przeglądarki i szyfruje je WebRTC.

**Najpierw lokalnie.** Wszystko, co piszesz, trafia najpierw do własnej bazy
danych przeglądarki, a dopiero potem do przekaźników. Aplikacje czytają z tej
bazy na urządzeniu, więc działają także offline. Gdy urządzenie odzyska
połączenie, wysyła przekaźnikowi wszystkie dane, których ten już nie ma. Dane
przepadają więc tylko wtedy, gdy zniknie każde urządzenie, które je miało,
*a do tego* nie ma kopii zapasowej.

**Co widzą inni.** Ograniczenia opisują same repozytoria:

- Przekaźniki widzą metadane: kto pisze pod jakie adresy, kiedy, ile i z jakiego
  adresu IP. Jeśli ma to dla ciebie znaczenie, korzystaj z VPN-u albo Tora.
- Klucz przestrzeni nie jest tajemnicą. Sprawia jedynie, że wpisów społeczności
  nie da się czytać całkiem otwarcie. Przekaźniki widzą polubienia, zgłoszenia
  i to, kto co skomentował.
- Notki w DevBoard i zgłoszenia do moderacji są z założenia publiczne.
- Twój klucz jest przechowywany w pamięci przeglądarki. Wszystkie strony GitHub
  Pages jednego konta mają wspólny origin, a przeglądarki rozdzielają pamięć
  stron właśnie według originu. Hub pod własną domeną lub subdomeną jest więc
  bezpieczniejszym rozwiązaniem.
- Przy bezpośrednim przesyłaniu plików i w trakcie rozmowy obie przeglądarki
  poznają nawzajem swoje adresy IP. Oba adresy widzą też serwery STUN, które
  pomagają zestawić połączenie. Domyślnie są to serwery STUN firm Google
  i Cloudflare. Hub może ustawić własne.
- „Bez naszego serwera” oznacza, że aplikacje nie zależą od żadnego serwera
  prowadzonego przez projekt. Nadal korzystają jednak z przekaźników, serwerów
  multimediów, a w przypadku kalendarza także z serwera CalDAV. Które to będą
  serwery, wybierasz ty albo twój hub.

## Moderacja { #moderation }

Moderacja ma trzy warstwy. Pierwsza to twoja własna lista zablokowanych,
zaszyfrowana tak, że tylko ty możesz ją odczytać. Druga to zgłoszenia, które są
publiczne i podpisane. Trzecia to zasady poszczególnych przekaźników.

Każda przestrzeń ma moderatorów. Wpis zgłoszony przez moderatora jest od razu
zwijany. W pozostałych przypadkach wpis zostaje zwinięty po trzech zgłoszeniach
od osób, które nie są zablokowane. Wpis można oznaczyć jako 18+ albo jako
reklamę, a oznaczone wpisy widzą tylko osoby, które mają konto.

## Czytaj dalej { #read-on }

- [Armory i jego aplikacje](armory.md)
- [Własny hub](hubs.md)
- Dokumentacja samego frameworka: [architektura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  i [protokół komunikacji](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
