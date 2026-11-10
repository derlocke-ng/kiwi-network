# Modules

A module is one service that a machine in your Kiwi Network runs, for example
the VPN server, the DNS server with ad blocking, Nextcloud or the nightly
backup. Modules are how you decide what each machine does. A [role](roles.md)
brings a set of modules with it, and you can change that set in the fleet
file.

A renderer turns the modules of one host into a **stack**, which is everything
the machine needs to run these services. The renderer is
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), and kiwi-server
includes a copy of it. A stack consists of a compose file, **podman quadlets**
(one systemd unit per container), the configuration files, the systemd units
for the host, and `stack.sh`, a manifest that lists all of them.
[kiwi-stack](single.md) installs the stack on the machine. All templates are
filled in on the computer that renders the stack. The machine that runs the
stack only needs podman 4.4 or later, or docker with the compose plugin if you
set `runtime: docker`.

This command lists every module with its settings.

```bash
kiwi-server modules -v      # every module and every setting with its default
```

## The network

These modules build the mesh, which is the private WireGuard network that
connects all your machines, and they control how its traffic reaches the
Internet.

| Module | What it is | Runs on | Requires | On the host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, the WireGuard server that every client and node connects to. Its default route is the VPN client, so traffic to the Internet goes on through the master's commercial VPN (the double hop) | master | none | `51820/udp`, and the web interface on `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, the VPN tunnel that a machine's traffic goes through. On a node the tunnel leads to the master, and on the master it leads to a commercial VPN | both | none | none |
| `dns` | **Pi-hole 6**, a DNS server that blocks ads for the mesh or the LAN. It answers for the fleet's names and can also provide names for Mullvad's SOCKS5 proxies | both | none | `53` on a node |
| `tor` | A **Tor SOCKS5** proxy for clients in the mesh. It only uses Tor nodes in the countries you set | both | none | `127.0.0.1:9050` on a node, and the mesh address `:9050` on a master |
| `reverse-proxy` | **nginx** with TLS. It has one server block per service, so each service is reachable under its own name. Admin pages can be reached from the mesh only. Public names with Let's Encrypt certificates are optional | both | none | `80`, `443` on a node, or on a master with `public` turned on |
| `gateway` | Policy routing on the host. Devices in the LAN that use this machine as their gateway have their Internet traffic sent through the VPN | node | vpn-client | a systemd unit on the host |
| `dhcp-relay` | Passes the LAN's DHCP requests on to Pi-hole, so that Pi-hole can be the LAN's DHCP server | node | dns | `67/udp` |

## Services

| Module | What it is | Runs on | Requires |
|---|---|---|---|
| `cloud` | **Nextcloud**, built from the AIO project's containers but *without* the AIO master container. It therefore needs no docker socket and runs on podman. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, full-text search and Whiteboard can each be switched on or off | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, a password manager that is compatible with Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** and **JDownloader**. Both run in the VPN client's network namespace, which means that they use its network connection and have none of their own. They transfer nothing while the tunnel is down | node | vpn-client |
| `sftp` | An SFTP server on its own port (`2224`), from which you can fetch the downloads | node | none |
| `portainer` | **Portainer CE**, a web interface for the containers. It is reachable at `127.0.0.1:9443` and at `portainer.<host>` | both | none |
| `opencloud` | **OpenCloud**, for files and file sharing, in a single Go binary (to try out) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, for photos and videos (to try out) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, for scanned documents, with OCR and full-text search (to try out) | node | vpn-client, reverse-proxy |

The last three modules are not part of any preset. To use one of them, add it
to `modules:`.

## People

A hub is a community's own site in the browser. These two modules run a hub
and the relay on which the hub stores its events.

| Module | What it is | Runs on | Requires |
|---|---|---|---|
| `nostr-relay` | **strfry**, the relay that a hub keeps its events on. It is reachable at `relay.<host>`. People who connect from the Internet may post only if they are members and have proved that they own their key (NIP-42). With `approved`, the members are the keys on a list that the admins sign. With `registered`, anyone who has an account is a member. Connections from the mesh may always post | master | reverse-proxy |
| `hub` | A **kiwi-framework hub** that runs as a container. By default it is Armory, and it is reachable at `hub.<host>`. A hub can be private, semi-public or public | master | reverse-proxy |

See [Running your own hub](../people/hubs.md).

## Backups and disks

| Module | What it is | Runs on | Requires |
|---|---|---|---|
| `backup` | Backs up this machine's data with **restic**, encrypted, to a node that runs the backup-server module. The backup runs every night at `03:00`, or up to 15 minutes later, and whenever you run `kiwi-stack backup`. Each module defines which of its data is backed up. Planned for the next release are backups to several servers and a rebuilt machine that restores its own data ([details](operations.md#coming-in-the-next-release)) | both | none |
| `backup-server` | A **restic REST server** that stores the backups. Each machine can reach only its own repository, and it can only add to it (append-only) | node | vpn-client, reverse-proxy |
| `tang` | **Tang** servers, which let machines with encrypted disks unlock them at boot without a person present. One ring is one Tang server with its own keys. The default is a ring named `infra` on port `7500` | node | none |

See [Operations](operations.md).

## Important settings

| Module | Setting | Default | Notes |
|---|---|---|---|
| vpn-server | `wg_host` | (required) | the name or IP address that clients connect to |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | see [client groups](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | ports on the master through which machines behind NAT reach their Tang ring |
| vpn-client | `vpn_provider` | `custom` | `custom` uses the WireGuard configuration that the master issued, which is what a node needs. Otherwise name a gluetun provider (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | the countries and cities of the commercial VPN servers to use |
| | `dot_providers` | `quad9` | the DNS-over-TLS provider that gluetun uses |
| | `extra_dnat_rules` | `[]` | additional forwarding rules, for example for SSH from the mesh to the host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | used only while the master is unreachable |
| | `dhcp_enabled` | `false` | used together with `dhcp_start`, `dhcp_end` and `dhcp_router` |
| | `mullvad_socks` | `true` on a master | [Mullvad's proxies by name](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | the countries of the Tor entry and exit nodes, enforced with `StrictNodes` |
| reverse-proxy | `public` | `false` | master only. It opens 80/443 and uses Let's Encrypt for names outside the fleet's domain |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | set it to a directory on a large disk |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | turn it on to create the first account, then turn it off again |
| downloader | `download_dir` | (required) | |
| nostr-relay | `members` | `approved` | or `registered` |
| | `write_pubkeys` | `[]` | the keys of the admins. Admins may always post, and only their member lists and ban lists are valid |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | the image of any hub built with kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | set these for a semi-public hub |
| backup | `server` | (required) | the `https://…` address of a backup-server node that lists this machine |
| tang | `rings` | `{ infra: "7500" }` | each ring's name and port |

If you leave out a password or a key, it is generated from the fleet's seed.

## Names

Each module registers the names of its services with the reverse proxy and with
the fleet's DNS. Every name is made of the service's name and the host's name.

| Service | Name |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (any host with `dns` and the reverse proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relay / hub | `relay.<host>` / `hub.<host>` |
| backup server | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Containers

- Under podman, each service is a quadlet in `/etc/containers/systemd`. The
  quadlets are started through `kiwi-stack.target`, and their logs go to the
  systemd journal. A container that shares another container's network
  namespace is bound to that container, so it is restarted together with it.
- Secrets are written to `kiwi/env/<service>.env` files that only root can
  read. They are never written into the units.
- The containers have fixed addresses that follow the address plan of v1, so a
  machine that was migrated from v1 keeps its addresses. They are vpn-client
  `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`, vault `.7`,
  tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` and sftp `.251`.
  Other modules get addresses that count up from `.100`. Containers without a
  fixed address get one from the third quarter of the network (`.128/26`).
- Fedora CoreOS and uCore run with SELinux enabled, so bind mounts are given
  the `:z` label. The mounts of the container socket and of `/lib/modules` are
  never labelled.

## Writing a module

A module is a directory with the following files.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` describes the module. It declares the module's metadata and the
node types it runs on, its dependencies, and the ports it opens on the host. It
names the module's templates and where their output is written, its storage,
and which of its data is backed up. It also declares the host integration
(sysctls and kernel modules), the nginx server blocks that the module
registers, the URLs that are printed when the role has finished, the validation
rules, and the module's `settings`.

The settings schema has two uses. It validates the fleet file, and the
kiwi-server app builds its settings form from it. The templates are written in
Jinja2 and can use the host context. This context contains the host's name and
type, every module's address, the mesh, the fleet's names, the enabled modules
and every module's settings.

Under podman, the compose file is translated into quadlets. The translation
supports a fixed set of compose keys, and any other key causes an error when
the stack is rendered.

Modules are developed and released in
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). The full format
reference is
[kiwi-server's docs/modules.md](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
