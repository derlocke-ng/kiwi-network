# Mitmachen

Alles ist Open Source. Issues und Pull Requests gehören in das Repository, das sie
betreffen; siehe [Repositories & Status](status.md).

- **Eine App für den Katalog.** Füge ein `kiwi.manifest` und ein `install.sh` hinzu,
  veröffentliche mit einem signierten Tag und öffne einen Pull Request gegen
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Siehe
  [Eine App veröffentlichen](../desktop/catalogs.md#publishing-an-app).
- **Ein Modul.** Module werden in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) entwickelt: ein
  Verzeichnis mit einer `module.yaml` und Jinja-Templates. Siehe [Ein Modul schreiben](../server/modules.md#writing-a-module).
- **Ein Hub oder eine Hub-App.** Forke [Armory](https://github.com/derlocke-ng/armory),
  erzeuge das Gerüst einer App mit `npm run new-app` und trage deinen Hub in
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) ein. Siehe
  [Einen eigenen Hub betreiben](../people/hubs.md).
- **Ein kiwi-proxy-Provider.** Jeder Provider stellt SOCKS5 bereit und sonst nichts.
  Der Vertrag steht in kiwi-proxys
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
- **Diese Website und diese Doku** liegen in
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Dieses Repository { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # Live-Vorschau unter http://127.0.0.1:8000
mkdocs build --strict    # was die CI baut: scheitert an kaputten Links und Ankern
python -m http.server -d site 8080   # die Homepage
```

Ein Push auf `main` veröffentlicht beides über GitHub Pages.

Bitte halte die Doku **treu zu den Repositories**. Beschreib, was ein Werkzeug
heute tut, kennzeichne alles Geplante als geplant und verlinke für Details auf den
Quellcode, statt sie zu kopieren.
