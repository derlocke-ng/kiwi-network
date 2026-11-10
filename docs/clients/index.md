# Working with many client networks

If you work remotely for many clients, you usually need a separate VPN or SOCKS
connection to reach each client's network. Ten clients then mean ten
connections. Running all of them on the host causes problems: ten tunnels are
up at the same time, their routes conflict with each other, and traffic for one
client's network can end up in another's.

The Kiwi desktop apps let you work in each client's network in isolation. The
host is not filled with tunnels and routes, and you do not have ten VPN
connections running at once. Each connection is put into a container of its
own, and the only route out of that container leads to that one client. Such a
connection is called an **exit**. Your tools run in a container or a browser
profile that joins the exit they need, and nothing else on the host changes.

| App | What it does |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | The engine that the other apps build on. An **exit** is one upstream connection that you save under a name. The upstream is the proxy your traffic is sent to: either a SOCKS5 proxy you were given, or one that a provider module creates. When you bring an exit up, kiwi-proxy creates a **gateway** for it. A gateway is a network namespace (a separate network stack with its own routes and firewall) whose only route leads to that upstream. Programs on the host can use an exit through a local SOCKS5 port |
| [**kiwi-custodia**](kiwi-custodia.md) | **Linux distributions in boxes that use an exit.** A box is a rootless container (one that runs without root rights) with Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky or Alpine and its own home directory. *All* network traffic from the box goes through the exit. That includes package managers, games and statically linked programs that ignore proxy settings |
| [**kiwi-fox**](kiwi-fox.md) | **Browser profiles that use an exit.** Each profile runs Camoufox, Firefox or Tor Browser and has its own storage |
| [**Provider modules**](providers.md) | Modules that create exits through Tor, a VPN (with gluetun), 9proxy or Mysterium. Tor and Mysterium are a quick way to get more IP addresses, which is useful for testing |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## How the exits stay separate { #how-it-stays-clean }

- **A gateway fails closed.** This means that a failure stops the traffic and
  never lets it take another path. The firewall in a gateway drops everything
  that is not addressed to the gateway's one upstream. If the gateway stops,
  everything that joined it has no route any more. No program has to notice
  the failure and react to it, because without the gateway there is no route.
- **Only what you use is running.** When a box or a browser starts a gateway,
  the gateway is removed again as soon as the last box or browser on it has
  stopped. Only exits that you start yourself with `kiwi-proxy up` keep
  running.
- **Clients are kept separate.** Boxes and browsers on the same exit share it,
  so they have the same IP address and the same network namespace. Clients
  that must not see each other get different exits. Each box also has its own
  home directory, so the SSH keys and browser profiles of one client are not
  available in another client's box.
- **No root rights and no routes on the host.** Everything runs in rootless
  Podman, which runs containers as your own user. The host's own network is
  not changed.
- **DNS queries go through the exit as well.** By default, names are resolved
  with DNS over HTTPS (DoH) through the exit, and lists of advertising domains
  are blocked. To resolve a client's **internal hostnames**, use
  `--dns remote` instead. The names are then passed to the client's side and
  resolved there. Tor and `.onion` names need this mode too.

## Limits

These limits are stated in the repositories:

- **Only TCP and only IPv4.** UDP is not forwarded, so QUIC and WebRTC media
  do not work. There is no route for IPv6.
- **One VPN configuration per machine.** The VPN provider module has a single
  gluetun configuration, with one `vpn.json` and one custom WireGuard config.
  Its exits differ only in the server country. If you need several clients'
  own VPNs at the same time, the way to do that today is a SOCKS5 endpoint
  for each client.
- **A box restricts the network, but it is not a sandbox.** Like a distrobox
  container, it shares your display, your session bus and your clipboard.
  What it cannot do is reach the network in any way other than through its
  exit.
- **Mysterium:** one identity can have only one connection at a time.

## Get started

The following commands install the apps, save one client's SOCKS5 proxy as an
exit, and open a shell in a Fedora box that uses this exit:

```bash
kiwi install kiwi-custodia            # brings kiwi-proxy along
kiwi-custodia setup                   # images and DNS data

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
