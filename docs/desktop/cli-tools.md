# kiwi-cli-tools-desktop

Four small command-line helpers for a Linux desktop.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Latest release: **v1.2.1**. It is in the [Kiwi catalog](catalogs.md), user scope.

```bash
kiwi install kiwi-cli-tools-desktop   # or ./install.sh install, into ~/.local/bin
```

## `torlink`: reach a machine over Tor

A poor man's VPN: reach any TCP service (SSH, a web UI, a database) on another
machine over Tor, with no open ports, no accounts and no server. Tor and socat
run in one rootless Podman container, so Podman is all you need.

An onion address is the identity. The offering side makes an **invite code**
for one peer, and the other side accepts it. The code carries a Tor client
authorization key, so the service is invisible to everyone without it: treat
the code like a password.

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

Each invite is its own onion service with only the services you listed, so
`torlink revoke bob` removes that access for good. `torlink ls` shows services,
peers and forwards. Tor is TCP only, and the first connection takes a while. The
container's SOCKS port (19050) listens on loopback only. State, including your
onion keys, lives in `~/.local/share/torlink`, and `torlink purge` deletes it.

## `pweb`: share a folder over HTTPS

Serves the **current directory** over HTTPS on a random free port, for handing
a file to another machine on the same network. A self-signed certificate is
made on the first run and reused afterwards. It serves to the whole LAN, so
start it in the folder you mean to share and stop it with Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`: pick an SSH host

A numbered menu of every concrete `Host` alias in your `~/.ssh/config`. Pick one
and it connects. Tag hosts with a `# tags: work prod` comment inside the `Host`
block to filter:

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # the tags you have
$ select-server -f other.conf   # another config file
```

## `tethering`: the TTL fix

Sets TTL 64 on traffic arriving from one interface, so devices tethered through
this machine look like the machine's own traffic to a carrier that counts hops.
It asks for sudo, adds one `iptables` mangle rule, and the rule does **not**
survive a reboot.

```
tethering            # pick the interface, set the rule
tethering --status
tethering --off
```
