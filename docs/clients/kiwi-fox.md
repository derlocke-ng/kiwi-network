# kiwi-fox

kiwi-fox gives you a separate browser for each client network you work in, and
for each account you manage. A browser profile for a client reaches that
client's web consoles through that client's connection and has no other way
out. You do not need a VPN connection on the host for it.

Each profile is one persistent identity. It has its own storage, runs one of
three browsers in a rootless Podman container (a container that runs as your
own user without root rights), and usually uses a [kiwi-proxy](kiwi-proxy.md)
exit. An exit is a named upstream connection, such as a client's SOCKS5 proxy.
For each exit, kiwi-proxy runs a gateway. The gateway is a container whose only
route leads to that upstream, and it contains a DNS resolver that blocks
advertising domains.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Latest release: **v0.7.1**. It is in the [Kiwi catalog](../desktop/catalogs.md), user scope.
- The browsers, which kiwi-fox calls engines, are downloaded to your machine
  and never redistributed. Camoufox (MPL-2.0) is downloaded during setup.
  Firefox and Tor Browser are downloaded when you ask for them
  (`kiwi-fox engine fetch`), and their signatures are verified.

| Engine | What a page sees |
|---|---|
| **Camoufox** (default) | An ordinary Windows 11 machine with its own region, whose values all fit together. This fingerprint (the set of values that a page can read from a browser to recognise it again) is spoofed and does not change |
| **Firefox** | Unmodified Mozilla Firefox, which spoofs nothing. A page sees this machine's own values. The connection still goes through the profile's exit |
| **Tor Browser** | Unmodified Tor Browser, connected through an exit on the tor module. Each site gets its own circuit (its own path through the Tor network), and `.onion` names work |

kiwi-fox is for people who manage several accounts that they own or are
authorised to run, and who do not want these accounts to be linked to each
other through the browser fingerprint or the IP address.

## Install

```bash
kiwi install kiwi-fox      # brings kiwi-proxy along; or ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # or torbrowser: signature-verified
```

kiwi-fox needs rootless Podman, kiwi-proxy, Python 3.12+, GTK4 with
libadwaita, and `secret-tool`. It is made for a Wayland session. X11 works
too, but the isolation is weaker there. `gpg`/`gpgv` are needed to verify
Firefox and Tor Browser. With the proprietary NVIDIA driver, kiwi-fox also
needs `nvidia-container-toolkit` with its CDI spec.

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

With `--desktop-entry`, a profile gets its own entry in the app grid. Tags let
you group profiles.

## Profiles and exits

A profile does not own an exit. It refers to one, and several profiles can
refer to the same exit. Profiles on the same exit share its gateway, and with
it one network namespace, one exit IP address and one set of Tor circuits.
Identities that must not share an exit need different exits. A profile created
with `--no-proxy` has no gateway. Its browser container has a network of its
own and uses this machine's own connection. Nothing is sealed in that case,
which means that its traffic is not restricted to one route.

The browser container joins the gateway's network namespace. Every Linux
capability is dropped from it except `SYS_CHROOT`, which Firefox's own sandbox
needs. The container runs with `no-new-privileges`, and the engine is mounted
read-only.

## A Camoufox profile

A Camoufox profile presents the most common machine there is, because
detection systems flag values that are rare. It reports a 1920×1080 screen,
the fonts that every Windows 11 installation has and no others, and this
machine's own graphics card, named the way Firefox on Windows names it.
Region, language, time zone and voices are set to match the exit. You can
change all of this afterwards with `kiwi-fox set`, `kiwi-fox webgl` and
`kiwi-fox fonts`. A change is saved only if the profile stays coherent, which
means that its values still fit together.

## What it does not do

kiwi-fox does not promise that a profile is "undetectable". Profiles are
separated from each other in their storage, their IP address and every value
that the engine can spoof. They are **not** separated in identifiers that come
from the hardware and are the same in every browser. The frames that the GPU
actually draws and the timing of the hardware come from the real machine, so
they are the same for every profile on it. The file `docs/detection-notes.md`
in the repository documents what is measured.

kiwi-fox has no automation. It does not run bots and does not create accounts
in bulk. It is made for interactive browsing only.
