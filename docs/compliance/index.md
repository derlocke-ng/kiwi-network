# Compliance

Kiwi Network aims to support real-world compliance requirements, and much of
that falls out of the architecture rather than being bolted on.

## Focus areas

- **Data minimization and access control.** Services are reachable only via VPN
  or LAN; there is no public surface to harvest from.
- **Secure-by-default network exposure.** Only a single WireGuard port faces the
  Internet. Everything else is denied by default, not allowed by omission.
- **Auditable, reproducible configuration.** Servers are built from a single
  [`fleet.yaml`](../build/kiwi-server.md) that you keep under version control.
  `kiwi-server show` prints exactly what a host ends up with (secrets masked),
  and the same file rebuilds an identical machine.
- **Change management.** Desktop software is installed from open git
  [catalogs](../apps/kiwi-catalog.md) through [kiwi-updater](../apps/kiwi-updater.md);
  every app is a readable repo, `kiwi diff` shows what an update changes before
  it runs, and `kiwi pin` holds a version until you choose to move.
- **Authorized-use enforcement.** Where testing is involved,
  [kiwi-pentesting](../privacy-apps/kiwi-pentesting.md) records a written
  authorization reference, enforces an in-scope allowlist, and keeps an
  append-only audit log of every action.
- **Controlled egress and DNS.** One resolver chain for the whole network, with
  filtering at the master, and a [fail-closed kill switch](../privacy-apps/kiwi-killswitch.md)
  on workstations so a dropped tunnel never leaks.

## How the pieces help

| Requirement | Mechanism |
|---|---|
| No unauthorized exposure | WireGuard-only entry point; private services behind the tunnel |
| Known, reproducible state | `fleet.yaml` under version control; deterministic renders |
| Internal PKI without public CAs | one [fleet CA](../getting-started/network-model.md#one-ca-for-the-fleet); keys generated offline with [kiwi-gen](../privacy-apps/kiwi-gen.md) |
| Update traceability | git catalogs, `kiwi diff`, `kiwi pin` |
| Leak prevention on endpoints | [kiwi-killswitch](../privacy-apps/kiwi-killswitch.md) |

!!! note
    Compliance depends on your deployment, processes and contracts. This section
    documents recommended practices and the technical capabilities the project
    provides; it is not itself a certification or legal advice.
