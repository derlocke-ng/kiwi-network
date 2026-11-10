# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop is a package of four small command-line tools for a
Linux desktop. `torlink` reaches a service on another machine over Tor, `pweb`
shares a folder over HTTPS, `select-server` lets you pick an SSH host from a
menu, and `tethering` adjusts the TTL of traffic from tethered devices.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Latest release: **v1.2.1**. It is in the [Kiwi catalog](catalogs.md), user scope.

```bash
kiwi install kiwi-cli-tools-desktop   # or ./install.sh install, into ~/.local/bin
```

## `torlink`: reach a machine over Tor

`torlink` lets you reach any TCP service on another machine, such as SSH, a
web interface or a database, over the Tor network. It is a simple substitute
for a VPN: neither machine needs an open port, you need no account, and there
is no server to run. Tor and socat run together in one rootless Podman
container, so Podman is all you need.

A machine that offers services is identified by its onion address, which is an
address inside the Tor network. On that machine you create an **invite code**
for one peer, which is the other party that should get access. The peer
accepts the code on the other machine. The code contains a Tor client
authorization key. Nobody without this key can see that the service exists,
so treat the code like a password.

```bash
# machine A: offer SSH and a web UI to "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # prints torlink1:…  (secret!)

# machine B: use them
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH over Tor
torlink connect alice web           # 127.0.0.1:2200 → alice's web UI
torlink ssh-config >> ~/.ssh/config # then `ssh alice-tor`; `select-server tor` lists them
```

Each invite is a separate onion service that contains only the services you
listed in it. This is why `torlink revoke bob` removes that access
permanently. `torlink ls` shows your services, your peers and your forwards,
which are the local ports that lead to a peer's services. Tor carries only
TCP, and the first connection takes a while. The SOCKS port of the container
(19050) listens on the loopback interface only. The state of `torlink`,
including your onion keys, is stored in `~/.local/share/torlink`, and
`torlink purge` deletes it.

## `pweb`: share a folder over HTTPS

`pweb` serves the **current directory** over HTTPS on a random free port. Use
it to pass a file to another machine on the same network. It creates a
self-signed certificate the first time it runs and reuses this certificate
afterwards. Every machine on the local network can reach the folder while
`pweb` is running. Start it in the folder you really want to share, and stop
it with Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: pick an SSH host

`select-server` shows a numbered menu of every concrete `Host` alias in your
`~/.ssh/config`, which means every alias that is not a wildcard pattern.
Choose one, and it connects to that host. To filter the menu, tag your hosts.
Add a comment such as `# tags: work prod` inside the `Host` block, and pass a
tag on the command line:

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # the tags you have
$ select-server -f other.conf   # another config file
```

## `tethering`: set the TTL for tethered devices { #tethering-the-ttl-fix }

`tethering` is for the case where other devices use this machine's Internet
connection, which is called tethering. Some carriers count the network hops of
the traffic, and they can tell tethered devices from the machine itself that
way. `tethering` sets the TTL to 64 on all traffic that arrives from one
interface. To the carrier, the traffic of the tethered devices then looks like
the machine's own traffic. The tool asks for sudo and adds one `iptables`
mangle rule. The rule does **not** survive a reboot.

```
tethering            # pick the interface, set the rule
tethering --status
tethering --off
```
