# Modules

A module is one service of a Kiwi Network machine. A [role](roles.md) picks a set
of modules, and kiwi-server renders them for one host into a **stack**: a
`docker-compose.yml`, the module config files and the host units. The host's
role script unpacks and starts the stack on first boot. The machine needs docker
and nothing else, because all templating happens on the machine that runs
`kiwi-server`.

`kiwi-server modules -v` lists every module with every setting and its default.

## The modules

| Module | What it is | Runs on | Requires | Host ports |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**: the entry point for every client and node. Its default route points at the VPN client for the double hop | master | none | `51820/udp` |
| `vpn-client` | **gluetun**: the tunnel every host hangs off. On a node it uses the WireGuard config the master issued; on the master it connects to a commercial VPN (the exit) | both | none | none |
| `dns` | **Pi-hole 6**: an ad-blocking resolver for the mesh or the LAN that serves the fleet's own names and, optionally, the Mullvad SOCKS5 proxies' names | both | none | `53` (nodes) |
| `tor` | A **Tor SOCKS5** proxy for mesh clients, pinned to a set of countries | both | none | none |
| `reverse-proxy` | **nginx** with TLS: one server block per service the other modules announce, with certificates from the fleet CA | node | none | `80`, `443` |
| `cloud` | **Nextcloud All-in-One**: files, calendar, contacts, Talk | node | vpn-client, reverse-proxy | `3478` tcp+udp (Talk) |
| `vault` | **Vaultwarden**, the Bitwarden-compatible password manager | node | vpn-client, reverse-proxy | none |
| `downloader` | **Transmission** and **JDownloader** inside the VPN client's network namespace: no tunnel, no traffic | node | vpn-client | none |
| `gateway` | Policy routing on the host: LAN clients that use this machine as their gateway leave through the VPN client | node | vpn-client | none |
| `dhcp-relay` | Relays the LAN's DHCP broadcasts to the Pi-hole container, so Pi-hole can be the LAN's DHCP server | node | dns | `67/udp` |
| `portainer` | **Portainer CE**: a web UI for the containers on this machine | both | none | none |
| `sftp` | An SFTP server on its own port, for fetching downloads from the LAN or the mesh | node | none | `2224/tcp` |

Required modules are added automatically and rendered first.

## Important settings

| Module | Setting | Default | Notes |
|---|---|---|---|
| vpn-server | `wg_host` | (none) | the hostname or IP clients connect to |
| | `wg_port` | `51820` | |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `isolated_subnet` | `10.8.1.0/24` | clients here see the server and the nodes, not each other |
| | `admin_from_mesh` | `true` | wg-easy UI (51821) at the server's mesh address, never for isolated clients |
| vpn-client | `vpn_provider` | `custom` | `custom` = a WireGuard config file (a node); or a gluetun provider (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | (none) | for `custom`: the client config wg-easy issued |
| | `wireguard_private_key`, `wireguard_addresses` | (none) | for commercial providers |
| | `server_countries`, `server_cities` | (none) | where the exit is |
| | `dot_providers` | `quad9` | gluetun's DNS-over-TLS upstream |
| | `extra_dnat_rules` | `[]` | e.g. `2222/tcp:172.128.0.1:22` for SSH from the mesh |
| dns | `pihole_password` | (secret) | |
| | `fallback_dns` | `9.9.9.9;149.112.112.112` | only while the master is unreachable |
| | `dhcp_enabled` (+ `dhcp_start`, `dhcp_end`, `dhcp_router`) | `false` | Pi-hole as the LAN's DHCP server, with dhcp-relay |
| | `fleet_records` | `true` | every host and service name at its mesh address |
| | `mullvad_socks` | `false` (`true` on master) | see [DNS](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | everything else excluded (`StrictNodes`) |
| | `socks_policy_accept` | `10.8.0.0/16` | who may use it |
| cloud | `nextcloud_datadir` | stack directory | point it at a big disk |
| | `memory_limit`, `upload_limit` | `4096M`, `50G` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes` | |
| vault | `signups_allowed` | `false` | turn on for the first account, then off again |
| | `admin_token` | (empty) | empty keeps `/admin` off |
| downloader | `download_dir` | (required) | |
| | `jdownloader` | `true` | |
| reverse-proxy | `tls_fullchain`, `tls_privkey` | (fleet CA) | bring your own certificate |
| | `hsts` | `true` | |
| sftp | `sftp_port` | `2224` | |
| portainer | `admin_password` | (secret) | set before the first start, so no first-run page waits open |

Several admin interfaces bind to `127.0.0.1` by default: wg-easy (`51821`),
Pi-hole's plain-HTTP UI (`8080`), and the Nextcloud AIO master container, which
holds the docker socket (`8080`). Reach them through the reverse proxy, the
mesh, or `ssh -L`.

## Default names

Each module announces its names to the reverse proxy and to the fleet's DNS,
under the host's name:

| Service | Name |
|---|---|
| Nextcloud | `cloud.<hostname>` (admin: `nc-admin.<hostname>`) |
| Vaultwarden | `vault.<hostname>` |
| Transmission / JDownloader | `dl.<hostname>` / `jd.<hostname>` |
| Pi-hole | `pihole.<hostname>` |
| Portainer | `portainer.<hostname>` |

## Container addresses

Addresses follow the v1 plan, so a migrated machine keeps them: vpn-client `.2`,
vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`, vault `.7`, tor `.8`,
downloader `.9`, gateway `.10`, portainer `.250`, sftp `.251`. Any other module
counts up from `.100`. A host overrides one with `container_ip:` in that
module's block.

## Writing a module

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships (nginx.conf, torrc, …)
```

`module.yaml` declares the module's metadata, its `dependencies`, the host
ports to open, firewall rules (collected into gluetun's post-rules or applied by
the module itself), its templates and where their output goes, storage, host
integration (sysctls, kernel modules), the URLs printed when the role has
finished, nginx server blocks for the reverse proxy, and its user-facing
`settings`. The settings schema validates the fleet file and builds the GUI form.

Templates are Jinja2 and see the **host context**: the hostname and node type,
the container prefix and network, every module's address, the mesh and master
addresses, the fleet's domain and DNS records, every enabled module (`has_…`),
and every module's resolved settings.

Fedora CoreOS and uCore run docker with SELinux enabled, so bind mounts carry
the `:z` label (`ro,z` for read-only mounts). A mount of `/var/run/docker.sock`
or `/lib/modules` must never be labelled.

To try a new module, add it to a role's `modules:` (or a host's `modules:`
override), render a host and read `output/<host>/<host>.stack/`.
`KIWI_SERVER_MODULES=/path/to/modules` points kiwi-server at another module
tree. The full format reference is
[docs/modules.md](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md)
in the repository.
