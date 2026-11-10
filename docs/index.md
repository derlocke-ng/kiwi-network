# Kiwi Network

*Hortus conclusus*: an enclosed garden.

Kiwi Network grows a private network of your own from one file. A **master**,
named after a fruit dish, keeps the gate, and it is the only door that faces the
Internet. Your **nodes**, named after fruits, grow behind it with your cloud,
your passwords and your backups. On top of it grow **hubs**, where your
community meets without a platform, and a **desktop** that installs straight
from git. Open source, self-hosted, no accounts.

## The network

[kiwi-server](server/index.md) turns one `fleet.yaml` into an unattended install
ISO per machine (Fedora CoreOS, uCore or Debian), then applies each machine's
role over SSH:

| Role | What the machine becomes |
|---|---|
| `master` | the gate: the WireGuard entry point, whose traffic leaves through a commercial VPN (the double hop) or straight out, with Pi-hole, Tor and the admin pages, and optionally a relay and a hub |
| `node` · `gateway` | routes a LAN through the VPN, with Pi-hole, DHCP relay, a download station and SFTP |
| `node` · `cloud` | Nextcloud with Collabora, and Vaultwarden |
| `node` · `minimal` | the VPN client and nginx, for modules of your choice: backups, Tang, Immich, Paperless-ngx, OpenCloud … |
| `bare` | just the base system |

The master publishes one port by default: WireGuard, UDP 51820. Everything else
dials out to it and meets in the mesh. See [How the network works](network/index.md),
and [Where it is going](server/roadmap.md) for the control node, federation and
the orchard.

## Hubs

[kiwi-framework](people/index.md) is the engine for community hubs on nostr:
[an open marketplace, a feed, chat, file sharing, shared lists, a password
manager](people/apps.md), all running in the browser, sealed before anything
leaves it, on relays the community chooses. Anyone can run a hub, any hub can
serve another's spaces, and a master can carry a private hub of its own.
[Armory](people/armory.md) is the first distribution.

## The desktop

[kiwi-updater](desktop/kiwi-updater.md) installs apps from **git catalogs** on
Fedora Silverblue and Bluefin. An app is a repo, a release is a tag, and an app
that needs root says why before it asks.

| App | What it does |
|---|---|
| [kiwi-killswitch](desktop/kiwi-killswitch.md) | a fail-closed VPN kill switch for GNOME |
| [ensconce](desktop/ensconce.md) | post-install setup for Bluefin-DX from plain list files |
| [kiwi-proxy](clients/kiwi-proxy.md), [kiwi-custodia](clients/kiwi-custodia.md), [kiwi-fox](clients/kiwi-fox.md) | one sealed exit per client network, with distro boxes and browsers inside |
| [gnome-monitor](desktop/gnome-monitor.md) | display layouts for GNOME |
| [syncman](desktop/syncman.md) | two-way folder sync |
| [kiwi-cli-tools-desktop](desktop/cli-tools.md) | `torlink`, `pweb`, `select-server`, `tethering` |
| [kiwi-server](server/index.md) | the network's gardener, as a GTK app too |

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

## Where things stand

Young projects, described as they are. kiwi-server was proven on hardware in
October and November 2026, and some modules and providers are still to be
validated. The [status page](project/status.md) lists every repository, its
release and its known gaps.

*Ex fructu arbor agnoscitur*: the tree is known by its fruit.
