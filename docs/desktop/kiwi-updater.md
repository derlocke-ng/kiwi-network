# kiwi-updater

`kiwi` installs and updates open-source apps from **git catalogs** on Fedora
Silverblue, Bluefin and other ostree systems. An app is a git repo with a
`kiwi.manifest` and an `install.sh`. kiwi clones it, checks out its latest
release tag, runs its installer, and keeps it updated in the background,
including kiwi itself.

There are no accounts, no store and no vendor. A catalog is a repo you can read,
fork and send a pull request to.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Latest release: **v2.0.0**
- **`kiwi`** is the CLI. It needs `git`, coreutils, `util-linux` (`flock`) and
  `awk`, all of which are in the Silverblue/Bluefin base image.
- **`kiwi-gui`** is the desktop app, **Kiwi Apps**: search, filter and browse
  the catalogs, with a detail view per app. It is a thin layer over
  `kiwi list --porcelain`; the CLI is the single source of truth.

## Install

**Recommended:** the user scope plus the root-owned system scope, with one
password prompt:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system
```

**Minimal:** 100% user-level. Everything goes in `~/.local`, with no root and no
password, ever:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Apps that are only files in your home (the CLI tools, ensconce, kiwi-fox) are
complete on the minimal install. An app with a root half, such as
kiwi-killswitch, needs the system scope. If it is missing,
`kiwi install kiwi-killswitch` sets it up on the spot with one password. If you
would rather type a password for *every* system change than allow passwordless
system updates, use `--with-system=manual`. It installs the same thing without
the polkit rule.

Then register a catalog:

```bash
kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
kiwi list
```

## Commands

```bash
kiwi list [--check]          # every app this machine knows about
kiwi search vpn              # find an app across all registered catalogs
kiwi info kiwi-killswitch    # what it is, what it installs, whether it needs root
kiwi install <app>           # a name, or an explicit --all
kiwi update [<app>]          # everything with a new release
kiwi uninstall <app>         # --purge also drops its config
kiwi check                   # exit 10 if anything has an update

kiwi add <git-url>           # track one repo directly, without a catalog
kiwi catalog add|list|remove # manage catalogs
kiwi sync                    # refresh catalogs now
kiwi self-update             # update kiwi itself
```

Before you run something, and when something goes wrong:

```bash
kiwi info --installer <app>  # print the script an install would run, before it runs
kiwi diff <app>              # what an update would change, its installer included
kiwi pin <app> v1.2.0        # stay on that tag; kiwi unpin <app> to follow releases
kiwi install <app> --dry-run # scope, URL, ref, installer path, and do nothing
kiwi doctor                  # stale locks, version skew, bad list files, timers
```

Options: `--user` / `--system` (limit to one scope), `--cli-only` / `--gui`,
`--purge`, `--force`, `--dry-run`, `--quiet`, `--notify`.

## Releases are git tags

An app follows its latest **version tag**: one matching
`^v?[0-9]+(\.[0-9]+){0,3}$`, such as `v1`, `v1.2`, `1.2.3` or `v1.2.3.4`. Tags
like `v2.0.0-rc1`, `nightly` or `wip-test` do not count, so a pre-release never
overtakes the release it precedes. A repo with no version tag follows its
default branch. You can still ask for a specific tag with `ref=v2.0.0-rc1` on an
`apps.list` line.

## Dependencies

An app's `DEPENDS=` lists what it needs. A word that resolves to an app in a
registered catalog or list is installed *first* (the kiwi-fox providers depend
on kiwi-fox, for example). Any other word is a plain binary checked with
`command -v`, and kiwi warns if it is missing.

## One app, one line, even when it needs root

Some apps are only a binary in `~/.local/bin`. Others, like a VPN kill switch,
are a root daemon **and** a desktop app **and** a GNOME extension. Those halves
install in different places with different privileges, because **root must
never execute a file the user can write**. System apps are cloned as root into
`/var/lib`; user apps go into `~/.local`.

The app declares this in its manifest:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

A catalog lists that app **once**. kiwi installs each half correctly, and shows
`ROOT_REASON` before asking for your password, so you know what the password is
for.

## Where things go

| Piece | Location | Why |
|---|---|---|
| `kiwi`, `kiwi-gui`, user apps | `~/.local` | no root needed, survives an ostree rebase |
| root-owned `kiwi` copy (opt-in) | `/usr/local/bin` (the writable `/var/usrlocal`) | the root half must never execute a user-writable file |
| system app repos and config | `/var/lib`, `/etc` | writable on ostree, root-owned |
| your list / root's list | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | a machine's own entries always beat catalog entries |

The immutable `/usr` is never touched. If you never install a system app,
nothing outside your home is ever written. The shape is flatpak's: a user
installation that needs no root, plus an optional system installation guarded
by polkit and a root-owned helper.

## Background updates

There is one timer, and it is yours: `kiwi-updater.timer` runs
`kiwi update --all` every six hours, as you. It updates user halves directly.
System halves, including kiwi's own root-owned copy, go through
`/usr/local/libexec/kiwi-system-update`, a fixed-purpose helper that the polkit
rule allows for active `wheel` sessions without a password. It only updates apps
already in root's list or root's catalogs, never anything new. There is no root
timer. With `--with-system=manual`, system halves wait for your next interactive
`kiwi update`, where you type the password.

| | Needs root | Asks for a password |
|---|---|---|
| anything in the user scope | no | no |
| **updating** a system app | yes | **no** (yes with `manual`) |
| **installing** a system app | yes | yes |
| **uninstalling** a system app | yes | yes |

## Trust

Installing an app **runs that repo's `install.sh`**, and an app that declares
the system scope runs it **as root**. kiwi says so when you add a catalog.
Catalogs are curated by whoever maintains them; they are not audited. Add
catalogs you trust, the way you would add a package repository.

The tools for deciding deliberately: `kiwi info --installer` shows the script
before the first install, `kiwi diff` shows an update's changes (the installer's
diff in full), and `kiwi pin` holds a version until you move it.

Still planned in kiwi-updater:

- a hosted registry of trusted catalogs (`kiwi catalog browse`);
- signature verification (`signer=<fingerprint>`, checked with `git verify-tag`
  before an installer runs).

A signature narrows *who may publish*. It says nothing about *what the published
thing does*. Pinning and diffs are what let you see the change.
