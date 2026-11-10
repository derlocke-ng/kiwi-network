# Working with many client networks

Ten remote clients often means ten VPNs or SOCKS endpoints, one to reach each
client's network. Running them all on the host is a mess: ten tunnels at once,
routes that fight, and one network leaking into the next. The Kiwi desktop apps
give each one a **sealed exit** instead: a container whose only route is that
one upstream. Your tools join the exit they need, and nothing else on the host
changes.

| App | What it does |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | The engine. An **exit** is one upstream by name: a SOCKS5 you were given, or one a provider module makes. Bringing it up makes a **gateway**, a network namespace whose only route is that upstream. Host apps can use it as a local SOCKS5 port |
| [**kiwi-custodia**](kiwi-custodia.md) | **Distro boxes on an exit**: Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky or Alpine in a rootless container with its own home. *Everything* in the box leaves through the exit: package managers, games, static binaries that never heard of a proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Browser profiles on an exit**: Camoufox, Firefox or Tor Browser, each profile with its own storage |
| [**Provider modules**](providers.md) | Exits from Tor, a VPN (gluetun), 9proxy or Mysterium. Tor and Mysterium are the quick way to more exit IPs, handy for testing |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## How it stays clean

- **Fail closed.** A gateway's firewall drops everything except its one
  upstream. If the gateway dies, whatever joined it loses its route. The kill
  switch is the absence of a route, not software that has to notice.
- **Nothing runs that isn't used.** A gateway that a box or browser brought up
  goes away when the last one leaves. Only exits you start with
  `kiwi-proxy up` stay up.
- **Apart stays apart.** Things on the same exit share it (one IP, one
  namespace). Clients that must not meet get different exits, and each box has
  its own home, so SSH keys and browser profiles do not cross.
- **No root, no host routes.** Everything runs in rootless Podman, and the
  host's own network is untouched.
- **DNS goes through the exit too.** By default names resolve over DoH through
  the exit, with ad-blocking lists. For a client's **internal hostnames**, hand
  the names to the client's side instead with `--dns remote` (also the mode for
  Tor and `.onion` names).

## Limits

These come from the repositories:

- **TCP only, IPv4 only.** UDP leaves nowhere (no QUIC, no WebRTC media), and
  IPv6 gets no route.
- **One VPN configuration per machine.** The VPN provider module holds one
  gluetun configuration (one `vpn.json`, one custom WireGuard config), and its
  exits differ only by server country. For several clients' own VPNs side by
  side, a SOCKS5 endpoint per client is the path today.
- **A box is network custody, not a sandbox.** It shares your display, session
  bus and clipboard, like distrobox. What it cannot do is reach the network
  other than through its exit.
- **Mysterium:** one identity holds one connection at a time.

## Get started

```bash
kiwi install kiwi-custodia            # brings kiwi-proxy along
kiwi-custodia setup                   # images and DNS data

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
