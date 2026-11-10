# kiwi-updater

`kiwi` installs and updates open-source apps from **git catalogs** on Fedora
Silverblue, Bluefin and other ostree systems. An app is a git repo with a
`kiwi.manifest` and an `install.sh`. kiwi clones it, checks out its latest
release tag, runs its installer, and keeps it updated in the background,
itself included.

There are no accounts, no store and no vendor. A catalog is a repo you can read,
fork and send a pull request to.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Latest release: **v2.4.0**, a security release
- **`kiwi`** is the CLI. It needs `git`, coreutils, `util-linux` and `awk`, all
  in the base image, plus `ssh-keygen` for signature checks.
- **Kiwi Apps** (`kiwi-gui`) is the GTK4 app: search, filters, a detail view per
  app with its icon, screenshots and dependencies. It shows the installer and
  an update's diff before running either, and queues your clicks. It reads only
  from the apps' clones, never from the network.

## Install

```bash
# recommended: user scope plus the root-owned system scope, one password prompt
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimal: 100 % user level, ~/.local only, no root and no password, ever
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# no passwordless action at all: every system change asks for a password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

The [Kiwi catalog](catalogs.md) is registered by the install. Go straight to
`kiwi list` or open **Kiwi Apps**.

Apps that are only files in your home (the CLI tools, ensconce, syncman) are
complete on the minimal install. An app with a root half, such as
kiwi-killswitch, needs the system scope. On a minimal install,
`kiwi install kiwi-killswitch` sets it up on the spot with one password.

## Commands

```bash
kiwi list [--check]          # every app this machine knows about
kiwi search vpn              # find an app in every registered catalog
kiwi info kiwi-killswitch    # what it is, what it installs, whether it needs root
kiwi install <app>           # a name, or an explicit --all
kiwi update [<app>]          # everything with a new release
kiwi uninstall <app>         # --purge also drops its config
kiwi check                   # exit 10 if anything has an update

kiwi add <https-url>         # track one repo directly, without a catalog
kiwi catalog add|list|remove # manage catalogs
kiwi sync                    # refresh catalogs now
kiwi self-update
kiwi trust --system <app>    # forget the signing key pinned for a system app
```

Before you run something, and when something goes wrong:

```bash
kiwi info --installer <app>  # the script an install would run, before it runs
kiwi diff <app>              # what an update would change, its installer included
kiwi pin <app> v1.2.0        # stay there; kiwi unpin <app> to follow releases again
kiwi install <app> --dry-run # scope, URL, ref, installer path, and nothing else
kiwi doctor                  # stale locks, version skew, bad list files, timers
```

## Releases are tags

An app follows its latest **version tag**, one matching
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Pre-releases
and scratch tags never overtake a release. A repo without a version tag follows
its default branch. `ref=<tag>` on a list line asks for a specific one.

## Dependencies

`DEPENDS=` in a manifest names what an app needs. A word that is an app in your
own catalog or list is installed **first**, in the same scope, at install time.
`kiwi install kiwi-plugin-tor`, for example, brings kiwi-proxy along. Any other
word is a program, checked with `command -v`.

## One app, two halves

Some apps are only a binary in `~/.local/bin`. Others, like a VPN kill switch,
are a root daemon **and** a desktop app **and** a GNOME extension. The halves
install with different privileges, because **root must never execute a file the
user can write**. The app declares it:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

A catalog lists that app once, and kiwi installs each half correctly. Before
asking for your password, it shows the `ROOT_REASON`.

| Piece | Where | Why |
|---|---|---|
| `kiwi`, Kiwi Apps, user apps | `~/.local` | no root needed; survives an ostree rebase |
| root's own copy of kiwi | `/usr/local/bin`, cloned into `/var/lib/kiwi-updater/repos/` | root never runs a file you can write |
| system apps | `/var/lib`, `/etc` | writable on ostree, root-owned |
| lists | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | a machine's own entries beat any catalog |
| pinned signing keys | `/etc/kiwi-updater/signers/<app>` | see below |

The immutable `/usr` is never touched.

## Root, passwords and signatures

| | Needs root | Asks for a password |
|---|---|---|
| anything in the user scope | no | no |
| **updating** a system app | yes | **no**, for a release signed by the key root pinned for that app. **Yes** for an unsigned release, and always in `manual` mode |
| **installing** or **uninstalling** a system app | yes | yes |

Since 2.4.0:

- **Signed releases.** Root pins one SSH signing key per system app, the first
  one it sees (trust on first use). A release tag signed by that key
  updates without a password. An unsigned release asks for one and says it could
  not verify. A tag signed by a different key, or an unsigned tag after signed
  ones, is refused until you run `kiwi trust --system <app>`. This applies to
  the system scope.
- **Root installs only sources it lists**: `/etc/kiwi-updater/apps.list` and
  catalogs registered for root. For anything else kiwi installs the user half
  and names the `kiwi add --system <https-url>` to run. Kiwi Apps offers
  *Register and Install*.
- **https only.** `http://` sources are refused everywhere.

Passwordless system updates go through one fixed-purpose helper,
`/usr/local/libexec/kiwi-system-update`. A polkit rule allows it for active
`wheel` sessions, and it takes app names only as a selection from root's own
lists.

## Background updates

There is one timer, and it is yours: `kiwi-updater.timer` runs
`kiwi update --all` six hours after the last run (ten minutes after boot, with
some random delay). It updates user halves directly, and system halves through
the helper above. There is no root timer. In `manual` mode, system halves wait
for your next interactive `kiwi update`.

## Trust

Installing an app **runs that repo's `install.sh`**, and an app that declares
the system scope runs it **as root**. Catalogs are curated, not audited. Add
the ones you trust, the way you would add a package repository, and use
`kiwi info --installer`, `kiwi diff` and `kiwi pin` to decide with your eyes
open. A signature narrows *who may publish*. It says nothing about *what the
published thing does*.

Still planned: a hosted registry of trusted catalogs (`kiwi catalog browse`)
with signer fingerprints per entry.
