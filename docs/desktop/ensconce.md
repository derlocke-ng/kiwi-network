# ensconce

ensconce sets up a freshly installed [Bluefin-DX](https://projectbluefin.io/)
for you, so that you do not have to configure every new machine by hand. You
describe your workstation in plain list files, and ensconce turns the fresh
install into that workstation. It handles layered packages, Flatpaks, GNOME
extensions, Nextcloud sync, an SSH config that is synchronised between your
machines, the settings of the desktop and the login screen, and your Kiwi apps.
Layered packages are RPM packages that are added on top of the system image.
The setup is modular, which means that it consists of separate steps that you
can run or skip.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  The license is GPL-3.0-or-later according to its manifest. The README says
  GPL-3.0.
- Latest release: **v2.5.0**. It is in the [Kiwi catalog](catalogs.md) and is
  installed in the user scope, which is your home directory.

```bash
kiwi install ensconce
ensconce --init          # create ~/.config/ensconce from the examples
ensconce                 # run the setup
```

You can also run it from a clone of the repository. Run `./ensconce.sh --init`,
edit the files in `config/`, then run `./ensconce.sh`.

## Steps

The setup is divided into steps. Each step is a script in `steps/`, and the
steps run in this order:

| # | Step | Does |
|---|---|---|
| 01 | `rebase` | switches the system to Bluefin-DX |
| 02 | `ujust` | sets up developer groups and CLI tools |
| 03 | `repos` | adds RPM repositories |
| 04 | `packages` | layers RPM packages |
| 05 | `flatpaks` | installs Flatpak apps. `FLATPAK_LANGUAGES` selects the languages of their translations |
| 06 | `overrides` | sets Flatpak permission overrides |
| 07 | `extensions` | installs GNOME Shell extensions |
| 08 | `cacert` | installs custom CA certificates |
| 09 | `nextcloud` | configures the Nextcloud folder sync in advance |
| 10 | `dconf` | applies GNOME desktop settings |
| 11 | `gdm` | configures the login screen |
| 12 | `ssh` | sets up the synchronised SSH config, with Bitwarden or GNOME as the SSH agent |
| 13 | `kiwi` | installs kiwi-updater in the way that `KIWI_INSTALL=recommended\|manual\|minimal` selects, and then every app in `kiwi-apps.list` |
| 14 | `sysctl` | installs the kernel settings files from `sysctl.d/`. An example file limits how much unwritten data the kernel keeps in memory, which helps on slow SSDs |
| 15 | `power` | with `SYSTEM_SLEEP=off`, masks the sleep targets, so that the machine cannot go to sleep |

Before it starts, ensconce checks the environment. The system must be a
Bluefin image, and `rpm-ostree`, `flatpak`, `dconf`, `jq` and `curl` must be
available. ensconce saves its progress, so it continues where it stopped after
a reboot. It keeps the machine awake for the whole run and restores your power
settings afterwards.

These options control a run:

```bash
ensconce --dry-run                  # preview without changing anything
ensconce --skip rebase,ujust        # skip steps
ensconce --only extensions,dconf    # run only these
ensconce --status | --list-steps | --reset
ensconce --log [file]               # save the output
ensconce --config-dir               # print the active config directory
```

## Configuration

ensconce looks for its configuration directory in four places and uses the
first one that exists. It looks at `$ENSCONCE_CONFIG` first, then at
`~/.config/ensconce/`, which is used when ensconce was installed with kiwi,
then at `config/` in a clone, and finally at `config.example/`. When it uses
`config.example/`, it prints a warning.

| File / directory | Purpose |
|---|---|
| `settings.sh` | server URLs, and the switches for SSH, kiwi-updater, Flatpak languages and sleep |
| `packages.list`, `flatpaks.list`, `extensions.list` | the packages, Flatpaks and GNOME extensions to install, one item per line |
| `kiwi-apps.list` | the Kiwi apps to install |
| `repos.d/`, `flatpak-overrides/` | repository files, and overrides for individual apps in Flatpak's own format |
| `nextcloud/folders.list` | the folders to synchronise, written as `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | what is excluded from synchronisation, for all folders and for individual folders that have a tag |
| `certs/` | CA certificates (`.pem`), for example your fleet's `kiwiCA.pem` |
| `sysctl.d/` | kernel settings |
| `dconf-settings.ini`, `gtk3-bookmarks` | GNOME settings and Nautilus bookmarks |
| `gdm/dconf.d/`, `gdm/monitors.xml` | the settings and the display layout of the login screen |

A tag in `nextcloud/folders.list` gives a folder its own exclusions. For
example, the tag `browser` places `exclude.d/browser.lst` in that folder. The
databases of a browser profile are then not synchronised, because
synchronising them can corrupt them, while `user.js` is still synchronised.

## Cloning a machine

`--export` does the opposite of the steps. It reads the running system and
writes an ensconce configuration directory from it. You can then set up a new
machine with that directory:

```bash
ensconce --export ./my-setup        # on the configured machine
ensconce --init                     # on the new one
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

The export contains only what you added to the system. It lists the packages
that you requested and not the whole image. It lists only the extensions that
really come from extensions.gnome.org. It contains your own repository files,
and selected dconf subtrees in place of a full dump. Treat the export as a
starting point. `certs/` and `nextcloud/` can contain private material.

ensconce is a **user-scope** app. The steps that need root ask for it
themselves. To add a step of your own, create a file `steps/NN-<name>.sh` with
a function `step_<name>()`.
