# kiwi-fox provider plugins

A [kiwi-fox](kiwi-fox.md) provider module gives a browser identity a network
**exit**. Each plugin runs an exit in a container on the `kf-providers` bridge
and exposes SOCKS5, where a kiwi-fox gateway reaches it; kiwi-fox manages the
container's lifecycle. They install into kiwi-fox's modules directory and depend
on kiwi-fox, which `kiwi` installs first.

Install any of them with `kiwi install kiwi-plugin-<name>`, then
`kiwi-fox module setup <name>`.

| Plugin | Exit | Needs | Repository |
|---|---|---|---|
| `kiwi-plugin-tor` | The Tor network — per-profile circuits (`IsolateSOCKSAuth`) | nothing (free) | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) |
| `kiwi-plugin-vpn` | A WireGuard/OpenVPN tunnel via [gluetun](https://github.com/qdm12/gluetun) | a VPN subscription | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) |
| `kiwi-plugin-9proxy` | A [9proxy](https://9proxy.com/) residential exit | a 9proxy account + the proprietary client | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) |
| `kiwi-plugin-myst` | The [Mysterium](https://mysterium.network/) dVPN | a registered consumer identity | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) |

All are GPL-3.0-or-later and run their containers unprivileged.

## Two shapes

**Tor** already speaks SOCKS5, so the module is just a Tor client that exposes
its SocksPort on the bridge. Each profile gets its own circuit.

**VPN, 9proxy and Mysterium** ride a tunnel that does not itself speak SOCKS5,
so these use kiwi-fox's `TunnelProvider` pattern: the tunnel container runs on
the bridge, and a tiny **microsocks adapter joins the tunnel's network
namespace** to offer SOCKS5 that rides the tunnel.

```
tunnel container ──────── kf-providers bridge ── kiwi-fox gateway ── browser
  tunnel up, /dev/net/tun                         permits only <tunnel-ip>:port
     ▲ shares netns
microsocks adapter  (SOCKS5, rides the tunnel)
```

## Use

```sh
kiwi-fox module list                         # the installed providers
kiwi-fox module leases <name>                # what you can select (countries / providers)
kiwi-fox new work --module tor --country de  # the module produces the endpoint
kiwi-fox run work
```

A shared exit container serves every profile on the same lease and is torn down
once no running gateway still uses it. See kiwi-fox's
`docs/plugin-system.md` for the provider contract. Per-plugin configuration
(gluetun provider settings, a 9proxy account, a Mysterium identity) lives in
each module's state directory under
`~/.local/share/kiwi-fox/modules-state/<name>/`, outside any repo — keep real
keys out of git.
