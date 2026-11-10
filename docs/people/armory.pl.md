# Armory

**Narzędzia webowe peer-to-peer, uzbrojone w nostr.** Każde narzędzie działa
w całości w twojej przeglądarce i synchronizuje się przez przekaźniki, które
wybierasz. Bez rejestracji, bez naszego serwera, bez śledzenia, a wszystko
jest szyfrowane, zanim opuści twoje urządzenie. Zainstaluj je jako aplikację
webową ze strony startowej.

- **Otwórz:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repozytorium: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Dystrybucja [kiwi-framework](index.md) 0.32.1 (przypięta commitem). Nie ma
  jeszcze tagów wydań.
- Po angielsku, niemiecku, francusku, hiszpańsku, włosku, niderlandzku,
  polsku i portugalsku.

Armory nazywał się wcześniej weaponized.js.

## Narzędzia { #the-tools }

| Narzędzie | Co robi |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Wspólne listy zakupów i zadań, domowe inwentarze i notatki w Markdown na wszystkich twoich urządzeniach i z każdym, komu je udostępnisz. Szyfrowane end-to-end, z linkami do edycji lub tylko do odczytu. Działa offline, a twoje urządzenia przywracają to, co przekaźniki zapomną. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Wiadomości i pliki do znajomych (NIP-17, zapieczętowane na twoim urządzeniu), grupy, które trwają, dopóki ich gospodarz ich nie zamknie, i pokoje na żywo dla każdego z linkiem, znikające, gdy opustoszeją. Odpowiedzi, reakcje, edycje, przypięcia, wyszukiwanie na urządzeniu, znikające wiadomości oraz rozmowy głosowe i wideo dla maksymalnie sześciu osób. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Udostępnianie plików: link, który czeka zaszyfrowany na twoich serwerach multimediów, dopóki go nie usuniesz; pliki do znajomych i grup w Uplink; albo prosto z twojej przeglądarki do ich, nigdzie nie przechowywane. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Menedżer haseł: logowania, notatki, karty i kody dwuskładnikowe na każdym urządzeniu, na którym się logujesz. Generator, raport kondycji (hasła słabe, powtórzone, stare i, jeśli to włączysz, ujawnione w wyciekach), import i eksport, klucze SSH, urząd certyfikacji SSH, CA X.509 i certyfikaty TLS. Zapieczętowany własną frazą dostępu. Bez autouzupełniania. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Kody dwuskładnikowe (TOTP) do twoich kont gdzie indziej: dodaj konto z kodu QR, linku lub sekretu albo z eksportu Google Authenticator. Przechowywane w tym samym zapieczętowanym sejfie. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Twoje kalendarze z własnego Nextcloud lub dowolnego serwera CalDAV: najbliższe dni albo miesiąc, powtarzające się wydarzenia, przypomnienia, gdy strona jest otwarta. Nic nie trafia do przekaźników; logowanie jest zapieczętowane na twoim koncie. Twój serwer musi zezwalać na origin Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Raporty i dzienniki uprawy: wpisy ze zdjęciami, tydzień po tygodniu, dla wszystkich w Outpost, znajomych, kręgu albo tylko ciebie. Hashtagi, polubienia i komentarze. Zapieczętowane na twoim urządzeniu, zdjęcia zaszyfrowane. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Rynek konopny: nasiona, sadzonki i sprzęt ze zdjęciami, wyszukiwane według kategorii i tego, dokąd idzie wysyłka. „Message seller” otwiera Uplink. Dla osób z kontem (bez weryfikacji wieku). Sprzedawcy muszą najpierw pokazać się w Outpost (trzy posty, każdy polubiony przez trzy osoby) albo zostać zatwierdzeni przez moderatora. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Tablica ogłoszeń dla freelancerów: napisz, że szukasz ludzi albo jesteś dostępny – podpisane twoim kluczem, poparte proof of work, oceniane głosami, znika po wygaśnięciu (od 24 godzin do 30 dni). Celowo publiczna. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro Pong dla dwóch graczy między dwiema przeglądarkami. Udostępnij link lub kod QR albo wybierz otwartą grę, albo ćwicz offline z komputerem. |

Blog jest zaplanowany.

Każde narzędzie to jedna z aplikacji frameworka, zamontowana pod nazwą
Armory: Loadout to `boards`, Uplink `chat`, Outpost `feed`, Trading Post
`market`, DevBoard `notices`, pongjs `pong`.

## Jedno konto, każde narzędzie { #one-account-every-tool }

Zaloguj się lub załóż konto na stronie startowej (nazwa użytkownika i hasło
albo klucz nostr), a każde narzędzie będzie go używać. Listy utworzone na
urządzeniu przed zalogowaniem są przenoszone. Bez konta każde urządzenie
używa własnego klucza.

Strona ustawień obejmuje cały hub: twoje konto i urządzenia, znajomych i
kręgi, zablokowane osoby, przekaźniki, przestrzenie i serwery multimediów,
powiadomienia oraz zaszyfrowane kopie zapasowe.

## Przekaźniki i serwery multimediów { #relays-and-media-servers }

Domyślne przekaźniki Armory to `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` i `wss://relay.primal.net`. Domyślne serwery multimediów
(Blossom) to `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (tylko
zdjęcia) i `blossom.primal.net`. Własne wybierzesz w ustawieniach.

Przekaźniki przekazują dane, ale nie mogą odczytać tego, co wcześniej
zaszyfrowano. [Model prywatności](index.md#privacy-model) wymienia, co mogą
zobaczyć.

## Moderacja { #moderation }

Moderatorzy Armory moderują Outpost, Trading Post i DevBoard. Wpisy w Outpost
może oznaczyć jako 18+ lub jako reklamę ich autor, dwa zgłoszenia albo
moderator. Takie wpisy widzą tylko osoby z kontem.

## Własny Armory { #your-own-armory }

Armory to szablon dla twojego własnego huba. Sforkuj go (albo użyj jako
szablonu), zmień `distribution.js` i tłumaczenia, a potem go opublikuj.
Zobacz [Własny hub](hubs.md).
