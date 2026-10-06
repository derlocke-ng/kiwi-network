# kiwi-fox

Isolated Windows 11 browser identities in rootless Podman.

Each profile is one persistent identity: its own storage, its own proxy exit,
its own ad-blocking DNS resolver and its own frozen fingerprint. A website sees
a coherent, ordinary Windows 11 machine, with its own region, exit and storage.

It is for people who manage several accounts they own or are authorised to run,
and who do not want those accounts cross-linked by browser fingerprint or IP.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Latest release: **v0.1.3**. It is in the [Kiwi catalog](../desktop/catalogs.md).
- The browser engine is [Camoufox](https://github.com/daijro/camoufox) (MPL-2.0),
  pinned and fetched at setup time, never redistributed.

## Install

```bash
kiwi install kiwi-fox      # or: ./install.sh install from a clone
kiwi-fox setup             # images, browser engine, blocklists (first run only)
```

`setup` is a separate step on purpose: it builds container images and downloads
a ~630 MB browser engine, which should not happen silently during an install.
Run it again after an update. It rebuilds the images only when what they are
built from changed.

**Requirements:** rootless Podman, a Wayland session (X11 works with a weaker
boundary), Python 3.12+, GTK4 + libadwaita for the GUI, and `secret-tool` for
credential storage. On a machine whose desktop runs on the proprietary NVIDIA
driver, also `nvidia-container-toolkit` with its CDI spec generated.

## Use

```bash
kiwi-fox new work socks5://user:pass@host:port   # probes the exit, draws a matching identity
kiwi-fox list
kiwi-fox run work                                # or use the GUI
kiwi-fox stop work
kiwi-fox check                                   # is every profile still coherent?
kiwi-fox selfcheck work                          # measure what pages see, then audit it
kiwi-fox doctor                                  # including whether the browser gets a real GPU
kiwi-fox-gui                                     # "Kiwi-Fox" in your app grid
```

Endpoints can be `socks5://user:pass@host:port`, `http://…`, `https://…`, or the
vendor paste format `host:port:user:pass`. On kiwi-fox's `main` branch (not in
v0.1.3), an exit can also come from a [provider module](kiwi-fox-providers.md):
Tor, a VPN, 9proxy or Mysterium.

## What a new profile is

The commonest machine there is, because rare values are what detectors flag:
a 1920×1080 screen, the fonts every Windows 11 installation has and no others,
and this machine's own graphics card, worded the way Firefox on Windows words
it. Region, language, timezone and voices follow the exit. A Dutch profile is a
Dutch Firefox, with Dutch menus, `nl, en-US, en` as its languages and Dutch date
formats.

Everything can be changed afterwards, in the GUI under **Edit…** or on the
command line. Edits are checked together, and nothing is saved unless the result
is coherent:

```bash
kiwi-fox set work --screen 2560x1440 --cores 12
kiwi-fox set work --country SE --timezone Europe/Stockholm
kiwi-fox set work --language english          # an English Firefox used in that region
kiwi-fox webgl work --card "UHD 620"          # which graphics card the profile reports
```

## How a profile is isolated

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder: adds proxy credentials, the browser never sees them
                    dnscrypt-proxy: ad-blocking, upstream through the same exit
browser container   joins that namespace, with no routing table of its own
```

The kill switch is the absence of a route, not software that has to notice. If
the gateway dies, the profile simply loses connectivity.

## What it does not do

It does not promise "undetectable". Profiles are isolated for storage, IP and
every surface the engine can spoof, but **not** against hardware-level
cross-browser identifiers. The frames the GPU actually draws and hardware timing
come from the real machine, and they are the same for every profile on it. That
limit is measured and documented in the repository's `docs/detection-notes.md`,
not hidden.

There is no automation: no bots and no bulk account creation. It is for
interactive browsing only.
