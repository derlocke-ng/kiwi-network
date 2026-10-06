# kiwi-fox

Isolated Windows 11 browser identities in rootless Podman.

Each profile is one persistent identity: its own storage, its own proxy exit,
its own ad-blocking DNS resolver and its own frozen fingerprint. A website sees
a coherent, ordinary Windows 11 machine, with its own region, exit and storage.

For people who manage several accounts they own or are authorised to run and do
not want those accounts cross-linked by browser fingerprint or IP.

- Repository: <https://github.com/derlocke-ng/kiwi-fox>
- License: GPL-3.0-or-later. Browser engine: [Camoufox](https://github.com/daijro/camoufox)
  (MPL-2.0), pinned and fetched at setup time.

## Install

```sh
kiwi install kiwi-fox      # or: ./install.sh install
kiwi-fox setup             # images, browser engine, blocklists (first run only)
```

`setup` is a separate step on purpose: it builds container images and downloads
a ~630 MB browser engine, which should not happen silently during an install.

## Use

```sh
kiwi-fox new work socks5://user:pass@host:port   # probes the exit, draws a matching identity
kiwi-fox list
kiwi-fox run work                                # or use the GUI
kiwi-fox check                                   # is every profile still coherent?
kiwi-fox-gui                                     # "Kiwi-Fox" in your app grid
```

## What a new profile is

The commonest machine there is, because rare values are what detectors flag: a
1920×1080 screen, the fonts every Windows 11 has and no others, and this
machine's own graphics card as Firefox on Windows words it. Region, language,
timezone and voices follow the exit. Everything can be changed afterwards
(`kiwi-fox set work --country SE`, `--screen`, `--font-add`, `--user-agent`, …);
edits are checked together and nothing is saved unless the result is coherent.

## How a profile is isolated

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder: adds proxy credentials, the browser never sees them
                    dnscrypt-proxy: ad-blocking, upstream through the same exit
browser container   joins that namespace — no routing table of its own
```

The kill switch is the absence of a route, not software that has to notice. If
the gateway dies the profile simply loses connectivity.

The exit itself comes from a [provider plugin](plugins.md) (Tor, a commercial
VPN, 9proxy, Mysterium) or any SOCKS5/HTTP endpoint you supply.

## What it does not do

It does not promise "undetectable". Profiles are isolated for storage, IP and
every surface the engine can spoof, but **not** against hardware-level
cross-browser identifiers: the frame the GPU actually draws and hardware timing
come from the real machine and are the same for every profile on it. That limit
is measured and documented, not hidden (`docs/detection-notes.md`).

No automation, no bots, no bulk account creation. Interactive browsing only.

## Requirements

Rootless Podman, a Wayland session, Python 3.12+, GTK4 + libadwaita for the GUI,
and `secret-tool` for credential storage. On an NVIDIA machine, also
`nvidia-container-toolkit` with its CDI spec generated.
