# Routers: a whole LAN in the mesh

A device in the mesh resolves every fleet name and reaches every node. A LAN
behind a router can do the same without each device running WireGuard, in one
of two ways:

- **The router is a mesh client.** It runs WireGuard with a config the master's
  wg-easy issued and routes the mesh subnet (`10.8.0.0/16`) into the tunnel.
  That is the *split* tunnel: only mesh traffic goes through it. The *full*
  tunnel sends everything, so the whole LAN reaches the Internet through the
  master's exit.
- **A static route to a gateway node.** The router has no tunnel. It sends the
  mesh subnet to a node on the LAN that runs the `gateway` module, which
  forwards it through its VPN client.

Either way, one DNS rule replaces per-host overrides: the fleet's domain
(`*.home`) is forwarded to the master's Pi-hole, which knows every host and
service name. Nothing else about the router's DNS changes.

What the LAN cannot do is reach a device *behind another router* by its LAN
address. The mesh only carries mesh addresses, by design.

## OpenWrt

kiwi-server writes the whole configuration as a `uci` script:

```bash
# the router as a mesh client, with the config the master's wg-easy issued
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split: only the mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full: everything

# no tunnel on the router: a static route to the gateway node m1
# (m1 needs a static LAN address in the fleet: network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via m1
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copy the output to the router and run it:

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

The script installs the WireGuard package if it is missing. It creates an
interface `kiwi` (change the name with `--name`) with one peer for the master
and `route_allowed_ips`, a firewall zone the LAN may forward into (with
masquerading and MSS clamping), and the dnsmasq forward for the fleet's domain
(`server=/home/10.8.0.1`). With `--full`, dnsmasq sends every lookup to the
master's Pi-hole. Every section is named, so running the script again replaces
what it wrote before.

## FritzBox

Fritz!OS has a WireGuard client and static routes, but no per-domain DNS
forwarding, so the DNS rule moves to a node:

1. **Tunnel:** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   connect to another WireGuard service → import the config the master issued.
   Its `AllowedIPs` decides split or full.
2. **Or a static route:** Home Network → Network → Network Settings → IPv4
   Routes. Destination `10.8.0.0`, subnet mask `255.255.0.0`, gateway the
   gateway node's LAN address.
3. **DNS:** point the LAN at a Pi-hole. Either set the gateway node as the local
   DNS server, or let the node's Pi-hole be the LAN's DHCP server (`dns.dhcp_*`
   settings plus the dhcp-relay module). The node's Pi-hole carries the fleet's
   names and forwards the rest to the master.

The tunnel and static routes can coexist. The tunnel wins for the mesh.

## Any other router

Three facts are enough. Either give the router a WireGuard client config, or
add a static route for `10.8.0.0/16` to the gateway node's LAN address. Then
point the LAN's DNS at a Pi-hole that knows the fleet, which is any node running
the `dns` module. Routers with dnsmasq underneath (DD-WRT, Tomato, pfSense's
forwarder) also take the one-line forward `server=/home/10.8.0.1`.
