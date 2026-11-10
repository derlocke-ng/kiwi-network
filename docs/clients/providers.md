# Provider modules

In [kiwi-proxy](kiwi-proxy.md), an exit is a named upstream connection that
your boxes and browsers send their traffic through. Usually this is a
connection you were given, such as the SOCKS5 proxy that leads into a client's
network. A provider module is for the other case: it creates the exit itself,
through Tor, a VPN subscription, 9proxy or Mysterium. Tor and Mysterium in
particular are there to give you more IP addresses for testing.

Each module is in its own repository. kiwi-updater installs it into
kiwi-proxy's modules directory, and kiwi-proxy manages it from then on.
kiwi-proxy builds the module's container image, starts the module when an exit
needs it, and stops it when no gateway uses it any more. A gateway is the
container that kiwi-proxy runs for an exit while the exit is up.

| Module | Repository | Release | Exit | Needs |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | the Tor network, with one circuit for each exit and any exit country | nothing (it is free) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | a WireGuard or OpenVPN tunnel through [gluetun](https://github.com/qdm12/gluetun) | a VPN subscription |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | a residential exit from [9proxy](https://9proxy.com/) | a 9proxy account and 9proxy's proprietary client, which is not redistributed |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | the [Mysterium](https://mysterium.network/) dVPN (a decentralised VPN), with a list of nodes that you can choose from by country and IP type | a registered consumer identity with a MYST balance |

All four modules are licensed under GPL-3.0-or-later and are in the
[Kiwi catalog](../desktop/catalogs.md). Each declares `DEPENDS=kiwi-proxy`, so
kiwi-updater installs kiwi-proxy first. Tor and Mysterium are the quick way to
get more exit IP addresses, for example for testing.

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

For a Tor exit, the country is enforced with Tor's `StrictNodes` option. A
circuit that cannot exit in this country fails, and it never exits in another
country. Exits on the tor module pass on the SOCKS credentials that Tor
Browser sends for each site. This is their default setting
(`--socks-auth passthrough`).

## How a provider connects to a gateway { #how-it-is-wired }

**Every provider offers SOCKS5 and nothing else.** A provider container needs
a connection to the Internet of its own. It therefore cannot run in a
gateway's network namespace, because everything except traffic to one
destination is dropped there. Instead, the provider and the gateway are
connected through a bridge network in rootless Podman, `kf-providers`, on
which each module has a fixed address:

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** offers SOCKS5 itself. kiwi-proxy sends a separate credential for
  each exit, and Tor's `IsolateSOCKSAuth` option then gives each exit its own
  circuit, which is its own path through the Tor network.
- **VPN and Mysterium** use a tunnel, and a tunnel does not offer SOCKS5. A
  small adapter, microsocks, therefore joins the tunnel's network namespace.
  It offers SOCKS5 and sends the traffic through the tunnel.
- **9proxy** runs the 9proxy client, which opens a SOCKS5 port that leads to a
  residential exit.

One provider container serves every exit that uses the same module and the
same lease. A lease is one of the selectable exits that a module offers, for
example a VPN server country or a Mysterium node. If a tunnel loses its
session, it fails closed, which means that no traffic gets out, and it is
restarted.

## Configuration

Each module's state is stored in
`~/.local/share/kiwi-proxy/modules-state/<module>/`, outside any repository:

- **vpn**: The file `vpn.json` contains gluetun's settings, such as
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` and `WIREGUARD_ADDRESSES`. Every key in
  upper case is passed to gluetun unchanged. The file can also contain a
  `leases` list. An optional `gluetun/` directory holds further files, for
  example a `wireguard.conf` for gluetun's `custom` provider. There is one
  such configuration per machine, and the exits on it differ by server
  country.
- **9proxy**: The configuration file is `config/account.conf`. The
  proprietary client is not included. Before you run
  `kiwi-proxy module setup 9proxy`, put the client in the plugin's
  `module/containers/vendor/` directory and add `COPY vendor/ /opt/9proxy/` to
  the plugin's `Containerfile`. Without the client the image is still built,
  but the provider refuses to start and does not open a port.
- **mysterium**: Run `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, or use *Configure…* in the Kiwi Proxy app. The passphrase
  is stored as a Podman secret. One identity can have only one connection at a
  time.

## Status

Tor needs no account. The Mysterium module was verified end to end on
2026-11-07. According to their READMEs, the VPN and 9proxy modules are
complete and unit-tested, but they have not been run end to end with a real
subscription or account.
