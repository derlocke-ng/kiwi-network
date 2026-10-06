# Contributing

Everything is open source, and issues and pull requests go to the repository
they concern; see [Repositories & status](status.md).

- **An app for the catalog.** Add a `kiwi.manifest` and an `install.sh`, tag a
  release, and open a pull request against
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). See
  [Publishing an app](../desktop/catalogs.md#publishing-an-app).
- **A kiwi-server module or role.** Modules are a directory with a `module.yaml`
  and Jinja templates. Add one to `tests/test_kiwiserver.py` the way the
  existing presets are tested. See [Modules](../server/modules.md#writing-a-module).
- **A kiwi-fox provider.** Every provider exposes SOCKS5 and nothing else. The
  contract is in kiwi-fox's
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-fox/blob/main/docs/plugin-system.md).
- **This website and these docs** live in
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## This repository

```
site/          the homepage, plain HTML/CSS/JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

```bash
python -m pip install mkdocs-material
mkdocs serve             # live preview at http://127.0.0.1:8000
mkdocs build --strict    # what CI builds, into build/docs
```

A push to `main` deploys both through GitHub Pages
(`.github/workflows/pages.yml`).

Please keep the docs **true to the repositories**. Describe what a tool does
today, mark anything planned as planned, and link to the source for details
rather than copying them.
