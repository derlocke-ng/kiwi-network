# Repositories & status

This page lists every repository of the Kiwi Network project: what it is, its
latest release and its license. At the end it lists what is known to be
missing or untested.

All repositories are at [github.com/derlocke-ng](https://github.com/derlocke-ng).
"Released" means that a repository has a version tag, because a version tag is
what kiwi-updater installs. The versions are as of November 2026.

## The network

| Repository | What it is | Release | Catalog | License |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | builds and runs the network: it turns the fleet file into install ISOs and applies each machine's role over SSH | v2.42.0 | yes | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | the 20 modules and their renderer, which turns one machine file into a stack bundle | v0.23.0 | no | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | the part that runs on the machine: it puts a bundle onto the machine and keeps it running | v0.5.0 | no | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | lists and DNS records of Mullvad's SOCKS5 proxies, rebuilt every 6 hours | the `list` branch | no | MIT (README) |

## People

| Repository | What it is | Release | License |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | the framework that federated community hubs on nostr are built with | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | the first hub built with kiwi-framework, with ten peer-to-peer web tools ([live](https://derlocke-ng.github.io/armory/)) | follows `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | a catalog of hubs and their apps | (a list) | CC0 (README) |

## The desktop

| Repository | What it is | Release | Catalog | License |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installs and updates apps from git catalogs | v2.4.0 | yes | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | the Kiwi app catalog | (a list) | n/a | none stated |
| [ensconce](https://github.com/derlocke-ng/ensconce) | sets up Bluefin-DX after it has been installed | v2.5.0 | yes | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | a fail-closed VPN kill switch for GNOME: when the VPN connection drops, traffic is blocked | v0.2.3 | yes | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | SOCKS5 and VPN exits in rootless Podman, each sealed in a container whose only route is that connection | v0.7.3 | yes | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | distro boxes (Linux distributions in containers) whose traffic can reach the Internet only through a kiwi-proxy exit | v0.2.3 | yes | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | isolated browser identities that connect through kiwi-proxy exits | v0.7.1 | yes | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | kiwi-proxy provider: Tor | v0.3.0 | yes | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | kiwi-proxy provider: a VPN through gluetun | v0.2.2 | yes | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | kiwi-proxy provider: 9proxy | v0.2.0 | yes | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | kiwi-proxy provider: Mysterium | v0.5.2 | yes | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | display layouts for GNOME | v0.3.2 | yes | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | two-way folder synchronisation, run as systemd user services | v0.4.1 | yes | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | yes | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | creates SSH and TLS keys and certificates offline in the browser ([live](https://derlocke-ng.github.io/kiwi-gen/)) | web page | no | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | the app icons ([preview](https://derlocke-ng.github.io/kiwi-icons/)) | no tags | no | none stated |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | this website and documentation | n/a | n/a | GPL-3.0-or-later, CC BY-SA 4.0 |

## Known gaps

The repositories themselves name these gaps:

- **kiwi-server**: It has been shown to work on real hardware, in
  October–November 2026. In those tests node backups were restored from one
  node onto another, and the tunnel MTU was tuned, including for mobile
  connections. Four additions are on the `several-servers` branches of
  kiwi-server and kiwi-modules and are not released yet. They are several
  backup servers, the
  automatic restore of a rebuilt machine, a prune timer, and a health check
  that restarts a stuck connection to the commercial VPN provider. Federation
  between networks has not been shown to work yet. Everything is IPv4 only,
  and the Debian ISO exists for amd64 only. The control plane is designed, not
  built.
- **kiwi-modules**: The OpenCloud, Immich and Paperless-ngx modules are marked
  "to try out". A TURN server for calls is waiting to be merged.
- **kiwi-stack**: There is no rollback. You can only restore data and apply an
  older bundle again.
- **kiwi-framework**: Several parts are still to come. They are the blog,
  moderation approvals, following spaces that a hub does not ship, and
  NIP-07/NIP-46 signers.
- **kiwi-updater**: A hosted registry of trusted catalogs is planned. The
  release tags of the other apps are not signed yet. For this reason the part
  of kiwi-killswitch that runs as root asks for a password when it is
  updated.
- **kiwi-proxy**: Its module for kiwi-server has not run on a machine yet.
  Exits carry TCP and IPv4 only. The VPN module holds one configuration per
  machine.
- **Provider modules**: The VPN and 9proxy modules have not been validated end
  to end against a real account. The Mysterium module has been validated, on
  7 November 2026.
- **kiwi-custodia**: Some parts still have to be measured on a real machine.
  These are tun2socks in a rootless gateway and compositors other than GNOME.
- **Licenses**: kiwi-icons, kiwi-catalog and mullvad-socks5 have no LICENSE
  file, and kiwi-killswitch states its license only in its README and
  manifest.
