# Kiwi Network

Kiwi Network is a set of open-source tools for running your own private
network: a WireGuard mesh of machines you own, with its own DNS, its own
certificate authority and your own services behind it, and an atomic Fedora
desktop with privacy apps on top.

It has two halves, and you can use either one without the other.

## The network: `kiwi-server`

[kiwi-server](server/index.md) builds the machines. You describe them in one
`fleet.yaml`; it renders a first-boot script, an Ignition or preseed config and
an unattended install ISO for each host. Boot the ISO, and the machine installs
itself and comes back as one of these:

| Role | What the machine becomes |
|---|---|
| `master` | The **kiwi-master**: the WireGuard entry point (wg-easy), whose own traffic leaves through a commercial VPN (gluetun, the "double hop"), with Pi-hole and a Tor SOCKS proxy for the mesh |
| `node-gw` | A **kiwi-node** in gateway mode: routes a LAN through the VPN, with Pi-hole, DHCP relay, a download station and SFTP |
| `node-cloud` | A **kiwi-node** in cloud mode: Nextcloud AIO and Vaultwarden behind nginx |
| `bare` | Just the base system: admin user, SSH, automatic updates |

The master is the only machine that has to be reachable from the Internet, and
its stack publishes exactly one port there: WireGuard, UDP 51820. Nodes,
laptops, phones and routers dial *out* to it and meet in the mesh
(`10.8.0.0/16`). See [How the network works](network/index.md).

Targets: Fedora CoreOS, uCore and Debian stable. Updates install continuously;
reboots only happen in a window you choose.

## The desktop: `kiwi-updater`

[kiwi-updater](desktop/kiwi-updater.md) installs and updates apps from **git
catalogs** on Fedora Silverblue, Bluefin and other ostree systems. No accounts,
no store: an app is a git repo with a `kiwi.manifest` and an `install.sh`, a
release is a git tag, and a catalog is a repo listing app URLs.

The [Kiwi catalog](desktop/catalogs.md) ships:

| App | What it does |
|---|---|
| [kiwi-killswitch](apps/kiwi-killswitch.md) | Fail-closed VPN kill switch for GNOME, with a root nftables daemon and no password prompts |
| [kiwi-fox](apps/kiwi-fox.md) | Isolated Windows 11 browser identities in rootless Podman |
| [kiwi-fox providers](apps/kiwi-fox-providers.md) | Tor, VPN (gluetun), 9proxy and Mysterium exits for kiwi-fox |
| [ensconce](desktop/ensconce.md) | Post-install setup for Bluefin-DX from plain list files, and `--export` to clone a machine |
| [kiwi-cli-tools-desktop](apps/cli-tools.md) | `pweb`, `select-server`, `tethering` |
| kiwi-updater | Itself: it updates itself like any other app |

Also documented here: [kiwi-gen](apps/kiwi-gen.md) (an offline, in-browser SSH
and TLS key and certificate manager) and
[kiwi-pentesting](apps/kiwi-pentesting.md) (early scaffold).

## Where to start

- **Run the network:** [kiwi-server quick start](server/index.md)
- **Set up a desktop:** [Desktop overview](desktop/index.md)
- **Where each piece stands:** [Repositories & status](project/status.md)

!!! note "Status"
    These are young projects. kiwi-server's
    generators are tested, but booting each target end to end on real hardware
    is still in progress. The [status page](project/status.md) says what is
    released, what tracks `main`, and what is only a scaffold.
