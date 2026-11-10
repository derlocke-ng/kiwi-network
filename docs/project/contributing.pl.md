# Współtworzenie

Wszystko jest open source. Zgłoszenia i pull requesty trafiają do
repozytorium, którego dotyczą; zobacz [Repozytoria i stan](status.md).

- **Aplikacja do katalogu.** Dodaj `kiwi.manifest` i `install.sh`, wydaj ją z
  podpisanym tagiem i otwórz pull request do
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Zobacz
  [Publikowanie aplikacji](../desktop/catalogs.md#publishing-an-app).
- **Moduł.** Moduły są rozwijane w
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules): katalog z
  `module.yaml` i szablonami Jinja. Zobacz [Pisanie modułu](../server/modules.md#writing-a-module).
- **Hub lub aplikacja huba.** Sforkuj [Armory](https://github.com/derlocke-ng/armory),
  utwórz szkielet aplikacji przez `npm run new-app` i dodaj swój hub do
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Zobacz
  [Własny hub](../people/hubs.md).
- **Dostawca kiwi-proxy.** Każdy dostawca udostępnia SOCKS5 i nic więcej.
  Kontrakt jest w
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  kiwi-proxy.
- **Ta strona i ta dokumentacja** są w
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## To repozytorium { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material
mkdocs serve             # podgląd na żywo pod http://127.0.0.1:8000
mkdocs build --strict    # to, co buduje CI: kończy się błędem przy zepsutych linkach i kotwicach
python -m http.server -d site 8080   # strona główna
```

Push do `main` wdraża oba przez GitHub Pages.

Dbaj, żeby dokumentacja była **wierna repozytoriom**. Opisuj, co narzędzie
robi dziś, oznaczaj wszystko zaplanowane jako zaplanowane i linkuj do źródła
po szczegóły zamiast je kopiować.
