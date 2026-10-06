# Network Model

Kiwi Network is designed so that internal services are **never** exposed to the
Internet. One hardened entry point faces the world; everything else lives
behind the tunnel.

## High-level flow

```
Public Internet
      │  only WireGuard UDP (e.g. :51820) is open
      ▼
┌──────────────┐
│ kiwi-master  │  WireGuard entry point (wg-easy)
│              │  default route goes OUT through a commercial VPN (gluetun)
│              │  Pi-hole DNS · optional Tor
└──────┬───────┘
       │  encrypted mesh (default 10.8.0.0/16)
       ▼
┌──────────────┐     ┌──────────────┐
│ kiwi-node    │     │ kiwi-node    │
│ (cloud)      │     │ (gateway)    │
│ Nextcloud    │     │ LAN gateway  │
│ Vaultwarden  │     │ Pi-hole/DHCP │
│ nginx + CA   │     │ downloads    │
└──────────────┘     └──────────────┘
       ▲
       │  VPN tunnel
┌──────────────────┐
│ kiwi-workstation │  and phones/laptops as WireGuard clients
└──────────────────┘
```

## What is exposed

- **Public Internet** → only the `kiwi-master` WireGuard UDP port. No HTTP,
  no HTTPS, no SSH open to the world.
- **Mesh (VPN)** → every node and service is reachable by its mesh address
  from any machine on the tunnel.
- **LAN** → a `node-gw` can serve a whole office LAN through the VPN without
  each device running WireGuard.

## One resolver chain for the whole network

DNS is a single chain:

- VPN clients ask the master's Pi-hole.
- A gateway node's Pi-hole serves its LAN and asks the master's Pi-hole first
  (a public resolver such as Quad9 answers only while the master is
  unreachable).
- Names under the fleet's domain (`*.home` by default) are resolved by the
  master and never leave it.
- Every host carries the fleet's names in its hosts file plus a route into the
  mesh, so backups and certificate renewals resolve even if a Pi-hole is down.

The example fleet uses `.home` because ICANN will not delegate it as a public
top-level domain, so a fleet name can never leak to a public registry or get a
browser-trusted certificate issued for it by someone else. `.internal` is the
formally reserved alternative.

## One CA for the fleet

Hosts that run the reverse proxy get a `*.<hostname>` certificate signed by a
single fleet CA. Every machine built by `kiwi-server` trusts that CA, so
internal HTTPS "just works" without exposing anything publicly or depending on
a public ACME endpoint.

## Why it matters

This model is well suited to regulated environments: the attack surface stays
small — one hardened entry point, with every private service behind the tunnel.
There is nothing public to scan, enumerate or brute-force except a single
WireGuard port, which does not respond to unauthenticated packets at all.
