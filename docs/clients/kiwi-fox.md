# kiwi-fox

Isolated browser identities in rootless Podman.

Each profile is one persistent identity: its own storage and, usually, a
[kiwi-proxy](kiwi-proxy.md) exit with its sealed gateway and ad-blocking
resolver, in one of three browsers. For a client network, that means a browser
that reaches the client's web consoles through the client's exit, and nothing
else.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Latest release: **v0.7.1**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.
- The engines are fetched, never redistributed: Camoufox (MPL-2.0) at setup,
  Firefox and Tor Browser on request (`kiwi-fox engine fetch`), signature-verified.

| Engine | What a page sees |
|---|---|
| **Camoufox** (default) | a coherent, ordinary Windows 11 machine with its own region: a frozen, spoofed fingerprint |
| **Firefox** | stock Mozilla Firefox, spoofing nothing: this machine's own values, through the same sealed exit |
| **Tor Browser** | Tor Browser, unmodified, through an exit on the tor module, with a circuit per site and `.onion` names |

kiwi-fox is for people who manage several accounts they own or are authorised
to run, and who do not want those accounts cross-linked by browser fingerprint
or IP.

## Install

```bash
kiwi install kiwi-fox      # brings kiwi-proxy along; or ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # or torbrowser: signature-verified
```

It needs rootless Podman and kiwi-proxy, a Wayland session (X11 works with a
weaker boundary), Python 3.12+, GTK4 + libadwaita, `secret-tool`, and
`gpg`/`gpgv` to verify Firefox and Tor Browser. On the proprietary NVIDIA
driver, it also needs `nvidia-container-toolkit` with its CDI spec.

## Use

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # an exit, defined once, in kiwi-proxy
kiwi-fox new work --exit client-a     # a profile on it: probes it, draws a matching identity
kiwi-fox new plain --no-proxy         # this machine's own connection, nothing sealed
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # or the app
kiwi-fox stop work
kiwi-fox check                        # is every profile still coherent?
kiwi-fox selfcheck work               # measure what pages see, then audit it
kiwi-fox-gui                          # "Kiwi Fox" in the app grid
```

`--desktop-entry` puts a profile in the app grid, and tags group profiles.

## Profiles and exits

A profile references an exit, and exits are shared: profiles on one exit share
its gateway (one namespace, one exit IP, one set of Tor circuits). Identities
that must not share an exit take different exits. With `--no-proxy` there is no
gateway: the browser container has a network of its own on this machine's
connection, and nothing is sealed.

The browser container joins the gateway's namespace with every capability
dropped except `SYS_CHROOT` (Firefox's own sandbox needs it). It runs with
`no-new-privileges`, and the engine is mounted read-only.

## A Camoufox profile

It is the commonest machine there is, because rare values are what detectors
flag: a 1920×1080 screen, the fonts every Windows 11 has and no others, and
this machine's own graphics card as Firefox on Windows words it. Region,
language, timezone and voices follow the exit. Everything can be changed
afterwards (`kiwi-fox set`, `kiwi-fox webgl`, `kiwi-fox fonts`), and edits are
saved only if the result stays coherent.

## What it does not do

It does not promise "undetectable". Profiles are isolated for storage, IP and
every surface the engine can spoof, but **not** against hardware-level
cross-browser identifiers: the frames the GPU actually draws and hardware timing
come from the real machine and are the same for every profile on it. The
repository's `docs/detection-notes.md` documents what is measured.

There is no automation: no bots and no bulk account creation. It is for
interactive browsing only.
