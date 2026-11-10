# Catalogs & publishing apps

## The Kiwi catalog

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) is the
app catalog for the Kiwi Network. The kiwi-updater install registers it, and
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` registers it
by hand.

| App | Release | Scopes | What it is |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | the updater itself |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | fail-closed VPN kill switch for GNOME |
| [ensconce](ensconce.md) | v2.5.0 | user | post-install setup for Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | sealed SOCKS5/VPN exits in rootless Podman |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | isolated browser identities on kiwi-proxy exits |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | distro boxes whose traffic leaves only through an exit |
| [kiwi-server](../server/index.md) | v2.42.0 | user | build and run your own network |
| [syncman](syncman.md) | v0.4.1 | user | two-way folder sync |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | display layouts for GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | kiwi-proxy provider: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | kiwi-proxy provider: a VPN through gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | kiwi-proxy provider: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | kiwi-proxy provider: Mysterium |

kiwi syncs the catalog before every check and update, so managing a fleet of
desktops is just git:

- **add an app**: add its URL to `apps.list` and commit;
- **pin or roll back**: append `ref=<tag>` to its line (on one machine,
  `kiwi pin <app> <tag>` does the same);
- **remove it**: delete the line (installed copies stay until you uninstall them).

## Your own catalog

A catalog is a git repo with an `apps.list` and, optionally, a
`catalog.manifest` describing itself:

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list: one line per app, even when it has a root half and a user half
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Option | Meaning |
|---|---|
| `branch=<name>` | track a branch instead of release tags |
| `ref=<tag>` | pin an exact version |
| `scope=user\|system` | install only that half on machines using this list. This is a *filter*, not a declaration |

A machine's own list (`~/.config/kiwi-updater/apps.list`, or
`/etc/kiwi-updater/apps.list` for root) always beats a catalog. `kiwi add <url>`
adds a line to it.

## Publishing an app

Put a `kiwi.manifest` and an `install.sh` in your repo root. Templates are in
kiwi-updater's [`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates).

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Other keys: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (a file Kiwi
Apps shows), `DEPENDS` and, for anything with a system half, `ROOT_REASON`.
`ICON=` is an SVG or PNG of at most 1 MiB inside the repo. The Kiwi apps use
their icon from [kiwi-icons](../project/brand.md).

!!! warning "Comments go on their own line"
    A value runs to the end of the line. `COMPONENTS=cli  # … gui …` makes the
    comment part of the value, and the app is then treated as having a GUI.

kiwi runs your installer once **per declared scope**, with:

| Variable | Value |
|---|---|
| `KIWI_SCOPE` | `user` or `system` |
| `KIWI_PREFIX` | `~/.local` or `/usr/local` |
| `KIWI_APP_DIR` | absolute path of the clone |
| `KIWI_ACTION` | `install`, `update` or `uninstall` |
| `KIWI_GUI` | `0` on a headless machine, or with `--cli-only` |
| `KIWI_PURGE` | `1` when the user asked for `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` first; a fixed system path for the system scope |

A dual-scope installer branches on `KIWI_SCOPE` and does only that half each
time. Without `--purge`, leave the user's configuration where it is.

**Release with a signed tag**, so that a system half updates without a
password:

```bash
git config gpg.format ssh            # sign with your SSH key
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater's `templates/release.yml` publishes a GitHub release only for a tag
signed by a key in `.github/allowed_signers`, and never creates tags itself.
Then open a pull request adding your URL to the catalog. Anything open source
and genuinely usable without an account, a subscription or a tracker is welcome.

## Trust

The catalog is **curated, not audited**. Being listed means someone thought the
app was worth having, not that its code has been reviewed. Read
`kiwi info <app>` before installing something you do not already know, and
`kiwi info --installer <app>` to see exactly what will run.
