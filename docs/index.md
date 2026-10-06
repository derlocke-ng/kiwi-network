# Kiwi Network

Kiwi Network is an all-in-one, privacy-first approach to self-hosting your own
infrastructure with open source and Linux — for private individuals, SMBs and
public offices.

The core idea is simple: **expose as little as possible.** Only a single
WireGuard entry point ever faces the public Internet; everything else lives
behind the tunnel.

## The three machine roles

| Role | What it is | Built from |
|---|---|---|
| [**kiwi-master**](architecture/kiwi-master.md) | The hardened public entry point — WireGuard + core network services | `kiwi-server`, `master` role |
| [**kiwi-node**](architecture/kiwi-node.md) | Private services (cloud, vault, downloads, LAN gateway), reachable only via VPN/LAN | `kiwi-server`, `node-gw` / `node-cloud` roles |
| [**kiwi-workstation**](architecture/kiwi-workstation.md) | An easy daily-driver desktop OS (Fedora Silverblue / Bluefin DX) with the Kiwi apps | the Kiwi app suite, installed via `kiwi-updater` |

These are no longer hand-assembled compose stacks. They are **produced by
tooling** you run on your own machine.

## How it fits together

```
          ┌─────────────────────────────────────────────┐
          │  kiwi-server    write one fleet.yaml →        │
          │                 first-boot scripts + ISOs     │
          └───────────────┬──────────────┬───────────────┘
                   builds │              │ builds
                          ▼              ▼
                    kiwi-master      kiwi-node(s)
                  (WireGuard entry) (cloud / gateway)
                          ▲              ▲
                          │   VPN tunnel │
          ┌───────────────┴──────────────┴───────────────┐
          │  kiwi-workstation  (Silverblue / Bluefin)      │
          │    kiwi-updater → installs the Kiwi apps:      │
          │    kiwi-fox · kiwi-killswitch · kiwi-gen · …    │
          └───────────────────────────────────────────────┘
```

- **[kiwi-server](build/kiwi-server.md)** builds the servers. Write one
  `fleet.yaml`, get a first-boot script, an Ignition/preseed config and an
  unattended install ISO per host. Boot the ISO, walk away, and the machine
  comes back as a `kiwi-node` or `kiwi-master`.
- **[kiwi-updater](apps/kiwi-updater.md)** + **[kiwi-catalog](apps/kiwi-catalog.md)**
  install and update the desktop apps from open git catalogs — no accounts, no
  store, no vendor lock-in.
- **[The Kiwi apps](privacy-apps/index.md)** are the privacy and self-hosting
  tools that run on the workstation.

## Start here

- New to the project? Read the [Getting Started overview](getting-started/index.md)
  and the [Network Model](getting-started/network-model.md).
- Want to deploy servers? See [kiwi-server](build/kiwi-server.md).
- Setting up a desktop? See [kiwi-updater](apps/kiwi-updater.md) and the
  [Privacy Apps](privacy-apps/index.md).

---

- Homepage: <https://kiwi-network.eu>
- Docs: <https://docs.kiwi-network.eu>
- Source: <https://github.com/derlocke-ng>
