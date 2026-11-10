# DNS, names & certificates

Every machine and every service in a Kiwi Network has a name, such as
`cloud.papaya.home`, and you open it over HTTPS with a certificate that your
devices trust. This page explains how names are looked up in the network, how
the names are built, and where the certificates come from. The DNS servers are
Pi-holes, which also block unwanted domains with a shared blocklist.

## One resolver chain

All DNS queries in the network pass along the same chain of DNS servers:

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **VPN clients** (laptops, phones) send their queries to the master's Pi-hole
  at `10.8.0.1`.
- **A node's Pi-hole** asks the master's Pi-hole first. As a result the whole
  network shares one blocklist, and every query reaches the Internet through
  the master's exit, which is the master's connection to the Internet. Quad9
  (`9.9.9.9`, `149.112.112.112`, set with `fallback_dns`) comes next in strict
  order, so it only answers while the master is unreachable.
- **The master's Pi-hole** forwards queries to the DNS-over-TLS resolver of its
  VPN client. By default that resolver is Quad9 (`dot_providers`).
- **Names under the fleet's domain** are forwarded to the master and are never
  sent on from there. The master marks the domain as local.

Every machine that runs a stack also has the fleet's names in its `/etc/hosts`
file, with its own names pointing at itself. Backups and certificate renewals
can therefore resolve names without a Pi-hole. On Fedora CoreOS and uCore, the
machine itself uses the Pi-hole of its own stack as its resolver.

**Neighbours on the same LAN.** If other nodes of the fleet have a static
address in a node's own subnet, that node's Pi-hole and hosts file answer with
their **LAN address**. Traffic between two machines on the same LAN then stays
on that LAN. The master keeps answering with mesh addresses.

## Names: `service.hostname.home`

Each host has the name `<host>.<domain>`, for example `papaya.home`. Each
service that runs on it gets a name under the host's name: `cloud.papaya.home`,
`vault.papaya.home`, `portainer.papaya.home`, `dl.lychee.home`, and on the
master `wg.sorbet.home`, `pihole.sorbet.home`, `hub.sorbet.home`,
`relay.sorbet.home`. Every name that a module announces is entered in the
fleet's DNS records with the host's **mesh address**. Every Pi-hole in the
fleet can resolve every host name and every service name. The setting for this
is `fleet_records`, and the technique is called split-horizon DNS, because the
names are answered inside your network only. You can add your own records with
`extra_records`.

The default domain is **`.home`**. It was chosen because ICANN will not
delegate it as a public top-level domain (TLD). A name in your fleet can
therefore never end up in a public registry, and nobody else can register it or
get a certificate for it that browsers trust. `.kiwi`, on the other hand, is a
real TLD, which is why Kiwi Network no longer uses it. kiwi-server checks the
domain you choose. `home`, `corp`, `mail`, `internal`, `arpa` and `test` are
accepted without comment. `.local` is refused, because it belongs to mDNS.
`.lan` gets a warning, because routers answer it themselves, and public TLDs
get a warning too.

Names *outside* the fleet's domain, which you need for a public hub or relay,
get Let's Encrypt certificates if the master's reverse proxy is public.

## Mullvad SOCKS5 proxies by name

Mullvad's SOCKS5 proxies have addresses in a private range, and this feature
lets you use them by name. Since kiwi-server 2.2.0 the master's Pi-hole answers
for every **Mullvad SOCKS5 proxy**, both under its full name, such as
`de-fra-wg-socks5-001.relays.mullvad.net`, and under a short name, such as
`de-fra-001.mullvad.home`. gluetun refuses DNS answers that point to private
addresses, which is its protection against DNS rebinding. Without these records
the names would therefore only resolve through the fallback resolvers. A timer
on the host (`km-mullvad-socks.timer`, every 6 hours) refreshes the list from
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
From that list, only `*.relays.mullvad.net` names with `10.x` addresses are
accepted, so the list can never redirect any other name.

The feature is switched on in the master preset, because the preset's exit is
Mullvad. To switch it off, set `mullvad_socks: false` in the master's `dns:`
block.

## One CA for the fleet

A certificate authority (CA) signs the certificates that your services use for
HTTPS. With `tls.auto: true`, which is the default, kiwi-server keeps **one
certificate authority** for the whole fleet in `secrets/ca/`. The CA consists of
the files `kiwiCA.key` and `kiwiCA.pem`, uses RSA-4096 and is valid for 3650
days. kiwi-server creates it the first time a host needs a certificate. Every
host that runs the reverse proxy gets a certificate for `<hostname>` and
`*.<hostname>`. This certificate is valid for 825 days, which is the longest
lifetime browsers still accept, and it is renewed when fewer than 30 days are
left. Every machine that kiwi-server builds installs the CA in its trust store.

If you set **name constraints**, the CA can only sign names under the fleet's
domain: `tls: { name_constraints: [home] }`. The example fleet sets this, but
the built-in default is no constraint. With the constraint, a stolen
`kiwiCA.key` is worthless for any other name. This matters because every
machine trusts the CA.

```bash
kiwi-server ca fleet.yaml        # show the fleet CA
```

Import `kiwiCA.pem` on your own devices (browsers, phones) so that they trust
`https://cloud.papaya.home`. If you would rather use your own certificates, set
`tls_fullchain` and `tls_privkey` in the reverse-proxy module.

!!! warning "Keep `secrets/` private"
    `kiwiCA.key` signs certificates that every one of your machines trusts.
    Keep `secrets/` and `output/` out of git (`output/` is already in
    kiwi-server's `.gitignore`).
