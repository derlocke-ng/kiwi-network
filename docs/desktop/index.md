# The desktop

The Kiwi desktop tools are built for **Fedora Atomic desktops**: Fedora
Silverblue and [Bluefin](https://projectbluefin.io/) (Bluefin-DX in
particular). These are image-based systems with an immutable `/usr` and easy
rollback. There is no special Kiwi image: you install a stock one and add three
layers on top.

1. **[kiwi-updater](kiwi-updater.md)** installs and updates apps from git
   catalogs: everything in your home, plus a root-owned part only for apps that
   need one. It updates itself too.
2. **[ensconce](ensconce.md)** sets up a fresh Bluefin-DX from plain list files:
   packages, Flatpaks, GNOME extensions, Nextcloud sync, SSH, sysctl and power
   settings, the login screen, and your Kiwi apps. `--export` clones a machine.
3. **The apps**, from the [Kiwi catalog](catalogs.md):

| App | What it does |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | A fail-closed VPN kill switch for GNOME |
| [Client networks](../clients/index.md): kiwi-proxy, kiwi-custodia, kiwi-fox | One sealed exit per VPN or SOCKS endpoint, and distro boxes and browsers that live inside them |
| [kiwi-server](../server/index.md) | Build and run your own network |
| [gnome-monitor](gnome-monitor.md) | Save and switch display layouts; turn single monitors off and on |
| [syncman](syncman.md) | Two-way folder sync (game saves and more) as user services |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Also here: [kiwi-gen](kiwi-gen.md), a key and certificate manager that runs
offline in the browser.

## From a fresh install

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

**Kiwi Apps** (`kiwi-gui`) in the app grid does the same with a click.

## Joining your network

A desktop joins the mesh like any other device: `kiwi-server enroll fleet.yaml
laptop --group devices` writes a WireGuard config, which you import into GNOME
Settings. Import the fleet's CA (`kiwiCA.pem`) so its HTTPS names are trusted.
ensconce installs every `.pem` in its `certs/` directory system-wide.

[kiwi-killswitch](kiwi-killswitch.md) then keeps the machine fail-closed around
that connection. Its *trusted kiwi-nodes* setting lets a gateway node on your
LAN stand in for the tunnel at home.
