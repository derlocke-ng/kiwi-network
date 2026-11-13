# kiwi-updater

kiwi-updater installs open-source apps on your computer and keeps them up to
date. Its command is `kiwi`. It gets the apps from **git catalogs**: a catalog
is a git repository that lists apps, and an app is a git repository with a
`kiwi.manifest` file and an `install.sh` script. kiwi clones the app, checks
out its newest release tag and runs its installer. After that it updates the
app in the background, and it updates itself the same way.

You do not need an account, and there is no app store and no vendor. A catalog
is a repository that you can read, fork and send a pull request to. All Kiwi
desktop apps are installed this way.

- Repository: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Latest release: **v2.5.1**
- **`kiwi`** is the command-line tool. **Kiwi Apps** (`kiwi-gui`) is the
  desktop app: you can browse and search the apps, install them, and read an
  app's installer before it runs.

## Where it runs

kiwi-updater was built for Fedora Atomic desktops, and it now runs on other
Linux distributions as well. Every change to kiwi-updater is tested with the
full test suite and a real install on these systems:

| System | What works |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | everything |
| Alpine | everything, once the GNU tools are installed |
| Debian 12, Ubuntu 22.04 (tested, but not on every change) | `kiwi` and command-line apps. Their libadwaita is too old for the desktop apps |

## Install

This installs the user part in your home directory and the root part for apps
that need root, with one password prompt:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

If you want nothing outside your home directory, and never a password prompt,
install only the user part:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

The installer checks that the release it installs is signed by kiwi-updater's
release key, and it refuses one that is not. The Kiwi catalog is registered
during the install. Then:

```bash
kiwi list                    # every app you can install
kiwi install <app>           # install one
kiwi info --installer <app>  # read its installer before it runs
kiwi-gui                     # the desktop app
```

## Root parts and signed releases

Some apps need root, for example kiwi-killswitch, which has a firewall daemon.
Their root part is installed by a root-owned copy of kiwi, and only from
sources that root itself lists. Installing or removing such an app always asks
for your password. In the default mode, an update runs without a password only
if the release is signed by the key that root stored for that app.

## The full documentation

kiwi-updater documents itself in its own repository:

| Page | What it covers |
|---|---|
| [Install](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | supported systems, packages per distribution, install modes, uninstalling |
| [Using kiwi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | every command, Kiwi Apps, background updates, settings |
| [Catalogs](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | adding catalogs, `apps.list`, pins and overrides |
| [Security](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | what runs as root, when you type a password, what kiwi checks |
| [Writing an app](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, dependencies, icons, releases |
| [Signed releases](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | signing your app's releases with `kiwi-release` |
| [Development](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | tests, CI, releasing kiwi-updater |

From kiwi-updater's next release on, these pages also appear here, in the menu
under kiwi-updater.

To publish your own app, see [Catalogs & publishing](catalogs.md).
