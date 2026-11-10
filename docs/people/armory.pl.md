# Armory

Armory to pierwszy hub zbudowany na kiwi-framework, czyli oprogramowaniu,
dzięki któremu każda społeczność może prowadzić własny hub. W języku frameworka
Armory jest **dystrybucją**: frameworkiem razem z nazwą, domyślnymi
przekaźnikami i wybranym zestawem aplikacji. Armory zawiera wszystkie dziesięć
aplikacji frameworka i nadaje im własne nazwy. Rynek i kanał są tu przygotowane
dla hodowców konopi. To wybór tego jednego huba, a nie frameworka, i inna
społeczność użyłaby tych samych aplikacji do własnego tematu. Z Armory możesz
korzystać bez zmian albo skopiować je jako szablon własnego huba.

Każde narzędzie działa w całości w twojej przeglądarce. Narzędzia
synchronizują się przez przekaźniki, czyli serwery, które przechowują twoje
dane i przekazują je dalej, a to ty wybierasz, z których przekaźników
korzystasz. Nie musisz się rejestrować, projekt nie prowadzi dla Armory
żadnego własnego serwera i nic cię nie śledzi. Wszystko jest szyfrowane, zanim
opuści twoje urządzenie. Ze strony startowej możesz zainstalować Armory jako
aplikację webową.

- **Otwórz:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repozytorium to [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  a licencja to GPL-3.0-or-later.
- Armory jest dystrybucją [kiwi-framework](index.md) 0.32.1 i przypina jego
  wersję do commita. Samo Armory nie ma jeszcze tagów wydań.
- Jest dostępne po angielsku, niemiecku, francusku, hiszpańsku, włosku,
  niderlandzku, polsku i portugalsku.

Dawniej Armory nazywało się weaponized.js.

## Narzędzia { #the-tools }

| Narzędzie | Do czego służy |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Wspólne listy zakupów i zadań, domowe inwentarze i notatki w Markdownie. Są takie same na wszystkich twoich urządzeniach i u osób, którym je udostępnisz. Wszystko jest szyfrowane end-to-end, a listę udostępniasz linkiem, który pozwala edytować albo tylko przeglądać. Loadout działa offline, a twoje urządzenia odsyłają do przekaźników wszystko, co przekaźniki utraciły. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Wiadomości i pliki dla znajomych (NIP-17, szyfrowane na twoim urządzeniu). Grupa istnieje, dopóki jej gospodarz jej nie zamknie. Do pokoju na żywo może wejść każdy, kto ma link, a pokój znika, gdy wyjdzie z niego ostatnia osoba. Uplink ma odpowiedzi, reakcje, edycję, przypinanie, wyszukiwanie na urządzeniu i znikające wiadomości. Rozmowy głosowe i wideo działają dla maksymalnie sześciu osób. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Udostępnianie plików na trzy sposoby. Możesz utworzyć link do plików, które pozostają zaszyfrowane na twoich serwerach multimediów, dopóki ich nie usuniesz. Możesz wysłać pliki znajomym i grupom w Uplink. Możesz też przesłać pliki bezpośrednio ze swojej przeglądarki do przeglądarki drugiej osoby i wtedy nie są nigdzie przechowywane. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Menedżer haseł dla loginów, notatek, kart płatniczych i kodów dwuskładnikowych, dostępny na każdym urządzeniu, na którym się zalogujesz. Ma generator haseł i raport kondycji. Raport wskazuje hasła słabe, używane wielokrotnie i stare, a jeśli włączysz tę kontrolę, także hasła, które wyciekły. Vault importuje i eksportuje wpisy. Zarządza też kluczami SSH, urzędem certyfikacji SSH, urzędem certyfikacji X.509 i certyfikatami TLS. Jest zaszyfrowany osobną frazą dostępu. Nie wpisuje za ciebie haseł na stronach internetowych. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Kody dwuskładnikowe (TOTP) do twoich kont w innych serwisach. Konto dodajesz z kodu QR, z linku lub sekretu albo z eksportu z Google Authenticator. Kody są przechowywane w tym samym zaszyfrowanym sejfie, z którego korzysta Vault. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Twoje kalendarze z własnego Nextclouda lub dowolnego innego serwera CalDAV. Pokazuje najbliższe dni albo cały miesiąc, obsługuje wydarzenia cykliczne i przypomina o wydarzeniach, o ile otwarta jest któraś ze stron. Nic nie trafia do przekaźników, a dane logowania do twojego serwera są przechowywane w postaci zaszyfrowanej na twoim koncie. Twój serwer musi przyjmować żądania z originu Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Kanał Armory, używany do relacji i dzienników z uprawy. Publikujesz wpisy ze zdjęciami, tydzień po tygodniu. Każdy wpis może być dla wszystkich w Outpost, dla twoich znajomych, dla jednego kręgu znajomych albo tylko dla ciebie. Wpisy mogą mieć hashtagi, polubienia i komentarze. Wpisy są szyfrowane na twoim urządzeniu, podobnie jak zdjęcia. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Rynek Armory, przeznaczony do handlu konopiami: nasionami, sadzonkami i sprzętem. Ogłoszenia mają zdjęcia, a kupujący znajdują je według kategorii i miejsc, do których sprzedawca wysyła. „Napisz do sprzedawcy” otwiera Uplink. Do korzystania z Trading Post potrzebujesz konta, a weryfikacji wieku nie ma. Zanim ktoś zacznie sprzedawać, musi coś opublikować w Outpost (trzy wpisy, każdy polubiony przez trzy osoby) albo zostać zatwierdzony przez moderatora. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Tablica ogłoszeń dla freelancerów. Publikujesz notkę, że szukasz ludzi do pracy albo że możesz przyjąć zlecenie. Każda notka jest podpisana twoim kluczem i wymaga proof of work, czyli niewielkiego obliczenia, które sprawia, że masowe publikowanie dużo kosztuje. Inni mogą na notkę głosować. Notka znika, gdy wygaśnie, czyli po czasie od 24 godzin do 30 dni od publikacji. Wszystkie notki są z założenia publiczne. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro Pong dla dwóch graczy w dwóch przeglądarkach. Żeby zacząć grę, udostępnij link lub kod QR albo wybierz jedną z otwartych gier. Możesz też trenować offline z komputerem. |

Planowany jest blog.

Każde narzędzie to jedna z aplikacji frameworka pod nazwą nadaną przez Armory.
Loadout to aplikacja `boards` z frameworka, Uplink to `chat`, Outpost to
`feed`, Trading Post to `market`, DevBoard to `notices`, a pongjs to `pong`.

## Jedno konto we wszystkich narzędziach { #one-account-every-tool }

Logujesz się albo zakładasz konto na stronie startowej, nazwą użytkownika
i hasłem albo kluczem nostr. Potem z tego konta korzysta każde narzędzie.
Listy, które utworzysz na urządzeniu przed zalogowaniem, przechodzą na konto.
Jeśli nie używasz konta, każde urządzenie działa z własnym kluczem.

Strona ustawień dotyczy całego huba. Obejmuje twoje konto i urządzenia,
znajomych i kręgi, zablokowane osoby, przekaźniki, przestrzenie i serwery
multimediów, powiadomienia oraz zaszyfrowane kopie zapasowe.

## Przekaźniki i serwery multimediów { #relays-and-media-servers }

Domyślne przekaźniki Armory to `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` i `wss://relay.primal.net`. Serwery multimediów przechowują
pliki, które wysyłasz, i korzystają z protokołu o nazwie Blossom. Domyślne
serwery multimediów Armory to `nostr.download`, `blossom.yakihonne.com`,
`blossom.band` (który przyjmuje tylko zdjęcia) i `blossom.primal.net`. Własne
przekaźniki i serwery multimediów możesz wybrać w ustawieniach.

Przekaźniki przechowują dane i przekazują je dalej, ale nie mogą odczytać
niczego, co zostało zaszyfrowane przed wysłaniem. Co przekaźniki jednak widzą,
opisuje [model prywatności](index.md#privacy-model).

## Moderacja { #moderation }

Moderatorzy Armory odpowiadają za Outpost, Trading Post i DevBoard. Wpis
w Outpost można oznaczyć jako 18+ albo jako reklamę. Oznaczenie może ustawić
autor, moderator albo dwa zgłoszenia. Oznaczone wpisy widzą tylko osoby, które
mają konto.

## Własne Armory { #your-own-armory }

Armory jest też szablonem dla twojego własnego huba. Zrób fork repozytorium
albo użyj go jako szablonu, zmień plik `distribution.js` i tłumaczenia,
a potem opublikuj wynik. Poszczególne kroki opisuje strona
[Własny hub](hubs.md).
