# ensconce

Modular post-installation setup for [Bluefin-DX](https://projectbluefin.io/).
ensconce turns a fresh Bluefin install into your configured workstation from
plain list files: layered packages, Flatpaks, GNOME extensions, Nextcloud sync,
a synced SSH config, desktop and login-screen settings, and your Kiwi apps.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (its manifest; the README says GPL-3.0)
- Latest release: **v2.5.0**. It is in the [Kiwi catalog](catalogs.md), user scope.

```bash
kiwi install ensconce
ensconce --init          # create ~/.config/ensconce from the examples
ensconce                 # run the setup
```

Or from a clone: `./ensconce.sh --init`, edit `config/`, then `./ensconce.sh`.

## Steps

Each phase is a script in `steps/`, run in order:

| # | Step | Does |
|---|---|---|
| 01 | `rebase` | switch to Bluefin-DX |
| 02 | `ujust` | developer groups and CLI tools |
| 03 | `repos` | add RPM repositories |
| 04 | `packages` | layer RPM packages |
| 05 | `flatpaks` | install Flatpak apps (`FLATPAK_LANGUAGES` picks their translations) |
| 06 | `overrides` | Flatpak permission overrides |
| 07 | `extensions` | GNOME Shell extensions |
| 08 | `cacert` | custom CA certificates |
| 09 | `nextcloud` | preseed Nextcloud folder sync |
| 10 | `dconf` | GNOME desktop settings |
| 11 | `gdm` | the login screen |
| 12 | `ssh` | a synced SSH config, with Bitwarden or GNOME as the SSH agent |
| 13 | `kiwi` | install kiwi-updater (`KIWI_INSTALL=recommended\|manual\|minimal`) and every app in `kiwi-apps.list` |
| 14 | `sysctl` | drop-ins from `sysctl.d/` (an example caps dirty writeback for slow SSDs) |
| 15 | `power` | `SYSTEM_SLEEP=off` masks the sleep targets |

ensconce checks the environment first (a Bluefin image, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). It saves its progress and resumes after
reboots, and keeps the machine awake for the whole run, restoring your power
settings afterwards.

```bash
ensconce --dry-run                  # preview without changing anything
ensconce --skip rebase,ujust        # skip steps
ensconce --only extensions,dconf    # run only these
ensconce --status | --list-steps | --reset
ensconce --log [file]               # save the output
ensconce --config-dir               # print the active config directory
```

## Configuration

The config directory is the first that exists of: `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (installed via kiwi), `config/` in a clone, and
`config.example/` (with a warning).

| File / directory | Purpose |
|---|---|
| `settings.sh` | server URLs and switches: SSH, kiwi-updater, Flatpak languages, sleep |
| `packages.list`, `flatpaks.list`, `extensions.list` | one item per line |
| `kiwi-apps.list` | the Kiwi apps to install |
| `repos.d/`, `flatpak-overrides/` | repo files; per-app overrides in Flatpak's own format |
| `nextcloud/folders.list` | sync folders as `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | global and per-folder (tagged) sync exclusions |
| `certs/` | CA certificates (`.pem`), for example your fleet's `kiwiCA.pem` |
| `sysctl.d/` | kernel settings |
| `dconf-settings.ini`, `gtk3-bookmarks` | GNOME settings, Nautilus bookmarks |
| `gdm/dconf.d/`, `gdm/monitors.xml` | the login screen's settings and display layout |

A per-folder exclusion tag such as `browser` places `exclude.d/browser.lst` in
that folder, which keeps a browser profile's databases from being synced (and
corrupted) while `user.js` still syncs.

## Cloning a machine

`--export` reads the live system and writes an ensconce config tree, the
inverse of the steps:

```bash
ensconce --export ./my-setup        # on the configured machine
ensconce --init                     # on the new one
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

It captures only what you added: requested packages rather than the whole
image, extensions actually from extensions.gnome.org, your own repo files, and
curated dconf subtrees rather than a full dump. Treat it as a starting point.
`certs/` and `nextcloud/` can hold private material.

ensconce is a **user-scope** app. The steps that need root ask for it
themselves. Add your own step as `steps/NN-<name>.sh` with a `step_<name>()`
function.
