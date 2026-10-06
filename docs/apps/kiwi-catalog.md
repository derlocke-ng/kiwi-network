# kiwi-catalog

The app catalog for the Kiwi Network, consumed by
[kiwi-updater](kiwi-updater.md). Register it once:

```bash
kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
```

- Repository: <https://github.com/derlocke-ng/kiwi-catalog>

`kiwi` syncs this repo before every check and update, so managing a fleet is
just git:

- **add an app** → add its URL to `apps.list` and commit
- **pin or roll back** → append `ref=<tag>` (on one machine, `kiwi pin <app>
  <tag>` does the same locally)
- **remove** → delete the line (installed copies stay until uninstalled)

A machine's own `apps.list` always wins over a catalog.

## What's in the catalog

The default catalog ships the Kiwi apps:

- [kiwi-updater](kiwi-updater.md)
- [kiwi-killswitch](../privacy-apps/kiwi-killswitch.md)
- [kiwi-fox](../privacy-apps/kiwi-fox.md) and its
  [provider plugins](../privacy-apps/plugins.md) (tor, vpn, 9proxy, myst)
- [kiwi-cli-tools-desktop](../privacy-apps/cli-tools.md)
- `ensconce` (dotfile / config manager)

[kiwi-server](../build/kiwi-server.md) and
[kiwi-pentesting](../privacy-apps/kiwi-pentesting.md) are also kiwi apps and can
be installed the same way.

## One line per app

An app that installs both a root service and a desktop component is listed
**once**. Its `kiwi.manifest` declares `SCOPES=user system` and `kiwi` installs
each half correctly — the user half from `~/.local`, the system half cloned and
run as root, so root never executes a file the user can write.

`scope=` on a catalog line is a *filter* for machines that should only get one
half, not a declaration.

## Adding your app

Put a `kiwi.manifest` and an `install.sh` in your repo root, tag a release, then
open a PR adding the URL. Anything open source and genuinely usable without an
account, a subscription or a tracker is welcome. If your app needs root, say why
in `ROOT_REASON=` — `kiwi` shows that sentence before it asks for a password.

## Trust

Installing an app runs that repo's `install.sh`, and an app declaring the system
scope runs it **as root**. This catalog is curated, not audited — being listed
here means someone thought the app was worth having, not that its code has been
reviewed. Read `kiwi info <app>` before installing something you do not already
know.
