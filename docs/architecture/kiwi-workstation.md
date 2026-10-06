# kiwi-workstation

The workstation is the user/operator OS for daily work. It is not a special
build — it is an ordinary **immutable Fedora desktop** with the Kiwi apps
installed on top.

## Base

- **Fedora Silverblue** or **Bluefin DX** — an atomic, image-based OS with
  easy rollback.

## Goals

- Easy onboarding for ordinary users.
- Safe defaults and VPN-first workflows.
- Simple updates and rollback, with the immutable `/usr` never touched by Kiwi.

## Getting the Kiwi apps

The workstation gets its software through
[**kiwi-updater**](../apps/kiwi-updater.md), which installs and updates apps
from open git [catalogs](../apps/kiwi-catalog.md). Nothing is layered onto the
base image and nothing outside your home is written unless you opt into an app
that needs root.

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system
kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git
kiwi install kiwi-killswitch   # for example
```

## Typical app set

A privacy-focused workstation usually runs:

- [**kiwi-killswitch**](../privacy-apps/kiwi-killswitch.md) — fail-closed VPN
  protection so the machine never leaks when a tunnel drops.
- [**kiwi-fox**](../privacy-apps/kiwi-fox.md) — isolated browser identities for
  managing separate accounts without cross-linking.
- [**kiwi-gen**](../privacy-apps/kiwi-gen.md) — generating the SSH and TLS keys
  and certificates the network uses.
- [**kiwi-server**](../build/kiwi-server.md) — building and managing the fleet
  (it is itself a Kiwi app with a GTK4 GUI).
- [**desktop CLI tools**](../privacy-apps/cli-tools.md) — everyday helpers.

See the [Privacy Apps overview](../privacy-apps/index.md) for the full suite.
