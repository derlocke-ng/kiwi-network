# Contributing

Kiwi Network is open source and community contributions are welcome. The project
spans several repositories under <https://github.com/derlocke-ng>.

## How to help

- **Improve the docs.** This site lives in
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network) (`docs/` for the
  MkDocs documentation, `site/` for the homepage). Clarity for both beginners
  and admins is the goal.
- **Provide tested compose stacks and hardening notes** for
  [kiwi-server](build/kiwi-server.md) modules and roles.
- **Write or package an app.** Any open-source tool usable without an account,
  subscription or tracker is welcome in the [catalog](apps/kiwi-catalog.md) —
  add a `kiwi.manifest` and `install.sh`, tag a release, and open a PR.
- **Report issues and propose safer defaults** on the relevant repository.

## Where each thing lives

| Area | Repository |
|---|---|
| This website + docs | [kiwi-network](https://github.com/derlocke-ng/kiwi-network) |
| Server builder | [kiwi-server](https://github.com/derlocke-ng/kiwi-server) |
| App installer | [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) |
| App catalog | [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) |
| Browser identities | [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) + `kiwi-plugin-*` |
| VPN kill switch | [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) |
| Key/cert generator | [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) |
| Testing suite | [kiwi-pentesting](https://github.com/derlocke-ng/kiwi-pentesting) |
| Desktop CLI tools | [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) |

## Building the docs locally

```bash
python -m pip install mkdocs-material
mkdocs serve      # live preview
mkdocs build      # output to build/docs
```

Most Kiwi code is licensed **GPL-3.0-or-later**; a few browser-based tools
(kiwi-gen, kiwi-blog) are **MIT**. Check each repository's `LICENSE`.
