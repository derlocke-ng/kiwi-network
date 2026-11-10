# kiwi-proxy

Sealed SOCKS5 and VPN exits in rootless Podman, for browsers, testing tools,
host applications and kiwi-server machines.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Latest release: **v0.7.3**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.
- A CLI (`kiwi-proxy`), a GTK4 app (**Kiwi Proxy**) and systemd user units. It
  is the proxy engine that used to live in kiwi-fox, split out so it serves more
  than one app.

An **exit** is one upstream, by name: a SOCKS5 you were given, or one a
[provider module](providers.md) produces (Tor, a VPN tunnel, 9proxy,
Mysterium). An exit is just data. Bringing it up makes a **gateway**:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Whatever joins the gateway's namespace (a kiwi-fox browser, a kiwi-custodia
box, a tool container) has no route but that upstream. If the gateway dies, its
members lose their route.

## Install

```bash
kiwi install kiwi-proxy      # kiwi-fox and kiwi-custodia bring it along
kiwi-proxy setup             # the gateway image, DNS data, provider module images
```

It needs rootless Podman, Python 3.12+ with pydantic, and GTK4 + libadwaita for
the app. Passwords go to the desktop keyring (`secret-tool`), or to 0600 files
on a machine without one.

## Use

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # an exit; nothing runs yet
kiwi-proxy add tor-de --module tor --country de        # an exit from a provider module
kiwi-proxy list
kiwi-proxy check client-a      # what the world sees through it
kiwi-proxy up client-a         # bring its gateway up and keep it up
kiwi-proxy down client-a       # tear it down, with whoever joined it
kiwi-proxy ps                  # running gateways, whichever app started them
kiwi-proxy reap                # tear down gateways nobody uses
kiwi-proxy-gui                 # "Kiwi Proxy" in the app grid
```

Endpoints are `socks5://user:pass@host:port`, `http://…`, `https://…`, or the
vendor format `host:port:user:pass`. `kiwi-proxy test ENDPOINT` probes one
without creating anything.

### Exits for host applications

Any program on the host can use an exit through a published SOCKS5 port, one
port per exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

The port listens on `127.0.0.1` by default. Another address needs a username
(`--expose-user`) or an explicit `--expose-open`.
`systemctl --user enable --now kiwi-proxy@NAME` keeps an exit up from login.

### DNS

- **Resolver mode** (the default): dnscrypt-proxy resolves over DoH through the
  exit (Google, Cloudflare, Quad9 or Mullvad as the upstream), with blocklists
  (OISD) refreshed daily.
- **Remote mode** (`--dns remote`): names go to the upstream itself, for Tor and
  `.onion` names. The blocklists still apply.

### Rules of the gateway

- UDP leaves nowhere: no QUIC, no WebRTC media, no plaintext DNS.
- To the world an exit is IPv4. A name without an IPv4 address is refused.
- A gateway a consumer brought up goes when its last member leaves. One brought
  up with `kiwi-proxy up` stays until `kiwi-proxy down`.
- One exit, one gateway, any number of members. Members that must stay apart
  use different exits.

## The app

**Kiwi Proxy** adds and edits exits (a SOCKS5 you were given, or a provider
module, with a searchable country list or node picker), brings them up and
down, offers one as a SOCKS5 port on this computer and copies its address,
checks what the world sees, shows who joined a gateway and their logs, and sets
up and configures provider modules.

## On a kiwi-server machine

kiwi-proxy also carries a kiwi-server module that hosts exits for the whole mesh
(one gateway per exit, published on the host's mesh address). It is not in
kiwi-server's tree yet and has not run on a machine, as its documentation says.
Provider modules are a desktop mechanism and do not run there.

Further reading: [architecture](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumers](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[plugin system](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
