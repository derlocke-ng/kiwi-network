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

## Ein Kiwi-Werkzeug dokumentieren { #documenting-a-kiwi-tool }

Jedes Kiwi-Werkzeug wird in seinem eigenen Repository dokumentiert. Seine
`README.md` ist kurz. Sie sagt, was das Werkzeug ist, wie du es installierst
und wo der Rest steht. Die vollständige Dokumentation liegt im Verzeichnis
`docs/`. Diese Website zeigt für jedes Werkzeug eine übersetzte Überblicksseite
und darunter die Seiten aus seinem Verzeichnis `docs/`, so wie sie in seinem
neuesten Release stehen. Wenn du die Dokumentation eines
Werkzeugs korrigierst, erscheint die Korrektur hier also mit dem nächsten
Release dieses Werkzeugs.

Wie du eine README und ein `docs/`-Verzeichnis schreibst, steht im Leitfaden
**kiwi-docs**. Er beschreibt den Ton und den Aufbau, erklärt, wie du jede
Aussage am Code überprüfst, und bringt ein Skript mit, das Links und Struktur
prüft. Sein Quelltext liegt in diesem Repository unter
[plugins/kiwi-docs](https://github.com/derlocke-ng/kiwi-network/tree/main/plugins/kiwi-docs/skills/kiwi-docs).
Die Repositories der Werkzeuge enthalten eine Kopie davon in
`.claude/skills/kiwi-docs/`, sodass Claude-Code-Sitzungen in diesen
Repositories ihn von selbst verwenden. Welche Repositories diese Website
einbindet und unter welcher Seite sie erscheinen, steht in
[docs-sources.yml](https://github.com/derlocke-ng/kiwi-network/blob/main/docs-sources.yml).

## Dieses Repository { #this-repository }

Das Repository kiwi-network enthält die Homepage und diese Dokumentation:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Um die Dokumentation und die Homepage auf deinem eigenen Rechner anzusehen,
führe Folgendes aus:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # Live-Vorschau unter http://127.0.0.1:8000
mkdocs build --strict    # schlägt bei kaputten Links und Ankern fehl
python -m http.server -d site 8080   # die Homepage
```

Die Version, die die CI baut, enthält außerdem die Seiten der Werkzeuge. Um
diese Version zu bauen, führe Folgendes aus:

```bash
python tools/pull-docs.py                      # diese Dokumentation plus docs/ aus jedem Werkzeug
mkdocs build --strict -f build/mkdocs.yml      # das Ergebnis liegt in build/docs/
```

Wenn du nach `main` pushst, werden Homepage und Dokumentation über GitHub Pages
veröffentlicht.

Bitte sorg dafür, dass die Dokumentation **zu den Repositories passt**.
Beschreib, was ein Werkzeug heute tut, kennzeichne alles Geplante als geplant,
und verlinke für Einzelheiten auf den Quellcode, statt sie abzuschreiben.
