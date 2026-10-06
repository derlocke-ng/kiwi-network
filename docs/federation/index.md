# Federation

Federation is the idea of connecting multiple Kiwi Networks — e.g. Company A and
Company B — so they can collaborate while keeping their internal services
private.

## The building blocks are already there

A Kiwi Network is a WireGuard mesh with one hardened master. Federating two of
them is a matter of linking the meshes in a controlled way rather than exposing
anything publicly:

- **Controlled VPN links.** A WireGuard link between the two masters (or a
  dedicated peer) carries exactly the traffic you allow and nothing else. The
  [network model](../getting-started/network-model.md) already routes a mesh
  subnet and resolves fleet names through the master, so extending that to a
  second fleet is the same mechanism.
- **App-level federation.** Services that federate natively — **Nextcloud**
  federation for files and calendars, for example — can share across the two
  organizations over the VPN link, with no service ever reachable from the
  public Internet.

## Example

```
Company A                         Company B
┌──────────────┐  controlled     ┌──────────────┐
│ kiwi-master  │  WireGuard link  │ kiwi-master  │
│   + nodes    │◀────────────────▶│   + nodes    │
└──────────────┘                  └──────────────┘
   Nextcloud  ◀── federated share ──▶  Nextcloud
```

- Company A runs its fleet; Company B runs its own.
- A controlled VPN link joins them; routing and firewall rules define exactly
  which services and users can communicate between the networks.
- All inter-network traffic travels through encrypted WireGuard tunnels.

## Status

Federation is a **planned** area. The primitives it needs — the mesh, one CA
per fleet, fleet-wide DNS, and [kiwi-server](../build/kiwi-server.md)'s
module/role system — exist today. Documented reference patterns for linking two
fleets, and the fleet-file settings to express a federation link, are on the
[roadmap](../roadmap.md).
