# kiwi-master

The master is the public-facing entry point. It exposes **only** what is
needed to the Internet: the WireGuard UDP port, and nothing else.

Built by [kiwi-server](../build/kiwi-server.md) with the `master` role.

## What the machine becomes

- A **WireGuard entry point** (`wg-easy`) that issues and manages client
  configs. This is the one port open to the public Internet.
- Its **default route goes out through a commercial VPN client** (`gluetun`,
  e.g. to Mullvad or any supported provider) — the "double hop": inbound
  clients arrive over WireGuard, and their egress leaves through the upstream
  VPN, so the master's own ISP address is never the exit.
- **Pi-hole** for network-wide DNS resolution and filtering, and as the root of
  the [fleet's resolver chain](../getting-started/network-model.md#one-resolver-chain-for-the-whole-network).
- Optional **Tor** proxy.
- An **isolated-client subnet**, so that a remote user you hand a WireGuard
  config to can reach the services you intend and nothing more.

## Modules

`vpn-server`, `vpn-client`, `dns`, `tor`.

## Deploying one

In `fleet.yaml`:

```yaml
hosts:
  gate:
    role: master
    target: debian
    master:
      vpn-client: { vpn_provider: mullvad, wireguard_private_key: …, wireguard_addresses: 10.66.1.2/32 }
      vpn-server: { wg_host: vpn.example.org, wg_password: … }
      dns: { pihole_password: … }
```

Then `kiwi-server build fleet.yaml` produces its install ISO. See
[kiwi-server](../build/kiwi-server.md) for the full workflow.

## Notes

- WireGuard client configs are issued by the master's `wg-easy`; you place them
  under `secrets/` and point each node's `vpn-client.wireguard_config` at them.
- The master masquerades mesh traffic as its mesh address, so every host — and
  its containers, including Pi-hole — can reach every node.
