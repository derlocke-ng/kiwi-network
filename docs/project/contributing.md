# Contributing

Everything in the Kiwi Network project is open source. This page tells you
where each kind of contribution goes. Open issues and pull requests in the
repository they concern. The repositories are listed on
[Repositories & status](status.md).

- **An app for the catalog.** The catalog is the list of apps that
  kiwi-updater can install. Add a `kiwi.manifest` and an `install.sh` to your
  app, release it with a signed tag, and open a pull request against
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). See
  [Publishing an app](../desktop/catalogs.md#publishing-an-app).
- **A module.** Modules are developed in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). A module is a
  directory with a `module.yaml` and Jinja templates. See
  [Writing a module](../server/modules.md#writing-a-module).
- **A hub or a hub app.** Fork [Armory](https://github.com/derlocke-ng/armory),
  create the skeleton of an app with `npm run new-app`, and add your hub to
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). See
  [Running your own hub](../people/hubs.md).
- **A kiwi-proxy provider.** A provider is a plugin that gives kiwi-proxy a
  kind of connection, such as Tor or a VPN. Every provider offers SOCKS5 and
  nothing else. The contract that a provider has to keep is in kiwi-proxy's
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
- **This website and these docs** are in the
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network) repository.

## This repository

The kiwi-network repository contains the homepage and this documentation:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

To preview the docs and the homepage on your own computer, run:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # live preview at http://127.0.0.1:8000
mkdocs build --strict    # what CI builds: fails on broken links and anchors
python -m http.server -d site 8080   # the homepage
```

When you push to `main`, both the homepage and the docs are published
through GitHub Pages.

Please keep the docs **true to the repositories**. Describe what a tool does
today, mark anything planned as planned, and link to the source for details
rather than copying them.
