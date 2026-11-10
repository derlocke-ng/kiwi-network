# Repositories & status

Every repository lives under [github.com/derlocke-ng](https://github.com/derlocke-ng).
"Released" means a version tag, which is what kiwi-updater installs. Versions
are as of November 2026.

## The network

| Repository | What it is | Release | Catalog | License |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | build and run the network: fleet file → install ISOs → apply over SSH | v2.42.0 | yes | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | the 20 modules and their renderer: one machine file → a stack bundle | v0.23.0 | no | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | the machine side: puts a bundle onto a machine and keeps it running | v0.5.0 | no | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | Mullvad's SOCKS5 proxies as lists and DNS records, rebuilt every 6 hours | the `list` branch | no | MIT (README) |

## People

| Repository | What it is | Release | License |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | the engine of federated community hubs on nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | the first hub: ten peer-to-peer webtools ([live](https://derlocke-ng.github.io/armory/)) | follows `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | a catalog of hubs and their apps | (a list) | CC0 (README) |

## The desktop

| Repository | What it is | Release | Catalog | License |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installs and updates apps from git catalogs | v2.4.0 | yes | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | the Kiwi app catalog | (a list) | n/a | none stated |
| [ensconce](https://github.com/derlocke-ng/ensconce) | post-install setup for Bluefin-DX | v2.5.0 | yes | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | fail-closed VPN kill switch for GNOME | v0.2.3 | yes | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | sealed SOCKS5/VPN exits in rootless Podman | v0.7.3 | yes | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | distro boxes whose traffic leaves only through an exit | v0.2.3 | yes | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | isolated browser identities on kiwi-proxy exits | v0.7.1 | yes | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | kiwi-proxy provider: Tor | v0.3.0 | yes | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | kiwi-proxy provider: a VPN through gluetun | v0.2.2 | yes | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | kiwi-proxy provider: 9proxy | v0.2.0 | yes | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | kiwi-proxy provider: Mysterium | v0.5.2 | yes | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | display layouts for GNOME | v0.3.2 | yes | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | two-way folder sync as user services | v0.4.1 | yes | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | yes | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | SSH and TLS keys and certificates, offline in the browser ([live](https://derlocke-ng.github.io/kiwi-gen/)) | web page | no | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | the app icons ([preview](https://derlocke-ng.github.io/kiwi-icons/)) | no tags | no | none stated |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | this website and documentation | n/a | n/a | AGPL-3.0 |

## Known gaps

From the repositories themselves:

- **kiwi-server**: proven on hardware in October–November 2026, with node
  backups restored across nodes and the tunnel MTU tuned, mobile paths
  included. Federation between networks is not proven yet. IPv4 only, and the
  Debian ISO is amd64 only. The control plane is designed, not built.
- **kiwi-modules**: OpenCloud, Immich and Paperless-ngx are "to try out". A TURN
  server for calls is waiting to be merged.
- **kiwi-stack**: no rollback beyond restoring data and re-applying an older
  bundle.
- **kiwi-framework**: the blog, moderation approvals, following spaces a hub
  does not ship, and NIP-07/NIP-46 signers are still to come.
- **kiwi-updater**: a hosted registry of trusted catalogs is planned. The other
  apps' release tags are not signed yet, so kiwi-killswitch's root half asks
  for a password to update.
- **kiwi-proxy**: its kiwi-server module has not run on a machine. Exits are TCP
  and IPv4 only. The VPN module holds one configuration per machine.
- **Provider modules**: VPN and 9proxy are not validated end to end against a
  real account; Mysterium is (7 November 2026).
- **kiwi-custodia**: some parts are still to be measured on a real machine
  (tun2socks in a rootless gateway, non-GNOME compositors).
- **Licenses**: kiwi-icons, kiwi-catalog and mullvad-socks5 have no LICENSE
  file, and kiwi-killswitch states its license only in its README and manifest.
