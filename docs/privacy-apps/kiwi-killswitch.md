# kiwi-killswitch

A **fail-closed VPN kill switch** for GNOME on Fedora Silverblue / Bluefin. One
root daemon owns the firewall; a GNOME Quick Settings toggle, a GTK4 app and a
CLI drive it over the D-Bus system bus — with no password prompt, ever.

It protects **one** VPN connection at a time, WireGuard or OpenVPN. It does not
connect your VPN for you: you bring connections up in GNOME Settings, and the
kill switch builds a leak-proof firewall around whatever is actually alive.

- Repository: <https://github.com/derlocke-ng/kiwi-killswitch>
- License: GPL-3.0-or-later.

```
┌─ your session (unprivileged) ────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

## What it does

- **Fail-closed.** `policy drop` on output, input and forward, IPv4 and IPv6,
  swapped atomically. Traffic leaves only through the protected tunnel. If the
  VPN drops, you reboot, or you switch Wi-Fi → tethering, everything stays
  blocked until a permitted path is back.
- **New interfaces cannot leak.** Plug in USB tethering or turn on Wi-Fi while
  armed and it is blocked by default, not allowed by omission.
- **Three enforcement depths.** *Standard* filters output and input. *Strict*
  (default) also filters **forwarded** traffic — containers, VMs and Waydroid
  route through the host. *Paranoid* adds a **netdev egress** chain on each NIC,
  the only layer that sees raw-socket traffic.
- **DNS cannot wander off.** Through the VPN, the network's own (trusted
  kiwi-nodes only), or a resolver you pick — applied through systemd-resolved
  with an nftables backstop that drops every other lookup.
- **Hostname endpoints are pinned, not trusted to DNS.** The daemon resolves a
  VPN server hostname itself over DNS-over-HTTPS, to a pinned IP with a verified
  certificate.
- **Staged changes.** Reconfigure from "home LAN + kiwi-node" to "tethering +
  VPN" *while already on tethering*, then hit Apply — one atomic transaction, no
  disarm window in between.
- **Survives everything.** Reboot, logout, login, NetworkManager restarts: the
  rules stay. A separate unit installs a hard block before the network comes up.

## Install

Requires `nftables`, `NetworkManager`, `python3-gobject` and (for WireGuard)
`wireguard-tools` — all present on Silverblue/Bluefin. Nothing is written to the
immutable `/usr`.

```bash
kiwi install kiwi-killswitch   # installs both halves (user + root)
```

Or from a clone:

```bash
sudo ./install.sh install     # root daemon, CLI, bus policy, systemd units
./install.sh install          # GNOME extension + settings app
```

Log out and back in so GNOME loads the extension. Your user must be in `wheel`.

## Use

**Quick Settings → Kill Switch** to arm, disarm and pick which VPN is protected.
**Kiwi Kill Switch** in the app grid for everything else.

```bash
kiwi-killswitch status                   # what is enforced right now
kiwi-killswitch list                     # VPN connections NM knows about
kiwi-killswitch vpn lime                 # stage which one is protected
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # one atomic transaction
kiwi-killswitch arm                      # or: arm <vpn>
kiwi-killswitch disarm
```

!!! warning "Before you arm on a machine you reach over SSH"
    Arming cuts a session from a subnet not in `mgmt_subnets` — that is correct
    kill-switch behaviour. Set it first:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

## Coexistence and limits

- **firewalld can stay on** (its chains run at priority 10, ours at −10).
- Do **not** run it alongside another output-drop kill switch.
- A VPN with a *hostname* endpoint cannot reconnect while armed unless DNS is
  set to a resolver you choose (NetworkManager/OpenVPN look the name up through
  the blocked system resolver). Connections with a literal IP are unaffected.
- This is not Tails or Whonix: it stops network-level leaks, not browser
  fingerprinting or an app that deliberately phones home through the tunnel.

It derives from the author's `gnome-vpn-killswitch`, `kiwi-vpn-monitor` (gateway
intelligence) and `nova-killswitch` (the daemon architecture and leak fixes).
