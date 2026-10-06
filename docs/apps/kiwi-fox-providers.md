# kiwi-fox providers

A **provider module** gives a [kiwi-fox](kiwi-fox.md) identity its exit. Each one
lives in its own repository, installs through kiwi-updater into kiwi-fox's
modules directory, and is managed by kiwi-fox: it builds the provider's container
image, brings it up on demand, and points a profile's gateway at it.

| Module | Repository | Exit | Needs |
|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | the Tor network, with one circuit per profile | nothing (free) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | a WireGuard/OpenVPN tunnel via [gluetun](https://github.com/qdm12/gluetun) | a VPN subscription |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | a [9proxy](https://9proxy.com/) residential exit | a 9proxy account and its proprietary client (not redistributed) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | the [Mysterium](https://mysterium.network/) dVPN | a registered consumer identity (free to create; connecting spends a small balance) |

All four are GPL-3.0-or-later, at version 0.1.0 with no release tag yet, and are
in the [Kiwi catalog](../desktop/catalogs.md). Each declares `DEPENDS=kiwi-fox`,
so kiwi installs kiwi-fox first.

!!! warning "Needs kiwi-fox from `main` for now"
    The provider subsystem (`kiwi-fox module …`) was added to kiwi-fox **after**
    its v0.1.3 release, and kiwi installs the latest release tag. Until the next
    kiwi-fox release, make kiwi follow kiwi-fox's `main` branch on this machine.
    Your own list beats the catalog:
    ```bash
    echo 'https://github.com/derlocke-ng/kiwi-fox.git branch=main' >> ~/.config/kiwi-updater/apps.list
    kiwi update kiwi-fox
    ```

## Install and use

```bash
kiwi install kiwi-plugin-tor
kiwi-fox module setup tor                     # build its image (kiwi-fox setup does all)
kiwi-fox module list
kiwi-fox module leases tor                    # what you can select: countries, regions, providers
kiwi-fox new work --module tor --country de   # the module produces the endpoint
kiwi-fox run work
```

`--country` / `--lease` picks the exit. For Tor that is a two-letter country,
held with `StrictNodes`, so the circuit fails rather than exit elsewhere. For
`vpn` it is gluetun's `SERVER_COUNTRIES` naming, for 9proxy a region, and for
Mysterium a provider identity (`0x…`).

## How it is wired

**Every provider exposes SOCKS5 and nothing else.** A provider runs its own
container with its own exit, so it cannot share the gateway's network namespace,
where everything but one destination is dropped. The two meet on a shared
rootless podman bridge, `kf-providers`:

```
provider container ──── kf-providers bridge ──── gateway container ──── browser
(own exit to the internet)                       nftables: default drop,       (joins the
SOCKS5 on <bridge-ip>:port                       permit only <provider-ip>:port  gateway netns)
```

kiwi-fox resolves the provider's current bridge address at every launch and
passes that literal address to the gateway, which permits exactly it. If the
provider dies, the gateway's one permitted destination stops answering.

- **Tor** already speaks SOCKS5, so its module is just a Tor client. kiwi-fox
  sends a stable per-profile credential, and Tor's `IsolateSOCKSAuth` gives each
  profile its own circuit.
- **VPN and Mysterium** ride a tunnel that does not speak SOCKS5. They run the
  tunnel container plus a tiny **microsocks adapter inside the tunnel's network
  namespace** (kiwi-fox's `TunnelProvider` pattern).
- **9proxy** runs the 9proxy client, which opens a SOCKS5 port bound to a
  residential exit.

A shared provider container serves every profile on the same lease and is torn
down once no running gateway still uses it.

## Configuration

Per-module configuration lives outside any repo, in
`~/.local/share/kiwi-fox/modules-state/<module>/`:

- **vpn**: `vpn.json` with gluetun's settings (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, …) and an optional `leases` list. Every
  `UPPER_CASE` key goes to gluetun as it is.
- **9proxy**: `config/account.conf`, mounted read-only into the client. Drop the
  proprietary client into the plugin's `module/containers/vendor/` before
  `module setup`. Without it the image still builds, but the provider refuses to
  come up rather than expose an open port.
- **mysterium**: the node's identity and keystore under `myst/`, plus
  `kf-consumer-id` holding your registered consumer identity.

## Status

The wiring, lifecycle and images of all four modules are complete and
unit-tested against the kiwi-fox provider contract. Tor needs no account. The
VPN, 9proxy and Mysterium modules need a real subscription, account or funded
identity to be validated end to end, so try `kiwi-fox module up <name>` on your
own machine after configuring it.
