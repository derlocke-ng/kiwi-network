# kiwi-updater

Install and update open-source apps from **git catalogs**, on Fedora Silverblue /
Bluefin and other ostree systems. An app is just a git repo with a
`kiwi.manifest` and an `install.sh`; `kiwi` clones it, checks out its latest
release tag, runs its installer, and keeps it updated in the background —
including itself.

No accounts, no store, no vendor. A [catalog](kiwi-catalog.md) is a repo you can
read, fork and send a pull request to.

- Repository: <https://github.com/derlocke-ng/kiwi-updater>
- License: GPL-3.0-or-later.

## What you get

- **`kiwi`** — the CLI (needs `git`, coreutils, `util-linux` for `flock`, and
  `awk`; all are in the Silverblue/Bluefin base image).
- **`kiwi-gui`** — the desktop app, **Kiwi Apps** in your app grid: search,
  filter and browse the catalogs, with a detail view per app.
- **Releases are git tags** — apps follow their latest version tag (one shaped
  like `v1.2.3`); pre-releases and scratch tags are never picked up by
  accident; untagged repos follow HEAD.
- **systemd timers** for background updates of user apps and, opt-in, system
  apps.

## Install

**Recommended** — the user scope plus the root-owned system scope, one password
prompt:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system
```

**Minimal** — 100% user-level (`~/.local`, no root, ever):

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Then register a catalog:

```bash
kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
kiwi list
```

## Use

```bash
kiwi list [--check]        # everything this machine knows about
kiwi search vpn            # find an app across every registered catalog
kiwi info kiwi-killswitch  # what it installs, and whether it needs root
kiwi install <app>         # a name, or an explicit --all
kiwi update                # everything with a new release
kiwi uninstall <app>       # --purge also drops its config
kiwi-gui                   # the desktop app ("Kiwi Apps")
```

Before you run something, and when something goes wrong:

```bash
kiwi info --installer <app>  # print the script an install would run
kiwi diff <app>              # what an update would change, installer included
kiwi pin <app> v1.2.0        # stay there; kiwi unpin <app> to follow releases
kiwi install <app> --dry-run # scope, URL, ref, installer path — and do nothing
kiwi doctor                  # stale locks, version skew, bad list files, timers
```

## One app, one line — even when it needs root

Some apps are only a binary in `~/.local/bin`. Others — a VPN kill switch, say —
are a root daemon **and** a desktop app **and** a GNOME extension. Those halves
install in different places with different privileges, because **root must never
execute a file the user can write**: system apps are cloned as root into
`/var/lib`, user apps into `~/.local`.

The app declares the split in its manifest:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

A catalog lists that app **once**. `kiwi` reads the manifest, installs each half
correctly, and before asking for your password it shows the `ROOT_REASON` so you
know what the password is for.

## The app convention

Put a `kiwi.manifest` and an `install.sh` in your repo root:

```ini
NAME=my-tool
DESCRIPTION=Short description
COMPONENTS=cli
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
INSTALLER=install.sh
```

`kiwi` runs your installer once per declared scope, with `KIWI_SCOPE`,
`KIWI_PREFIX`, `KIWI_APP_DIR`, `KIWI_ACTION`, `KIWI_GUI` and `KIWI_PURGE` in the
environment. Release by tagging: `git tag v1.3.0 && git push --tags`.

## Trust

Installing an app **runs that repo's `install.sh`**, and an app declaring the
system scope runs it **as root**. Catalogs are curated by whoever maintains
them — they are **not** audited. Add catalogs you trust, the same way you would
add a package repository. The tools for deciding deliberately exist:
`kiwi info --installer`, `kiwi diff` and `kiwi pin`. Signature verification is
planned.

## Why the split layout

| Piece | Location | Why |
|---|---|---|
| `kiwi`, `kiwi-gui`, user apps | `~/.local` | no root, survives an ostree rebase |
| root-owned `kiwi` copy (opt-in) | `/usr/local/bin` | the root update timer must never execute a user-writable file |
| system app repos / config | `/var/lib`, `/etc` | writable on ostree, root-owned |

The immutable `/usr` is never touched. If you never install a system app,
nothing outside your home is ever written. The shape mirrors flatpak: a user
installation needing no root, plus an optional system installation guarded by
polkit and a root-owned helper.

## Background updates

One timer, yours: `kiwi-updater.timer` runs `kiwi update --all` every six hours
as you. User halves it updates directly; system halves go through a
fixed-purpose, path-restricted polkit helper that authorises `wheel` users
without a prompt (or, in `--with-system=manual` mode, with a prompt every time).
There is no root timer — nothing of kiwi's runs as root except on behalf of your
update.
