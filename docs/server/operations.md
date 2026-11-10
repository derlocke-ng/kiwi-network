# Operations

Day-two work on a running fleet, all from the operator's machine.

## Status

```bash
kiwi-server status fleet.yaml            # every host
kiwi-server status fleet.yaml papaya        # one
```

Each machine reports over SSH (read-only): its role, its stack, problems (a
failed role, a stopped container), its disks and whether they are encrypted or
locked, its backups, and how long its certificates have left. A backup node also
reports its capacity. The Kiwi Server app shows the same thing on each host's
*Overview*.

## Secrets

Everything secret lives in `secrets/` next to the fleet file: the seed every
generated password derives from, the fleet CA, WireGuard configs, LUKS keys and
SSH host keys.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ becomes one age-encrypted file
kiwi-server secrets unlock fleet.yaml    # open it into memory (--for 8h; 0 keeps it open)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` keeps one key in the GNOME Keyring and shows a **recovery key**
once. While the store is open, anything running as you can read it.

## Backing up the fleet itself

After every successful render or build, the fleet directory is encrypted
(AES-256 with PBKDF2, 600,000 iterations) and copied to the nodes listed in
`backup.hosts`, which keep the newest ten. On a fresh machine:

```bash
kiwi-server restore --from core@lychee.home  # the fleet directory back
kiwi-server backup fleet.yaml --local /mnt/usb   # or a copy to a directory, any time
```

## Backing up the machines' data

Give a node the `backup-server` module (a restic REST server), and every
machine that should be backed up the `backup` module, pointing at it:

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Each night at 03:00 (within 15 minutes after) restic sends what each module asks to keep,
encrypted. Each machine can reach only its own repository, and only add to it.
So removing old snapshots runs from the operator's machine:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # on the machine
kiwi-server prune fleet.yaml            # keep 7 daily, 4 weekly, 6 monthly
```

A restore was tested node to node: papaya's backups onto lychee.

### Coming in the next release

!!! info "On the `several-servers` branch"
    This work is pushed to the `several-servers` branches of kiwi-modules and
    kiwi-server, but it isn't merged or released yet. Several servers and the
    automatic restore were tested on hardware. The VPN health check was not.

- **Several backup servers.** `backup.servers` takes a list, and each server
  gets a full copy of its own. If one server fails, only its copy is missed.
  A restore takes the freshest copy from whichever server has it, and
  `kiwi-stack snapshots` lists them server by server. The single `server`
  still works.
- **A rebuilt machine restores itself.** If a machine finds itself in the
  backups but has made none of them (a rebuild), it restores every module by
  itself before its first backup, then backs up as before (`backup.restore:
  auto`, the default). With `hold` it waits for `kiwi-stack restore` or
  `kiwi-stack backup --new`.
- **Pruning on a timer.** `kiwi-server prune fleet.yaml --every week` (or
  `day`) installs a systemd user timer on your computer, the only place that
  holds the keys that may delete. A missed run comes at the next login.
  `kiwi-server status` shows each backup copy, and warns when a backup node
  has not been pruned for three weeks.
- **A stuck commercial exit starts anew.** gluetun gets a health check. After
  five unhealthy minutes the container is killed, and its next start picks
  another server.

## Encrypted disks and unlocking

- **Debian** (`debian.encrypt: true`) installs with a one-time key you type at
  the first boot (`secrets/luks/<host>.once`). The first `apply` replaces it
  with `secrets/luks/<host>.key`, and a master also gets a fresh volume key.
  Losing that key file locks the disk, so keep the fleet backed up.
- **CoreOS / uCore** encrypt at install through Ignition (with about 4 GiB of
  RAM at first boot).
- **Tang rings** let encrypted machines unlock at boot without a person
  present. A node runs the `tang` module (each ring is one Tang server with its
  own keys, `infra` on port 7500 by default), and a host's `unlock:` block binds
  its disk to rings with a threshold.
- **SSH in the initramfs** (`unlock.ssh: true`: dropbear on Debian, dracut-sshd
  on CoreOS) uses its own restricted key, `secrets/unlock_ed25519`, which can
  only run the unlock.
- `kiwi-server unlock fleet.yaml <host>` forwards a ring into a machine waiting
  at boot, and `--manual` hands over the key itself. An `operator` ring is
  served from your own machine while it is needed. `vpn-server.unlock_relay`
  reaches machines behind NAT.

## Tunnel MTU

WireGuard adds its own headers, so a tunnel carries smaller packets than the
line beneath it, and a mobile path carries smaller ones still. A packet that is
too big for some link on the way gets dropped or split, and connections stall.
Kiwi handles this in three layers:

- **Two settings.** `wg_mtu` (default **1376**, a multiple of 16 because
  WireGuard pads to 16) is the MTU of gluetun, wg-easy's client configs and
  `wg0`. `bridge_mtu` (default **1500**) is the MTU of the stack network.
  `validate` refuses a `wg_mtu` whose padded packet plus 80 bytes of headers
  does not fit the bridge, and anything below 1280, the least IPv6 works with.
- **The MSS is clamped both ways** to `wg_mtu - 40`, in wg-easy and in the VPN
  client, so TCP never tries a segment that cannot pass.
- **TCP probes for itself.** The VPN client runs with
  `net.ipv4.tcp_mtu_probing=1` and `tcp_base_mss=1024`, so a connection that
  hits a path silently dropping big packets finds a size that works instead of
  hanging.

### Measuring a path: `kiwi-server mtu`

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # a node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # a device from secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # and write wg_mtu into the fleet file
```

The probe sends don't-fragment pings through the tunnel, from inside the
namespace that holds it. It measures a node from its own VPN client (whose
firewall drops pings coming in), and a device from the WireGuard server. It
starts with an ordinary ping, then tries every multiple of 16 from 1280 up and
reports the largest that arrives **whole**. While it pings, it reads the
kernel's reassembly counters, so a reply that was split on the way and put back
together does not count as fitting.

It also says what to set. For a **device**, that is the device's own `MTU =` in
its WireGuard config, and nobody else is affected. For a **node**, it is
`wg_mtu` on that node and on its master, which `--write` puts in the fleet file
(changing only those lines). A packet that is split only on its way out and put
back together by the far end cannot be seen from this end.

The defaults were measured on the test fleet. For a phone on mobile data, where
paths are often IPv6-only behind 464XLAT with nested encapsulation, measure the
phone itself and lower its own `MTU =` if the probe says so.

## netcup VPSes

```bash
kiwi-server vps login fleet.yaml         # device-flow login; the token goes to secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wipe the server and install the host's ISO
```

`vps install` asks first unless you pass `--yes`. It refuses an ISO that
carries role secrets, a wrong `disk:`, and CoreOS disk encryption on less than
3500 MiB of RAM.
