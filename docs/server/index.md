# kiwi-server

kiwi-server is the tool that creates and manages a Kiwi Network. You describe
every machine in one file, `fleet.yaml`, and kiwi-server sets the machines up
from it, so you do not have to install and configure each one by hand.

For each host, kiwi-server makes an **unattended install ISO**. This is an
install image that installs Fedora CoreOS, uCore or Debian without asking any
questions and then powers the machine off. kiwi-server then **applies** the
machine's role over SSH, which turns the machine into a `kiwi-master` or a
`kiwi-node`. After that it keeps working with the fleet: it enrolls WireGuard
clients, reads each machine's health, keeps the secrets, backs up the fleet,
and unlocks encrypted disks.

kiwi-server comes as a command-line tool (CLI), `kiwi-server`, and as a GTK4
app, **Kiwi Server**. Both are installed into `~/.local` and need no root
rights.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Latest release: **v2.42.0**. It is available in the [Kiwi catalog](../desktop/catalogs.md).
- kiwi-server is built on [kiwi-modules](single.md) v0.23.0, which contains the
  modules and the program that renders them, and on [kiwi-stack](single.md)
  v0.5.0, which is the part that runs on each machine. Both are vendored, which
  means a copy of each is included in kiwi-server, and they are pinned by tag.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Install

```bash
kiwi install kiwi-server        # with kiwi-updater
```

Or install it from a checkout of the repository: run `./install.sh install`,
then `kiwi-server doctor`.

kiwi-server needs Python 3.9+ with PyYAML and Jinja2, and the programs
`openssl` and `ssh`. The secret store needs `age`. To build ISOs you need
`butane`, `coreos-installer` and `xorriso`, and for Debian also `cpio`, `gzip`
and `curl`. On Silverblue or Bluefin, do not layer these packages onto the
system. Build the ISO tools as one container image instead:

```bash
kiwi-server toolchain build     # used automatically when the tools are missing
```

`qrencode` (for `enroll --qr`), `shellcheck` and `docker compose` are optional.

## From nothing to a running network

The commands below take you from an empty directory to a running network with
a master, a node and your own devices:

```bash
kiwi-server init                          # a commented fleet.yaml
$EDITOR fleet.yaml                        # hosts, roles, your SSH key, the install disk
kiwi-server secrets init fleet.yaml       # optional: secrets/ as one age-encrypted store
kiwi-server validate fleet.yaml

# the master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   boot it; it installs and powers off; start it again
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# each node: its WireGuard client first, then media, then the role
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# your own devices
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # what every machine reports
```

By default an install ISO contains **none of the stack's secrets**. It contains
only the base system, and the role and its stack are sent to the machine
afterwards by `apply`. If a machine cannot be reached over SSH,
`build --offline` puts the whole role and its secrets on the ISO instead. Do
not upload such an ISO to a hosting provider's ISO store, and delete it after
the install.

**If you do not want to use an ISO at all,** `kiwi-server script fleet.yaml papaya`
prints the script for a machine that you installed yourself. With `--offline`
the script contains the whole role.

On a VPS from netcup, `kiwi-server vps install fleet.yaml sorbet` wipes the
server and installs the ISO through netcup's API, so nobody has to sit at a
console. netcup is the only hosting provider supported so far. Others are
[planned](roadmap.md#more-hosters-and-network-boot).

## Commands

| Command | What it does |
|---|---|
| `init [fleet.yaml]` | Writes the example fleet file. `--domain` sets the domain, and the default is `home`. |
| `validate fleet.yaml [host…]` | Checks the fleet file. It renders every stack, so that errors in modules are found too. |
| `list` / `show fleet.yaml <host>` | The first lists the hosts and what has been generated for them. The second shows one host's effective config, with the secrets masked. |
| `render fleet.yaml [host…]` | Writes the role scripts, stacks and install configs into `output/<host>/`. |
| `build fleet.yaml [host…]` | Renders, then builds the ISO. By default the ISO contains only the base system, and with `--offline` it contains the whole role. |
| `script fleet.yaml <host>` | Prints the script for any machine. With `--offline` the script contains the whole role. |
| `apply fleet.yaml <host…>` | Renders again, sends the role to the machine over SSH and runs it there (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Shows what the machines report: role, stack, problems, disks, backups and certificates. |
| `enroll fleet.yaml <host\|name>` | Creates a WireGuard client on the master, or fetches one that exists already (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Manage `secrets/` as one age-encrypted file, which is opened into memory when you unlock it (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Shows a host's generated passwords. |
| `ca fleet.yaml` | Shows the fleet CA. |
| `mtu fleet.yaml <node\|device\|address>` | Measures a tunnel's real MTU and tells you what value to set (`--write`). |
| `openwrt fleet.yaml` | Writes a script that joins an OpenWrt router to the mesh ([Routers](../network/routers.md)). |
| `backup` / `restore` / `prune` | Back up the fleet directory to nodes, bring it back from there, and remove old machine backups ([Operations](operations.md)). |
| `unlock fleet.yaml <host>` | Forwards a Tang ring to a machine that is waiting at boot for its encrypted disk to be unlocked ([Operations](operations.md)). |
| `vps login\|list\|probe\|install` | Work with netcup's Server Control Panel API. |
| `roles [-v]`, `modules [-v]`, `targets` | Show what is available, with every setting and its default. |
| `toolchain [status\|build]`, `doctor` | Manage the ISO tools, and check this machine. |

Every command accepts `--porcelain` (output as JSON), `-o/--output-dir`,
`--quiet` and `-v`. `kiwi-server <command> -h` explains a single command.

## The app

The app **Kiwi Server** opens the fleet you worked on last. Its sidebar has an
overview, one row for each host, and the defaults. A host's *Overview* shows
current information from `kiwi-server status`. The app fetches it once a minute
while the window is focused, over SSH and read-only. A host's *Settings* is a
form that is built from the roles and modules. *Apply*, *Build* and *Render* run
the command-line tool and show its output as it is produced. Before *Build*
starts, it lists the disks it will wipe. *Unlock* and *Lock* open and close the
secret store. The app writes plain YAML, so the comments in a fleet file that
you wrote by hand are lost when the app saves it.

## Things to keep in mind { #mind }

!!! danger "The ISOs wipe the disk they are told to"
    An install ISO wipes the disk it was built for as soon as a machine boots
    from it, without asking. Label your ISOs. This is exactly why `build`
    requires the `disk:` setting.

- **The output contains secrets.** These are password hashes, WireGuard keys,
  TLS keys and LUKS keys. The files are written with mode 0600, and `output/` is
  ignored by git. Handle ISOs made with `--offline` with the same care.
- **Service passwords are generated** from `secrets/seed` if you leave them
  out of the fleet file. `validate` warns you about passwords that are written
  in the fleet file, and `kiwi-server secrets show` prints the generated ones.
  A machine refuses an apply that was made with a different seed.
- **SSH host keys** are recorded in `secrets/known_hosts` the first time
  kiwi-server connects to a machine. If a machine's key changes later, the
  connection is refused. After you reinstall a machine, delete its line from
  that file.
- **A role script runs as root.** Before you trust a role that you did not
  write, read the output of `kiwi-server script fleet.yaml <host>
  --offline`.
- **A failed role is reported.** The machine keeps the file
  `/var/lib/kiwi-server/role.failed`, which names the step and the command that
  failed, and `status` shows it.

## Status

The whole process, from the fleet file to a running machine, was tested on real
hardware in October and November 2026. Debian, uCore and Fedora CoreOS went
through the whole process on two VPSes, a mini PC and a VM. In an exercise that simulated a dead node, an encrypted Debian machine was
rebuilt in about 14 minutes. Node backups were restored from one node onto
another (papaya to lychee). The tunnel MTU was measured and tuned on real
connections, including mobile ones. The automated tests (CI) render every role,
run shellcheck on every script and validate every Butane config. They also
compare four reference stacks, called golden stacks, with their stored output
byte for byte.

Federation between networks has not been tested yet. Everything uses IPv4. The
Debian ISO exists for amd64 only. A control plane (`kiwi-server serve`) is
planned and designed, but it is not built.

Read on: [The fleet file](fleet.md) · [Roles](roles.md) · [Modules](modules.md) ·
[Machines](machines.md) · [Operations](operations.md) ·
[One machine without a fleet](single.md)
