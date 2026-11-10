# Routers: a whole LAN in the mesh

This page shows how to connect a whole local network (LAN), for example your
home or office network, to your Kiwi Network through its router. A device in
the mesh, which is the private WireGuard network of your machines, can resolve
every name in the fleet and reach every node. The devices on a LAN behind a
router can do the same without each of them running WireGuard. There are two
ways to set this up:

- **The router is a client in the mesh.** The router runs WireGuard with a
  config that wg-easy, the master's WireGuard server, issued
  (`kiwi-server enroll fleet.yaml router --group routers`). It routes the mesh
  subnet (`10.8.0.0/16`) into the tunnel. This is called a *split* tunnel,
  because only traffic for the mesh goes through it. A *full* tunnel sends all
  traffic through it, so the whole LAN reaches the Internet through the
  master's exit, which is the master's connection to the Internet.
- **The router has a static route to a gateway node.** The router has no
  tunnel. It sends traffic for the mesh subnet to a node on the LAN that runs
  the `gateway` module, and that node forwards the traffic through its VPN
  client.

In both cases one DNS rule is enough, and you need no entries for individual
hosts. The rule forwards queries for the fleet's domain (`*.home`) to the
master's Pi-hole, which knows every host name and every service name. Nothing
else about the router's DNS changes.

One thing does not work: a device on the LAN cannot reach a device *behind
another router* by that device's LAN address. The mesh carries traffic for mesh
addresses only, and this is intended.

## OpenWrt

For OpenWrt, kiwi-server writes the whole configuration as a `uci` script:

```bash
# the router as a mesh client, with the config the master's wg-easy issued
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: only the mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: everything

# no tunnel on the router: a static route to the gateway node lychee
# (lychee needs a static LAN address in the fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copy the output to the router and run it there:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

The script installs the WireGuard package if it is missing. It creates an
interface called `kiwi`, and you can change that name with `--name`. The
interface uses the fleet's `wg_mtu` as its MTU and has one peer, the master. The
peer is created with `route_allowed_ips`, so OpenWrt adds the routes itself.
The script also creates a firewall zone that the LAN is allowed to forward
into, with masquerading and MSS clamping. Finally it adds the dnsmasq rule that
forwards the fleet's domain to the master (`server=/home/10.8.0.1`). With
`--full`, dnsmasq sends every DNS query to the master's Pi-hole. Every section
the script writes has a name, so running the script again replaces what it
wrote before.

## FritzBox

Fritz!OS has a WireGuard client and static routes, but it cannot forward DNS
queries for a single domain. The DNS rule therefore has to be handled by a
node:

1. **Tunnel:** go to Internet → Permit Access → VPN (WireGuard) → Add
   Connection → connect to another WireGuard service, and import the config
   that the master issued. The `AllowedIPs` line of that config decides whether
   the tunnel is split or full.
2. **Or a static route:** go to Home Network → Network → Network Settings →
   IPv4 Routes. Enter `10.8.0.0` as the destination, `255.255.0.0` as the subnet
   mask, and the gateway node's LAN address as the gateway.
3. **DNS:** make the LAN use a Pi-hole as its DNS server. Either set the gateway
   node as the local DNS server, or let the node's Pi-hole be the LAN's DHCP
   server (the `dns.dhcp_*` settings together with the dhcp-relay module). The
   node's Pi-hole knows the fleet's names and forwards all other queries to the
   master.

You can use the tunnel and static routes at the same time. Traffic for the mesh
then goes through the tunnel.

## Any other router

For any other router, three things are enough. Either give the router a
WireGuard client config, or add a static route for `10.8.0.0/16` that points to
the gateway node's LAN address. Then make the LAN use a Pi-hole that knows the
fleet as its DNS server. Any node that runs the `dns` module is such a Pi-hole.
Routers that are built on dnsmasq (DD-WRT, Tomato, the forwarder in pfSense)
also accept the one-line forwarding rule `server=/home/10.8.0.1`.
