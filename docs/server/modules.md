# Modules

A module is one service of a Kiwi Network machine. A [role](roles.md) picks a
set of modules, and the renderer turns them into a **stack** for one host. The
renderer is [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), which
kiwi-server vendors. The stack is a compose file, **podman quadlets** (one
systemd unit per container), the configs and host units, and `stack.sh`, the
manifest that names them all. [kiwi-stack](single.md) puts it on the machine.
All templating happens on the machine that renders. The target only needs
podman 4.4 or later (or docker with the compose plugin, with `runtime: docker`).

```bash
kiwi-server modules -v      # every module and every setting with its default
```

## The network

| Module | What it is | Runs on | Requires | On the host |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: the entry point for every client and node; its default route is the VPN client (the double hop) | master | none | `51820/udp`; the UI on `127.0.0.1:51821` |
| `vpn-client` | **gluetun**: the tunnel every machine hangs off: to the master on a node, to a commercial VPN on the master | both | none | none |
| `dns` | **Pi-hole 6**: blocks ads for the mesh or the LAN, serves the fleet's names and, optionally, Mullvad's SOCKS5 proxies by name | both | none | `53` on a node |
| `tor` | a **Tor SOCKS5** proxy for mesh clients, pinned to countries | both | none | `127.0.0.1:9050` on a node; the mesh address `:9050` on a master |
| `reverse-proxy` | **nginx** with TLS: one server block per service; admin pages answer the mesh only; optional public names with Let's Encrypt | both | none | `80`, `443` on a node, or on a public master |
| `gateway` | policy routing on the host: LAN clients that use this machine as their gateway leave through the VPN | node | vpn-client | a host unit |
| `dhcp-relay` | relays the LAN's DHCP to Pi-hole, so Pi-hole can be the LAN's DHCP server | node | dns | `67/udp` |

## Services

| Module | What it is | Runs on | Requires |
|---|---|---|---|
| `cloud` | **Nextcloud** from the AIO project's containers, *without* the AIO master container (no docker socket, runs on podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, full-text search and Whiteboard are switches | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, the Bitwarden-compatible password manager | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** and **JDownloader** inside the VPN client's network namespace: no tunnel, no traffic | node | vpn-client |
| `sftp` | an SFTP server on its own port (`2224`), for fetching downloads | node | none |
| `portainer` | **Portainer CE**, a web UI for the containers (`127.0.0.1:9443`, and `portainer.<host>`) | both | none |
| `opencloud` | **OpenCloud**: files and sharing in one Go binary (to try out) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**: photos and videos (to try out) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**: scanned documents with OCR and full-text search (to try out) | node | vpn-client, reverse-proxy |

The last three are in no preset; add them to `modules:`.

## People

| Module | What it is | Runs on | Requires |
|---|---|---|---|
| `nostr-relay` | **strfry**, the relay a hub keeps its events on (at `relay.<host>`). From the Internet, members may post after proving their key (NIP-42): `approved` keys on the admins' signed list, or anyone `registered` with an account. The mesh may always post | master | reverse-proxy |
| `hub` | a **kiwi-framework hub** as a container (Armory by default, at `hub.<host>`), private, semi-public or public | master | reverse-proxy |

See [Running your own hub](../people/hubs.md).

## Backups and disks

| Module | What it is | Runs on | Requires |
|---|---|---|---|
| `backup` | this machine's data with **restic**, encrypted, to a backup-server node: nightly at `03:00` (within 15 minutes after) and with `kiwi-stack backup`. Each module says what of it is kept. Next release: several servers and a rebuilt machine that restores itself ([details](operations.md#coming-in-the-next-release)) | both | none |
| `backup-server` | a **restic REST server**; each machine reaches only its own repository, append-only | node | vpn-client, reverse-proxy |
| `tang` | **Tang** servers so encrypted machines unlock at boot; one ring is one server with its own keys (default `infra` on `7500`) | node | none |

See [Operations](operations.md).

## Important settings

| Module | Setting | Default | Notes |
|---|---|---|---|
| vpn-server | `wg_host` | (required) | the name or IP clients connect to |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | see [client groups](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | Tang ports for machines behind NAT |
| vpn-client | `vpn_provider` | `custom` | `custom`: the WireGuard config the master issued (a node); or a gluetun provider (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | where a commercial exit is |
| | `dot_providers` | `quad9` | gluetun's DNS-over-TLS |
| | `extra_dnat_rules` | `[]` | e.g. SSH from the mesh to the host |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | only while the master is unreachable |
| | `dhcp_enabled` | `false` | with `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` on a master | [Mullvad's proxies by name](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | entry and exit nodes, `StrictNodes` |
| reverse-proxy | `public` | `false` | master only: 80/443 with Let's Encrypt for names outside the fleet's domain |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | point it at a big disk |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | turn on for the first account, then off |
| downloader | `download_dir` | (required) | |
| nostr-relay | `members` | `approved` | or `registered` |
| | `write_pubkeys` | `[]` | the admins: they may always post, and only their member and ban lists count |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | any kiwi-framework hub |
| | `public_relays`, `public_mounts` | `[]` | a semi-public hub |
| backup | `server` | (required) | `https://…` of a backup-server node that lists this machine |
| tang | `rings` | `{ infra: "7500" }` | name and port |

Passwords and keys you leave out are generated from the fleet's seed.

## Names

Each module announces its names to the reverse proxy and to the fleet's DNS,
under the host's name:

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

- Under podman, each service is a quadlet in `/etc/containers/systemd`, started
  through `kiwi-stack.target`, with its log in the journal. A container that
  lives in another's network namespace is bound to it and comes back with it.
- Secrets go to root-only `kiwi/env/<service>.env` files, never into the units.
- Fixed addresses follow the v1 plan, so a migrated machine keeps them:
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Other modules count up from `.100`. Containers without a fixed address
  use the third quarter of the network (`.128/26`).
- Fedora CoreOS and uCore run with SELinux enabled, so bind mounts carry the
  `:z` label. Mounts of the container socket and `/lib/modules` are never
  labelled.

## Writing a module

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` declares the module's metadata and node types, its dependencies,
the host ports it opens, its templates and where their output goes, storage,
what of it is backed up, host integration (sysctls, kernel modules), the nginx
server blocks it announces, the URLs printed when the role has finished, its
validation rules, and its `settings`. The settings schema validates the fleet
file and builds the app's form. Templates are Jinja2 and see the host context:
the host name and type, every module's address, the mesh, the fleet's names,
every enabled module, and every module's settings.

Under podman, the compose file is translated into quadlets. Only a known set of
compose keys is translated, and anything else is an error at render time.

Modules are developed and released in
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). The full format
reference is
[kiwi-server's docs/modules.md](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
