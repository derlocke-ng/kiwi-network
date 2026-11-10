# kiwi-updater

kiwi-updater installs open-source apps on your desktop and keeps them up to
date. Its command is `kiwi`. It gets the apps from **git catalogs** and works
on Fedora Silverblue, Bluefin and other ostree systems. A catalog is a git
repository that lists apps. An app is a git repository with a `kiwi.manifest`
file and an `install.sh` script. kiwi clones the app's repository, checks out
its latest release tag and runs its installer. After that it updates the app in
the background, and it updates itself in the same way.

You do not need an account, and there is no app store and no vendor. A catalog
is a repository that you can read, fork and send a pull request to.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Latest release: **v2.4.0**, a security release
- **`kiwi`** is the command-line tool (CLI). It needs `git`, coreutils,
  `util-linux` and `awk`, which are all part of the base image. To check
  signatures it also needs `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) is the desktop app, built with GTK4. You can
  search and filter the apps, and each app has a detail view with its icon,
  screenshots and dependencies. Kiwi Apps shows you the installer before it
  installs an app, and what an update changes before it updates one. When
  you click several actions in a row, it puts them in a queue. It gets its
  data from the CLI. It reads icons and screenshots from the local clones of
  the apps, so it does not download anything to show them.

## Install

kiwi works in two scopes. The user scope is everything in your home directory
and never needs root. The system scope is a part that is owned by root, for
apps that need root. You choose at install time how much of the system scope
you want:

```bash
# recommended: user scope plus the root-owned system scope, one password prompt
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimal: 100 % user level, ~/.local only, no root and no password, ever
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# no passwordless action at all: every system change asks for a password
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

The installation registers the [Kiwi catalog](catalogs.md), so you can run
`kiwi list` or open **Kiwi Apps** right away.

Some apps consist only of files in your home directory, for example the CLI
tools, ensconce and syncman. These apps are complete on the minimal install. An
app with a half that runs as root, such as kiwi-killswitch, needs the system
scope. On a minimal install, `kiwi install kiwi-killswitch` sets up the system
scope at that moment and asks for your password once.

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

The following commands show you what an app will do before you run it, and
they help when something goes wrong:

```bash
kiwi info --installer <app>  # the script an install would run, before it runs
kiwi diff <app>              # what an update would change, its installer included
kiwi pin <app> v1.2.0        # stay there; kiwi unpin <app> to follow releases again
kiwi install <app> --dry-run # scope, URL, ref, installer path, and nothing else
kiwi doctor                  # stale locks, version skew, bad list files, timers
```

## Releases are tags

kiwi uses git tags as releases. An app follows its latest **version tag**. A
version tag is a tag that matches `^v?[0-9]+(\.[0-9]+){0,3}$`, for example
`v1`, `v1.2`, `1.2.3` or `v1.2.3.4`. Pre-release tags and temporary tags do not
match, so they are never used in place of a release. A repository without a
version tag follows its default branch. To ask for one specific version, add
`ref=<tag>` to the app's line in a list.

## Dependencies

The `DEPENDS=` line in a manifest names what an app needs. If a word in that
line is the name of an app in your own catalog or list, kiwi installs that app
**first**, in the same scope, at the time you install the app that needs it.
For example, `kiwi install kiwi-plugin-tor` also installs kiwi-proxy. kiwi
treats every other word as the name of a program and checks with `command -v`
whether that program is present.

## One app, two halves

Some apps are only one program in `~/.local/bin`. Others, such as a VPN kill
switch, consist of a daemon that runs as root **and** a desktop app **and** a
GNOME extension. Such an app has two halves, a user half and a system half, and
the halves are installed with different privileges. The reason is that **root
must never execute a file the user can write**. The app declares its parts and
its scopes in its manifest:

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

A catalog lists such an app only once, and kiwi installs each half in the right
scope. Before kiwi asks for your password, it shows you the `ROOT_REASON`.

| Piece | Where | Why |
|---|---|---|
| `kiwi`, Kiwi Apps, user apps | `~/.local` | needs no root, and is kept when the system is rebased to another ostree image |
| root's own copy of kiwi | `/usr/local/bin`, cloned into `/var/lib/kiwi-updater/repos/` | root never runs a file that you can write |
| system apps | `/var/lib`, `/etc` | these directories are writable on ostree systems and owned by root |
| lists | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | the entries in a machine's own list take precedence over every catalog |
| pinned signing keys | `/etc/kiwi-updater/signers/<app>` | see the next section |

kiwi never changes anything in the immutable `/usr`.

## Root, passwords and signatures

The table shows which actions need root and which actions ask for a password.

| | Needs root | Asks for a password |
|---|---|---|
| anything in the user scope | no | no |
| **updating** a system app | yes | **no**, if the release is signed with the key that root has pinned for that app. **Yes**, if the release is unsigned, and always in `manual` mode |
| **installing** or **uninstalling** a system app | yes | yes |

Since version 2.4.0, these rules apply:

- **Signed releases.** For each system app, root pins one SSH signing key. To
  pin a key means to remember it and to accept only that key from then on. Root
  pins the first key it sees for the app, which is called trust on first use.
  If a release tag is signed with the pinned key, the update is installed
  without a password. If a release is unsigned, kiwi asks for your password and
  says that it could not verify the release. kiwi refuses a tag that is signed
  with a different key, and it refuses an unsigned tag when earlier tags were
  signed. It refuses them until you run `kiwi trust --system <app>`. These
  rules apply to the system scope.
- **Root installs only from sources that it lists itself.** These sources are
  `/etc/kiwi-updater/apps.list` and the catalogs that are registered for root.
  If an app comes from any other source, kiwi installs only the user half and
  names the `kiwi add --system <https-url>` command that you have to run. Kiwi
  Apps offers *Register and Install* in this case.
- **Only https.** kiwi refuses `http://` sources everywhere.

System updates without a password are done by one helper program,
`/usr/local/libexec/kiwi-system-update`, which has only this one purpose. A
polkit rule allows users in the `wheel` group to run it when their session is
active. The helper accepts only app names, and a name can only select an app
from root's own lists.

## Background updates

There is one timer for background updates, and it is a user timer, so it runs
as your user and not as root. `kiwi-updater.timer` runs `kiwi update --all` six
hours after the last run, and ten minutes after boot, with some random delay.
This run updates user halves directly. It updates system halves through the
helper described above. There is no root timer. In `manual` mode the timer does
not update system halves. They wait until you run `kiwi update` yourself.

## Trust

When you install an app, kiwi **runs the `install.sh` from that app's
repository**. If the app declares the system scope, kiwi runs this script **as
root**. Catalogs are curated, not audited. This means that someone has selected
the apps. It does not mean that their code has been reviewed. Add only the
catalogs that you trust, in the same way as you would add a package repository.
Use `kiwi info --installer`, `kiwi diff` and `kiwi pin` to see what an app does
before you decide. A signature limits *who may publish* a release. It says
nothing about *what the published release does*.

One thing is still planned: a hosted registry of trusted catalogs, with the
command `kiwi catalog browse` and with the fingerprints of the signers for each
entry.
