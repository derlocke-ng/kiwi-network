# Roles

A role is what a machine becomes. Every role runs on all three
[targets](targets.md).

| Role | Title | Modules |
|---|---|---|
| `bare` | Bare system | none |
| `master` | kiwi-master | `vpn-client`, `vpn-server`, `dns`, `tor` |
| `node-gw` | kiwi-node (gateway) | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node-cloud` | kiwi-node (cloud) | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |

`master`, `node-gw` and `node-cloud` are **module roles**: a preset list of
[modules](modules.md), rendered on your machine into a docker compose stack that
the host starts on first boot.

## `bare`

Admin user, SSH and automatic updates: a clean machine to build on by hand.

## `master`

The WireGuard entry point, with a double hop through a commercial VPN, Pi-hole
DNS and a Tor SOCKS proxy for the mesh. The preset changes these module
defaults:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server` (Pi-hole answers at the master's mesh
  address), `mullvad_socks: true`
- `tor`: `network_mode: vpn-server`

Containers are named `km-…` and live on the `knet-master` network
(`172.64.0.0/24`). See [How the network works](../network/index.md#the-master).

## `node-gw`

A LAN gateway through the VPN, with Pi-hole, DHCP relay, Transmission and
JDownloader behind nginx, plus Portainer and SFTP. The preset turns on Pi-hole's
plain-HTTP web UI (`expose_web_ui: true`) on `web_ui_bind:web_ui_port`, which is
`127.0.0.1:8080` unless you change it. The reverse proxy serves the admin page
over TLS at `pihole.<hostname>` either way. Containers are named `kn-…` on
`knet-node` (`172.128.0.0/24`).

## `node-cloud`

Nextcloud AIO and Vaultwarden behind nginx, reachable on the LAN and through
the mesh, plus Portainer.

## Changing a preset

Inside a host's role block, `modules:` replaces the preset's list. Module
dependencies are added automatically (for example, `vault` requires
`vpn-client` and `reverse-proxy`):

```yaml
sh3:
  role: node-cloud
  node-cloud:
    modules: [vpn-client, reverse-proxy, cloud, vault, downloader]
    downloader: { download_dir: /mnt/data/downloads, transmission_password: … }
```

## Writing a role

A role is a directory `roles/<name>/` with a `role.yaml` and an `apply.sh`. A
module role lists its modules and includes the shared stack settings. Its
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

A role without modules does its own thing in `ks_role_apply()` with the library
in `roles/common/lib.sh`: `ks_say`/`ks_warn`/`ks_die`, `ks_apt`, `ks_file`,
`ks_write`, `ks_subst`, `ks_ensure_user`, `ks_ensure_docker`, `ks_git_clone`,
`ks_unit`, `ks_firewall_open`. Settings in `role.yaml` become `KS_ROLE_<KEY>`.
The script runs as root with `set -euo pipefail` and sees `KS_HOSTNAME`,
`KS_ADMIN_USER`, `KS_TARGET` and `KS_OS` (`debian` or `ostree`). The tests
render and shellcheck every role in the tree.
