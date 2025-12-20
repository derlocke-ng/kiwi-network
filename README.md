# kiwi-network

Kiwi Network is an all-in-one, privacy-first approach to self-hosted infrastructure for private individuals, SMBs, and public offices.

The core idea is simple: expose as little as possible.

- **Public Internet**: only the WireGuard entry point
- **Private network**: everything else (services live behind the tunnel)

## Components

- **kiwi-master**: the public-facing entry point (WireGuard + network services)
  - Example services: `wg-easy`, `gluetun`, `pihole`, optional Tor proxy, optional Portainer
- **kiwi-node**: local/private services connected to the master via WireGuard
  - Example services: Nextcloud (AIO), NGINX reverse proxy, Vaultwarden, downloads/services via Docker
- **kiwi-workstation**: an easy-to-use workstation OS
  - Based on Fedora Silverblue / Bluefin DX

## This repository

This repo hosts:

- **Homepage**: https://kiwi-network.eu (see the `site/` folder)
- **Documentation**: https://docs.kiwi-network.eu (MkDocs in `docs/`)
- **References** to the other repos (some may not exist yet)

## Docs (MkDocs)

Run locally:

- Install: `python -m pip install mkdocs-material`
- Serve: `mkdocs serve`
- Build: `mkdocs build`

MkDocs output is configured to go to `build/docs` so it does not clash with the `site/` homepage folder.

## Planned repos

- `kiwi-master` (docker-compose + configs)
- `kiwi-node` (docker-compose + configs)
- `kiwi-workstation` (OS customization)
- `kiwi-iso` (ISO build tooling)

## License

AGPL-3.0 (see `LICENSE`).
