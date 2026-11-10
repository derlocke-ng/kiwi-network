# kiwi-network

The website and documentation of **Kiwi Network**: open-source tools for
connecting what is yours, meaning your machines, your people and your desktop.

- **Homepage:** <https://kiwi-network.eu> (`site/`)
- **Documentation:** <https://kiwi-network.eu/docs/> (`docs/`, MkDocs Material)

## What Kiwi Network is

| | Tools |
|---|---|
| **Network**: a private WireGuard mesh with its own DNS, CA, services and backups, built from one file | [kiwi-server](https://github.com/derlocke-ng/kiwi-server) (fleet file → install ISOs → apply over SSH), with [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) (20 modules, the renderer) and [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) (the machine side) |
| **People**: peer-to-peer web tools over nostr, sealed in the browser | [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework), [Armory](https://github.com/derlocke-ng/armory) ([live](https://derlocke-ng.github.io/armory/)), [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) |
| **Desktop**: apps for Fedora Atomic, installed from git catalogs | [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) and the [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog): kiwi-killswitch, ensconce, kiwi-proxy, kiwi-custodia, kiwi-fox and its provider modules, gnome-monitor, syncman, kiwi-cli-tools-desktop |

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
