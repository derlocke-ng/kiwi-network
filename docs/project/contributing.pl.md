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
  katalog z plikiem `module.yaml` i szablonami Jinja. Zobacz
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
- **Ta strona i ta dokumentacja** są w repozytorium
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## To repozytorium { #this-repository }

Repozytorium kiwi-network zawiera stronę główną i tę dokumentację:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

Żeby obejrzeć dokumentację i stronę główną na swoim komputerze, uruchom:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # podgląd na żywo pod http://127.0.0.1:8000
mkdocs build --strict    # to buduje CI: kończy się błędem przy zepsutych linkach i kotwicach
python -m http.server -d site 8080   # strona główna
```

Po wypchnięciu zmian do `main` strona główna i dokumentacja są publikowane
przez GitHub Pages.

Dbaj o to, żeby dokumentacja **zgadzała się z repozytoriami**. Opisuj, co
narzędzie robi dziś, oznaczaj wszystko, co planowane, jako planowane,
a po szczegóły odsyłaj do źródła, zamiast je kopiować.
