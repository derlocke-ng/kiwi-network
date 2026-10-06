# Catalogs & publishing apps

## The Kiwi catalog

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) is the
app catalog for the Kiwi Network. Register it once per machine:

```bash
kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
```

It lists these apps:

| App | Release | Scopes | What it is |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.0.0 | user | the updater itself |
| [kiwi-killswitch](../apps/kiwi-killswitch.md) | v0.2.2 | user + system | fail-closed VPN kill switch for GNOME |
| [ensconce](ensconce.md) | v2.1.1 | user | post-install setup for Bluefin-DX |
| [kiwi-cli-tools-desktop](../apps/cli-tools.md) | v1.0.0 | user | `pweb`, `select-server`, `tethering` |
| [kiwi-fox](../apps/kiwi-fox.md) | v0.1.3 | user | isolated browser identities |
| [kiwi-plugin-tor](../apps/kiwi-fox-providers.md) | untagged (0.1.0) | user | kiwi-fox provider: Tor |
| [kiwi-plugin-vpn](../apps/kiwi-fox-providers.md) | untagged (0.1.0) | user | kiwi-fox provider: gluetun VPN |
| [kiwi-plugin-9proxy](../apps/kiwi-fox-providers.md) | untagged (0.1.0) | user | kiwi-fox provider: 9proxy |
| [kiwi-plugin-myst](../apps/kiwi-fox-providers.md) | untagged (0.1.0) | user | kiwi-fox provider: Mysterium |

"Untagged" apps have no release tag yet, so kiwi follows their default branch.
The number in brackets is the version in their `kiwi.manifest`.

kiwi syncs the catalog before every check and update, so managing a fleet of
desktops is just git:

- **add an app**: add its URL to `apps.list` and commit;
- **pin or roll back**: append `ref=<tag>` to its line (on a single machine,
  `kiwi pin <app> <tag>` does the same);
- **remove it**: delete the line (installed copies stay until you uninstall them).

## Your own catalog

A catalog is a git repo with an `apps.list` and, optionally, a
`catalog.manifest` describing itself:

```ini
# catalog.manifest
NAME=kiwi-catalog
DESCRIPTION=The Kiwi Network app catalog — open source, no accounts, no lock-in
HOMEPAGE=https://github.com/derlocke-ng/kiwi-catalog
MAINTAINER=derlocke-ng
```

```
# apps.list: one line per app, even when the app has a root half and a user half
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/derlocke-ng/kiwi-killswitch.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Optional per-line options:

| Option | Meaning |
|---|---|
| `branch=<name>` | track a branch instead of release tags |
| `ref=<tag>` | pin to an exact version |
| `scope=user\|system` | install only that half on machines using this list. This is a *filter*, not a declaration |

A machine's own `apps.list` (`~/.config/kiwi-updater/apps.list`, or
`/etc/kiwi-updater/apps.list` for root) always beats a catalog, so a machine can
pin or override anything. `kiwi add <url>` adds a line to it.

## Publishing an app

Put a `kiwi.manifest` and an `install.sh` in your repo root (templates are in
kiwi-updater's
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)):

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module …
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
INSTALLER=install.sh
```

Other keys the Kiwi apps use: `AUTHOR`, `CATEGORY`, `TAGS`, `ICON`,
`SCREENSHOTS`, `ABOUT` (a file shown in Kiwi Apps), `DEPENDS`, and `ROOT_REASON`
for anything with a system half.

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
| `KIWI_PURGE` | `1` when the user asked for `--purge` (uninstall only) |

A dual-scope installer branches on `KIWI_SCOPE` and does only that half each
time. Without `--purge`, leave the user's configuration where it is.

Release by tagging: `git tag v1.3.0 && git push --tags`. Then open a pull
request adding your URL to the catalog. Anything open source and genuinely
usable without an account, a subscription or a tracker is welcome.

## Trust

The catalog is **curated, not audited**. Being listed means someone thought the
app was worth having, not that its code has been reviewed. Read
`kiwi info <app>` before installing something you do not already know, and
`kiwi info --installer <app>` to see exactly what will run.
