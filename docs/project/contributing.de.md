# Mitmachen

Alles im Projekt Kiwi Network ist Open Source. Auf dieser Seite erfährst du,
wohin welche Art von Beitrag gehört. Issues und Pull Requests eröffnest du in
dem Repository, um das es geht. Eine Liste aller Repositories findest du unter
[Repositories & Status](status.md).

- **Eine App für den Katalog.** Der Katalog ist die Liste der Apps, die
  kiwi-updater installieren kann. Ergänze deine App um eine `kiwi.manifest` und
  eine `install.sh`, veröffentliche sie mit einem signierten Tag und eröffne
  einen Pull Request gegen
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Siehe [Eine App
  veröffentlichen](../desktop/catalogs.md#publishing-an-app).
- **Ein Modul.** Module werden in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) entwickelt. Ein
  Modul ist ein Verzeichnis mit einer `module.yaml` und Jinja-Vorlagen. Siehe
  [Ein eigenes Modul schreiben](../server/modules.md#writing-a-module).
- **Ein Hub oder eine App für Hubs.** Forke
  [Armory](https://github.com/derlocke-ng/armory), leg mit `npm run new-app` das
  Grundgerüst einer App an und trag deinen Hub in
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) ein. Siehe
  [Einen eigenen Hub betreiben](../people/hubs.md).
- **Ein Provider für kiwi-proxy.** Ein Provider ist ein Plugin, das kiwi-proxy
  eine bestimmte Art von Verbindung bereitstellt, etwa Tor oder ein VPN. Jeder
  Provider bietet SOCKS5 an und sonst nichts. Welche Regeln ein Provider
  einhalten muss, steht in
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  von kiwi-proxy.
- **Diese Website und diese Dokumentation** liegen im Repository
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Dieses Repository { #this-repository }

Das Repository kiwi-network enthält die Homepage und diese Dokumentation:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

Um die Dokumentation und die Homepage auf deinem eigenen Rechner anzusehen,
führe Folgendes aus:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # Live-Vorschau unter http://127.0.0.1:8000
mkdocs build --strict    # das baut auch die CI: schlägt bei kaputten Links und Ankern fehl
python -m http.server -d site 8080   # die Homepage
```

Wenn du nach `main` pushst, werden Homepage und Dokumentation über GitHub Pages
veröffentlicht.

Bitte halte die Dokumentation **im Einklang mit den Repositories**. Beschreib,
was ein Werkzeug heute tut, kennzeichne alles Geplante als geplant, und verlinke
für Einzelheiten auf den Quellcode, statt sie abzuschreiben.
