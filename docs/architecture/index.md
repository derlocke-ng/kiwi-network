# Architecture

Kiwi Network is split into three machine roles with distinct responsibilities.
The server roles are **rendered by [kiwi-server](../build/kiwi-server.md)** from
a single `fleet.yaml`; the workstation is an ordinary immutable Fedora desktop
with the Kiwi apps installed on top.

| Role | Responsibility | How it is built |
|---|---|---|
| [`kiwi-master`](kiwi-master.md) | VPN entry point, outbound VPN hop, DNS, Tor | `kiwi-server` role `master` |
| [`kiwi-node`](kiwi-node.md) | Private service host (cloud or LAN gateway) | `kiwi-server` roles `node-cloud` / `node-gw` |
| [`kiwi-workstation`](kiwi-workstation.md) | Daily-driver desktop for operators and users | Silverblue/Bluefin + `kiwi-updater` |

## Modules, not snowflakes

Each server role is a preset of **modules** in kiwi-server's module system
(`modules/<name>`), each rendered on your machine into a Docker Compose stack
the host starts on first boot. The presets correspond to the live
kiwi-master, kiwi-node-gw and kiwi-cloud setups, taken apart into reusable
modules:

| Module | What it provides |
|---|---|
| `vpn-server` | WireGuard entry point (wg-easy) |
| `vpn-client` | Outbound tunnel through a commercial VPN (gluetun) |
| `dns` | Pi-hole (filtering + fleet name resolution) |
| `tor` | Tor proxy |
| `reverse-proxy` | nginx with the fleet CA certificate |
| `cloud` | Nextcloud AIO |
| `vault` | Vaultwarden |
| `downloader` | Transmission + JDownloader (fail-closed in the VPN namespace) |
| `dhcp-relay` | DHCP relay for a gateway LAN |
| `gateway` | Policy routing that sends a LAN through the VPN |
| `portainer` | Container management UI |
| `sftp` | SFTP access |

You can compose your own role from these modules, or
[write a new one](../build/kiwi-server.md#roles-and-modules).

See each role page for the exact module set it ships.
