# Where it is going

!!! info "Designed, not built"
    This page summarises kiwi-server's
    [control-plane design](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md),
    agreed in October 2026. Unless a line says *built*, none of it exists yet.
    The [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    tracks the order.

Today kiwi-server is a desktop tool: the fleet file, the secrets and the CA live
on the operator's machine. The plan is to make it a **service** that can run
on a node, so a network can be created and managed without a Linux desktop,
from a phone, and by more than one person. Machines stay reproducible from the
fleet file. The control plane is just what holds that file and runs the
renderer.

## The layers

1. **kiwi-modules**: the modules and the render contract for one machine. *Built.*
2. **kiwi-stack**: the machine side, from `kiwi-stack apply`. *Built.*
3. **kiwi-server core**: the fleet, hosts, targets, ISOs, the CA, enrolment and
   apply, headless as today. *Built.*
4. **The control module**: the core as a container, with an API and a web UI,
   running as a module on a node like any other.
5. **Clients**: the web UI first. The GTK app stays and talks to the local CLI
   or to a controller over the mesh, and the CLI stays too. No front end grows
   logic of its own.

## The control node

The controller runs on a node at home (the *control node*), reachable from the
mesh for admins only, on an encrypted disk. It holds the seed, the CA key, the
fleet file and every configuration.

The rented **master becomes replaceable relay infrastructure**. It holds only
what it needs to run: its WireGuard keys and peers, its own passwords and its
certificate. Losing it costs a re-apply from the control node. Losing the
control node costs a restore of the fleet backup.

## Users

A `users:` block with two roles: a **fleet admin** who can do everything, and
**node admins** bound to their own hosts. A node admin sees those hosts'
status, logs, workloads and backups, and enrols devices into the groups the
fleet admin allows, but sees nothing of the master, the CA or the other nodes.
Login is a password plus a client certificate from the fleet CA or WebAuthn,
and every change goes to an audit log.

## Joining a machine

Both paths stay:

- **A per-host ISO** with its role (today's `build --offline`), for offline
  installs.
- **A generic bootstrap ISO** per target, built once by CI and carrying no
  secrets. On first boot it fetches its role from the controller with a
  one-time **join token**. A hand-installed machine or a VPS joins with one
  line: `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Every CoreOS-lineage machine is meant to run **one bootc image**, with the role
arriving at first boot.

## Federation and multi-hop

Networks that trust each other's CA and delegate names to each other become
clients of each other. With the third exit mode, one network's master can
leave the Internet through another's: **multi-hop**, where the second master
sees only the first. Several masters run by one operator then make a VPN
service of one's own: entry masters in one country, exit masters in others,
Tor inside.

## The orchard

The orchard is for people who run many masters for others. It is a separate app
or a kiwi-server plugin that creates VPSes through provider APIs, hands each
master its install and a registration token, collects a heartbeat from every
master (version, health, disk, last update), and rolls out updates by moving
image tags per channel.

It cannot log into a master, read a fleet or touch a node. Each tenant's
control node at home keeps their network. The host of the master cannot read
it, and runs one VM per tenant. kiwi-server's netcup support (`kiwi-server
vps`, *built*) is the first piece of its provider driver.

## Also on the list

A standby master, rootless podman, IPv6 end to end, ARM boards, port ranges
and a games module, and a restore of a node's data on first boot.
