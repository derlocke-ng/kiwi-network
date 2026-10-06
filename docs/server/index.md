# kiwi-server

kiwi-server builds the machines of a Kiwi Network. Write one `fleet.yaml` and it
produces, for each host, a **first-boot script**, an **Ignition or preseed
config**, and an **unattended install ISO**. Boot the ISO and walk away: the
machine installs itself, reboots and comes back as a `kiwi-master` or a
`kiwi-node`, on Fedora CoreOS, uCore or Debian stable, with automatic updates
that only reboot in the window you chose.

```
fleet.yaml ──render──▶ <host>.role.sh        the role, as one bash script
                       <host>.bu / .ign       CoreOS, uCore: Butane → Ignition
                       <host>.preseed.cfg     Debian: preseed + /kiwi-server files
           ──build───▶ <host>.iso             installs to the given disk WITHOUT ASKING,
                                              reboots, runs the role script once
```

It has a CLI, `kiwi-server`, and a GTK4 desktop app, **Kiwi Server**
(`kiwi-server-gui`). Both install into `~/.local` and need no root.

- Repository: [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Version 2.2.0 (`kiwi.manifest`). There are no release tags yet, so installs
  track `main`.

## Install

kiwi-server is a [kiwi-updater](../desktop/kiwi-updater.md) app, but it is not
in the Kiwi catalog yet. Track the repo directly:

```bash
kiwi add https://github.com/derlocke-ng/kiwi-server.git
kiwi install kiwi-server
```

Or install from a checkout, with the same installer kiwi runs:

```bash
git clone https://github.com/derlocke-ng/kiwi-server.git && cd kiwi-server
./install.sh install            # ~/.local/bin/kiwi-server, kiwi-server-gui, the library
kiwi-server doctor              # python, PyYAML, Jinja2, build tools, container runtime
```

It needs `python3` with PyYAML and Jinja2 (`pip install --user jinja2` if the
image lacks it), `openssl` and `git`. Building ISOs also needs `butane`,
`coreos-installer` and `xorriso`. On Fedora, `dnf install butane
coreos-installer xorriso`. On Silverblue or Bluefin, build one container image
with all three instead of layering packages:

```bash
kiwi-server toolchain build     # used automatically when the tools are missing
kiwi-server toolchain           # which tools run natively, which in the container
```

## Quick start

```bash
kiwi-server init                     # writes a commented fleet.yaml
$EDITOR fleet.yaml                   # hosts, roles, your SSH key, the install disk
kiwi-server validate fleet.yaml
kiwi-server render fleet.yaml        # scripts + configs into ./output/<host>/
kiwi-server build fleet.yaml         # + the ISOs (base images cached in ~/.cache/kiwi-server)
sudo dd if=output/sh3/sh3.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Boot the machine from that stick. CoreOS and Debian install, reboot, and run
the role on first boot. uCore reboots twice more first (an unsigned rebase, then
a signed one). Follow along with `journalctl -u kiwi-role -f`. The file
`/var/lib/kiwi-server/role.done` appears when the role has finished.

**No ISO needed?** `kiwi-server script fleet.yaml sh3 > sh3.sh` prints the same
script the ISO runs. Copy it to any installed Debian, CoreOS or uCore machine
and run `sudo bash sh3.sh`.

### Building a network, in order

1. **The master first.** Give it `role: master` and a provider key for its
   exit (see [the fleet file](fleet.md)), and set `wg_host` to the name or IP
   address clients will connect to. Build it and boot it.
2. **Issue WireGuard configs.** In the master's wg-easy (`127.0.0.1:51821`
   over `ssh -L`, or at `10.8.0.1:51821` from the mesh), create one client per
   node and per router, and save each config under `secrets/`.
3. **The nodes.** Point each node's `vpn-client.wireguard_config` at its
   config, then build and boot it. A node's mesh address is read from the
   config's `Address`.
4. **Your devices.** Import `secrets/ca/kiwiCA.pem` so the fleet's HTTPS names
   are trusted. Add laptops and phones as wg-easy clients.

## Commands

| Command | What it does |
|---|---|
| `init [path]` | write a commented `fleet.yaml` |
| `validate fleet.yaml [hosts…]` | check the fleet file, with warnings |
| `list fleet.yaml` | the hosts and what has been generated for them (name, hostname, target, role, address) |
| `show fleet.yaml <host>` | what a host ends up with, secrets masked |
| `render fleet.yaml [hosts…]` | role scripts, stacks and configs into `output/` |
| `build fleet.yaml [hosts…]` | render, then build the install ISOs |
| `script fleet.yaml <host>` | print one host's role script |
| `ca fleet.yaml` | show the fleet CA |
| `openwrt fleet.yaml …` | a `uci` script that joins an OpenWrt router to the mesh ([Routers](../network/routers.md)) |
| `roles [-v]`, `modules [-v]`, `targets` | what is available, with every setting and its default |
| `toolchain [status\|build]` | the ISO build tools, native or in a container |
| `doctor` | check this machine for everything above |

Global options include `-o/--output-dir`, `--cache`,
`--toolchain auto|native|container` and `--porcelain` (JSON for the GUI and scripts).

## The GUI

**Kiwi Server** in the app grid opens or creates a fleet. Pick *Defaults* or a
host on the left and edit on the right. Every host field shows what it
inherits. The role's stack settings and one group per module are built from
`role.yaml` and the modules' `module.yaml`, so changing the `modules` list
changes the groups. *Render* and *Build ISOs* run the CLI and stream its output.
*Build* lists every host with the disk it will wipe before it starts.

The GUI writes plain YAML, so comments in a hand-written fleet file are lost
when it saves.

## Mind

!!! danger "The ISOs wipe the disk they are told to"
    On boot, without asking. Label them. `disk:` is required for `build` for
    exactly that reason.

- **The output holds secrets**: password hashes, WireGuard keys, TLS keys, the
  LUKS passphrase. Files are written with mode 0600 and `output/` is in
  `.gitignore`. Treat the ISOs the same way.
- **A role script runs as root.** Read `kiwi-server script fleet.yaml <host>`
  before trusting a role you did not write, as you would any installer.

## Status

kiwi-server 2.x renders the modules from the kiwi-v2 module system. The three
presets are the live v1 setups (kiwi-master, kiwi-node-gw, kiwi-cloud) taken
apart into modules and verified against them file by file. The generators are
tested in CI: every rendered script is shellchecked, every Butane config is
validated with `butane --strict`, every preset's compose file is checked with
`docker compose config`, and the Debian ISO rebuild runs against a mock netinst.
The first boot of each target end to end on a real machine has **not** yet been
verified from this pipeline.

Read on: [The fleet file](fleet.md) · [Roles](roles.md) ·
[Modules](modules.md) · [Targets, updates & first boot](targets.md)
