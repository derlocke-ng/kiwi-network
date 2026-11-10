# How the network works

A Kiwi Network is a **WireGuard mesh with one hub**, the *kiwi-master*. Every
other machine (nodes at home or in the office, laptops, phones, routers) dials
out to the master and meets the others in the mesh. All of it is described in
one fleet file and built by [kiwi-server](../server/index.md).

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## The master

The `master` role runs five modules. Pi-hole, Tor and nginx live inside the
WireGuard server's network namespace and come back with it.

- **vpn-server** (wg-easy) is the entry point for every client and node, and
  issues their WireGuard configs. kiwi-server can create them for you
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) connects to a commercial VPN provider: Mullvad in the
  preset, any gluetun provider in general. The WireGuard server's default route
  points at it, so traffic from the mesh leaves through the provider, not the
  master's own address. That is the **double hop**. A master without a
  vpn-client exits directly.
- **dns** (Pi-hole 6) answers at the master's mesh address, `10.8.0.1`. See
  [DNS, names & certificates](dns.md).
- **tor** offers SOCKS5 at `10.8.0.1:9050` to mesh clients, with entry and exit
  nodes pinned to a set of countries (default `de,ch,at,nl,fr`, `StrictNodes`).
- **reverse-proxy** (nginx) serves the admin pages, `wg.<master>` and
  `pihole.<master>`, to admin groups in the mesh.

A master can also carry a **nostr relay** and a **hub** for
[people on your network](../people/hubs.md#on-a-kiwi-network), plus Portainer
and backups.

### What is reachable from the Internet

By default the master publishes **one port**: WireGuard, UDP 51820. The admin
pages answer the mesh only. Two settings add more:

- `reverse-proxy.public: true` publishes 80 and 443, with Let's Encrypt
  certificates for names outside the fleet's domain. Everything else still
  answers only the mesh, and admin pages answer 403 from outside. This is for
  a public hub or relay.
- `vpn-server.unlock_relay` opens the TCP ports of
  [Tang rings](../server/operations.md#encrypted-disks-and-unlocking) for
  machines behind NAT.

SSH stays as the operating system has it (keys only by default). kiwi-server
uses it for `apply` and `status`.

## Client groups

wg-easy's clients are sorted into **groups** by address. Each group decides what
its members can reach:

| Group | Subnet | Reaches | Sees other clients | Admin pages |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | the nodes | no | no |
| `pentest` | `10.8.2.0/24` | nothing in the mesh | no | no |
| `devices` | `10.8.3.0/24` | everything | yes | yes |
| `routers` | `10.8.4.0/24` | everything | yes | no |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # a QR code for the WireGuard app
kiwi-server enroll fleet.yaml anna  --group guests --split # only the mesh goes through the tunnel
```

Every group may leave for the Internet through the exit unless you set
`internet: false`. Clients outside every group (`10.8.0.x`) are the plain
mesh: they reach everything, and see the admin pages while `admin_from_mesh` is
on. Groups are a setting of the vpn-server module (`groups`), so you can change
them or add your own (`reach` takes `all`, `nodes`, host names, addresses or
subnets). The old single `isolated_subnet` still exists but is off by
default.

## Nodes

A node's vpn-client does not talk to a commercial VPN. It uses the WireGuard
config the master issued for it (`kiwi-server enroll` writes
`secrets/<hostname>.conf`, and the node picks it up by itself). A node needs no
open port on the Internet: it dials out to the master, so it works behind a home
router's NAT.

The `node` role has three presets:

| Preset | What the machine becomes |
|---|---|
| `gateway` (default) | A LAN gateway. LAN clients that use it as their default gateway leave through the VPN and can reach the mesh. Pi-hole serves the LAN (optionally as its DHCP server). Transmission and JDownloader run *inside* the VPN client's network namespace, so they have no route at all when the tunnel is down. With nginx, Portainer and SFTP. |
| `cloud` | Nextcloud (from the AIO project's containers, without the AIO master container) with Collabora, plus Vaultwarden, behind nginx, plus Portainer |
| `minimal` | Just the VPN client and nginx, for your own choice of modules |

Nodes can also run backups, a backup server, Tang, and (to try out) OpenCloud,
Immich and Paperless-ngx. See the [module list](../server/modules.md).

Services on a node are reachable on its LAN and at its **mesh address** (e.g.
`10.8.0.25`). Mesh traffic to that address on 80 and 443 is forwarded to the
reverse proxy.

## Addressing

| What | Default |
|---|---|
| The whole mesh (routed on every host) | `10.8.0.0/16` (`mesh_subnet`) |
| wg-easy clients | `10.8.0.0/24`; the server is `10.8.0.1` |
| Client groups | `10.8.1.0/24` … `10.8.4.0/24` |
| Stack network | `172.64.0.0/24` on a master, `172.128.0.0/24` on a node |
| WireGuard MTU | `1376` (`wg_mtu`), measured with `kiwi-server mtu` |
| Stack bridge MTU | `1500` (`bridge_mtu`) |

Every stack host routes the mesh through its VPN client (on the master, through
the WireGuard server), so the host and its containers reach every node.

## Keeping it fresh

Each machine gets two timers from its stack settings: a **daily VPN restart**
(`07:00`, for a fresh exit address) and a **weekly update** (Sunday 00:00, which
runs `podman auto-update` while `auto_update: registry` is set). The operating
system updates itself and reboots only in [your window](../server/machines.md#updates).

## A whole LAN in the mesh

A router can join the mesh as a WireGuard client in the `routers` group, or send
the mesh subnet to a gateway node with a static route. Then every device on that
LAN reaches every node without running WireGuard. See [Routers](routers.md).
