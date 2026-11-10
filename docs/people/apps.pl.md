# Aplikacje frameworka

kiwi-framework to oprogramowanie, dzięki któremu społeczność może prowadzić
własny hub. Ta strona opisuje dziesięć aplikacji, które są w nim dostępne.
Są wśród nich otwarty rynek, kanał społeczności, czat i udostępnianie plików.

Framework nadaje swoim aplikacjom proste nazwy, takie jak `market`.
Dystrybucja, czyli konkretny hub zbudowany na frameworku, **montuje**
aplikacje, których potrzebuje. Zamontować aplikację to znaczy użyć jej w jednej
przestrzeni (społeczności z własnymi moderatorami i przekaźnikami) i nadać jej
nazwę wybraną przez hub. Tę samą aplikację można zamontować wiele razy. Bank
nasion i sklep z kamieniami szlachetnymi mogą być na przykład tym samym kodem
`market` w dwóch przestrzeniach. Każdy z nich ma wtedy własnych moderatorów
i przekaźniki, a w hubie pojawiają się jako dwa osobne kafelki.

| Aplikacja | Czym jest | W Armory nazywa się |
|---|---|---|
| `market` | **Otwarty rynek** dla społeczności, którą obsługuje dany mount. Ogłoszenie ma zdjęcia, cenę oraz miejsca, z których i do których sprzedawca wysyła, albo informację o odbiorze osobistym. Kupujący znajdują ogłoszenia według kategorii i własnej lokalizacji. Wyszukiwanie korzysta z etykiet, które przekaźniki potrafią dopasować, ale nie potrafią odczytać. Kupujący pisze do sprzedawcy na czacie, gdzie czeka już szkic wiadomości o ogłoszeniu. Ogłoszenie można zarezerwować, oznaczyć jako sprzedane, odnowić i zgłosić, a po 30–90 dniach wygasa. Mount może wymagać, żeby sprzedawca był wcześniej aktywny w kanale albo został zatwierdzony przez moderatora. | Trading Post |
| `feed` | **Kanał społeczności.** Publikujesz wpisy ze zdjęciami i hashtagami, a inni mogą je polubić i komentować. Wpis może być dla całej przestrzeni, dla twoich znajomych, dla jednego kręgu (grupy twoich znajomych) albo tylko dla ciebie. Dziennik to seria wpisów z okładką. Wpisy można oznaczyć jako 18+ albo jako reklamę. | Outpost |
| `chat` | **Wiadomości.** Wysyłasz znajomym prywatne wiadomości i pliki (NIP-17). Grupa istnieje, dopóki jej gospodarz jej nie zamknie, a pokój na żywo znika, gdy wyjdzie z niego ostatnia osoba. Czat ma odpowiedzi, reakcje, edycję, przypinanie, wyszukiwanie na urządzeniu i znikające wiadomości. Rozmowy głosowe i wideo działają dla maksymalnie sześciu osób. | Uplink |
| `notices` | **Tablica ogłoszeń** z publicznymi notkami. Każda notka jest podpisana przez autora i wymaga proof of work, czyli niewielkiego obliczenia, które sprawia, że masowe publikowanie dużo kosztuje. Na notki można głosować i je zgłaszać, a po pewnym czasie wygasają. | DevBoard |
| `boards` | **Wspólne listy i notatki.** Są to listy kontrolne, inwentarze z liczbą sztuk i notatki w Markdownie. Są szyfrowane end-to-end, a udostępniasz je linkami, które pozwalają edytować albo tylko przeglądać. | Loadout |
| `payload` | **Udostępnianie plików** na trzy sposoby: jako link do plików przechowywanych w postaci zaszyfrowanej na twoich serwerach multimediów, jako pliki wysłane znajomym i grupom albo bezpośrednio z jednej przeglądarki do drugiej. | Payload |
| `vault` | **Menedżer haseł** dla loginów, notatek, kart płatniczych i kodów dwuskładnikowych. Ma generator haseł i raport kondycji. Zarządza też kluczami SSH, urzędem certyfikacji SSH, urzędem certyfikacji X.509 i certyfikatami TLS. Jest zaszyfrowany osobną frazą dostępu. | Vault |
| `authenticator` | **Kody dwuskładnikowe** (TOTP). Są przechowywane w tym samym zaszyfrowanym sejfie co wpisy menedżera haseł. | Authenticator |
| `calendar` | **Twoje kalendarze** z Nextclouda lub dowolnego innego serwera CalDAV. Nic nie trafia do przekaźników. | Calendar |
| `pong` | **Pong dla dwóch graczy** grających w dwóch przeglądarkach. | pongjs |

Każdy hub ma ponadto stronę startową, stronę konta i stronę ustawień.
W ustawieniach są twoje konto i urządzenia, znajomi i kręgi, zablokowane osoby,
przekaźniki, przestrzenie, serwery multimediów i kopie zapasowe. Powiadomienia
nie są osobną aplikacją, tylko częścią samego huba.

## Przestrzenie i mounty { #spaces-and-mounts }

- **Przestrzeń** to społeczność z nazwą i właścicielem. Ma id, klucz
  właściciela, nazwę, moderatorów, własne przekaźniki i oznaczenie, czy jest
  przeznaczona dla dorosłych. Wzorem są moderowane społeczności nostr (NIP-72),
  więc mogą ją odczytać także inne klienty nostr. Każdy wpis i każde ogłoszenie
  należy do dokładnie jednej przestrzeni.
- **Mount** to jedna aplikacja używana w jednej przestrzeni, z własnym id,
  nazwą i ikoną. Żeby dodać do swojego huba sklep innej społeczności,
  dopisujesz jeden wiersz, który definiuje mount.
- **Link wskazuje aplikację, przestrzeń i element, ale nigdy hosta.** Hub
  otwiera taki link we własnym mouncie tej aplikacji i tej przestrzeni. Jeśli
  takiego mountu nie ma, hub informuje, czyja to przestrzeń, i proponuje powrót.
- **Przestrzenie są sfederowane**, to znaczy, że przestrzeń nie jest
  przywiązana do jednego huba. Tę samą przestrzeń mogą obsługiwać dwa huby.
  Przekaźniki przestrzeni przenoszą wyłącznie treści tej przestrzeni.

Trzy rzeczy są planowane, ale jeszcze niezrealizowane. Huby będą ogłaszać swoje
istnienie podpisanym manifestem, żeby inni mogli je znaleźć. Moderacja zyska
zatwierdzanie wpisów. Będzie też można obserwować przestrzeń, której twój hub
nie zawiera.

## Pisanie aplikacji { #writing-an-app }

To polecenie tworzy w twojej dystrybucji szkielet nowej aplikacji:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Powstaje aplikacja React korzystająca z zestawu komponentów interfejsu
frameworka. Ma ramę (obudowę wokół stron aplikacji), stronę główną i stronę
ustawień, teksty we wszystkich językach, wpis w rejestrze aplikacji oraz mount.
Aplikacje korzystają wyłącznie z publicznego API frameworka i nigdy nie sięgają
bezpośrednio do pamięci przeglądarki ani do kluczy. Jak zbudować i opublikować
hub, wyjaśnia strona [Własny hub](hubs.md).
