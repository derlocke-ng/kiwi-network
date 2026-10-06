# kiwi-cli-tools-desktop

Three small CLI helpers for a Linux desktop.

- Repository: [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Latest release: **v1.0.0**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.

```bash
kiwi install kiwi-cli-tools-desktop   # or ./install.sh install, into ~/.local/bin
```

## `pweb`

Serves the **current directory** over HTTPS on a random free port, for handing a
file to another machine on the same network without setting anything up. A
self-signed certificate is generated on first run (it needs `openssl`) and
reused afterwards, so the browser warning only happens once per machine. It
serves to the whole LAN: start it in the directory you mean to share, and stop
it with Ctrl+C when done.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server`

A numbered menu of every concrete `Host` alias in your `~/.ssh/config`. Pick one
and it connects. Wildcard patterns are skipped, and aliases are de-duplicated
and sorted. Pass a different config file as the first argument.

```
$ select-server
1) backup    3) pi
2) hetzner   4) work
connect to: 3
```

## `tethering`

Sets TTL 64 on traffic arriving from one interface, so devices tethered through
this machine look like the machine's own traffic to a carrier that counts hops.
It elevates itself with sudo and applies one `iptables` mangle rule, which
intentionally does **not** survive a reboot.

```
tethering            # pick the interface, set the rule (idempotent)
tethering --status   # show what is set
tethering --off      # remove it now
```
