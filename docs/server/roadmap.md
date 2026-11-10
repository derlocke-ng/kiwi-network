# Where it is going

This page describes what kiwi-server is planned to become, and which parts of
that plan exist already.

!!! info "Designed, not built"
    This page summarises kiwi-server's
    [control-plane design](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md),
    which was agreed in October 2026. Nothing described here exists yet,
    unless a line says *built*. The
    [roadmap](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    tracks the order of the work.

Today kiwi-server is a desktop tool. The fleet file, the secrets and the CA
(the fleet's certificate authority) are kept on the operator's machine. The
plan is to make it a **service** that can run on a node. A network can then be
created and managed without a Linux desktop, from a phone, and by more than
one person. Machines stay reproducible from the fleet file. The control plane
is the part that holds that file and runs the renderer, the program that turns
the fleet file into each machine's configuration.

## The layers

The design divides the software into five layers.

1. **kiwi-modules** contains the modules and the render contract, which
   defines how the configuration of one machine is rendered. *Built.*
2. **kiwi-stack** is the part that runs on the machine. It starts with
   `kiwi-stack apply`, which puts a rendered configuration onto the machine.
   *Built.*
3. **The kiwi-server core** handles the fleet, hosts, targets, ISOs, the CA,
   enrolment and apply. It is headless, which means it has no graphical
   interface of its own, as today. *Built.*
4. **The control module** is the core packaged as a container, with an API and
   a web UI. It runs on a node as a module like any other.
5. **Clients** are the programs you use to work with the control module. The
   web UI comes first. The GTK app stays, and it talks either to the local CLI
   or to a controller (a running control module) over the mesh, the private
   WireGuard network. The CLI stays too. All logic stays in the core, so no
   client gets logic of its own.

## The control node

The controller runs on a node at home, which is called the *control node*.
Only admins can reach it, and only from the mesh, and its disk is encrypted.
It holds the seed, the CA key, the fleet file and every configuration.

The rented **master becomes a relay that can be replaced**. It passes the
network's traffic on and holds only what it needs to run, which is its
WireGuard keys and peers, its own passwords and its certificate. If the master
is lost, you apply it again from the control node. If the control node is
lost, you restore the fleet backup.

## Users

A `users:` block defines users with one of two roles. A **fleet admin** can do
everything. A **node admin** is bound to their own hosts. A node admin sees
the status, logs, workloads and backups of those hosts, and can enrol devices
into the groups that the fleet admin allows. A node admin sees nothing of the
master, the CA or the other nodes. To log in, a user needs a password plus
either a client certificate from the fleet CA or WebAuthn. Every change is
written to an audit log.

## Joining a machine

There are two ways for a machine to join the network, and both stay:

- **A per-host ISO** that carries the machine's role, which is today's
  `build --offline`. It is for offline installs.
- **A generic bootstrap ISO** per target, which is built once by CI and
  carries no secrets. On first boot the machine fetches its role from the
  controller with a one-time **join token**. A machine that was installed by
  hand, or a VPS, joins with one line:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Every machine of the CoreOS family is meant to run **one bootc image**, a
single bootable container image that is the same for all of them. The machine
receives its role at first boot.

## Federation and multi-hop

Federation connects separate Kiwi Networks. Networks that trust each other's
CA and delegate names to each other become clients of each other. A master
has three exit modes, which decide how its traffic reaches the Internet. With
the third one, a network's master sends its Internet traffic through the
master of another network. This is called **multi-hop**, and the second master
sees only the first one. An operator who runs several masters in this way has
a VPN service of their own, with entry masters in one country, exit masters in
other countries, and Tor inside the network.

## The orchard

The orchard is the planned service for people who run many masters for other
people. It is a separate app or a kiwi-server plugin. It creates VPSes through
the hosting providers' APIs and gives each master its install and a
registration token. It collects a heartbeat, a regular status report, from
every master (version, health, disk, last update). It rolls out updates by
moving the image tag of each update channel.

The orchard cannot log in to a master, read a fleet or change a node. Each
tenant, meaning each person whose master is run for them, keeps their network
on their own control node at home. The fleet and the keys stay there, so the
hosting provider that runs the master's VM cannot read the tenant's network
data. Each tenant's master runs in a VM of its own. The orchard needs a driver
for the providers' APIs, and kiwi-server's netcup support (`kiwi-server vps`,
*built*) is the first piece of it.

## More hosting providers, and network boot { #more-hosters-and-network-boot }

*Planned.* The aim is that a machine can be installed fully automatically,
wherever it is.

- **Hosting providers as plugins.** Support for netcup is built in today. The
  plan is a separate repository for the providers' APIs, so that anyone can
  add AWS, Hetzner and other providers. A plugin would work the way the
  netcup support works now: it creates or wipes a server, puts the install on
  it and boots it.
- **Wake-on-LAN and PXE boot** are planned for machines at home.
  Wake-on-LAN switches a machine on over the network, and PXE lets it boot
  from the network. A node then wakes up and installs itself over the
  network, and no USB stick is needed.

## Also on the list

The roadmap also lists a standby master, rootless podman, IPv6 from end to
end, ARM boards, port ranges and a games module, and restoring a node's data
on first boot.
