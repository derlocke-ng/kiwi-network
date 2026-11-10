# Operations

This page covers the work that comes after the machines are installed and
running: checking their health, keeping the secrets safe, backing up the fleet
and the machines' data, unlocking encrypted disks, tuning the tunnel MTU and
installing on a netcup server. You do all of it with kiwi-server from your own
computer, the *operator's machine*, where the fleet file and the secrets are
kept.

## Status

`kiwi-server status` shows how the machines of the fleet are doing, either all
of them or the one you name:

```bash
kiwi-server status fleet.yaml            # every host
kiwi-server status fleet.yaml papaya        # one
```

kiwi-server connects to each machine over SSH and only reads from it. Each
machine reports its role and its stack (the set of containers and services it
runs), any problems such as a failed role or a stopped container, its disks and
whether they are encrypted or locked, its backups, and how long its
certificates are still valid. A backup node also reports its capacity. The
Kiwi Server app shows the same information on each host's *Overview*.

## Secrets

Everything secret is stored in `secrets/`, the directory next to the fleet
file. It holds the seed from which every generated password is derived, the
fleet's own certificate authority (CA), the WireGuard configs, the LUKS keys
of the encrypted disks and the SSH host keys. kiwi-server can keep this
directory encrypted and open it only while you work with it:

```bash
kiwi-server secrets init fleet.yaml      # secrets/ becomes one age-encrypted file
kiwi-server secrets unlock fleet.yaml    # open it into memory (--for 8h; 0 keeps it open)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` creates the encrypted store. It puts one key in the GNOME
Keyring and shows you a **recovery key**. The recovery key is shown only
once. While the store is open, every program that runs under your user
account can read it.

## Backing up the fleet itself

The fleet directory holds the fleet file and `secrets/`, and kiwi-server backs
it up by itself. After every successful render or build (the two steps that
generate the hosts' configuration and their install ISOs), it encrypts the
fleet directory (AES-256 with PBKDF2, 600,000 iterations) and copies it to the
nodes listed in `backup.hosts`. Each of these nodes keeps the newest ten
copies. On a new computer you get the fleet directory back from one of those
nodes. You can also write a copy to a directory of your choice at any time:

```bash
kiwi-server restore --from core@lychee.home  # the fleet directory back
kiwi-server backup fleet.yaml --local /mnt/usb   # or a copy to a directory, any time
```

## Backing up the machines' data

The data on the machines is backed up with restic, a backup program. One node
stores the backups. Give that node the `backup-server` module, which runs a
restic REST server. Every machine that should be backed up gets the `backup`
module, with a setting that points at that server:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Every night at 03:00, or up to 15 minutes later, restic sends the data that
each module wants kept to the backup server, encrypted. A machine can reach
only its own repository on the server, and it can only add to it. It cannot
delete anything there. This is why the command that removes old snapshots is
run on the operator's machine. A snapshot is what restic calls the saved
state of one backup run. The first command below is for the machine itself,
the second for your computer:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # on the machine
kiwi-server prune fleet.yaml            # keep 7 daily, 4 weekly, 6 monthly
```

A restore has been tested between two nodes, by restoring papaya's backups
onto lychee.

### Coming in the next release

!!! info "On the `several-servers` branch"
    This work has been pushed to the `several-servers` branches of
    kiwi-modules and kiwi-server, but it is not merged or released yet.
    Running several backup servers and the automatic restore were tested on
    hardware. The VPN health check was not.

- **Several backup servers.** `backup.servers` takes a list of servers, and
  each server gets a full copy of its own. If one server fails, only its copy
  is affected. A restore takes the most recent copy from whichever server has
  it, and `kiwi-stack snapshots` lists the snapshots server by server. The
  single `server` setting still works.
- **A rebuilt machine restores itself.** A machine that has been rebuilt
  finds backups of itself on the server, although it has made none of them.
  In that case it restores every module by itself before it makes its first
  backup, and then backs up as before. This is the default, 
  `backup.restore: auto`. With `hold`, the machine waits until you run `kiwi-stack restore` or
  `kiwi-stack backup --new`.
- **Pruning on a timer.** Pruning means removing old snapshots.
  `kiwi-server prune fleet.yaml --every week` (or `day`) installs a systemd
  user timer on your computer, which is the only place that holds the keys
  that are allowed to delete. If a run is missed, it is made up at the next
  login. `kiwi-server status` shows each backup copy, and it warns when a
  backup node has not been pruned for three weeks.
- **A stuck connection to the commercial VPN provider recovers by itself.**
  gluetun, the VPN client container, gets a health check. When it has been
  unhealthy for five minutes, the container is killed, and at its next start
  it picks another server.

## Encrypted disks and unlocking

An encrypted disk has to be unlocked every time the machine boots. This
section describes how each target (the operating system a machine is
installed with) encrypts its disk, and how the disk can be unlocked with or
without a person present.

- **Debian** (`debian.encrypt: true`) is installed with a one-time key, which
  you type in at the first boot. You find it in `secrets/luks/<host>.once`.
  The first `apply` replaces it with `secrets/luks/<host>.key`, and a master
  also gets a new volume key at that point. If you lose that key file, the
  disk stays locked, so keep the fleet backed up.
- **CoreOS / uCore** encrypt the disk as part of the install, through
  Ignition, the tool that configures a CoreOS machine at its first boot. The
  machine needs about 4 GiB of RAM at first boot for this.
- **Tang rings** let encrypted machines unlock their disks at boot without a
  person present. Tang is a small server that a machine asks over the network
  for help with unlocking its disk. A node runs the `tang` module, and each
  ring is one Tang server with its own keys. By default there is one ring,
  `infra`, on port 7500. A host's `unlock:` block binds its disk to one or
  more rings and sets a threshold, the number of rings that have to answer.
- **SSH in the initramfs** (`unlock.ssh: true`) lets you reach a machine that
  is waiting for its disk to be unlocked. The initramfs is the small system
  that runs before the disk is open. The SSH server in it is dropbear on
  Debian and dracut-sshd on CoreOS. It accepts its own restricted key,
  `secrets/unlock_ed25519`, which can only run the unlock.
- `kiwi-server unlock fleet.yaml <host>` forwards a ring to a machine that is
  waiting at boot, so the machine can use a ring it cannot reach by itself.
  With `--manual` it hands over the key itself. A ring named `operator` is
  served from your own machine while it is needed. `vpn-server.unlock_relay`
  makes a ring reachable through the master for machines behind NAT.

## Tunnel MTU

The MTU is the largest packet a network link carries in one piece. WireGuard
adds its own headers to every packet, so a tunnel carries smaller packets than
the connection underneath it, and a mobile connection carries smaller ones
still. A packet that is too big for one of the links on its way is dropped or
split, and connections stall. Kiwi deals with this in three ways:

- **Two settings.** `wg_mtu` is the MTU of gluetun (the VPN client), of the
  client configs that wg-easy (the WireGuard server) issues, and of the
  WireGuard interface `wg0`.
  Its default is **1376**. That is a multiple of 16, because WireGuard pads
  every packet to the next multiple of 16 bytes. `bridge_mtu` is the MTU of
  the stack network, which connects the containers on a machine. Its default
  is **1500**. `validate` refuses a `wg_mtu` whose padded packet plus 80
  bytes of headers does not fit into the bridge. It also refuses anything
  below 1280, which is the smallest MTU that IPv6 works with.
- **The MSS is clamped in both directions.** The MSS is the largest amount of
  data that TCP puts into one packet. wg-easy and the VPN client both limit
  it to `wg_mtu - 40`, so TCP never tries a segment that cannot pass.
- **TCP finds a working size by itself.** The VPN client runs with
  `net.ipv4.tcp_mtu_probing=1` and `tcp_base_mss=1024`. When a connection
  runs over a path that silently drops big packets, TCP tries smaller ones
  until it finds a size that works, instead of hanging.

### Measuring a path: `kiwi-server mtu`

To find out what the path to a node or a device really carries, measure it:

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # a node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # a device from secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # and write wg_mtu into the fleet file
```

The probe sends pings through the tunnel with the don't-fragment flag set,
so they cannot be split on the way. It sends them from inside the network
namespace that holds the tunnel. A network namespace is a separate network
environment on a machine, such as the one a container has. A node is measured
from its own VPN client, because the client's firewall drops incoming pings.
A device is measured from the WireGuard server. The probe starts with an
ordinary ping, then tries every multiple of 16 from 1280 upwards and reports
the largest size that arrives **whole**. While it pings, it reads the
kernel's reassembly counters. This way a reply that was split on the way and
put back together does not count as fitting.

The probe also tells you what to set. For a **device**, that is the `MTU =`
line in the device's own WireGuard config, and nobody else is affected. For a
**node**, it is `wg_mtu` on that node and on its master. With `--write` the
probe puts the value into the fleet file and changes only those lines. One
thing cannot be seen from this end: a packet that is split only on its way
out and put back together by the far end.

The defaults were measured on the test fleet. A phone on mobile data needs
its own measurement, because mobile paths are often IPv6-only behind 464XLAT
with nested encapsulation. Measure the phone itself, and lower its own
`MTU =` if the probe says so.

## netcup VPSes

netcup is a hosting provider, and today it is the only one where kiwi-server
can install a rented server (a VPS) by itself. It does this through netcup's
Server Control Panel API. Other hosting providers are
[planned](roadmap.md#more-hosters-and-network-boot) as plugins.

```bash
kiwi-server vps login fleet.yaml         # device-flow login; the token goes to secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wipe the server and install the host's ISO
```

`vps install` wipes the server, so it asks first unless you pass `--yes`. It
refuses to install in three cases: when the ISO carries role secrets, when
`disk:` names the wrong disk, and when a CoreOS disk is to be encrypted on a
server with less than 3500 MiB of RAM.
