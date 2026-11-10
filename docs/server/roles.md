# Roles

A role is what a machine becomes. Every role runs on all three targets.

| Role | What the machine becomes | Modules |
|---|---|---|
| `bare` | the base system: admin user, SSH, automatic updates | none |
| `master` | the **kiwi-master**: WireGuard entry point with the double hop, Pi-hole, Tor and the admin pages | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | a **kiwi-node** that routes a LAN through the VPN, with Pi-hole, DHCP relay, a download station and SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | a **kiwi-node** with Nextcloud and Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | a **kiwi-node** to fill with modules of your choice | `vpn-client`, `reverse-proxy` |

`node-gw` and `node-cloud` still work as names for the `gateway` and `cloud`
presets.

The module roles render a **stack**: podman quadlets by default (docker compose
with `runtime: docker`), which `kiwi-stack` starts and keeps running. See
[Modules](modules.md).

## `master`

The preset changes these module defaults:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` and `reverse-proxy`: `network_mode: vpn-server`

So Pi-hole, Tor and nginx live in the WireGuard server's network namespace and
answer at the master's mesh address. Containers are named `km-…` on the
`knet-master` network (`172.64.0.0/24`).

A master can add `nostr-relay` and `hub` (a [hub for people](../people/hubs.md)),
`portainer` and `backup` to its `modules:`. The relay and the hub run on
masters only.

```yaml
gate:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node`

The preset picks the module list. `modules:` replaces it, and required modules
come in by themselves. Containers are named `kn-…` on the `knet-node` network
(`172.128.0.0/24`).

```yaml
sh3:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.m1.home }   # m1 runs the backup-server module
```

The gateway preset turns on Pi-hole's own web page (`expose_web_ui: true`) at
`127.0.0.1:8080`. The reverse proxy serves it over TLS at `pihole.<hostname>`
either way.

## Writing a role

A role is a directory `roles/<name>/` with a `role.yaml` and an `apply.sh`. A
module role lists its modules and includes the shared stack settings, and its
`apply.sh` is one call:

```yaml
name: node-media
title: kiwi-node (media)
targets: [coreos, ucore, debian]
node_type: node
modules: [vpn-client, reverse-proxy, downloader, portainer]
settings_include: [common/stack]
module_defaults:
  downloader: { jdownloader: false }
```

```bash
ks_role_apply() { ks_stack_apply; }
```

A role without modules does its own work in `ks_role_apply()`, using the
library in `roles/common/lib.sh` (which comes from kiwi-stack). Settings in
`role.yaml` become `KS_ROLE_<KEY>`. The script runs as root with
`set -euo pipefail`. The tests render and shellcheck every role in the tree.
