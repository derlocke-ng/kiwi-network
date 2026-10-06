# kiwi-network

The website and documentation of **Kiwi Network**: open-source tools for running
your own private network and desktop.

- **Homepage:** <https://kiwi-network.eu> (`site/`)
- **Documentation:** <https://kiwi-network.eu/docs/> (`docs/`, MkDocs Material)

## What Kiwi Network is

- **[kiwi-server](https://github.com/derlocke-ng/kiwi-server)** builds the
  network. One `fleet.yaml` becomes a first-boot script, an Ignition or preseed
  config and an unattended install ISO per host, on Fedora CoreOS, uCore or
  Debian. Roles: `master` (the WireGuard entry point, with a double hop through
  a commercial VPN, Pi-hole and Tor), `node-gw` (a LAN gateway through the VPN),
  `node-cloud` (Nextcloud AIO and Vaultwarden) and `bare`.
- **[kiwi-updater](https://github.com/derlocke-ng/kiwi-updater)** installs and
  updates apps from git catalogs on Fedora Silverblue and Bluefin. The
  **[kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog)** lists
  [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch),
  [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) and its provider plugins,
  [ensconce](https://github.com/derlocke-ng/ensconce) and
  [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop).

The full list of repositories, with release state and known gaps, is on the
[status page](https://kiwi-network.eu/docs/project/status/).

## This repository

```
site/              the homepage: plain HTML, CSS and JS, no build step, no third-party requests
docs/              the documentation (MkDocs Material)
mkdocs.yml         docs configuration (builds into build/docs)
.github/workflows/pages.yml   builds the docs, puts site/ at / and the docs at /docs/, deploys to GitHub Pages
```

Work on it locally:

```bash
python -m pip install mkdocs-material
mkdocs serve                 # docs at http://127.0.0.1:8000
mkdocs build --strict        # what CI runs: fails on broken links and anchors

python -m http.server -d site 8080   # the homepage
```

A push to `main` deploys both. Keep the docs true to the repositories they
describe: what a tool does today, with planned work marked as planned.

## License

AGPL-3.0 (see `LICENSE`). Each tool carries its own license; most are
GPL-3.0-or-later, and kiwi-gen and kiwi-blog are MIT.
