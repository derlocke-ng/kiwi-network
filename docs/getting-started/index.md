# Getting Started

Kiwi Network is built around one principle: **expose as little as possible.**

A full deployment has three parts, and you can adopt them in any order:

## 1. The servers — `kiwi-server`

The servers are built, not hand-configured. With
[**kiwi-server**](../build/kiwi-server.md) you write a single `fleet.yaml`
describing your hosts and roles, and it renders a first-boot script, an
Ignition or preseed config, and an unattended install ISO for each one. Boot a
machine from the ISO and it installs itself and comes up as:

- a [**kiwi-master**](../architecture/kiwi-master.md) — the public WireGuard
  entry point (role `master`), or
- a [**kiwi-node**](../architecture/kiwi-node.md) — private services in
  gateway mode (`node-gw`) or cloud mode (`node-cloud`).

Targets are Fedora CoreOS, uCore and Debian stable, all with automatic updates
that reboot only in a window you choose.

## 2. The desktop apps — `kiwi-updater`

On the [**kiwi-workstation**](../architecture/kiwi-workstation.md) (Fedora
Silverblue or Bluefin DX), [**kiwi-updater**](../apps/kiwi-updater.md) installs
and keeps up to date the Kiwi apps and anything else in a
[catalog](../apps/kiwi-catalog.md) you trust. No accounts, no store — a catalog
is just a git repo.

```bash
# recommended install (user scope + opt-in root-owned system scope)
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system

kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
kiwi list
```

## 3. The privacy apps

The [**Kiwi apps**](../privacy-apps/index.md) are the tools that run on the
workstation and nodes:

- [**kiwi-fox**](../privacy-apps/kiwi-fox.md) — isolated browser identities
- [**kiwi-killswitch**](../privacy-apps/kiwi-killswitch.md) — a fail-closed VPN
  kill switch for GNOME
- [**kiwi-gen**](../privacy-apps/kiwi-gen.md) — a local SSH/TLS key &
  certificate generator
- [**kiwi-pentesting**](../privacy-apps/kiwi-pentesting.md) — a containerized
  authorized-testing suite
- [**desktop CLI tools**](../privacy-apps/cli-tools.md) — small everyday helpers

## Next

- Read the [Network Model](network-model.md) to understand how traffic flows.
- Dive into the [Architecture](../architecture/index.md) of each role.
