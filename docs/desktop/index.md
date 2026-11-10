# The desktop

The desktop part of Kiwi Network is the computer you work on: a Linux
workstation that is set up automatically and gets its apps from git catalogs.
A catalog is a git repository that lists apps. You do not have to set the
machine up by hand, and you can set up the next one the same way.

The Kiwi desktop tools are built for **Fedora Atomic desktops**: Fedora
Silverblue and [Bluefin](https://projectbluefin.io/), and Bluefin-DX in
particular. These systems are installed and updated as one complete image.
Their `/usr` directory is immutable, which means that it cannot be changed, and
an update can be rolled back easily. There is no special Kiwi image. You
install a standard Silverblue or Bluefin image and add three things on top of
it.

1. **[kiwi-updater](kiwi-updater.md)** installs apps from git catalogs and
   keeps them updated. It installs everything into your home directory. Only
   an app that needs root also gets a part that is owned by root. kiwi-updater
   updates itself as well.
2. **[ensconce](ensconce.md)** sets up a freshly installed Bluefin-DX. You
   describe your setup in plain list files, and ensconce applies it: packages,
   Flatpaks, GNOME extensions, Nextcloud sync, SSH, sysctl and power settings,
   the login screen, and your Kiwi apps. With `--export` it writes the setup of
   an existing machine into such files, so that you can clone that machine.
3. **The apps**, which you install from the [Kiwi catalog](catalogs.md):

| App | What it does |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | A VPN kill switch for GNOME. It is fail-closed, which means that all traffic stays blocked when the VPN is down |
| [Client networks](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | An exit for each VPN or SOCKS endpoint. An exit is an isolated container that can only reach that one endpoint. Distro boxes and browsers can be attached to an exit, so that all their traffic goes through it |
| [kiwi-server](../server/index.md) | The tool with which you build and run your own network |
| [gnome-monitor](gnome-monitor.md) | Saves display layouts and switches between them. It also turns individual monitors off and on |
| [syncman](syncman.md) | Synchronises folders in both directions, for example game saves. The synchronisation runs as user services |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

This section also describes [kiwi-gen](kiwi-gen.md), a manager for keys and
certificates that runs in the browser and works offline.

## From a fresh install

These commands take you from a freshly installed system to a desktop with the
Kiwi apps:

```bash
# 1. kiwi-updater: user and system scope, one password prompt; the Kiwi catalog comes with it
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. set the machine up
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. the apps you want (or list them in ensconce's kiwi-apps.list)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

You can also install apps without the terminal. **Kiwi Apps** (`kiwi-gui`) in
the app grid installs an app with a click.

## Joining your network

A desktop joins the mesh in the same way as any other device. The mesh is the
private WireGuard network that connects your servers and devices. The command
`kiwi-server enroll fleet.yaml laptop --group devices` writes a WireGuard
configuration file, and you import this file in GNOME Settings. Also import the
certificate authority (CA) of your fleet, `kiwiCA.pem`, so that the desktop
trusts the HTTPS certificates of the names in your network. ensconce installs
every `.pem` file in its `certs/` directory for the whole system.

[kiwi-killswitch](kiwi-killswitch.md) then protects that connection and keeps
the machine fail-closed. This means that traffic which does not go through the
connection is blocked, also when the connection is down. At home, a gateway
node on your LAN may already send your traffic through a tunnel. With the
*trusted kiwi-nodes* setting, the kill switch accepts such a gateway node in
place of the tunnel.
