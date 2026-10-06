# Repositories & status

Every Kiwi Network repository lives under
[github.com/derlocke-ng](https://github.com/derlocke-ng). "Released" means the
repo has a version tag, which is what kiwi-updater installs. "Tracks `main`"
means kiwi follows the default branch, because there is no tag yet.

## Active

| Repository | What it is | Release | In the catalog | License |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | builds the network's machines: fleet file → scripts, configs, install ISOs | tracks `main` (2.2.0) | no, use `kiwi add` | GPL-3.0+ |
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installs and updates apps from git catalogs | v2.0.0 | yes | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | the Kiwi app catalog | (a list) | n/a | |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | fail-closed VPN kill switch for GNOME | v0.2.2 | yes | GPL-3.0+ |
| [ensconce](https://github.com/derlocke-ng/ensconce) | post-install setup for Bluefin-DX | v2.1.1 | yes | GPL-3.0 |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | isolated browser identities in rootless Podman | v0.1.3 | yes | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | kiwi-fox provider: Tor | tracks `main` (0.1.0) | yes | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | kiwi-fox provider: gluetun VPN | tracks `main` (0.1.0) | yes | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | kiwi-fox provider: 9proxy | tracks `main` (0.1.0) | yes | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | kiwi-fox provider: Mysterium | tracks `main` (0.1.0) | yes | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering` | v1.0.0 | yes | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | in-browser SSH/TLS key & certificate manager | web page ([live](https://derlocke-ng.github.io/kiwi-gen/)) | no | MIT |
| [kiwi-pentesting](https://github.com/derlocke-ng/kiwi-pentesting) | authorized-testing suite on kiwi-fox | scaffold, not installable | no | GPL-3.0+ |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | this website and documentation | n/a | n/a | AGPL-3.0 |

## Older and superseded

| Repository | What it was | Now |
|---|---|---|
| [kiwi-cloud](https://github.com/derlocke-ng/kiwi-cloud) | the v1 cloud-node compose stack (2025) | superseded by kiwi-server's `node-cloud` role, which is that stack taken apart into modules |
| [kiwi-vpn-monitor](https://github.com/derlocke-ng/kiwi-vpn-monitor) | a GNOME extension that watched the gateway and DNS and brought up WireGuard (2025) | its gateway detection lives on in kiwi-killswitch |
| [kiwi-blog](https://github.com/derlocke-ng/kiwi-blog) | a small Markdown static-site generator (MIT, 2025) | standalone; this site's docs theme takes its colours from it |
| [kiwi-network-welcome](https://github.com/derlocke-ng/kiwi-network-welcome) | a one-line placeholder (2025) | n/a |
| kiwi-modules, kiwi-stack | empty repositories | n/a |

## Known gaps

These come straight from the repositories:

- **kiwi-server**: the first boot of each target end to end on real hardware is
  not yet verified from the new pipeline. The generators are tested in CI.
- **kiwi-fox providers**: they need kiwi-fox's provider subsystem, which is on
  kiwi-fox `main` but not in the v0.1.3 release (see
  [the workaround](../apps/kiwi-fox-providers.md)). The VPN, 9proxy and
  Mysterium modules have not been validated end to end against a real account.
- **kiwi-updater**: a hosted registry of trusted catalogs
  (`kiwi catalog browse`) and tag signature verification are planned.
- **kiwi-pentesting**: the CLI, GUI and installer are not written yet.
