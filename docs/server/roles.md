# Roles

A role decides what a machine is used for in your Kiwi Network. You give every
host a role in the fleet file, and kiwi-server sets the machine up for it. A
machine can be a plain base system, the master that every device and node
connects to, or a node that runs your services. Every role works on all three
targets, which are the operating systems that kiwi-server can install.

| Role | What the machine becomes | Modules |
|---|---|---|
| `bare` | The base system only, with an admin user, SSH and automatic updates | none |
| `master` | The **kiwi-master**. It is the WireGuard entry point of the network and sends the network's Internet traffic on through a commercial VPN (the double hop). It also runs Pi-hole for DNS with ad blocking, Tor and the admin pages | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | A **kiwi-node** that sends the traffic of a local network (LAN) through the VPN. It also runs Pi-hole, a DHCP relay, a download station and SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | A **kiwi-node** that runs Nextcloud and Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | A **kiwi-node** with only the two basic modules, to which you add the modules you want | `vpn-client`, `reverse-proxy` |

The `node` role comes in presets. A preset is a ready-made list of modules.
The older role names `node-gw` and `node-cloud` still work, and they mean the
`gateway` and `cloud` presets.

The `master` and `node` roles are built from modules, and a module is one
service. kiwi-server turns the modules of a host into a **stack**, which is the
set of containers that the machine runs. By default the stack consists of
podman quadlets, which are systemd units that run containers. With
`runtime: docker` it is run by docker compose. On the machine, `kiwi-stack`
starts the stack and keeps it running. See [Modules](modules.md).

## `master`

The `master` role changes these module defaults:

- `vpn-client`: `vpn_provider: mullvad`, `mss_clamp: true`
- `dns`: `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` and `reverse-proxy`: `network_mode: vpn-server`

With these settings, Pi-hole, Tor and nginx share the network namespace of the
WireGuard server. A network namespace is the set of network interfaces and
addresses that a container sees. The three services are therefore reachable at
the master's mesh address, which is its address in the private WireGuard
network. The containers on a master are named `km-…` and are attached to the
`knet-master` network (`172.64.0.0/24`).

A master can also run `nostr-relay` and `hub` (for a
[hub for people](../people/hubs.md)), `portainer` and `backup`. To use them,
add them to the master's `modules:` list. The relay and the hub run on masters
only.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node`

The preset decides which modules a node runs. If you write your own `modules:`
list, it replaces the preset's list, and modules that the listed ones require
are added automatically. The containers on a node are named `kn-…` and are
attached to the `knet-node` network (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee runs the backup-server module
```

The gateway preset also makes Pi-hole's own web page available at
`127.0.0.1:8080` on the node (`expose_web_ui: true`). Whether or not this
setting is on, the reverse proxy serves the page over TLS at
`pihole.<hostname>`.

## Writing a role

You can write your own role. A role is a directory `roles/<name>/` that
contains a `role.yaml` and an `apply.sh`. A role that is built from modules
lists its modules in `role.yaml` and includes the shared stack settings. Its
`apply.sh` then consists of a single call.

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

A role without modules does its work itself in `ks_role_apply()`. It can use
the library in `roles/common/lib.sh`, which comes from kiwi-stack. The settings
that `role.yaml` declares are available to the script as variables named
`KS_ROLE_<KEY>`. The script runs as root with `set -euo pipefail`. The
project's tests render every role in the tree and run shellcheck on it.
