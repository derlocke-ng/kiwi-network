# kiwi-killswitch

A **fail-closed VPN kill switch** for GNOME on Fedora Silverblue and Bluefin. One
root daemon owns the firewall. A GNOME Quick Settings toggle, a GTK4 app and a
CLI drive it over the D-Bus system bus, without ever asking for a password.

It protects **one** VPN connection at a time, WireGuard or OpenVPN. It does not
connect your VPN for you: you bring connections up in GNOME Settings, and the
kill switch builds a leak-proof firewall around whatever is actually alive.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Latest release: **v0.2.2**. It is in the [Kiwi catalog](../desktop/catalogs.md), scopes user + system.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

A GNOME extension is an unprivileged process. It cannot and must not touch the
firewall, so enforcement lives in the daemon and the UI only asks.

## What it does

- **Fail-closed.** `policy drop` on output, input and forward, IPv4 and IPv6,
  swapped atomically. Traffic leaves only through the protected tunnel. If the
  VPN drops, you reboot, or you switch from Wi-Fi to tethering, everything stays
  blocked until a permitted path is back.
- **New interfaces cannot leak.** Plug in USB tethering or turn on Wi-Fi while
  armed, and the new interface is blocked by default, not allowed by omission.
- **Three enforcement depths.** *Standard* filters output and input. *Strict*
  (the default) also filters **forwarded** traffic, because containers, VMs and
  Waydroid route through the host and forwarded packets never pass the output
  hook. *Paranoid* adds a **netdev egress** chain on each NIC, the only layer
  that sees raw-socket traffic.
- **DNS cannot wander off.** Choose through the VPN, the network's own (trusted
  kiwi-nodes only), or a resolver you pick. It is applied through
  systemd-resolved's per-link settings, with an nftables backstop that drops
  every other lookup.
- **Hostname endpoints are pinned, not trusted to DNS.** The daemon resolves a
  VPN server's hostname itself, over DNS-over-HTTPS to a pinned IP with a
  verified certificate, and caches every answer.
- **Pick a connection, then Apply.** Changes are staged, so you can switch from
  "home LAN + kiwi-node" to "tethering + VPN" *while already on tethering*, then
  apply it as one atomic transaction with no disarmed window in between.
- **Trusted kiwi-nodes.** A gateway that already tunnels for you (a
  [node-gw](../server/roles.md#node-gw)), matched on IP **and** MAC, can stand
  in for the VPN on its own network. It is opt-in and never inferred.
- **One VPN, enforced.** Only the selected connection's server is reachable. Any
  other tunnel you start cannot connect, and the UI names it.
- **Survives everything.** Reboots, logout and login, NetworkManager restarts:
  the rules stay. A separate unit installs a hard block *before the network
  comes up*.

## Install

It requires `nftables`, `NetworkManager`, `python3-gobject` and, for WireGuard,
`wireguard-tools`, all present on Silverblue and Bluefin. Nothing is written to
the immutable `/usr`. Your user must be in `wheel`.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

Or from a clone: `sudo ./install.sh install` (the daemon, CLI, bus policy and
systemd units), then `./install.sh install` (the GNOME extension and settings
app). Log out and back in so GNOME loads the extension. Uninstalling disarms
first, so it cannot leave you locked out.

## Use

Open **Quick Settings → Kill Switch** to arm, disarm and pick which VPN is
protected, or **Kiwi Kill Switch** in the app grid for everything else.

```bash
kiwi-killswitch status                   # what is enforced right now
kiwi-killswitch list                     # VPN connections NetworkManager knows
kiwi-killswitch vpn <name>               # stage which one is protected
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # one atomic transaction
kiwi-killswitch arm                      # or: arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # what is staged; revert discards it
```

!!! warning "Arming over SSH"
    Arming cuts a session from a subnet that is not in `mgmt_subnets`. That is
    correct kill-switch behaviour. Set it first:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Recovery.** The CLI needs no network, so a TTY is always enough:
`kiwi-killswitch disarm`. If the daemon itself is gone:
`sudo nft delete table inet kiwi_ks` and `sudo nft delete table netdev kiwi_ks_egress`.

**Verifying.** Arm it, then take the VPN down (`nmcli connection down …`).
`curl --max-time 5 ifconfig.me` must **time out**, not show your real IP. Do
not judge it by comparing exit IPs: prove tunnel use with
`wg show <iface> transfer` or `ip route get 1.1.1.1`.

## Coexistence and known limits

- **firewalld can stay on.** Its chains run at priority 10 and ours at −10.
- Do **not** run it alongside another kill switch that owns an output-drop table.
- Leave `nftables.service` alone if you do not use it. Stopping it flushes every
  table. The daemon re-asserts its rules within seconds, but there is no reason
  to open that window.
- A VPN with a **hostname** endpoint cannot reconnect while armed, unless DNS is
  set to *a resolver I choose*. NetworkManager and OpenVPN look the name up
  through the system resolver, which is blocked while no tunnel is up.
  Connections with a literal IP are unaffected.
- **Passwordless control** is the D-Bus bus policy for group `wheel`. It also
  means any program running as you can turn the switch off without asking.
- It stops network-level leaks. It is not Tails or Whonix and does nothing about
  browser fingerprinting, WebRTC, or an app that phones home through the tunnel.
- It is a personal tool and has not been independently audited.

It descends from the author's `gnome-vpn-killswitch` (boot ordering),
[kiwi-vpn-monitor](https://github.com/derlocke-ng/kiwi-vpn-monitor) (gateway
detection) and `nova-killswitch` (the daemon architecture).
