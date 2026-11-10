# Operations

Day-two work on a running fleet, all from the operator's machine.

## Status

```bash
kiwi-server status fleet.yaml            # every host
kiwi-server status fleet.yaml sh3        # one
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
kiwi-server secrets show fleet.yaml sh3 [setting]   # a host's generated passwords
```

`secrets init` keeps one key in the GNOME Keyring and shows a **recovery key**
once. While the store is open, anything running as you can read it.

## Backing up the fleet itself

After every successful render or build, the fleet directory is encrypted
(AES-256 with PBKDF2, 600,000 iterations) and copied to the nodes listed in
`backup.hosts`, which keep the newest ten. On a fresh machine:

```bash
kiwi-server restore --from core@m1.home  # the fleet directory back
kiwi-server backup fleet.yaml --local /mnt/usb   # or a copy to a directory, any time
```

## Backing up the machines' data

Give a node the `backup-server` module (a restic REST server), and every
machine that should be backed up the `backup` module, pointing at it:

```yaml
m1:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [sh3.home, gate.home] }
sh3:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.m1.home }
```

Each night at 03:00 (±15 minutes) restic sends what each module asks to keep,
encrypted. Each machine can reach only its own repository, and only add to it.
So removing old snapshots runs from the operator's machine:

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # on the machine
kiwi-server prune fleet.yaml            # keep 7 daily, 4 weekly, 6 monthly
```

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

```bash
kiwi-server mtu fleet.yaml sh3 --write   # measure with don't-fragment pings, write wg_mtu
```

## netcup VPSes

```bash
kiwi-server vps login fleet.yaml         # device-flow login; the token goes to secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml gate  # wipe the server and install the host's ISO
```

`vps install` asks first unless you pass `--yes`. It refuses an ISO that
carries role secrets, a wrong `disk:`, and CoreOS disk encryption on less than
3500 MiB of RAM.
