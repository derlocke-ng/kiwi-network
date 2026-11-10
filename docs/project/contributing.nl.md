# Bijdragen

Alles is open source. Issues en pull requests gaan naar de repository waar ze
over gaan; zie [Repository's en status](status.md).

- **Een app voor de catalogus.** Voeg een `kiwi.manifest` en een `install.sh`
  toe, publiceer een release met een ondertekende tag, en open een pull request
  tegen [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Zie
  [Een app publiceren](../desktop/catalogs.md#publishing-an-app).
- **Een module.** Modules worden ontwikkeld in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules): een map met een
  `module.yaml` en Jinja-sjablonen. Zie [Een module schrijven](../server/modules.md#writing-a-module).
- **Een hub of een hub-app.** Fork [Armory](https://github.com/derlocke-ng/armory),
  zet een app op met `npm run new-app`, en voeg je hub toe aan
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Zie
  [Je eigen hub draaien](../people/hubs.md).
- **Een kiwi-proxy-provider.** Elke provider biedt SOCKS5 aan en verder niets.
  Het contract staat in
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  van kiwi-proxy.
- **Deze website en deze documentatie** staan in
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Deze repository { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # live-voorbeeld op http://127.0.0.1:8000
mkdocs build --strict    # wat CI bouwt: faalt bij kapotte links en ankers
python -m http.server -d site 8080   # de homepage
```

Een push naar `main` publiceert beide via GitHub Pages.

Houd de documentatie alsjeblieft **trouw aan de repository's**. Beschrijf wat een tool
vandaag doet, markeer alles wat gepland is als gepland, en link naar de bron
voor details in plaats van ze over te nemen.
