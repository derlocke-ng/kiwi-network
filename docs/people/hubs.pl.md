# Własny hub

Ta strona wyjaśnia, jak uruchomić hub dla własnej społeczności. Hub to strona
internetowa, którą społeczność dostaje dzięki kiwi-framework: otwarty rynek,
kanał, czat i inne aplikacje działające w przeglądarce. Hub składa się
wyłącznie z plików statycznych, więc do jego hostingu wystarczy udostępnić
folder z plikami przez HTTPS. Możesz to zrobić na trzy sposoby:

- **Korzystaj z Armory bez żadnych zmian.** Armory to pierwszy hub zbudowany
  na frameworku. Jest otwarte dla wszystkich pod adresem
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Zrób własną dystrybucję.** Dystrybucja to framework z twoją nazwą, twoimi
  przekaźnikami i twoim wyborem aplikacji. Możesz ją opublikować na dowolnym
  hostingu plików statycznych.
- **Uruchom kontener huba.** Możesz to zrobić na przykład we własnej sieci
  Kiwi Network, razem z własnym przekaźnikiem. Powstaje wtedy prywatny hub,
  dostępny wyłącznie z sieci mesh, czyli prywatnej sieci, do której należą
  twoje maszyny.

## Rodzaje hubów { #kinds-of-hub }

| Rodzaj | Jak działa | Przykład |
|---|---|---|
| **Publiczny** | Hub korzysta z publicznych przekaźników i każdy może go otworzyć. | Armory |
| **Prywatny** | Przekaźników huba nie da się podmienić (`policy.relays: 'locked'`), a strony czekają, aż któryś z nich odpowie (`requireHub`). Przekaźniki znajdują się wewnątrz VPN-u. | hub firmy na jej kiwi-masterze |
| **Półpubliczny** | Prywatny hub, który ma też strefę publiczną. Wybrane aplikacje, na przykład czat, korzystają w niej z publicznych przekaźników. | |

Przekaźniki huba tworzą osobne sieci: własną sieć huba, strefę publiczną oraz
sieci jego przestrzeni. Każde zdarzenie, czyli podpisana wiadomość nostr,
należy do jednej z tych sieci i nigdy nie trafia do innej.

## Własna dystrybucja { #your-own-distribution }

Zacznij od Armory, które służy za szablon. Przycisk *Use this template* na
GitHubie tworzy kopię repozytorium bez jego historii. Potem wykonaj te kroki:

1. Zmień plik **`distribution.js`**. Ustawia on id, nazwę, znak graficzny,
   opis, stronę domową, repozytorium, przekaźniki, serwery multimediów,
   przestrzenie, aplikacje i mounty. Jeśli twój hub ma obsługiwać także
   przestrzenie Armory, skopiuj ich `owner` i `id` z pliku `hub.json` w Armory.
2. Zmień pliki **`locales/*.json`**. Zawierają tytuł, tekst wprowadzający
   i stopkę oraz po jednym tekście karty dla każdego mountu. Gdy brakuje
   tłumaczenia, używany jest angielski.
3. Zaktualizuj **`kiwi.manifest`**. Jeśli chcesz, dodaj też swój hub do
   katalogu [kiwi-web-catalog](#kiwi-web-catalog).
4. Na GitHubie wybierz *Settings → Pages → Source: GitHub Actions*, a potem
   wypchnij zmiany.

Podczas pracy nad dystrybucją przydają się te polecenia:

```bash
npm install
npm run dev                  # hub z hot reloadem, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # lokalny przekaźnik testowy pod adresem ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # szkielet nowej aplikacji
```

Wersję kiwi-framework przypnij do commita albo tagu, nigdy do gałęzi. Podczas
budowania sprawdzany jest twój plik `distribution.js`. Na przykład hub
z publicznym mountem musi mieć publiczne przekaźniki, a hub z publicznymi
przekaźnikami musi mieć publiczny mount.

Wszystko, co widać w przeglądarce, jest napisane w TypeScripcie z Reactem 19
i budowane narzędziem Vite. Warstwa danych w `shared/` to zwykły JavaScript
z typami JSDoc. Testy uruchamia test runner wbudowany w Node.js, a te, które
potrzebują przeglądarki, działają w Playwright.

## Kontener huba { #the-hub-container }

Armory jest też dostępne jako obraz kontenera `ghcr.io/derlocke-ng/armory`.
Obraz powstaje z pliku `container/Dockerfile` z frameworka i serwuje hub przez
nginx. Przy starcie kontenera skrypt entrypoint zapisuje plik `hub.local.json`
na podstawie zmiennych `HUB_*`, a strona wczytuje ten plik, zanim nawiąże
jakiekolwiek połączenie. W ten sposób przy wdrożeniu można wybrać przekaźniki
i zasady, ale nie da się dodać kodu. Jeśli nie ustawisz żadnej zmiennej, hub
działa tak, jak został zbudowany.

Ten przykład uruchamia hub z własnym przekaźnikiem, którego nie da się
podmienić, i z jednym mountem korzystającym z przekaźnika publicznego:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Zmienna | Znaczenie |
|---|---|
| `HUB_RELAYS` | Własne przekaźniki huba. |
| `HUB_PUBLIC_RELAYS` | Przekaźniki strefy publicznej. Jeśli zmienna jest ustawiona, ale pusta, strefy publicznej nie ma. |
| `HUB_DIRECTORY_RELAYS` | Przekaźniki, na których publikuje się i wyszukuje listy przekaźników. |
| `HUB_RELAYS_LOCKED` | Przy wartości `true` nikt nie może podmienić przekaźników huba. |
| `HUB_REQUIRE_HUB` | Przy wartości `true` strony czekają tak długo, jak długo nie odpowiada żaden z przekaźników huba. |
| `HUB_PUBLIC_MOUNTS` | Mounty korzystające ze strefy publicznej, podane przez id. |
| `HUB_ACCOUNT_MOUNTS` | Mounty, które wymagają konta. |
| `HUB_REQUIRE_ACCOUNT` | Przy wartości `true` konta wymaga każdy mount. |
| `HUB_SPACE_RELAYS` | Przekaźniki poszczególnych przestrzeni, w zapisie `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | Klucze osób, które moderują każdą przestrzeń zdefiniowaną przez hub. |
| `HUB_REGISTER_POW` | Liczba bitów proof of work, których wymaga założenie konta. Służy przekaźnikom, które przyjmują wyłącznie członków. |
| `HUB_CALDAV` | Serwer Nextcloud. nginx przekazuje do niego ścieżkę `/remote.php/dav/`, więc kalendarz obywa się bez CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | Serwery STUN/TURN dla rozmów i bezpośredniego przesyłania plików. Pomagają dwóm przeglądarkom połączyć się ze sobą. Login do serwera TURN da się odczytać ze strony, dlatego załóż taki, którego używa tylko ten hub. |

Zmienna `HUB_USER_MOUNTS` jest odczytywana, ale na razie niczego nie zmienia.
Należy do funkcji, która dopiero powstanie: obserwowania przestrzeni, której
hub nie zawiera.

Hub musi być serwowany przez HTTPS, bo WebCrypto wymaga bezpiecznego kontekstu.
Jego przekaźniki muszą być dostępne przez `wss://`. Jeśli ktoś otworzy hub
przez zwykłe `http://` pod adresem innym niż localhost, strona poinformuje
o tym i przerwie działanie.

### Hub we własnej sieci Kiwi Network { #on-a-kiwi-network }

Kiwi-master to jedyny serwer sieci Kiwi Network, który jest dostępny
z internetu. Może uruchamiać własny przekaźnik i własny hub, a odpowiadają za to
dwa moduły. Moduł `nostr-relay` uruchamia przekaźnik strfry pod adresem
`relay.<host>`. Moduł `hub` uruchamia opisany wyżej obraz kontenera, domyślnie
z Armory, pod adresem `hub.<host>`.

Oba są domyślnie prywatne. Są dostępne tylko z sieci mesh i korzystają
z certyfikatu twojej sieci. Żeby hub był półpubliczny, dodaj `public_relays`
i `public_mounts`. Żeby był publiczny, dodaj `reverse-proxy.public`, a hub
dostanie certyfikaty Let's Encrypt.

Przekaźnik publicznego huba przyjmuje wpisy z sieci mesh. Z internetu przyjmuje
je tylko od członków, którzy udowodnią, że mają swój klucz (NIP-42). Członkami
są osoby z listy, którą podpisują administratorzy (`write_pubkeys`). Przy
ustawieniu `members: registered` członkiem jest każdy, kto ma konto na hubie.
Szczegóły znajdziesz w [opisie modułów](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
to katalog, czyli repozytorium git z listą innych repozytoriów. Wymienia huby,
ich aplikacje oraz framework i ma ten sam format co katalog aplikacji dla
desktopu. Plik `apps.list` zawiera po jednym adresie URL repozytorium git
w każdym wierszu. Wiersz może mieć opcję `path=`, która wskazuje aplikację
wewnątrz repozytorium huba, oraz `ref=`, która przypina wersję. Każda pozycja
zawiera plik `kiwi.manifest` z wartością `CATEGORY` równą `Framework`, `Hub`
albo `App`.

Obecnie katalog wymienia kiwi-framework, Armory i dziesięć aplikacji Armory.
**Nie** jest przeznaczony dla polecenia `kiwi catalog add`. Jego pozycje nie
mają instalatora i na razie nic nie odczytuje tego katalogu automatycznie.
Według jego README pliki katalogu należą do domeny publicznej (CC0).

Żeby dodać swój hub, zrób fork katalogu, dopisz wiersz, upewnij się, że twoje
repozytorium zawiera plik `kiwi.manifest`, i otwórz pull request.

## Jeszcze niezrealizowane { #not-built-yet }

Te pozycje są w planach samego frameworka i jeszcze nie istnieją:

- Blog.
- Zatwierdzanie wpisów przez moderatorów (NIP-72, kind 4550).
- Obserwowanie przestrzeni, której twój hub nie zawiera.
- Logowanie przez rozszerzenie przeglądarki (NIP-07) lub zdalny program
  podpisujący (NIP-46).
- Serwer TURN w stacku Kiwi. Potrzebne do tego prace czekają w repozytorium
  kiwi-modules. Bez serwera TURN dwa telefony korzystające z internetu
  mobilnego często nie potrafią zestawić bezpośredniego połączenia.
