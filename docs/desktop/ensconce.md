# ensconce

Modular post-installation setup for [Bluefin-DX](https://projectbluefin.io/).
ensconce turns a fresh Bluefin install into your configured workstation:
layered packages, Flatpaks, GNOME extensions, Nextcloud sync, desktop settings,
the login screen and more, all from plain list files.

- Repository: [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce), GPL-3.0
- Latest release: **v2.1.1**. It is in the [Kiwi catalog](catalogs.md).

## Quick start

```bash
kiwi install ensconce
ensconce --init          # create ~/.config/ensconce from the examples
ensconce                 # run the setup
```

Or from a clone:

```bash
git clone https://github.com/derlocke-ng/ensconce.git && cd ensconce
./ensconce.sh --init     # creates config/ from the examples
./ensconce.sh
```

## Steps

Each phase is a self-contained script in `steps/`, run in order:

| Step | Does |
|---|---|
| `rebase` | switch to Bluefin-DX |
| `ujust` | developer groups and CLI tools |
| `repos` | add RPM repositories |
| `packages` | layer RPM packages |
| `flatpaks` | install Flatpak apps |
| `overrides` | Flatpak permission overrides |
| `extensions` | GNOME Shell extensions |
| `cacert` | custom CA certificates (your fleet's `kiwiCA.pem`, for example) |
| `nextcloud` | preseed Nextcloud folder sync |
| `dconf` | GNOME desktop settings |
| `gdm` | login screen (GDM) settings |

ensconce saves its progress and resumes after reboots. It checks the
environment before running, and keeps the machine awake for the whole run
(logind inhibitor, a GNOME session inhibitor and the power settings, which are
restored afterwards).

```bash
ensconce --dry-run                  # preview without changing anything
ensconce --skip rebase,ujust        # skip steps
ensconce --only extensions,dconf    # run only these
ensconce --status                   # progress
ensconce --list-steps
ensconce --reset                    # clear progress, start fresh
ensconce --log [file]               # save the output
```

## Configuration

`ensconce --config-dir` prints the active directory: `$ENSCONCE_CONFIG`, then
`~/.config/ensconce/` (installed via kiwi), then `config/` in a clone.

| File / directory | Purpose |
|---|---|
| `settings.sh` | server URLs, feature toggles |
| `packages.list` | RPM packages to layer, one per line |
| `flatpaks.list` | Flatpak app IDs |
| `extensions.list` | GNOME extension UUIDs |
| `repos.d/` | `.repo` files for `/etc/yum.repos.d/` |
| `flatpak-overrides/` | per-app overrides, in Flatpak's own format |
| `nextcloud/folders.list` | sync folders as `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | global and per-folder (tagged) sync exclusions |
| `certs/` | CA certificates (`.pem`) |
| `dconf-settings.ini` | GNOME settings |
| `gtk3-bookmarks` | Nautilus sidebar bookmarks |
| `gdm/dconf.d/`, `gdm/monitors.xml` | login screen settings and display layout |

A per-folder exclusion tag such as `browser` places `exclude.d/browser.lst` as
`.sync-exclude.lst` in that folder. That keeps a browser profile's SQLite
databases from being synced (and corrupted), while files like `user.js` still
sync.

## Cloning a machine

`--export` reads the live system and writes an ensconce config tree, the inverse
of the steps. Set one machine up by hand, export it, edit, and run ensconce on
the next one:

```bash
ensconce --export ./my-setup        # on the configured machine
ensconce --init                     # on the new machine
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

The export captures only what you added: requested `rpm-ostree` packages (not
the whole image), extensions actually from extensions.gnome.org, your own repo
files (Bluefin's own are exported as `.repo.disabled`), and curated dconf
subtrees rather than a full dump. Treat an export as a starting point. `certs/`
and `nextcloud/` can contain private material, so check before sharing one.

## Notes

- It is a **user-scope** app. The steps that need root (`rpm-ostree`, `/etc`,
  GDM) ask for it themselves. Installing it as root would apply your dconf and
  Flatpak settings to the wrong account.
- Add your own step by dropping `NN-name.sh` with a `step_name()` function into
  `steps/`. It is discovered automatically.
