# Własny hub

Hub to pliki statyczne, więc hostowanie go to serwowanie folderu przez HTTPS.
Są trzy sposoby, żeby go prowadzić:

- **Używaj Armory takiego, jaki jest:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Zrób własną dystrybucję:** twoja nazwa, przekaźniki i aplikacje, na
  dowolnym hostingu statycznym.
- **Uruchom kontener huba:** na przykład wewnątrz własnej Kiwi Network, z
  własnym przekaźnikiem, jako prywatny hub osiągalny tylko z sieci mesh.

## Rodzaje hubów { #kinds-of-hub }

| Rodzaj | Jak | Przykład |
|---|---|---|
| **Publiczny** | Publiczne przekaźniki; każdy może go otworzyć | Armory |
| **Prywatny** | Przekaźniki huba są zablokowane (`policy.relays: 'locked'`), a strony czekają, aż któryś z nich odpowie (`requireHub`), z przekaźnikami wewnątrz VPN | firmowy hub na jej kiwi-master |
| **Półpubliczny** | Prywatny hub z publiczną strefą dla wybranych aplikacji (na przykład czatu) na publicznych przekaźnikach | |

Każde zdarzenie należy do jednej sieci (własnej sieci huba, strefy publicznej
lub sieci przestrzeni) i nigdy nie przechodzi do innej.

## Własna dystrybucja { #your-own-distribution }

Szablonem jest Armory (na GitHubie *Use this template* daje ci kopię bez
historii):

1. Edytuj **`distribution.js`**: id, nazwę, znak, opis, stronę domową,
   repozytorium, przekaźniki, serwery multimediów, przestrzenie, aplikacje i
   montowania. Żeby serwować też przestrzenie Armory, skopiuj ich `owner` i
   `id` z `hub.json` Armory.
2. Edytuj **`locales/*.json`**: tytuł, wstęp i stopkę oraz jeden tekst karty
   na montowanie. Angielski jest językiem zapasowym.
3. Zaktualizuj **`kiwi.manifest`** i opcjonalnie dodaj swój hub do
   [kiwi-web-catalog](#kiwi-web-catalog).
4. Na GitHubie: *Settings → Pages → Source: GitHub Actions*, potem push.

```bash
npm install
npm run dev                  # hub z hot reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # lokalny testowy przekaźnik na ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # szkielet nowej aplikacji
```

Przypinaj kiwi-framework commitem lub tagiem, nigdy gałęzią. Build sprawdza
twój `distribution.js` (na przykład publiczne montowanie wymaga publicznych
przekaźników i na odwrót).

Stos technologiczny to TypeScript, React 19 i Vite dla wszystkiego, co
widoczne. Warstwa danych w `shared/` to zwykły JavaScript z typami JSDoc.
Testy działają w test runnerze node, a dla przeglądarki w Playwright.

## Kontener huba { #the-hub-container }

Armory jest też obrazem kontenera, `ghcr.io/derlocke-ng/armory`, budowanym z
`container/Dockerfile` frameworka (nginx). Przy starcie jego entrypoint
zapisuje `hub.local.json` ze zmiennych `HUB_*`, a strona odczytuje go, zanim
się połączy. Wdrożenie może w ten sposób wybrać przekaźniki i politykę, ale nie
może dodać kodu. Bez ustawionych zmiennych hub działa tak, jak go zbudowano.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Zmienna | Znaczenie |
|---|---|
| `HUB_RELAYS` | własne przekaźniki huba |
| `HUB_PUBLIC_RELAYS` | przekaźniki strefy publicznej (ustawiona i pusta: brak strefy publicznej) |
| `HUB_DIRECTORY_RELAYS` | gdzie publikuje się i wyszukuje listy przekaźników |
| `HUB_RELAYS_LOCKED` | `true`: ludzie nie mogą zastąpić przekaźników huba |
| `HUB_REQUIRE_HUB` | `true`: strony czekają, dopóki żaden z przekaźników huba nie odpowiada |
| `HUB_PUBLIC_MOUNTS` | montowania w strefie publicznej, według id |
| `HUB_ACCOUNT_MOUNTS` | montowania, które wymagają konta |
| `HUB_REQUIRE_ACCOUNT` | `true`: każde montowanie wymaga konta |
| `HUB_SPACE_RELAYS` | przekaźniki dla każdej przestrzeni: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | klucze, które moderują każdą przestrzeń zdefiniowaną przez hub |
| `HUB_REGISTER_POW` | bity proof of work dla nowego konta (przekaźniki tylko dla członków) |
| `HUB_CALDAV` | Nextcloud; nginx przekazuje do niego `/remote.php/dav/`, więc kalendarz nie potrzebuje CORS |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | serwery STUN/TURN dla rozmów i bezpośrednich transferów. Login TURN jest widoczny na stronie, więc daj mu login tylko dla tego huba |

`HUB_USER_MOUNTS` jest odczytywana, ale jeszcze nic nie robi: obserwowanie
przestrzeni, których hub nie dostarcza, dopiero nadejdzie.

Hub musi być serwowany przez HTTPS (WebCrypto wymaga bezpiecznego kontekstu),
a jego przekaźniki przez `wss://`. Przez zwykłe `http://` (poza localhost)
strona to komunikuje i się zatrzymuje.

### W Kiwi Network { #on-a-kiwi-network }

kiwi-master może mieć własny przekaźnik i hub: moduł `nostr-relay` (strfry
pod `relay.<host>`) i moduł `hub` (ten obraz, domyślnie Armory, pod
`hub.<host>`). Domyślnie są prywatne: osiągalne tylko z sieci mesh, z
certyfikatem floty. Hub półpubliczny dodaje `public_relays` i
`public_mounts`. Publiczny dodaje `reverse-proxy.public`, które dostaje
certyfikaty Let's Encrypt. Przekaźnik przyjmuje wtedy posty z sieci mesh, a z
Internetu tylko od członków, którzy udowodnią swój klucz (NIP-42): tych z
listy podpisanej przez administratorów (`write_pubkeys`) albo, z
`members: registered`, od każdego, kto ma konto w hubie. Zobacz
[opis modułów](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
wymienia huby, ich aplikacje i framework, w tym samym kształcie co katalog
desktopowy: `apps.list` z jednym adresem URL git na linię (`path=` dla
aplikacji wewnątrz repozytorium huba, `ref=` do przypięcia) i
`kiwi.manifest` w każdym wpisie z `CATEGORY` równym `Framework`, `Hub` lub
`App`.

Dziś wymienia kiwi-framework, Armory i dziesięć aplikacji Armory. **Nie** jest
przeznaczony dla `kiwi catalog add`: te wpisy nie mają instalatora i nic
jeszcze nie odczytuje katalogu automatycznie. Pliki katalogu są w domenie
publicznej (CC0, według jego README).

Żeby dodać swój hub: zrób fork, dodaj linię, upewnij się, że repozytorium ma
`kiwi.manifest`, i otwórz pull request.

## Jeszcze niezbudowane { #not-built-yet }

To pochodzi z roadmapy samego frameworka:

- Blog.
- Zatwierdzenia moderacyjne (NIP-72 kind 4550).
- Obserwowanie przestrzeni, których hub nie dostarcza.
- Podpisywanie przez NIP-07 i NIP-46.
- Serwer TURN w stacku kiwi. Czeka w kiwi-modules; bez TURN dwa telefony na
  danych mobilnych często nie znajdują bezpośredniej ścieżki.
