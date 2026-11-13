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

## Documenting a Kiwi tool

Each Kiwi tool documents itself in its own repository. Its `README.md` is short
and says what the tool is, how to install it and where the rest is. Its `docs/`
folder holds the full documentation. This site shows a translated overview page
for each tool, and under it the pages of the tool's `docs/` folder, taken from
the tool's latest release. So a fix to a tool's documentation reaches this site
with the tool's next release.

How a README and a `docs/` folder are written is described in the **kiwi-docs**
guide: the voice, the layout, how to check every claim against the code, and a
script that checks links and structure. Its source is
[plugins/kiwi-docs](https://github.com/derlocke-ng/kiwi-network/tree/main/plugins/kiwi-docs/skills/kiwi-docs)
in this repository. The tool repositories carry a copy in
`.claude/skills/kiwi-docs/`, so Claude Code sessions in those repositories use
it on their own. Which repositories this site pulls in, and under which page,
is listed in
[docs-sources.yml](https://github.com/derlocke-ng/kiwi-network/blob/main/docs-sources.yml).

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
mkdocs build --strict    # fails on broken links and anchors
python -m http.server -d site 8080   # the homepage
```

What CI builds also contains the tools' pages. To build that version, run:

```bash
python tools/pull-docs.py                      # this repository's docs plus each tool's docs/
mkdocs build --strict -f build/mkdocs.yml      # the result is in build/docs/
```

When you push to `main`, both the homepage and the docs are published
through GitHub Pages.

Please keep the docs **true to the repositories**. Describe what a tool does
today, mark anything planned as planned, and link to the source for details
rather than copying them.
