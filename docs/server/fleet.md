# The fleet file

`fleet.yaml` describes every machine kiwi-server should build. It has two keys:
`defaults`, which applies to every host, and `hosts`, with one entry per
machine. Anything a host sets overrides the defaults. `kiwi-server init` writes
a commented starting point. The full reference is
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml)
in the repository.

A host has a **target** (what gets installed) and a **role** (what it becomes):

- `target`: `coreos`, `ucore` or `debian`. See [Targets](targets.md).
- `role`: `bare`, `master`, `node-gw` or `node-cloud`. See [Roles](roles.md).

## Defaults

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                     # host "sh3" becomes sh3.home; names are service.sh3.home
  timezone: Europe/Berlin
  locale: en_US.UTF-8
  keyboard: de
  disk: /dev/sda                   # WIPED by the ISO without asking. nvme: /dev/nvme0n1

  admin:
    user: core                     # passwordless sudo on every target
    password: change-me            # hashed at render time; or password_hash: $6$...
    ssh_keys: [~/.ssh/id_ed25519.pub]   # a key, or a file containing keys
    groups: [docker]
    ssh_password_auth: false       # keys only; the password is for the console

  network:
    dhcp: true                     # or dhcp: false with address/gateway/dns per host,
    # iprange: 192.168.1.20-192.168.1.99   # or an iprange handing out addresses in file order

  updates:                         # updates install continuously; this is when a REBOOT may happen
    enabled: true
    days: [Sun]                    # [] = any day
    time: "03:30"                  # local time
    length_minutes: 90

  tls:
    auto: true                     # one fleet CA, a *.<hostname> certificate per host
    ca_dir: secrets/ca
    name_constraints: [home]       # the CA may only sign names under the fleet's domain (default: [])

  ucore:
    image: ghcr.io/ublue-os/ucore:stable    # ucore-minimal / ucore / ucore-hci (+ -nvidia, -zfs)

  debian:
    release: trixie
    partitioning: lvm              # regular | lvm | crypto (with encrypt: true + passphrase:)
    packages: [vim, htop]
```

## Hosts

```yaml
hosts:
  gate:                            # the kiwi-master, on Debian
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
        wg_host: vpn.example.org   # what clients and nodes connect to
        wg_password: change-me-too # wg-easy admin
      dns:
        pihole_password: change-me-three

  m1:                              # a gateway node, on uCore (the default)
    role: node-gw
    node-gw:
      pub_iface: eth0              # the LAN side
      vpn-client:
        wireguard_config: secrets/m1.home.conf   # the client config wg-easy issued
      dns: { pihole_password: … }
      downloader: { download_dir: /mnt/data/downloads, transmission_password: … }
      sftp: { sftp_password: … }
      portainer: { admin_password: … }

  sh3:                             # a cloud node on uCore HCI
    role: node-cloud
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node-cloud:
      vpn_ip: 10.8.0.25
      vpn-client: { wireguard_config: secrets/sh3.home.conf }
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }    # for the first account; turn it off afterwards

  lab1:                            # just the base system
    target: coreos
    role: bare
```

## How settings combine

- Hosts override defaults **key by key**. The lists `admin.ssh_keys`,
  `debian.packages` and the `coreos.*` lists *add* to the defaults instead of
  replacing them.
- A module role's block (`master:`, `node-gw:`, `node-cloud:`) holds the
  **stack settings** at the top (`vpn_ip`, `pub_iface`, `docker_dir`,
  `service_user`, `docker_subnet`, `master_ip`, the VPN restart and update
  times) and then **one block per module**.
- `modules:` inside the role block **replaces** the preset's module list. A
  cloud node that also downloads is
  `modules: [vpn-client, reverse-proxy, cloud, vault, downloader]` plus the
  downloader's settings.
- **File settings** (WireGuard configs, certificates) are paths relative to the
  fleet file. Their *content* is embedded into the host's role script.
- `key:` with no value means the default.

## Values kiwi-server works out for you

- **A node's `vpn_ip`** is read from its WireGuard config's `Address` when it is
  not set. When both are given and differ, `validate` warns.
- **`master_ip`** (the master's mesh address, the nodes' DNS upstream) comes
  from the fleet's master host.
- **Static addresses** without typing them: `network: { dhcp: false, gateway: …,
  iprange: 192.168.1.20-192.168.1.99 }` in the defaults hands each static host
  the next free address in file order. A host's own `address:` is reserved
  first.
- **The data directories** belong to `service_user`, which is the admin user
  unless set (uid 1000 on a fresh install, matching the containers' `PUID`
  defaults). The rendered files stay root's.

## Checking what you wrote

```bash
kiwi-server validate fleet.yaml          # errors and warnings
kiwi-server show fleet.yaml sh3          # the effective config of one host, secrets masked
kiwi-server roles -v                     # every role and stack setting with its default
kiwi-server modules -v                   # every module setting with its default
```

## Migrating a v1 machine in place

A machine that ran one of the old v1 stacks (kiwi-master, kiwi-node-gw,
kiwi-cloud) can be taken over without losing data. Before the first start:

1. Set `docker_subnet` to what the old stack used (e.g. `172.129.0.0/24`), so
   the containers keep their addresses and wg-easy keeps its peers.
2. Rename the data directories to the module names: `kmvpn-server` →
   `km-vpn-server`, `knvault` → `kn-vault`, `kntransmission` →
   `kn-transmission`, and so on.

SSH to a node over the mesh is one DNAT rule:
`vpn-client: { extra_dnat_rules: ["2222/tcp:172.128.0.1:22"] }` (the docker
gateway is the host).
