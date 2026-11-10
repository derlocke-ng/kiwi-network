# Contribuer

Tout est open source. Les tickets et les pull requests vont au dépôt qu’ils
concernent ; voir [Dépôts et état](status.md).

- **Une application pour le catalogue.** Ajoutez un `kiwi.manifest` et un
  `install.sh`, publiez une version avec un tag signé, et ouvrez une pull request
  sur [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Voir
  [Publier une application](../desktop/catalogs.md#publishing-an-app).
- **Un module.** Les modules sont développés dans
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) : un répertoire avec
  un `module.yaml` et des modèles Jinja. Voir [Écrire un module](../server/modules.md#writing-a-module).
- **Un hub ou une app de hub.** Forkez [Armory](https://github.com/derlocke-ng/armory),
  générez le squelette d’une app avec `npm run new-app`, et ajoutez votre hub à
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Voir
  [Héberger votre propre hub](../people/hubs.md).
- **Un fournisseur kiwi-proxy.** Chaque fournisseur expose du SOCKS5 et rien
  d’autre. Le contrat se trouve dans
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  de kiwi-proxy.
- **Ce site web et cette documentation** se trouvent dans
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Ce dépôt { #this-repository }

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # aperçu en direct sur http://127.0.0.1:8000
mkdocs build --strict    # ce que la CI construit : échoue sur les liens et ancres cassés
python -m http.server -d site 8080   # la page d’accueil
```

Un push sur `main` déploie les deux via GitHub Pages.

Merci de garder la documentation **fidèle aux dépôts**. Décrivez ce qu’un outil
fait aujourd’hui, signalez comme prévu tout ce qui est prévu, et renvoyez à la
source pour les détails plutôt que de les recopier.
