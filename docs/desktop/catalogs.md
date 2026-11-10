# Catalogs & publishing apps

A catalog is a list of apps that kiwi-updater can install. It is a git
repository, so you can read it, copy it and propose changes to it. This page
describes the Kiwi catalog, shows how to make a catalog of your own, for
example for all the desktops you look after, and explains how to publish an
app so that other people can install it with kiwi.

## The Kiwi catalog

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) is the
app catalog of the Kiwi Network. It is registered automatically when you
install kiwi-updater. To register it by hand, run
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

The table lists the apps in the catalog. The *Scopes* column shows where an app
is installed. The user scope is your home directory. The system scope is a
part that is owned by root.

| App | Release | Scopes | What it is |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | user | the updater itself |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | user + system | VPN kill switch for GNOME. It is fail-closed, which means that all traffic stays blocked when the VPN is down |
| [ensconce](ensconce.md) | v2.5.0 | user | sets up a freshly installed Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | user | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | user | exits for SOCKS5 and VPN connections. An exit is an isolated container in rootless Podman |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | user | isolated browser identities that use kiwi-proxy exits |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | user | distro boxes (containers with a Linux distribution) whose traffic goes only through an exit |
| [kiwi-server](../server/index.md) | v2.42.0 | user | the tool with which you build and run your own network |
| [syncman](syncman.md) | v0.4.1 | user | synchronises folders in both directions |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | user | saves and switches display layouts in GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | user | provider module for kiwi-proxy: Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | user | provider module for kiwi-proxy: a VPN through gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | user | provider module for kiwi-proxy: 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | user | provider module for kiwi-proxy: Mysterium |

kiwi fetches the current catalog before every check and every update. You can
therefore manage the apps on a fleet of desktops with git alone:

- **To add an app**, add its URL to `apps.list` and commit.
- **To pin an app to a version or to roll it back**, append `ref=<tag>` to its
  line. On a single machine, `kiwi pin <app> <tag>` does the same.
- **To remove an app**, delete its line. Copies that are already installed
  stay installed until you uninstall them.

## Your own catalog

A catalog is a git repository with an `apps.list` file. It can also contain a
`catalog.manifest` file, in which the catalog describes itself:

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

A line in `apps.list` can have these options after the URL:

| Option | Meaning |
|---|---|
| `branch=<name>` | follow a branch instead of release tags |
| `ref=<tag>` | stay on exactly this version |
| `scope=user\|system` | install only that half of the app on machines that use this list. This option is a *filter*. It does not declare which scopes the app has |

Each machine also has a list of its own. It is
`~/.config/kiwi-updater/apps.list` for your user and
`/etc/kiwi-updater/apps.list` for root. An entry in the machine's own list
always takes precedence over a catalog. `kiwi add <url>` adds a line to this
list.

## Publishing an app

To publish an app, put a `kiwi.manifest` file and an `install.sh` script in the
top directory of your repository. You can find templates in the
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
directory of kiwi-updater.

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

A manifest can have more keys: `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`,
`ABOUT` (a file that Kiwi Apps shows), `DEPENDS` and `ROOT_REASON`. Every app
with a system half needs `ROOT_REASON`. `ICON=` names an SVG or PNG file of at
most 1 MiB inside the repository. Most Kiwi apps take their icon from
[kiwi-icons](../project/brand.md).

!!! warning "Put comments on their own line"
    A value continues to the end of its line. If you write
    `COMPONENTS=cli  # … gui …`, the comment becomes part of the value, and
    kiwi then treats the app as if it had a GUI.

kiwi runs your installer once **for each scope that the app declares**. It
sets these variables for the installer:

| Variable | Value |
|---|---|
| `KIWI_SCOPE` | `user` or `system` |
| `KIWI_PREFIX` | `~/.local` or `/usr/local` |
| `KIWI_APP_DIR` | absolute path of the clone |
| `KIWI_ACTION` | `install`, `update` or `uninstall` |
| `KIWI_GUI` | `0` on a headless machine (one without a graphical desktop), or with `--cli-only` |
| `KIWI_PURGE` | `1` when the user asked for `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` comes first. The system scope gets a fixed system path |

An installer for an app with both scopes must check `KIWI_SCOPE` and do only
the work for that half in each run. When the user did not ask for `--purge`,
leave the user's configuration where it is.

**Publish each release as a signed tag.** Only then can a system half be
updated without a password:

```bash
git config gpg.format ssh            # sign with your SSH key
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater provides a release workflow, `templates/release.yml`. It publishes
a GitHub release only for a tag that is signed with a key listed in
`.github/allowed_signers`, and it never creates tags itself. Finally, open a
pull request that adds your URL to the catalog. Every app is welcome that is
open source and can really be used without an account, a subscription or a
tracker.

## Trust

The catalog is **curated, not audited**. An app is listed because someone
thought it was worth having. It does not mean that its code has been reviewed.
Before you install an app that you do not know, read the output of
`kiwi info <app>`. Run `kiwi info --installer <app>` to see exactly what will
run.
