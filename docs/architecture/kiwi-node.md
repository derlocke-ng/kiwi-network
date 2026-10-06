# kiwi-node

A node is where most user-facing services live. Nodes connect to the master
over WireGuard and are reachable via the VPN mesh and/or the local LAN — never
publicly exposed by default.

Built by [kiwi-server](../build/kiwi-server.md) in one of two modes.

## Cloud node (`node-cloud`)

A private cloud host:

- **Nextcloud AIO** and **Vaultwarden** behind an **nginx** reverse proxy,
  reachable on the LAN and at the node's mesh address.
- Its certificate comes from the [fleet CA](../getting-started/network-model.md#one-ca-for-the-fleet),
  so internal HTTPS is trusted by every Kiwi machine.
- Optional **Portainer** for container management.

Modules: `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer`.

```yaml
hosts:
  sh3:
    role: node-cloud
    node-cloud:
      vpn_ip: 10.8.0.25
      vpn-client: { wireguard_config: secrets/sh3.home.conf }
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
```

## Gateway node (`node-gw`)

A LAN gateway that tunnels a whole local network through the VPN:

- **LAN DNS** (Pi-hole + DHCP relay).
- **Policy routing** that sends LAN clients out through the VPN client.
- **Transmission** and **JDownloader** running fail-closed inside the VPN
  client's network namespace — if the tunnel drops, they lose connectivity
  rather than leaking.
- **nginx**, **Portainer**, **SFTP**.

Modules: `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`,
`gateway`, `portainer`, `sftp`.

## Managing the stack

On the machine, the rendered stack is driven by one command:

```bash
sudo kiwi-stack start | stop | restart | update | status | logs | vpn-restart
```

`vpn-restart` also restarts the containers that share the VPN client's network
namespace (Transmission, JDownloader), so a tunnel cycle never leaves them in a
half-open state.

Nodes should be reachable via VPN and/or LAN, but are **not** publicly exposed.
