# Kiwi Network

Kiwi Network is a family of open-source tools for connecting what is yours:
your **machines**, your **people** and your **desktop**, without a platform in
between.

<div class="kiwi-pillars" markdown>

<div markdown>
![](assets/icons/kiwi-server.svg){ width=48 }

**[The network](network/index.md)**

A VPS and the machines you own become a WireGuard mesh with its own DNS, its
own certificate authority, your services and backups, all described in one file
and built by [kiwi-server](server/index.md).
</div>

<div markdown>
![](assets/icons/kiwi-chat.svg){ width=48 }

**[People](people/index.md)**

[Armory](people/armory.md) and [kiwi-framework](people/index.md): peer-to-peer
web tools over nostr (lists, chat, files, passwords, calendars and more), sealed
in your browser, with no sign-up and no server of ours.
</div>

<div markdown>
![](assets/icons/kiwi-updater.svg){ width=48 }

**[The desktop](desktop/index.md)**

Apps for Fedora Atomic desktops, installed and updated from git by
[kiwi-updater](desktop/kiwi-updater.md), including sealed exits for
[working with many client networks](clients/index.md).
</div>

</div>

## The network

[kiwi-server](server/index.md) turns one `fleet.yaml` into an unattended install
ISO per machine (Fedora CoreOS, uCore or Debian), then applies each machine's
role over SSH:

| Role | What the machine becomes |
|---|---|
| `master` | the **kiwi-master**: the WireGuard entry point, whose traffic leaves through a commercial VPN (the double hop), with Pi-hole, Tor and the admin pages, and optionally a relay and a hub for your people |
| `node` · `gateway` | routes a LAN through the VPN, with Pi-hole, DHCP relay, a download station and SFTP |
| `node` · `cloud` | Nextcloud with Collabora, and Vaultwarden |
| `node` · `minimal` | the VPN client and nginx, for modules of your choice: backups, Tang, Immich, Paperless-ngx, OpenCloud … |
| `bare` | just the base system |

The master is the only machine that has to be reachable from the Internet, and
by default it publishes one port: WireGuard, UDP 51820. Everything else dials
out to it and meets in the mesh. See [How the network works](network/index.md).

## People

A **hub** is a set of web apps that run entirely in the browser and sync over
nostr relays. [Armory](people/armory.md) is the first, live at
[derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/), and the
template for your own. A kiwi-master can carry its own relay and a private hub
for your fleet. See [People](people/index.md).

## The desktop

[kiwi-updater](desktop/kiwi-updater.md) installs apps from **git catalogs** on
Fedora Silverblue and Bluefin. An app is a repo, a release is a tag, and an app
that needs root says why before it asks. The [Kiwi catalog](desktop/catalogs.md)
has:

| App | What it does |
|---|---|
| [kiwi-killswitch](desktop/kiwi-killswitch.md) | a fail-closed VPN kill switch for GNOME |
| [ensconce](desktop/ensconce.md) | post-install setup for Bluefin-DX from plain list files |
| [kiwi-proxy](clients/kiwi-proxy.md), [kiwi-custodia](clients/kiwi-custodia.md), [kiwi-fox](clients/kiwi-fox.md) | sealed exits, and the distro boxes and browsers that live inside them |
| [provider modules](clients/providers.md) | exits from Tor, a VPN, 9proxy or Mysterium |
| [gnome-monitor](desktop/gnome-monitor.md) | display layouts for GNOME |
| [syncman](desktop/syncman.md) | two-way folder sync |
| [kiwi-cli-tools-desktop](desktop/cli-tools.md) | `torlink`, `pweb`, `select-server`, `tethering` |
| [kiwi-server](server/index.md) | the network's builder, as a GTK app too |

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

## Where things stand

Young projects, described as they are. kiwi-server was proven on hardware in
October and November 2026, and some modules and providers are still to be
validated. The [status page](project/status.md) lists every repository, its
release and its known gaps.
