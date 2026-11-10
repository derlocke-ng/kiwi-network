# The fleet file

The fleet file, `fleet.yaml`, is where you describe every machine of your Kiwi
Network. For each machine it says which operating system it gets, what the
machine is used for and how its services are set up. kiwi-server builds every
machine from this description, so you write down what you want once and do not
have to configure any machine by hand.

The file has two keys. `defaults` holds the settings that apply to every host,
and `hosts` has one entry per machine. A setting in a host's entry overrides
the same setting in the defaults. `kiwi-server init` writes a commented file
that you can start from, and the full reference is
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Each host has a **target**, which is the operating system that gets installed,
and a **role**, which is the job the machine does afterwards.

- `target` is `coreos`, `ucore` (the default) or `debian`. See [Machines](machines.md).
- `role` is `bare` (the default), `master` or `node`. See [Roles](roles.md).

## Example

This fleet file describes three machines. The first is the master, which is
the machine that all the others connect to, on a Debian VPS (a rented virtual
server). The second is a gateway node, which sends a local network's traffic
through the VPN. The third is a cloud node, which runs Nextcloud and
Vaultwarden.

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

The example contains no service passwords. kiwi-server generates every password
that you leave out from the seed in `secrets/seed`, and
`kiwi-server secrets show fleet.yaml papaya` prints the passwords of that host.

The example does not name the nodes' WireGuard configuration files either.
`kiwi-server enroll` writes a node's configuration to `secrets/<hostname>.conf`,
and the node's VPN client finds it there without an entry in the fleet file.
The node's mesh address is read from the same file. The mesh is the private
WireGuard network that connects all your machines, and the mesh address is a
machine's address in it.

## Defaults

If neither your `defaults` block nor a host sets a key, kiwi-server uses the
built-in value from this table.

| Key | Default |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | No default. `build` needs it, and the value must start with `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Set a `password_hash` if you want to log in at the console |
| `network` | `dhcp: true`. For a static address, set `address` (in CIDR notation), `gateway` and `dns`. Or set an `iprange`, from which the hosts get their addresses in the order they appear in the file |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (or `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | The Tang rings that the disk is bound to. A ring is a Tang server, which lets an encrypted machine unlock its disk at boot (see [Operations](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | The hosts that the fleet directory is backed up to, and how many backups are kept (`hosts: []`, `keep: 10`) |
| `vps` | `server:` the id, name or nickname of a netcup server |

## How settings combine

- A host overrides the defaults **key by key**, so a host only has to name the
  keys that differ. The lists `admin.ssh_keys`, `debian.packages`,
  `debian.kernel_arguments` and the `coreos.*` lists are the exception. A
  host's entries in these lists are *added* to the defaults and do not replace
  them.
- The roles that are built from modules, `master` and `node`, keep their
  settings in a block named after the role (`master:` or `node:`). This block
  holds the **stack settings** first and then **one block per module**. The
  stack is the set of containers that a machine runs for its modules, and the
  stack settings apply to all of them.
- A `modules:` list in that block **replaces** the preset's module list. A
  preset is a ready-made list of modules. Modules that the listed ones require
  are added automatically.
- **File settings**, such as certificates and configuration files, are given as
  paths relative to the fleet file. kiwi-server copies the content of these
  files into the host's role script, which is the script that sets the machine
  up for its role.
- A setting that you write without a value gets its default. If you misspell a
  key, kiwi-server reports an error and suggests the key you probably meant.

## Stack settings

The stack settings apply to a machine's whole stack. You write them directly in
the role's block.

| Setting | Default | Notes |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` or `minimal` |
| `runtime` | `podman` | `podman` runs the containers as podman quadlets, which are systemd units for containers. `docker` runs docker compose |
| `auto_update` | `registry` | `registry` runs `podman auto-update` once a week. With `off`, the container images only change when you apply the host again |
| `docker_dir` | `/home/user/docker` | the directory that holds the stack and its data |
| `service_user` | the admin user | the user that owns the data directories |
| `vpn_ip` | from the WireGuard config | the machine's mesh address |
| `master_ip` | from the fleet | the master's mesh address |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | you can measure them with `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | from the default route | the network interface on the LAN side |
| `daily_vpn_restart` | `07:00` | an empty value turns the daily restart off |
| `weekly_update` | `Sun *-*-* 00:00` | an empty value turns the weekly update off |

`kiwi-server roles -v` and `kiwi-server modules -v` list every setting with its
default.

## Checking what you wrote

kiwi-server can check the fleet file for you and show what it makes of one
host.

```bash
kiwi-server validate fleet.yaml          # errors and warnings
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server also checks the domain. It refuses `.local`, and it warns about
`.lan` and about public top-level domains (see
[DNS](../network/dns.md#names-servicehostnamehome)).

## Taking over a v1 machine

You can bring a machine that ran one of the old v1 stacks into the fleet
without losing its data. The default runtime is now podman, and the role script
does not stop docker containers that are still running. So either set
`runtime: docker` or stop the old stack first. Then set `docker_subnet` to the
subnet that the old stack used, and rename the data directories to the new
module names (`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`, …). The
containers then keep their addresses, and wg-easy keeps its peers.
