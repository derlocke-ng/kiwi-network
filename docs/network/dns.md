# DNS, names & certificates

## One resolver chain

DNS is one chain for the whole network:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **VPN clients** (laptops, phones) ask the master's Pi-hole at `10.8.0.1`.
- **A node's Pi-hole** asks the master's Pi-hole first, so the network shares
  one blocklist and every lookup leaves through the master's exit. Quad9
  (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) follows in strict order and
  only answers while the master is unreachable.
- **The master's Pi-hole** forwards to its VPN client's DNS-over-TLS resolver
  (Quad9 by default, `dot_providers`).
- **Names under the fleet's domain** are forwarded to the master and never
  leave it. The master marks the domain local.

Every stack host also carries the fleet's names in `/etc/hosts` (its own names
pointing at itself), so backups and certificate renewals resolve without a
Pi-hole. On Fedora CoreOS and uCore the host itself resolves through its own
stack's Pi-hole.

**Neighbours on the same LAN.** A node's Pi-hole and hosts file answer with the
**LAN address** of fleet nodes that have a static address in its own subnet, so
traffic between two machines in the same room stays in the room. The master
keeps answering with mesh addresses.

## Names: `service.hostname.home`

Each host is `<host>.<domain>` (`papaya.home`), and each service it runs is a name
under it: `cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home`, and on the master `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Every name a module announces goes into the fleet's DNS records at
the host's **mesh address**. Every Pi-hole in the fleet resolves every host and
service name (split-horizon, `fleet_records`). Add your own with
`extra_records`.

The default domain is **`.home`**, because ICANN will not delegate it as a
public top-level domain. A fleet name can never leak to a public registry, and
nobody else can register it or get a browser-trusted certificate for it.
`.kiwi` is a real TLD, which is why the fleet moved away from it. kiwi-server
checks your choice: `home`, `corp`, `mail`, `internal`, `arpa` and `test` pass
silently, `.local` is refused (it belongs to mDNS), `.lan` gets a warning
(routers answer it themselves), and public TLDs get a warning.

Names *outside* the fleet's domain, for a public hub or relay, get Let's
Encrypt certificates when the master's reverse proxy is public.

## Mullvad SOCKS5 proxies by name

Since kiwi-server 2.2.0 the master's Pi-hole answers for every **Mullvad SOCKS5
proxy**, both as `de-fra-wg-socks5-001.relays.mullvad.net` and as the short
`de-fra-001.mullvad.home`. gluetun refuses these private-range answers (DNS
rebinding protection), so without the records the names would only resolve
through the fallback resolvers. A host timer (`km-mullvad-socks.timer`, every 6
hours) refreshes the list from
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Only `*.relays.mullvad.net` names at `10.x` addresses are accepted from it, so
the list can never redirect any other name.

It is on in the master preset, whose exit is Mullvad. Turn it off with
`mullvad_socks: false` in the master's `dns:` block.

## One CA for the fleet

With `tls.auto: true` (the default), kiwi-server keeps **one certificate
authority** for the fleet in `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`, RSA-4096,
valid 3650 days), created the first time a host needs a certificate. Every host that runs the reverse proxy gets a certificate for
`<hostname>` and `*.<hostname>` (825 days, the longest lifetime browsers still
accept, renewed when fewer than 30 days are left), and every machine
kiwi-server builds installs the CA in its trust store.

Set **name constraints** and the CA can only sign names under the fleet's
domain: `tls: { name_constraints: [home] }`. The example fleet does this; the
built-in default is no constraint. A stolen `kiwiCA.key` is then worthless for
anything else, which matters because every machine trusts it.

```bash
kiwi-server ca fleet.yaml        # show the fleet CA
```

Import `kiwiCA.pem` on your own devices (browsers, phones) so that
`https://cloud.papaya.home` is trusted. To use your own certificates instead, set
`tls_fullchain` and `tls_privkey` in the reverse-proxy module.

!!! warning "Keep `secrets/` private"
    `kiwiCA.key` signs certificates every one of your machines trusts. Keep
    `secrets/` and `output/` out of git (`output/` is already in
    kiwi-server's `.gitignore`).
