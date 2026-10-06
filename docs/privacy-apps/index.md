# Privacy Apps

The Kiwi apps are the privacy and self-hosting tools that run on the
[workstation](../architecture/kiwi-workstation.md) and nodes. They are all open
source (GPL-3.0 or MIT), installable through
[kiwi-updater](../apps/kiwi-updater.md), and designed for immutable Fedora
(Silverblue / Bluefin) with rootless Podman where containers are involved.

| App | What it does | Install |
|---|---|---|
| [kiwi-fox](kiwi-fox.md) | Isolated Windows 11 browser identities in rootless Podman | `kiwi install kiwi-fox` |
| [Provider plugins](plugins.md) | Give kiwi-fox a Tor / VPN / 9proxy / Mysterium exit | `kiwi install kiwi-plugin-*` |
| [kiwi-killswitch](kiwi-killswitch.md) | Fail-closed VPN kill switch for GNOME | `kiwi install kiwi-killswitch` |
| [kiwi-gen](kiwi-gen.md) | Browser-based SSH/TLS key & certificate generator | web / `python3 -m http.server` |
| [kiwi-pentesting](kiwi-pentesting.md) | Containerized authorized-testing suite, a kiwi-fox client | `kiwi install kiwi-pentesting` |
| [Desktop CLI tools](cli-tools.md) | `pweb`, `select-server`, `tethering` | `kiwi install kiwi-cli-tools-desktop` |

## Also in the ecosystem

- **[kiwi-server](../build/kiwi-server.md)** — builds the fleet (GTK4 app
  "Kiwi Server").
- **[kiwi-updater](../apps/kiwi-updater.md)** — the installer itself ("Kiwi Apps").
- **kiwi-blog** — a lightweight Markdown static-site generator
  (<https://github.com/derlocke-ng/kiwi-blog>, MIT), which powers sites like
  this one.
- **kiwi-vpn-monitor** — the GNOME extension that first automated VPN/gateway
  detection for Kiwi infrastructure; its gateway intelligence now lives on in
  [kiwi-killswitch](kiwi-killswitch.md).
