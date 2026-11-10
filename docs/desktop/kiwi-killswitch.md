# kiwi-killswitch

kiwi-killswitch is a **VPN kill switch** for GNOME on Fedora Silverblue and
Bluefin. A kill switch makes sure that your computer sends no traffic outside
the VPN, for example when the VPN connection drops or when you change to
another network. This one is **fail-closed**. That means the firewall blocks
everything that is not explicitly allowed, so when something fails, traffic is
blocked and not let through.

One daemon that runs as root manages the firewall. You control it with a toggle
in GNOME Quick Settings, a GTK4 app or a command-line tool (CLI). These three
send their requests to the daemon over the D-Bus system bus, and they never ask
for a password.

It protects **one** VPN connection at a time, WireGuard or OpenVPN. It does not
connect your VPN for you. You start your connections in GNOME Settings, and the
kill switch sets its firewall rules for the connection that is really up, so
that no traffic can leave the computer outside that connection.

- Repository: [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Latest release: **v0.2.3**. It is in the [Kiwi catalog](catalogs.md) and has
  two scopes, user + system. One half is installed in your home directory and
  one half is owned by root.
- It works with GNOME Shell 45 to 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

A GNOME extension is a process without root rights. It cannot change the
firewall, and it must not be able to. For this reason the daemon does all the
blocking, and the user interface only sends requests to the daemon.

## What it does

- **It is fail-closed.** The firewall uses `policy drop` for outgoing, incoming
  and forwarded traffic, for IPv4 and IPv6. This means that every packet is
  dropped unless a rule allows it. A new set of rules replaces the old one in
  one atomic step. Traffic can leave only through the protected tunnel. If the
  VPN drops, if you reboot, or if you switch from Wi-Fi to tethering,
  everything stays blocked until a permitted path is available again.
- **New network interfaces are blocked.** If you plug in USB tethering or turn
  on Wi-Fi while the kill switch is armed, which means switched on, the new
  interface is blocked by default. It is not allowed merely because no rule
  mentions it.
- **There are three levels of filtering.** *Standard* filters outgoing and
  incoming traffic. *Strict* is the default and also filters **forwarded**
  traffic. This is needed because containers, VMs and Waydroid send their
  traffic through the host, and forwarded packets never pass through the output
  hook. *Paranoid* adds a **netdev egress** chain on each network card (NIC).
  This is the only layer that sees traffic from raw sockets.
- **DNS queries cannot bypass the tunnel.** You choose which DNS resolver is
  used while the kill switch is armed. You can send DNS queries through the VPN,
  use the resolver of the network you are on, or use a resolver that you pick
  yourself. The network's own resolver is used only on the network of a
  trusted kiwi-node. The kill switch applies your choice through the per-link
  settings of systemd-resolved. As a second safeguard, an nftables rule drops
  every other DNS lookup.
- **For a VPN server with a hostname, the daemon does not trust ordinary DNS.**
  It resolves the hostname of the VPN server itself. It uses DNS-over-HTTPS for
  this, connects to a pinned (fixed) IP address and verifies the certificate.
  It caches every answer.
- **You pick a connection, then you apply.** Changes are staged, which means
  that they are collected and take effect only when you apply them. You can
  therefore change from "home LAN + kiwi-node" to "tethering + VPN" *while you
  are already on tethering*. Apply then makes all changes in one atomic
  transaction, and the kill switch is not disarmed at any moment in between.
- **Trusted kiwi-nodes.** Your network may have a gateway that already sends
  your traffic through a tunnel. In a Kiwi network this is a
  [gateway node](../server/roles.md#node). On its own network, such a gateway
  can take the place of the VPN. The kill switch recognises it by its IP
  address **and** its MAC address. You have to turn this on yourself. The kill
  switch never decides on its own that a gateway is trusted.
- **Only one VPN can connect.** Only the server of the selected connection can
  be reached. Any other tunnel that you start cannot connect, and the user
  interface names it.
- **The rules stay in place.** They are still there after a reboot, after you
  log out and log in, and after NetworkManager restarts. A separate unit loads
  blocking rules *before the network comes up*.

## Install

kiwi-killswitch requires `nftables`, `NetworkManager` and `python3-gobject`,
and for WireGuard also `wireguard-tools`. All of these are present on
Silverblue and Bluefin. Nothing is written to the immutable `/usr`. Your user
must be in the `wheel` group.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

You can also install it from a clone of the repository. First run
`sudo ./install.sh install`, which installs the daemon, the CLI, the D-Bus
policy and the systemd units. Then run `./install.sh install`, which installs
the GNOME extension and the settings app. Log out and log in again so that
GNOME loads the extension. When you uninstall, the kill switch is disarmed
first, so the uninstall cannot leave you with a blocked network.

## Use

Open **Quick Settings → Kill Switch** to arm and disarm the kill switch and to
pick which VPN is protected. For everything else, open **Kiwi Kill Switch** in
the app grid. The CLI has these commands:

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
    When you arm the kill switch, an SSH session from a subnet that is not in
    `mgmt_subnets` is cut. That is correct kill-switch behaviour. If you work
    over SSH, set these values first:
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Recovery.** The CLI needs no network, so a text console (TTY) is always
enough to run `kiwi-killswitch disarm`. If the daemon itself is gone, delete
its firewall tables with `sudo nft delete table inet kiwi_ks` and
`sudo nft delete table netdev kiwi_ks_egress`.

**Virtual machines.** A bridged VM never sends its traffic through the host, so
the kill switch does not affect it. Avoid `paranoid` in this case, because that
level filters at the physical network card. A NAT'd VM sends its traffic
through the host. With `strict`, this traffic goes out through the tunnel and
is blocked when the tunnel is down. Add the VM's subnet to `mgmt_subnets`, so
that its DHCP and DNS requests reach the host. The table shows what each
setting allows:

| Setting | Outbound | Inbound | Kept outside the tunnel |
|---|---|---|---|
| `allow_lan` | yes (auto) | no | no |
| `bypass_subnets` | yes | no | no |
| `mgmt_subnets` | yes | yes | yes |

**Checking that it works.** Arm the kill switch, then take the VPN down with
`nmcli connection down …`. Now `curl --max-time 5 ifconfig.me` must **time
out**. It must not show your real IP address. Do not judge the result by
comparing the public IP addresses that you see. To prove that traffic uses the
tunnel, run `wg show <iface> transfer` or `ip route get 1.1.1.1`.

## Other firewalls and known limits { #coexistence-and-known-limits }

- **firewalld can stay on.** Its chains run at priority 10, and the chains of
  the kill switch run at −10.
- Do **not** run it together with another kill switch that has its own table
  that drops outgoing traffic.
- Leave `nftables.service` alone if you do not use it. When this service is
  stopped, it deletes every nftables table. The daemon loads its rules again
  within seconds, but for those seconds the rules are missing, and there is no
  reason to cause that.
- A VPN whose server is given as a **hostname** cannot reconnect while the kill
  switch is armed, unless DNS is set to *a resolver I choose*. The reason is
  that NetworkManager and OpenVPN look the name up through the system resolver,
  and the system resolver is blocked while no tunnel is up. Connections whose
  server is given as an IP address are not affected.
- **A resolver that you choose can be reached outside the tunnel** while the
  tunnel is down. Turn on DNS-over-TLS for it.
- **A trusted node that was saved without a MAC address** is recognised by its
  gateway address alone.
- **Control without a password** works through the D-Bus policy for the
  group `wheel`. This also means that any program that runs as your user can
  turn the kill switch off without asking you.
- It stops leaks at the network level. It is not Tails or Whonix. It does
  nothing against browser fingerprinting, WebRTC, or an app that sends data to
  its maker through the tunnel.
- It is a personal tool and has not been audited independently.
  `tests/run.sh` tests the real daemon with real nftables. Each test group
  runs in its own namespace, and the tests need no root.
- Its release tags are not signed yet. With kiwi-updater 2.4, its root half
  therefore asks for your password when it is updated.

kiwi-killswitch is based on three earlier tools by the same author. The boot
ordering comes from `gnome-vpn-killswitch`, the gateway detection from
`kiwi-vpn-monitor`, and the daemon architecture from `nova-killswitch`.
