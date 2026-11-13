# Współtworzenie

Cały projekt Kiwi Network jest open source. Na tej stronie dowiesz się, gdzie
trafia każdy rodzaj wkładu. Zgłoszenia (issues) i pull requesty otwieraj
w repozytorium, którego dotyczą. Lista repozytoriów jest na stronie
[Repozytoria i stan](status.md).

- **Aplikacja do katalogu aplikacji.** Katalog aplikacji to lista aplikacji,
  które może zainstalować kiwi-updater. Dodaj do swojej aplikacji pliki
  `kiwi.manifest` i `install.sh`, wydaj ją z podpisanym tagiem i otwórz pull
  request do [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog).
  Zobacz [Publikowanie aplikacji](../desktop/catalogs.md#publishing-an-app).
- **Moduł.** Moduły są rozwijane w repozytorium
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Moduł to
  folder z plikiem `module.yaml` i szablonami Jinja. Zobacz
  [Własny moduł](../server/modules.md#writing-a-module).
- **Hub albo aplikacja dla huba.** Zrób fork
  [Armory](https://github.com/derlocke-ng/armory), utwórz szkielet aplikacji
  poleceniem `npm run new-app` i dodaj swój hub do
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Zobacz
  [Własny hub](../people/hubs.md).
- **Dostawca dla kiwi-proxy.** Dostawca to wtyczka, która daje kiwi-proxy
  określony rodzaj połączenia, na przykład Tor albo VPN. Każdy dostawca
  udostępnia SOCKS5 i nic poza tym. Zasady, których dostawca musi
  przestrzegać, opisuje
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  w repozytorium kiwi-proxy.
- **Strona internetowa projektu i ta dokumentacja** są w repozytorium
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Dokumentowanie narzędzia Kiwi { #documenting-a-kiwi-tool }

Każde narzędzie Kiwi ma dokumentację we własnym repozytorium. Jego `README.md`
jest krótki i mówi, czym jest narzędzie, jak je zainstalować i gdzie szukać
reszty. Pełna dokumentacja jest w folderze `docs/`. Ta witryna pokazuje dla
każdego narzędzia przetłumaczoną stronę z przeglądem, a pod nią strony z
folderu `docs/` tego narzędzia, w wersji z jego najnowszego wydania. Poprawka w
dokumentacji narzędzia trafia więc tutaj razem z jego następnym wydaniem.

Jak pisać README i folder `docs/`, opisuje przewodnik **kiwi-docs**: styl,
układ plików, sposób sprawdzania każdego stwierdzenia w kodzie, a do tego
skrypt, który kontroluje linki i strukturę. Jego źródło jest w tym
repozytorium, w
[plugins/kiwi-docs](https://github.com/derlocke-ng/kiwi-network/tree/main/plugins/kiwi-docs/skills/kiwi-docs).
Repozytoria narzędzi mają jego kopię w `.claude/skills/kiwi-docs/`, więc sesje
Claude Code w tych repozytoriach korzystają z niego same. Które repozytoria ta
witryna pobiera i pod którą stroną je pokazuje, zapisano w
[docs-sources.yml](https://github.com/derlocke-ng/kiwi-network/blob/main/docs-sources.yml).

## To repozytorium { #this-repository }

Repozytorium kiwi-network zawiera stronę główną i tę dokumentację:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Żeby obejrzeć dokumentację i stronę główną na swoim komputerze, uruchom:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # podgląd na żywo pod http://127.0.0.1:8000
mkdocs build --strict    # kończy się błędem przy zepsutych linkach i kotwicach
python -m http.server -d site 8080   # strona główna
```

Wersja, którą buduje CI, zawiera też strony narzędzi. Żeby ją zbudować,
uruchom:

```bash
python tools/pull-docs.py                      # dokumentacja tego repozytorium plus folder docs/ każdego narzędzia
mkdocs build --strict -f build/mkdocs.yml      # wynik trafia do build/docs/
```

Po wypchnięciu zmian do `main` strona główna i dokumentacja są publikowane
przez GitHub Pages.

Dbaj o to, żeby dokumentacja **zgadzała się z repozytoriami**. Opisuj, co
narzędzie robi dziś, oznaczaj wszystko, co planowane, jako planowane,
a po szczegóły odsyłaj do źródła, zamiast je kopiować.
