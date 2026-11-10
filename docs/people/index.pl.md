# Huby, nie platformy

Sieć łączy twoje maszyny. **Huby** łączą ludzi. Hub to zestaw aplikacji
webowych (otwarty rynek, feed, czat, udostępnianie plików, wspólne listy,
menedżer haseł, kalendarz), które działają w całości w przeglądarce i
synchronizują się przez przekaźniki [nostr](https://nostr.com) wybrane przez
społeczność. Nie ma serwera kont ani backendu pośrodku, a wszystko, co
prywatne, jest szyfrowane na urządzeniu, zanim je opuści. Każdy może
prowadzić hub dla dowolnej społeczności. Zobacz
[aplikacje frameworka](apps.md).

Składają się na to trzy repozytoria:

| Repozytorium | Co to jest |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Silnik: tożsamość i konta, przekaźniki i synchronizacja, ludzie i udostępnianie, moderacja, zestaw projektowy, strony huba i dziesięć aplikacji. Sam nie dostarcza niczego, co użytkownik otwiera. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | Pierwsza **dystrybucja**: hub zbudowany na frameworku, z nazwą, domyślnymi przekaźnikami i wszystkimi dziesięcioma aplikacjami zamontowanymi pod własnymi nazwami. Szablon do sforkowania na własny hub. GPL-3.0-or-later. **Na żywo:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Katalog git hubów i ich aplikacji, w tym samym kształcie co desktopowy [kiwi-catalog](../desktop/catalogs.md) |

## Jak to się łączy { #how-it-fits-together }

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

## Pojęcia { #the-words }

- **Hub**: to, co daje dystrybucja. Pliki statyczne, więc hostowanie huba to
  serwowanie folderu. Każdy hub ma stronę startową, ustawienia i stronę konta.
- **Dystrybucja**: hub zbudowany na frameworku, z nazwą i wyglądem,
  domyślnymi przekaźnikami oraz wybranym zestawem aplikacji w wybranych
  przestrzeniach. Wszystko, co zmienia fork, leży w jednym pliku,
  `distribution.js`, plus jego tłumaczenia.
- **Aplikacja**: folder z manifestem, który podłącza się do dowolnej
  dystrybucji. Aplikacje rozmawiają tylko z publicznym API frameworka i nigdy
  nie dotykają bezpośrednio pamięci ani kluczy.
- **Przestrzeń** (space): nazwana społeczność z właścicielem, z własnymi
  moderatorami i opcjonalnie własnymi przekaźnikami (na wzór moderowanych
  społeczności NIP-72). Inny hub może serwować tę samą przestrzeń, podając jej
  adres.
- **Montowanie** (mount): kod aplikacji w przestrzeni, z własną nazwą,
  ścieżką i ikoną. Jedną aplikację można zamontować wiele razy. *Trading Post*
  w Armory to aplikacja `market` frameworka zamontowana w przestrzeni
  `tradingpost` Armory.

Dwie osoby w różnych dystrybucjach są znajomymi, udostępniają i czatują
dokładnie tak jak w jednej, bo tożsamość i dane to zdarzenia nostr, a nie
własność huba.

## Konta i klucze { #accounts-and-keys }

- Każde urządzenie dostaje klucz przy pierwszej wizycie, przechowywany w
  przeglądarce.
- **Konto** to nazwa użytkownika i hasło, zbudowane na zwykłych zdarzeniach
  nostr bez żadnego rejestru: hasło jest wzmacniane przez scrypt i odblokowuje
  twój klucz. Nikt nie może przejąć ani nadpisać konta bez hasła. **Nie ma
  resetu hasła**.
- Możesz też zalogować się istniejącym kluczem nostr (`nsec`, hex lub
  `ncryptsec`). Podpisywanie przez rozszerzenie przeglądarki i zdalne (NIP-07,
  NIP-46) jest zaplanowane, nie zbudowane.
- Jedno konto działa we wszystkich aplikacjach huba i na każdym urządzeniu,
  na którym się logujesz.

## Model prywatności { #privacy-model }

**Co jest szyfrowane.** Treść jest pieczętowana w przeglądarce, zanim
gdziekolwiek trafi: AES-256-GCM z kluczami wyprowadzanymi przez HKDF.
Prywatne wiadomości to wiadomości NIP-17 w opakowaniach prezentowych NIP-59
(gift wraps). Każdy plik dostaje losowy klucz AES-256-GCM, zanim trafi na
serwer multimediów, a zdjęcia są ponownie kodowane, co usuwa metadane
aparatu. Vault jest pieczętowany własną frazą dostępu (scrypt + AES-256-GCM).
Rozmowy idą z przeglądarki do przeglądarki, szyfrowane przez WebRTC.

**Najpierw lokalnie.** Każdy zapis trafia najpierw do własnej bazy danych
przeglądarki, potem do przekaźników. Odczyty pochodzą z urządzenia, więc
aplikacje działają offline. Gdy urządzenie znów się połączy, przywraca to, co
przekaźnik zapomniał: dane giną tylko wtedy, gdy zniknie każde urządzenie,
które je miało, *i* nie ma kopii zapasowej.

**Co widzą inni.** Repozytoria jasno mówią o ograniczeniach:

- Przekaźniki widzą metadane: kto pisze pod które adresy, kiedy, ile i z
  jakiego adresu IP. Jeśli to ma znaczenie, używaj VPN-a lub Tora.
- Klucz przestrzeni nie jest tajemnicą. Chroni posty społeczności przed
  odczytem na pierwszy rzut oka. Polubienia, zgłoszenia i to, kto co
  skomentował, są widoczne dla przekaźników.
- Notatki DevBoard i zgłoszenia moderacyjne są celowo publiczne.
- Twój klucz leży w pamięci przeglądarki. Wszystkie strony GitHub Pages
  jednego konta dzielą jeden origin, więc hub we własnej (sub)domenie to
  mocniejsza konfiguracja.
- Bezpośrednie transfery i rozmowy ujawniają adresy IP obu przeglądarek sobie
  nawzajem i serwerom STUN (domyślnie Google i Cloudflare; hub może ustawić
  własne).
- „Bez naszego serwera” oznacza: żadnego na ścieżce krytycznej. Aplikacje
  nadal korzystają z przekaźników, serwerów multimediów i, w przypadku
  kalendarza, z serwera CalDAV, które wybierasz ty lub twój hub.

## Moderacja { #moderation }

Trzy warstwy: twoja własna lista blokowanych (zaszyfrowana, tylko ty możesz ją
odczytać), zgłoszenia (publiczne, podpisane) i własna polityka przekaźników.
Przestrzeń ma moderatorów. Zgłoszenie moderatora od razu zwija post. W
przeciwnym razie potrzeba trzech zgłoszeń od osób, które nie są zablokowane.
Posty mogą być oznaczone jako 18+ lub jako reklama i te widzą tylko osoby z
kontem.

## Czytaj dalej { #read-on }

- [Armory i jego aplikacje](armory.md)
- [Własny hub](hubs.md)
- Dokumentacja samego frameworka: [architektura](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  i [protokół](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
