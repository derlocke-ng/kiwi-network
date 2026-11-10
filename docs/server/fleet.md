# The fleet file

`fleet.yaml` describes every machine kiwi-server builds. It has two keys:
`defaults`, which applies to every host, and `hosts`, with one entry per
machine. Anything a host sets overrides the defaults. `kiwi-server init` writes
a commented starting point, and the full reference is
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

A host has a **target** (what gets installed) and a **role** (what it becomes):

- `target`: `coreos`, `ucore` (the default) or `debian`. See [Machines](machines.md).
- `role`: `bare` (the default), `master` or `node`. See [Roles](roles.md).

## Example

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya becomes papaya.home; services are cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # WIPED by the ISO without asking
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # the master, a Debian VPS
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # what clients and nodes connect to

  lychee:                                # a gateway node
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # the LAN side
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # a cloud node on uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # for the first account; turn it off afterwards
```

There are no service passwords in it. Every password you leave out is
generated from `secrets/seed`, and `kiwi-server secrets show fleet.yaml papaya`
prints them. The nodes' WireGuard configs aren't named either:
`kiwi-server enroll` writes `secrets/<hostname>.conf`, which each node finds by
itself, and the node's mesh address is read from it.

## Defaults

| Key | Default |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | none; required for `build`, must start with `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`; give a `password_hash` for the console |
| `network` | `dhcp: true`; static with `address` (CIDR), `gateway`, `dns`, or an `iprange` that hands out addresses in file order |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (or `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Tang rings to bind the disk to (see [Operations](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | where the fleet directory is backed up to (`hosts: []`, `keep: 10`) |
| `vps` | `server:` a netcup server id, name or nickname |

## How settings combine

- Hosts override defaults **key by key**. The lists `admin.ssh_keys`,
  `debian.packages`, `debian.kernel_arguments` and the `coreos.*` lists *add*
  to the defaults instead.
- A module role keeps its settings in a block named after the role (`master:`,
  `node:`): the **stack settings** first, then **one block per module**.
- `modules:` in that block **replaces** the preset's module list. Required
  modules are added by themselves.
- **File settings** (certificates, configs) are paths relative to the fleet
  file. Their content is embedded in the host's role script.
- A setting given with no value means the default. A misspelled key is an error
  with a suggestion.

## Stack settings

| Setting | Default | Notes |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` or `minimal` |
| `runtime` | `podman` | podman quadlets; `docker` runs docker compose |
| `auto_update` | `registry` | weekly `podman auto-update`; `off`: images change with an apply |
| `docker_dir` | `/home/user/docker` | the stack and its data |
| `service_user` | the admin user | owns the data directories |
| `vpn_ip` | from the WireGuard config | the machine's mesh address |
| `master_ip` | from the fleet | the master's mesh address |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | measure with `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | from the default route | the LAN interface |
| `daily_vpn_restart` | `07:00` | empty: never |
| `weekly_update` | `Sun *-*-* 00:00` | empty: never |

`kiwi-server roles -v` and `kiwi-server modules -v` list every setting with its
default.

## Checking what you wrote

```bash
kiwi-server validate fleet.yaml          # errors and warnings
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server also checks the domain: `.local` is refused, `.lan` and public
top-level domains get a warning (see [DNS](../network/dns.md#names-servicehostnamehome)).

## Taking over a v1 machine

A machine that ran one of the old v1 stacks can be taken over without losing
data. The default runtime is now podman, and the role script does not stop
docker containers. So either set `runtime: docker`, or stop the old stack
first. Then set `docker_subnet` to what the old stack used, and rename the data
directories to the module names (`kmvpn-server` → `km-vpn-server`, `knvault` →
`kn-vault`, …). The containers keep their addresses and wg-easy keeps its peers.
