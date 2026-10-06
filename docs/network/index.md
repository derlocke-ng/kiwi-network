# How the network works

A Kiwi Network is a **WireGuard mesh** with one hub. Every machine is built by
[kiwi-server](../server/index.md) and gets a role. The
[modules](../server/modules.md) section has the details of each service.

```
                         Internet
                            ▲
                            │  exit: a commercial VPN (Mullvad, ProtonVPN, AirVPN, …)
                            │  through gluetun — the "double hop"
               ┌────────────┴─────────────────────────────┐
               │ kiwi-master  (a VPS, or any reachable box) │
               │   wg-easy     WireGuard server, 10.8.0.1   │  ◀── UDP 51820, the one
               │   gluetun     VPN client: the master's exit │      published port
               │   Pi-hole     DNS for the mesh             │
               │   Tor         SOCKS5 for mesh clients      │
               └────────────▲─────────────────────────────┘
                            │  WireGuard mesh 10.8.0.0/16 — everyone dials out to the master
        ┌───────────────────┼────────────────────┬──────────────────────┐
        │                   │                    │                      │
  kiwi-node (cloud)   kiwi-node (gateway)    laptops, phones       a router (OpenWrt,
  Nextcloud AIO,      routes its LAN through  (wg-easy clients)     FritzBox, …) joins
  Vaultwarden, nginx  the VPN; Pi-hole, DHCP                        a whole LAN
                      relay, downloads, SFTP
```

## The master

The master (role `master`) runs four modules:

- **vpn-server** (wg-easy) is the entry point for every client and node. It
  issues the WireGuard client configs. Its web UI listens on
  `127.0.0.1:51821` on the master and, by default (`admin_from_mesh`), at the
  server's mesh address for regular clients.
- **vpn-client** (gluetun) connects to a commercial VPN provider (Mullvad in
  the preset; any gluetun provider works). The WireGuard
  server's default route points at it, so traffic from the mesh to the
  Internet leaves through the provider, not the master's own address. That is
  the double hop: client → master → VPN provider → Internet.
- **dns** (Pi-hole) runs inside the WireGuard server's network stack and
  answers at the master's mesh address (`10.8.0.1`). See
  [DNS, names & certificates](dns.md).
- **tor** offers a Tor SOCKS5 proxy at the master's mesh address, for mesh
  clients only (`10.8.0.0/16`), with exits pinned to a set of countries
  (default `de,ch,at,nl,fr`, `StrictNodes`).

### What is reachable from the Internet

The master's stack publishes **one port**: WireGuard on UDP 51820 (set
`public_ip` to bind it to a single address). wg-easy's and Pi-hole's admin pages
are bound to localhost or the mesh. kiwi-server opens the stack's ports in
firewalld or ufw when one of them is active; it does not otherwise change the
target's firewall. In particular, **SSH** stays as the OS has it (keys only, by
default). If you want WireGuard to be the only thing reachable, restrict SSH at
your provider's firewall or to the mesh.

### Isolated clients

wg-easy hands out addresses from the mesh subnet (`10.8.0.0/24`). Clients given
an address in the **isolated subnet** (`10.8.1.0/24` by default) get the
Internet (through the double hop) and the fleet's nodes, but they cannot see
other clients, and they never get the admin pages. Use it for devices or people
you give access to services but not to your network.

## Nodes

A node's **vpn-client** (gluetun) does not talk to a commercial VPN. It uses the
WireGuard client config that the master's wg-easy issued for it
(`vpn_provider: custom`). A node therefore needs no open port of its own: it
dials out to the master, and it keeps working behind a home router's NAT.

Services on a node are reachable on its LAN and at its **mesh address** (e.g.
`10.8.0.25`). Mesh traffic to the node's mesh address on 80/443 is forwarded
(DNAT) to the reverse proxy.

- **node-cloud**: Nextcloud All-in-One and Vaultwarden behind nginx, plus
  Portainer.
- **node-gw**: a LAN gateway. LAN clients that use this machine as their
  default gateway leave through the VPN client: they can reach the mesh, but
  not the node's docker network. Pi-hole serves the LAN (optionally as its DHCP
  server, through the DHCP relay). Transmission and JDownloader run *inside*
  the VPN client's network namespace, so if the tunnel is down they have no
  route at all. Also nginx, Portainer and SFTP.

## Addressing

| What | Default |
|---|---|
| Mesh (routed on every host) | `10.8.0.0/16` (`mesh_subnet`) |
| wg-easy client range | `10.8.0.0/24`, server `10.8.0.1` |
| Isolated clients | `10.8.1.0/24` |
| Stack docker network | `172.64.0.0/24` on a master, `172.128.0.0/24` on a node |
| WireGuard MTU inside the stack | `1412` |

Every stack host routes the mesh subnet through its VPN client (through the
WireGuard server on the master), so the host and its containers, Pi-hole
included, reach every other node. The master masquerades that traffic as its
mesh address.

## Keeping the tunnel fresh

Each stack host gets two timers from the stack settings: a **daily VPN restart**
(`07:00` by default; the old cron did this for a fresh exit address) and a
**weekly `kiwi-stack update`** (Sunday 00:00: pull, restart, prune). Either can be
turned off by setting it empty. `kiwi-stack vpn-restart` also restarts the
containers that share the VPN client's network namespace.

## Reaching the mesh from a whole LAN

A router can join the mesh as a WireGuard client, or send the mesh subnet to a
gateway node with a static route. Then every device on that LAN reaches every
node without running WireGuard itself. See [Routers](routers.md).
