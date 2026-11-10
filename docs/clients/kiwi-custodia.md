# kiwi-custodia

kiwi-custodia gives you a separate Linux environment for each client network
you work in. Each environment is a container with a Linux distribution of your
choice, and all of its network traffic goes through one
[kiwi-proxy](kiwi-proxy.md) exit. An exit is a named upstream connection, for
example the SOCKS5 proxy that leads into one client's network. You can work
for ten clients this way without ten VPN connections on the host, and each
client's tools and keys stay in that client's environment. *If you know
distrobox: this is the same idea, but the container can reach the network
only through its exit.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Latest release: **v0.2.3**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.
- It has a command-line tool (`kiwi-custodia`) and a GTK4 app (**Kiwi Custodia**).

A **box** is one Linux distribution in a rootless Podman container, which is a
container that runs as your own user without root rights. The box has a home
directory of its own and is joined to the gateway of an exit. The gateway is
the container that kiwi-proxy starts for an exit, and the only route out of it
leads to the exit's upstream. Inside the box you can install anything with the
distribution's package manager. Its desktop apps open on your desktop, and you
can add them to the app grid. The box has no route other than the exit. That
is true for every program in it: for `dnf`, for a game client, and for a
statically linked program that ignores `$ALL_PROXY`. If the exit stops, the box
has no route at all.

This is why one box for each client network is a good way to work. Client A's
tools, keys and shell history are in one box and client B's are in another,
and each box reaches only its own client.

## Install

```bash
kiwi install kiwi-custodia   # brings kiwi-proxy along; or ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

kiwi-custodia needs rootless Podman with `catatonit`, kiwi-proxy, a Wayland
session and Python 3.12+ with pydantic. The app needs GTK4 and libadwaita.
Rootless containers must also be able to use `/dev/net/tun`. The images of the
distributions are not downloaded during setup. An image is downloaded when a
box that uses it starts for the first time. After an update, run
`kiwi-custodia setup` again.

## Use

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # an exit, defined once, in kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # a box on it; the first start installs a baseline
kiwi-custodia enter work                                   # a shell in it: sudo dnf install …
kiwi-custodia run work -- firefox                          # one command in it
kiwi-custodia check work                                   # what the world sees from inside
kiwi-custodia apps work                                    # the desktop apps it has
kiwi-custodia export work firefox                          # "Firefox (work)" in the app grid
kiwi-custodia stop work
kiwi-custodia reset work                                   # back to the base image; the home stays
kiwi-custodia-gui
```

The available distributions are `fedora` (the default), `fedora-toolbox`,
`ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`,
`arch-toolbox`, `opensuse`, `rocky` and `alpine`. You can also choose `custom`
and name an image yourself with `--image`.

## How a box is built

A running box consists of three containers that share one network namespace,
which means that they share the same network interfaces, routes and firewall
rules. The first is kiwi-proxy's **gateway**. The second is a **tunnel
sidecar**, a helper container that runs tun2socks on a TUN device. A TUN
device is a virtual network interface, and here it becomes the default route.
The third container is the **box** itself. All traffic from the box goes into
the TUN device and from there to the exit's SOCKS5 proxy. This works through
the default route and not through proxy settings, so programs that ignore
proxy settings are covered too.

- The box runs as your user, with the same uid, and `sudo` works in it without
  a password. Its home directory is
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Every box has its own home
  and does not use your real one, so two boxes are two separate identities.
- When a box stops, the changes made inside it are saved in a snapshot that
  belongs to this box. `reset` returns the box to the base image.
- Wayland, X11 (through Xwayland), PipeWire, the session bus and `/dev/dri`
  are made available inside the box, so that desktop apps and games work.
- DNS queries are answered by the gateway's resolver, which also blocks
  advertising domains. On an exit that uses remote DNS, the upstream resolves
  the names instead.

## What it is not

A box **restricts the network. It is not a sandbox that protects your desktop
from the programs in it.** Like a distrobox container, the box gets your
display and your session bus. A program in the box can therefore show windows,
read the clipboard and use the desktop portals. What it cannot do is reach the
network in any way other than through its exit. UDP is not forwarded, so QUIC
and WebRTC media do not work, and there is no route for IPv6.

Boxes on the same exit share it. Boxes that must be kept apart from each
other need different exits.
