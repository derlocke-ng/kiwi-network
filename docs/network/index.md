# How the network works

A Kiwi Network joins your own machines in one private network, wherever they
are: servers at home or in the office, laptops, phones, and whole home networks
behind a router. The machines can reach each other as if they were on the same
local network, and only one of them has to be reachable from the Internet. This
page explains how that network is built and what each part of it does.

The private network is a **WireGuard mesh**. WireGuard is the VPN software that
encrypts the connections, and *the mesh* is the name these pages use for the
private network that all your machines share. The mesh has one central machine,
the *kiwi-master*. Every other machine (nodes at home or in the office, laptops,
phones, routers) opens the connection to the master itself and can then reach
the others across the mesh. The whole network is described in one file, the
fleet file, and [kiwi-server](../server/index.md) builds it from that file.

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

The master is the machine that all the others connect to. Its role, `master`,
runs the five modules listed below. Pi-hole, Tor and nginx share the WireGuard
server's network namespace. A network namespace is a container's own set of
network interfaces, addresses and routes, so these three services use the
WireGuard server's network instead of having their own. For that reason they
are restarted together with the WireGuard server.

- **vpn-server** (wg-easy) is the WireGuard server. Every client and every node
  connects to it, and it issues their WireGuard configs. kiwi-server can create
  the configs for you (`kiwi-server enroll`).
- **vpn-client** (gluetun) connects the master to a commercial VPN provider. The
  preset uses Mullvad, and any provider that gluetun supports works. The
  WireGuard server's default route points at this VPN client, so traffic from
  the mesh to the Internet is sent through the provider, and websites see the
  provider's address and not the master's own. This connection is the master's
  *exit*, the route by which traffic from the mesh gets to the Internet. Because
  the traffic passes through two VPNs in a row, first yours and then the
  provider's, this setup is called the **double hop**. A master without a
  vpn-client sends the traffic to the Internet directly, from its own address.
- **dns** (Pi-hole 6) is the DNS server for the mesh. It answers at the master's
  mesh address, `10.8.0.1`. See [DNS, names & certificates](dns.md).
- **tor** offers a SOCKS5 proxy at `10.8.0.1:9050` to the clients in the mesh.
  Tor's entry and exit nodes are restricted to a set of countries (the default
  is `de,ch,at,nl,fr`, enforced with `StrictNodes`).
- **reverse-proxy** (nginx) serves the admin pages, `wg.<master>` and
  `pihole.<master>`. It serves them inside the mesh only, and only to clients
  that are allowed to see admin pages (see "Client groups" below).

A master can also run a **nostr relay** and a **hub** for the
[people on your network](../people/hubs.md#on-a-kiwi-network). A hub is a
community site that runs in the browser, and a nostr relay is the kind of
server that hubs synchronise over. Portainer and backups can be added to a
master as well.

### What is reachable from the Internet

By default the master has **one port** open to the Internet, which is WireGuard
on UDP 51820. The admin pages can only be opened from inside the mesh. Two
settings open more ports:

- `reverse-proxy.public: true` opens ports 80 and 443 and gets Let's Encrypt
  certificates for names outside the fleet's domain. Everything else can still
  be reached from the mesh only, and the admin pages answer requests from
  outside with the error 403. This setting is meant for a public hub or relay.
- `vpn-server.unlock_relay` opens the TCP ports of
  [Tang rings](../server/operations.md#encrypted-disks-and-unlocking) for
  machines behind NAT. Tang is a server that lets a machine with an encrypted
  disk unlock that disk at boot, and a ring is one Tang server with its own
  keys.

kiwi-server leaves SSH as the operating system sets it up, which by default
means login with keys only. kiwi-server itself uses SSH for `apply` and
`status`.

## Client groups

The clients of the WireGuard server (wg-easy) are sorted into **groups** by
their address. A group defines what its members are allowed to reach:

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

The members of every group can also reach the Internet through the master's
exit, unless you set `internet: false` for the group. A client whose address is
outside every group (`10.8.0.x`) is an ordinary member of the mesh. It can reach
everything, and it can open the admin pages as long as `admin_from_mesh` is on.

The groups are a setting of the vpn-server module (`groups`), so you can change
them or add your own. A group's `reach` setting accepts `all`, `nodes`, host
names, addresses or subnets. The older setting `isolated_subnet`, which defined
a single isolated group, still exists but is off by default.

## Nodes

A node is a machine at home or in the office that runs your services. It has a
vpn-client module too, but on a node this module does not connect to a
commercial VPN provider. It connects to the master, with the WireGuard config
that the master issued for the node. `kiwi-server enroll` writes this config to
`secrets/<hostname>.conf`, and the node uses it without any further setting. A
node needs no port open to the Internet, because it opens the connection to the
master itself. This is why a node works behind the NAT of a home router.

The `node` role has three presets:

| Preset | What the machine becomes |
|---|---|
| `gateway` (default) | A gateway for the local network (LAN). Devices on the LAN that use this machine as their default gateway reach the Internet through the VPN, and they can reach the mesh. Pi-hole is the DNS server for the LAN and can optionally be its DHCP server too. The download programs Transmission and JDownloader run *inside* the VPN client's network namespace, so they have no route at all while the tunnel is down. The preset also includes nginx, Portainer and SFTP. |
| `cloud` | Your own cloud: Nextcloud with Collabora for files, calendars and documents, and Vaultwarden for passwords. These services are behind nginx, and Portainer is included too. Nextcloud is built from the AIO project's containers, without the AIO master container. |
| `minimal` | Only the VPN client and nginx. You add the modules you want yourself. |

Nodes can also run backups, a backup server and Tang. OpenCloud, Immich and
Paperless-ngx are included for you to try out. See the
[module list](../server/modules.md).

You can reach the services on a node from its LAN and at the node's **mesh
address** (for example `10.8.0.25`). Traffic from the mesh to that address on
ports 80 and 443 is forwarded to the node's reverse proxy.

## Names

Machine names follow a convention. **Masters are named after fruit dishes**
(`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`,
`cider`) and **nodes after fruits** (`papaya`, `lychee`, `guava`, `quince`,
`damson`). This way you can tell from any log line what kind of machine a name
belongs to. It is only a convention, and any name works. A service gets a name
under the name of the machine it runs on: `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. See
[DNS, names & certificates](dns.md).

## How the mesh reaches the Internet { #ways-out }

A master is a WireGuard server with an exit, which is the route by which
traffic from the mesh gets to the Internet. The exit has three modes:

| Mode | How the mesh reaches the Internet | Status |
|---|---|---|
| **provider** | Through a commercial VPN provider (gluetun). This is the double hop, and it is what the master preset sets up. | built |
| **direct** | Directly through the master's own Internet connection. To get this mode, list the master's modules without `vpn-client`. | built |
| **master** | Through *another network's master*. Your master is a client there, in one of its groups that may reach the Internet and nothing else. This is called multi-hop. | designed; it needs enrolment across networks, which is federation |

Whatever its exit mode, every master also offers the Tor SOCKS5 proxy to the
mesh.

## One mesh per network

Each network has its own mesh with its own address range. The default range is
`10.8.0.0/16`. Masters and nodes are in `10.8.0.0/24`, and the groups follow:
guests in `.1`, pentest in `.2`, devices in `.3` and routers in `.4`. A second
network uses another range, for example `10.9.0.0/16`, so that a device which
belongs to both networks can tell them apart. Today the range is not one
setting but is spread over several (`mesh_subnet`, the vpn-server's `server_ip`,
`wg_subnet`, `wg_default_address` and `groups`, and Tor's
`socks_policy_accept`). The fleet file sets all of them.

## Addressing

| What | Default |
|---|---|
| The whole mesh (routed on every host) | `10.8.0.0/16` by default (`mesh_subnet`) |
| wg-easy clients | `10.8.0.0/24`; the server is `10.8.0.1` |
| Client groups | `10.8.1.0/24` … `10.8.4.0/24` |
| Stack network | `172.64.0.0/24` on a master, `172.128.0.0/24` on a node |
| WireGuard MTU | `1376` (`wg_mtu`), measured with [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| Stack bridge MTU | `1500` (`bridge_mtu`) |

A machine's stack is the set of containers that its modules run. Every machine
with a stack routes the mesh's address range through its VPN client, or on the
master through the WireGuard server. The machine and its containers can
therefore reach every node.

## Automatic restarts and updates { #keeping-it-fresh }

Each machine gets two timers, which are configured in its stack settings. The
first is a **daily VPN restart** at `07:00`, which gives the machine a new exit
address. The second is a **weekly update** on Sunday at 00:00, which runs
`podman auto-update` as long as `auto_update: registry` is set. The operating
system updates itself as well, and it reboots only in
[the time window you set](../server/machines.md#updates).

## A whole LAN in the mesh

A router can join the mesh as a WireGuard client in the `routers` group.
Alternatively, the router can send traffic for the mesh subnet to a gateway
node with a static route. In both cases every device on that router's LAN can
reach every node without running WireGuard itself. See [Routers](routers.md).
