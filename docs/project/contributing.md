# Contributing

Everything is open source. Issues and pull requests go to the repository they
concern; see [Repositories & status](status.md).

- **An app for the catalog.** Add a `kiwi.manifest` and an `install.sh`, release
  with a signed tag, and open a pull request against
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). See
  [Publishing an app](../desktop/catalogs.md#publishing-an-app).
- **A module.** Modules are developed in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules): a directory with a
  `module.yaml` and Jinja templates. See [Writing a module](../server/modules.md#writing-a-module).
- **A hub or a hub app.** Fork [Armory](https://github.com/derlocke-ng/armory),
  scaffold an app with `npm run new-app`, and add your hub to
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). See
  [Running your own hub](../people/hubs.md).
- **A kiwi-proxy provider.** Every provider exposes SOCKS5 and nothing else. The
  contract is in kiwi-proxy's
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
- **This website and these docs** live in
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## This repository

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses, copied from kiwi-icons
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material
mkdocs serve             # live preview at http://127.0.0.1:8000
mkdocs build --strict    # what CI builds: fails on broken links and anchors
python -m http.server -d site 8080   # the homepage
```

A push to `main` deploys both through GitHub Pages.

Please keep the docs **true to the repositories**. Describe what a tool does
today, mark anything planned as planned, and link to the source for details
rather than copying them.
