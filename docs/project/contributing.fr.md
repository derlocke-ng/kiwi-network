# Contribuer

Tout le projet Kiwi Network est open source. Cette page vous indique où
proposer chaque type de contribution. Ouvrez les issues et les pull requests
dans le dépôt concerné. La liste des dépôts se trouve sur la page
[Dépôts et état](status.md).

- **Une application pour le catalogue.** Le catalogue est la liste des
  applications que kiwi-updater peut installer. Ajoutez un `kiwi.manifest` et
  un `install.sh` à votre application, publiez-la avec un tag signé, puis
  ouvrez une pull request sur
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Voir
  [Publier une application](../desktop/catalogs.md#publishing-an-app).
- **Un module.** Les modules sont développés dans
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Un module est un
  dossier qui contient un `module.yaml` et des templates Jinja. Voir
  [Écrire un module](../server/modules.md#writing-a-module).
- **Un hub ou une application de hub.** Forkez
  [Armory](https://github.com/derlocke-ng/armory), créez le squelette d’une
  application avec `npm run new-app`, puis ajoutez votre hub à
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Voir
  [Héberger votre propre hub](../people/hubs.md).
- **Un module fournisseur pour kiwi-proxy.** Un module fournisseur est un
  plugin qui apporte à kiwi-proxy un type de connexion, par exemple Tor ou un
  VPN. Chaque module fournisseur propose du SOCKS5, et rien d’autre. Les règles
  qu’un module fournisseur doit respecter
  sont décrites dans le fichier
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  de kiwi-proxy.
- **Ce site et cette documentation** se trouvent dans le dépôt
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Ce dépôt { #this-repository }

Le dépôt kiwi-network contient la page d’accueil et cette documentation :

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Pour prévisualiser la documentation et la page d’accueil sur votre propre
ordinateur, lancez :

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # aperçu en direct sur http://127.0.0.1:8000
mkdocs build --strict    # ce que construit la CI : échoue sur les liens et ancres cassés
python -m http.server -d site 8080   # la page d'accueil
```

À chaque push sur `main`, la page d’accueil et la documentation sont publiées
par GitHub Pages.

Veillez à ce que la documentation reste **fidèle aux dépôts**. Décrivez ce
qu’un outil fait aujourd’hui, signalez comme prévu ce qui est prévu, et pour
les détails, renvoyez à la source plutôt que de les recopier.
