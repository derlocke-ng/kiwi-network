# kiwi-custodia

Distro containers whose every byte leaves through a
[kiwi-proxy](kiwi-proxy.md) exit. *Think distrobox, with the network in
custody.*

- Repository: [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Latest release: **v0.2.3**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.
- A CLI (`kiwi-custodia`) and a GTK4 app (**Kiwi Custodia**)

A **box** is one Linux distribution in a rootless Podman container, with a home
of its own, joined to the sealed gateway of an exit. Install anything in it with
its package manager, run its desktop apps on your desktop, and put them in the
app grid. The box has no route but the exit: not for `dnf`, not for a game
client, not for a static binary that never heard of `$ALL_PROXY`. If the exit
goes, the box has no route at all.

That makes a box per client network a clean way to work: client A's tools,
keys and shell history in one box, client B's in another, each reaching only
its own client.

## Install

```bash
kiwi install kiwi-custodia   # brings kiwi-proxy along; or ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

It needs rootless Podman with `catatonit`, kiwi-proxy, a Wayland session,
Python 3.12+ with pydantic, GTK4 + libadwaita for the app, and `/dev/net/tun`
usable by rootless containers. Distro images are pulled when a box first starts.
Run `kiwi-custodia setup` again after an update.

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

Distributions: `fedora` (the default), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine`, or `custom` with `--image`.

## How a box is built

Three containers share one network namespace: kiwi-proxy's **gateway**, a
**tunnel sidecar** (tun2socks on a TUN device that becomes the default route),
and the **box** itself. All traffic leaves through the TUN into the exit's
SOCKS5, so programs that ignore proxy settings are covered too.

- The box runs as your user, with the same uid and passwordless `sudo`. Its
  home is `~/.local/share/kiwi-custodia/boxes/<id>/home`, one per box rather
  than your real home: two boxes are two identities.
- Changes inside a box are kept in a per-box snapshot when it stops, and
  `reset` returns to the base image.
- Wayland, X11 (through Xwayland), PipeWire, the session bus and `/dev/dri`
  are passed in, so desktop apps and games work.
- DNS goes through the gateway's resolver (with ad-blocking), or through the
  upstream on a remote-DNS exit.

## What it is not

A box is **network custody, not a sandbox from your desktop**. Like distrobox,
it gets your display and session bus, so a program in the box can show windows,
read the clipboard and use the portals. What it cannot do is reach the network
other than through its exit. UDP has no way out (no QUIC, no WebRTC media), and
IPv6 has no route.

Boxes that must not share an exit take different exits.
