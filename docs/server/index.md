# kiwi-server

kiwi-server creates and manages a Kiwi Network. You describe every machine in
one `fleet.yaml`. kiwi-server makes an **unattended install ISO** for each host,
which installs Fedora CoreOS, uCore or Debian and powers the machine off. It
then **applies** the role over SSH, turning the machine into a `kiwi-master` or
a `kiwi-node`. After that it keeps working with the fleet: it enrolls WireGuard
clients, reads each machine's health, keeps the secrets, backs up the fleet,
and unlocks encrypted disks.

It has a CLI, `kiwi-server`, and a GTK4 app, **Kiwi Server**. Both install into
`~/.local` and need no root.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Latest release: **v2.42.0**. It is in the [Kiwi catalog](../desktop/catalogs.md).
- Built on [kiwi-modules](single.md) v0.23.0 (the modules and their renderer)
  and [kiwi-stack](single.md) v0.5.0 (the machine side), vendored and pinned by
  tag.

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

Or from a checkout: `./install.sh install`, then `kiwi-server doctor`.

It needs Python 3.9+ with PyYAML and Jinja2, `openssl` and `ssh`. The secret
store needs `age`. Building ISOs needs `butane`, `coreos-installer` and
`xorriso` (plus `cpio`, `gzip` and `curl` for Debian). On Silverblue or Bluefin,
build them as one container image instead of layering packages:

```bash
kiwi-server toolchain build     # used automatically when the tools are missing
```

`qrencode` (for `enroll --qr`), `shellcheck` and `docker compose` are optional.

## From nothing to a running network

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

Media carry **none of the stack's secrets** by default: only the base system.
The role and its stack arrive with `apply`. If a machine cannot be reached over
SSH, `build --offline` puts the whole role and its secrets on the ISO instead.
Keep such an ISO off a provider's ISO store and delete it after the install.

**No ISO at all?** `kiwi-server script fleet.yaml papaya` prints the script for a
machine you installed yourself (`--offline` for the whole role).

On a netcup VPS, `kiwi-server vps install fleet.yaml sorbet` wipes the server and
installs the ISO through netcup's API.

## Commands

| Command | What it does |
|---|---|
| `init [fleet.yaml]` | write the example fleet file (`--domain`, default `home`) |
| `validate fleet.yaml [host…]` | check it, rendering every stack to catch module errors |
| `list` / `show fleet.yaml <host>` | the hosts and what has been generated / one host's effective config, secrets masked |
| `render fleet.yaml [host…]` | role scripts, stacks and install configs into `output/<host>/` |
| `build fleet.yaml [host…]` | render, then the ISO: base system by default, `--offline` for the whole role |
| `script fleet.yaml <host>` | the script for any machine (`--offline` for the whole role) |
| `apply fleet.yaml <host…>` | re-render, send the role over SSH and run it (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | what the machines report: role, stack, problems, disks, backups, certificates |
| `enroll fleet.yaml <host\|name>` | create or fetch a WireGuard client on the master (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` as one age-encrypted file, opened into memory (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | a host's generated passwords |
| `ca fleet.yaml` | the fleet CA |
| `mtu fleet.yaml <node\|device\|address>` | measure a tunnel's real MTU and say what to set (`--write`) |
| `openwrt fleet.yaml` | a script that joins an OpenWrt router to the mesh ([Routers](../network/routers.md)) |
| `backup` / `restore` / `prune` | the fleet directory to nodes and back; old machine backups removed ([Operations](operations.md)) |
| `unlock fleet.yaml <host>` | forward a Tang ring to a machine waiting at boot ([Operations](operations.md)) |
| `vps login\|list\|probe\|install` | netcup's Server Control Panel API |
| `roles [-v]`, `modules [-v]`, `targets` | what is available, with every setting and its default |
| `toolchain [status\|build]`, `doctor` | the ISO tools; check this machine |

Every command takes `--porcelain` (JSON), `-o/--output-dir`, `--quiet` and
`-v`. `kiwi-server <command> -h` explains one command.

## The app

**Kiwi Server** opens your last fleet. The sidebar has an overview, one row per
host, and the defaults. A host's *Overview* shows live facts from
`kiwi-server status` (polled once a minute while the window is focused,
read-only over SSH). Its *Settings* is a form built from the roles and modules.
*Apply*, *Build* and *Render* run the CLI and stream its output, and *Build*
lists the disks it will wipe before it starts. *Unlock* and *Lock* open and
close the secret store. The app writes plain YAML, so comments in a
hand-written fleet file are lost when it saves.

## Mind

!!! danger "The ISOs wipe the disk they are told to"
    On boot, without asking. Label them. `disk:` is required for `build` for
    exactly that reason.

- **The output holds secrets**: password hashes, WireGuard keys, TLS keys, LUKS
  keys. Files are written 0600 and `output/` is git-ignored. Treat ISOs made
  with `--offline` the same way.
- **Service passwords are generated** from `secrets/seed` when you leave them
  out of the fleet file. `validate` warns about passwords written in it.
  `kiwi-server secrets show` prints them. A machine refuses an apply made with a
  different seed.
- **SSH host keys** are recorded in `secrets/known_hosts` on first contact, and
  a changed key is refused (after a reinstall, drop the line).
- **A role script runs as root.** Read `kiwi-server script fleet.yaml <host>
  --offline` before trusting a role you did not write.
- **A failed role says so.** The machine keeps `/var/lib/kiwi-server/role.failed`
  (the step and the command), and `status` shows it.

## Status

The pipeline was proven on hardware in October and November 2026. Debian,
uCore and Fedora CoreOS were booted end to end on two VPSes, a mini PC and a
VM, and a dead-node drill rebuilt an encrypted Debian machine in about 14
minutes. CI renders every role, shellchecks every script, validates every Butane
config, and pins four golden stacks byte for byte.

Not proven yet, as the repository says: federation, a phone on 5G, and restoring
a node's data. Everything is IPv4. The Debian ISO is amd64 only. A planned
control plane (`kiwi-server serve`) is designed but not built.

Read on: [The fleet file](fleet.md) · [Roles](roles.md) · [Modules](modules.md) ·
[Machines](machines.md) · [Operations](operations.md) ·
[One machine without a fleet](single.md)
