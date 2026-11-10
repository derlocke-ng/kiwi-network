# kiwi-proxy

kiwi-proxy is for people who work in many clients' networks and reach each one
through its own VPN or SOCKS connection. You save every connection as a named
**exit** and bring it up only when you need it. Each exit is kept apart from
the others, and a program that joins an exit can reach the network only
through it. Ten clients therefore do not mean ten VPN connections running on
the host at once. Browsers, testing tools, programs on the host and
kiwi-server machines can use an exit. kiwi-proxy runs in rootless Podman,
which means in containers that run as your own user without root rights.

- Repository: [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Latest release: **v0.7.3**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.
- It consists of a command-line tool (`kiwi-proxy`), a GTK4 app
  (**Kiwi Proxy**) and systemd user units. It is the proxy engine that used to
  be part of kiwi-fox. It was moved into a project of its own so that more
  than one app can use it.

An **exit** is one upstream connection with a name. The upstream is the proxy
that the traffic is sent to. It is either a SOCKS5 proxy you were given, or one
that a [provider module](providers.md) creates for you through Tor, a VPN
tunnel, 9proxy or Mysterium. An exit by itself is only a saved entry, and
nothing runs for it. When you bring an exit up, kiwi-proxy starts a **gateway**
container for it:

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

The gateway owns a network namespace, which is a separate network stack with
its own routes and firewall rules. A kiwi-fox browser, a kiwi-custodia box or a
tool container joins this namespace and becomes a member of the gateway. From
then on, its only route leads to the exit's upstream. If the gateway stops, its
members have no route left. This is called failing closed: a failure cuts the
connection and never opens another path.

## Install

```bash
kiwi install kiwi-proxy      # kiwi-fox and kiwi-custodia bring it along
kiwi-proxy setup             # the gateway image, DNS data, provider module images
```

kiwi-proxy needs rootless Podman and Python 3.12+ with pydantic. The app also
needs GTK4 and libadwaita. Passwords are stored in the desktop keyring through
`secret-tool`. On a machine without a keyring, they are stored in files with
mode 0600, which only your user can read.

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

An endpoint is the address of an upstream. You can write it as
`socks5://user:pass@host:port`, `http://…` or `https://…`, or in the vendor
format `host:port:user:pass`. `kiwi-proxy test ENDPOINT` tests an endpoint
without creating an exit.

### Exits for host applications

A program on the host does not have to run in a container to use an exit.
kiwi-proxy can publish an exit as a SOCKS5 port on the host, with one port for
each exit:

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

By default, the port listens on `127.0.0.1` only. If you let it listen on
another address, you must either set a username with `--expose-user` or allow
open access explicitly with `--expose-open`. To have an exit up from the moment
you log in, run `systemctl --user enable --now kiwi-proxy@NAME`.

### DNS

- **Resolver mode** is the default. dnscrypt-proxy resolves names with DNS
  over HTTPS (DoH) and sends these queries through the exit. The DoH resolver
  can be Google, Cloudflare, Quad9 or Mullvad. Blocklists (OISD) are applied,
  and they are refreshed daily.
- **Remote mode** (`--dns remote`) passes the names to the upstream, which
  resolves them itself. This mode is meant for Tor and `.onion` names. The
  blocklists apply in this mode too.

### Rules of the gateway

- UDP is not forwarded. That means no QUIC, no WebRTC media and no plain-text
  DNS.
- An exit reaches the outside world over IPv4 only. A name that has no IPv4
  address is refused.
- A gateway that another app started, such as kiwi-fox or kiwi-custodia, is
  removed when its last member leaves. A gateway that you started with
  `kiwi-proxy up` keeps running until you run `kiwi-proxy down`.
- Each exit has exactly one gateway, and any number of members can join it.
  Members that must be kept separate from each other use different exits.

## The app

In the **Kiwi Proxy** app you can add and edit exits, either from a SOCKS5
proxy you were given or from a provider module. For a module exit, you choose
from a searchable country list or from a list of nodes. You can bring exits up
and down, offer an exit as a SOCKS5 port on this computer and copy its
address, and check what the outside world sees when you connect through it.
The app also shows which members have joined a gateway and their logs, and it
sets up and configures provider modules.

## On a kiwi-server machine

The kiwi-proxy repository also contains a module for kiwi-server. With it, a
kiwi-server machine hosts exits for the whole mesh, which is the private
WireGuard network that connects your kiwi-server machines. The module runs
one gateway for each exit and publishes it on the host's mesh address. Its
documentation says that the module is not in kiwi-server's source tree yet
and that it has not been run on a machine. Provider modules only work on the
desktop and do not run on a kiwi-server machine.

Further reading: [architecture](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consumers](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[plugin system](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
