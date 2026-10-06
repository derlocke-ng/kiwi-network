# kiwi-network

Kiwi Network is an all-in-one, privacy-first approach to self-hosted
infrastructure for private individuals, SMBs, and public offices.

The core idea is simple: **expose as little as possible.**

- **Public Internet**: only the WireGuard entry point
- **Private network**: everything else (services live behind the tunnel)

This repository hosts the project's **homepage** and **documentation**. The
software itself lives in the other `kiwi-*` repositories under
[derlocke-ng](https://github.com/derlocke-ng).

- Homepage: <https://kiwi-network.eu> (see the `site/` folder)
- Documentation: <https://docs.kiwi-network.eu> (MkDocs in `docs/`)

## The three machine roles

- **kiwi-master** — the public-facing entry point (WireGuard + outbound VPN hop,
  Pi-hole DNS, optional Tor).
- **kiwi-node** — private services connected to the master via WireGuard
  (Nextcloud, Vaultwarden, reverse proxy, downloads) or a LAN gateway.
- **kiwi-workstation** — an easy-to-use immutable desktop OS (Fedora Silverblue
  / Bluefin DX) running the Kiwi apps.

The server roles are no longer hand-assembled — they are built by tooling.

## The ecosystem

| Repository | What it is |
|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | Build the fleet: one `fleet.yaml` → first-boot scripts + unattended install ISOs for `master` / `node-gw` / `node-cloud`, on CoreOS, uCore or Debian |
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | Install & update open-source apps from git catalogs on ostree desktops (CLI + GTK4 "Kiwi Apps") |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | The default app catalog consumed by kiwi-updater |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | Isolated Windows 11 browser identities in rootless Podman |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) · [vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) · [9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) · [myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | kiwi-fox provider modules (Tor, gluetun VPN, 9proxy, Mysterium exits) |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | Fail-closed VPN kill switch for GNOME on Silverblue/Bluefin |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | Browser-based SSH/TLS key & certificate generator (local encrypted vault) |
| [kiwi-pentesting](https://github.com/derlocke-ng/kiwi-pentesting) | Containerized authorized-testing suite, a client of kiwi-fox |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | Small desktop CLI helpers: `pweb`, `select-server`, `tethering` |
| [kiwi-blog](https://github.com/derlocke-ng/kiwi-blog) | A lightweight Markdown static-site generator |

See the [documentation](https://docs.kiwi-network.eu) for how they fit together.

## This repository

```
site/        the static homepage (kiwi-network.eu)
docs/        the MkDocs documentation (docs.kiwi-network.eu)
mkdocs.yml   docs configuration
```

## Docs (MkDocs)

Run locally:

- Install: `python -m pip install mkdocs-material`
- Serve: `mkdocs serve`
- Build: `mkdocs build`

MkDocs output goes to `build/docs` so it does not clash with the `site/`
homepage folder. GitHub Pages serves the homepage at the root and the docs under
`/docs` (see `.github/workflows/pages.yml`).

## License

The content of this repository is AGPL-3.0 (see `LICENSE`). The individual
`kiwi-*` tools carry their own licenses — most are GPL-3.0-or-later, a few
(kiwi-gen, kiwi-blog) are MIT.
