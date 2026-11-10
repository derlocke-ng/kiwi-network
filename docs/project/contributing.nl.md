# Bijdragen

Alles in het project Kiwi Network is open source. Op deze pagina lees je waar
je met welke bijdrage terechtkunt. Issues en pull requests open je in de
repository waar ze over gaan. Alle repository’s vind je op
[Repository’s en status](status.md).

- **Een app voor de catalogus.** De catalogus is de lijst met apps die
  kiwi-updater kan installeren. Voeg een `kiwi.manifest` en een `install.sh`
  aan je app toe, breng een release uit met een ondertekende tag en open een
  pull request bij
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Zie
  [Een app publiceren](../desktop/catalogs.md#publishing-an-app).
- **Een module.** Modules worden ontwikkeld in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Een module is
  een map met een `module.yaml` en Jinja-templates. Zie
  [Een module schrijven](../server/modules.md#writing-a-module).
- **Een hub of een app voor een hub.** Fork
  [Armory](https://github.com/derlocke-ng/armory), maak met `npm run new-app`
  het skelet van een app aan en voeg je hub toe aan
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Zie
  [Je eigen hub draaien](../people/hubs.md).
- **Een provider voor kiwi-proxy.** Een provider is een plug-in waarmee
  kiwi-proxy er een soort verbinding bij krijgt, bijvoorbeeld Tor of een VPN.
  Elke provider biedt SOCKS5 aan en verder niets. Het contract waaraan een
  provider zich moet houden, staat in
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  van kiwi-proxy.
- **Deze website en deze documentatie** staan in de repository
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Deze repository { #this-repository }

De repository kiwi-network bevat de homepage en deze documentatie:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Zo bekijk je de documentatie en de homepage op je eigen computer:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # live voorbeeld op http://127.0.0.1:8000
mkdocs build --strict    # wat CI bouwt: mislukt bij kapotte links en ankers
python -m http.server -d site 8080   # de homepage
```

Zodra je naar `main` pusht, worden de homepage en de documentatie via GitHub
Pages gepubliceerd.

Zorg dat de documentatie **klopt met de repository’s**. Beschrijf wat een tool
vandaag doet, geef bij alles wat gepland is aan dat het gepland is, en link voor
de details naar de bron in plaats van ze over te nemen.
