# The desktop

The Kiwi desktop tools are built for **Fedora Atomic desktops**: Fedora
Silverblue and [Bluefin](https://projectbluefin.io/) (Bluefin-DX in
particular). These are image-based systems with an immutable `/usr` and easy
rollback. There is no special "Kiwi" image. You install a stock image and add
three layers on top:

1. **[ensconce](ensconce.md)** sets up a fresh Bluefin-DX install from plain
   list files: packages, Flatpaks, GNOME extensions, Nextcloud sync folders,
   your CA certificate, dconf and login-screen settings. It can also export a
   configured machine to set up the next one the same way.
2. **[kiwi-updater](kiwi-updater.md)** installs and updates apps from git
   catalogs, in your home directory, plus a root-owned part only for apps that
   need one. It updates itself.
3. **The apps**, from the [Kiwi catalog](catalogs.md):
   [kiwi-killswitch](../apps/kiwi-killswitch.md),
   [kiwi-fox](../apps/kiwi-fox.md) and its
   [providers](../apps/kiwi-fox-providers.md), and
   [kiwi-cli-tools-desktop](../apps/cli-tools.md).

## From a fresh install

```bash
# 1. kiwi-updater, with the system scope (one password prompt)
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system

# 2. the Kiwi catalog
kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
kiwi list

# 3. set the machine up, then the apps you want
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

kiwi install kiwi-killswitch
kiwi install kiwi-fox && kiwi-fox setup
```

## Connecting to your network

A desktop joins the mesh like any other device, as a WireGuard client of the
master's wg-easy. Import the config into GNOME Settings (NetworkManager), and
import the fleet CA (`kiwiCA.pem`) so the fleet's HTTPS names are trusted.
ensconce installs every `.pem` in its `certs/` config directory system-wide (the `cacert` step).

[kiwi-killswitch](../apps/kiwi-killswitch.md) then keeps the machine fail-closed
around that connection. Its *trusted kiwi-nodes* setting lets a gateway node on
your LAN stand in for the tunnel at home.
