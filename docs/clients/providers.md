# Provider modules

A provider module gives [kiwi-proxy](kiwi-proxy.md) an exit it produces itself,
instead of a SOCKS5 you were given. Each one lives in its own repository,
installs through kiwi-updater into kiwi-proxy's modules directory, and is
managed by kiwi-proxy: it builds the module's image, brings it up when an exit
needs it, and tears it down when no gateway uses it any more.

| Module | Repository | Release | Exit | Needs |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | the Tor network, one circuit per exit, any exit country | nothing (free) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | a WireGuard or OpenVPN tunnel through [gluetun](https://github.com/qdm12/gluetun) | a VPN subscription |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | a [9proxy](https://9proxy.com/) residential exit | a 9proxy account and its proprietary client (not redistributed) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | the [Mysterium](https://mysterium.network/) dVPN, with a picker over nodes by country and IP type | a registered consumer identity with a MYST balance |

All four are GPL-3.0-or-later, in the [Kiwi catalog](../desktop/catalogs.md),
and declare `DEPENDS=kiwi-proxy`, so kiwi installs kiwi-proxy first. Tor and
Mysterium are the quick way to more exit IPs, for example for testing.

## Install and use

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # build its image (kiwi-proxy setup does all)
kiwi-proxy module list
kiwi-proxy module countries tor                  # where Tor can exit
kiwi-proxy add tor-de --module tor --country de  # an exit from it
kiwi-custodia new test --exit tor-de             # a box on it, or:
kiwi-fox new test --exit tor-de                  # a browser profile on it
```

For Tor, the country is held with `StrictNodes`, so the circuit fails rather
than exit elsewhere. Exits on the tor module pass Tor Browser's per-site SOCKS
credentials through by default (`--socks-auth passthrough`).

## How it is wired

**Every provider exposes SOCKS5 and nothing else.** A provider container needs
its own way out, so it cannot live in a gateway's namespace, where everything
but one destination is dropped. The two meet on a rootless Podman bridge,
`kf-providers`, where each module gets a fixed address:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** already speaks SOCKS5. kiwi-proxy sends a per-exit credential, and
  Tor's `IsolateSOCKSAuth` gives each exit its own circuit.
- **VPN and Mysterium** ride a tunnel that does not speak SOCKS5, so a small
  microsocks adapter joins the tunnel's network namespace and offers SOCKS5 that
  rides the tunnel.
- **9proxy** runs the 9proxy client, which opens a SOCKS5 port on a residential
  exit.

One provider container serves every exit on the same module and lease. A
tunnel that loses its session fails closed and is restarted.

## Configuration

Each module's state lives in `~/.local/share/kiwi-proxy/modules-state/<module>/`,
outside any repository:

- **vpn**: `vpn.json` with gluetun's settings (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …; every upper-case key goes to gluetun as
  it is), an optional `leases` list, and an optional `gluetun/` directory (for
  example a `wireguard.conf` for gluetun's `custom` provider). This is one
  configuration per machine: exits on it differ by server country.
- **9proxy**: `config/account.conf`. Put the proprietary client in the plugin's
  `module/containers/vendor/` and add `COPY vendor/ /opt/9proxy/` to its
  `Containerfile` before `kiwi-proxy module setup 9proxy`. Without it the image
  builds, but the provider refuses to come up rather than open a port.
- **mysterium**: `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, or *Configure…* in the Kiwi Proxy app. The passphrase
  becomes a Podman secret. One identity holds one connection at a time.

## Status

Tor needs no account. Mysterium was verified end to end on 2026-11-07. The VPN
and 9proxy modules are complete and unit-tested, but have not been run end to
end against a real subscription or account, as their READMEs say.
