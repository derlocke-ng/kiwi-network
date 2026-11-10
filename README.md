# kiwi-network

The website and documentation of **Kiwi Network**, an open-source Linux
environment that you run yourself: your servers, your devices and your desktop,
connected in one private network. It installs itself, keeps itself up to date,
makes a backup every night and can be rebuilt when something breaks.

- **Homepage:** <https://kiwi-network.eu> (`site/`)
- **Documentation:** <https://kiwi-network.eu/docs/> (`docs/`, MkDocs Material)

## What Kiwi Network is

| | Tools |
|---|---|
| **The network**: your servers and devices in one private WireGuard network, with its own DNS, certificates, services and backups. One file describes all of it, and the machines are installed and maintained automatically | [kiwi-server](https://github.com/derlocke-ng/kiwi-server) builds and runs the network. [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) holds the 20 modules and generates their configuration, and [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) runs them on each machine |
| **Hubs**: software for communities to run their own hub (an open marketplace, feed, chat, file sharing) in the browser, synchronised over nostr, with no central platform | [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework), [Armory](https://github.com/derlocke-ng/armory) ([live](https://derlocke-ng.github.io/armory/)), [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) |
| **The desktop**: a Fedora Atomic workstation that is set up automatically and gets its apps from git catalogs | [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) and the [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog): kiwi-killswitch, ensconce, kiwi-proxy, kiwi-custodia, kiwi-fox and its provider modules, gnome-monitor, syncman, kiwi-cli-tools-desktop |

Every repository, with its release and known gaps, is on the
[status page](https://kiwi-network.eu/docs/project/status/).

## This repository

```
site/              the homepage: plain HTML, CSS and JS; no build step, no third-party requests
site/icons/        app icons, copied from kiwi-icons
docs/              the documentation (MkDocs Material): page.md in English, page.de.md, page.fr.md … beside it
mkdocs.yml         docs configuration (builds into build/docs)
.github/workflows/pages.yml   builds the docs, puts site/ at / and the docs at /docs/, deploys to GitHub Pages
```

Work on it locally:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve                 # docs at http://127.0.0.1:8000
mkdocs build --strict        # what CI runs: fails on broken links and anchors

python -m http.server -d site 8080   # the homepage
```

A push to `main` deploys both. Keep the docs true to the repositories they
describe: what a tool does today, with planned work marked as planned.

The docs are in the languages Armory and kiwi-framework speak: English,
German, French, Spanish, Italian, Dutch, Polish and Portuguese. English is
the source. A translation sits beside its page with the language as suffix
(`modules.de.md`), keeps the English anchor on every heading
(`## Tunnel-MTU { #tunnel-mtu }`) so links and the language switcher land on
the same section, and a missing translation falls back to English.

## License

AGPL-3.0 (see `LICENSE`). Each tool carries its own license; most are
GPL-3.0-or-later, and kiwi-gen is MIT. The icons in `site/icons/` and
`docs/assets/icons/` come from
[kiwi-icons](https://github.com/derlocke-ng/kiwi-icons), and the Armory app icons
from [Armory](https://github.com/derlocke-ng/armory).
