# Targets, updates & first boot

## Targets

| Target | What gets installed | Install media |
|---|---|---|
| `coreos` | Fedora CoreOS, stable stream | the stock live ISO after `coreos-installer iso customize --dest-device <disk> --dest-ignition <host>.ign`. No network is needed for the install, and Ignition is embedded for the installed system |
| `ucore` | Fedora CoreOS that rebases itself onto a `ghcr.io/ublue-os/ucore*` image (`ucore-minimal`, `ucore`, `ucore-hci`, with `-nvidia` / `-zfs` variants), like uCore's own autorebase example | as for CoreOS, plus the autorebase units |
| `debian` | Debian stable (trixie) from the netinst image | the stock netinst with the preseed appended to the installer's initrd (so it answers from the first question on), boot menus that start the unattended entry after a second, and the host's files under `/kiwi-server`. `xorriso -boot_image any replay` keeps the original BIOS/UEFI boot setup |

Debian supports `partitioning: regular | lvm | crypto` (full-disk LUKS with
`encrypt: true` and a `passphrase:`). CoreOS and uCore take extra Butane
settings under `coreos:` (kernel arguments, services, `boot_device`, …).

The admin user gets passwordless sudo on every target. SSH is keys only unless
you set `ssh_password_auth: true`.

## Updates

Updates are fetched continuously on every target. The **reboot** into them only
happens inside your window (`updates.days`, `time`, `length_minutes`, in local
time).

| Target | Installs updates | Reboots |
|---|---|---|
| `coreos` | Zincati, continuously | only inside the window (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` stages them (the image's default) | `kiwi-staged-reboot.timer` reboots into a staged deployment in the window |
| `debian` | unattended-upgrades, daily | `kiwi-reboot-if-required.timer` reboots in the window when `/var/run/reboot-required` exists |

`updates.days: []` means any day, and `updates.enabled: false` turns all of it
off. The containers have their own schedule: the stack's weekly
`kiwi-stack update` (see below).

## First boot

`kiwi-role.service` is a oneshot that runs `/var/lib/kiwi-server/role.sh` as
root after the network is up. It never runs again once
`/var/lib/kiwi-server/role.done` exists.

- A failed run is retried on the next boot and shown on the console. The log is
  `/var/log/kiwi-server-role.log`. Follow it live with `journalctl -u kiwi-role -f`.
- On uCore the unit also waits for `/etc/ucore-autorebase/signed`, so the role
  always runs on the final image.
- `sudo bash /var/lib/kiwi-server/role.sh --force` runs it again by hand.

For a module role, the script then applies the stack:

1. it creates the service user, installs or enables docker, loads kernel
   modules and applies sysctls, and frees port 53 from systemd-resolved when the
   `dns` module is present;
2. it unpacks the stack into the stack directory (`docker_dir`, default
   `/home/user/docker`) and installs the host units;
3. it installs `/usr/local/bin/kiwi-stack` and `/etc/kiwi-server/stack.env`;
4. it opens the stack's ports in firewalld or ufw, if one of them is active;
5. it enables `kiwi-stack.service` (compose up at boot), the daily VPN restart
   and weekly update timers, and the module's own host units.

## On the machine: `kiwi-stack`

```bash
sudo kiwi-stack start         # compose up, routes into the mesh
sudo kiwi-stack stop
sudo kiwi-stack restart
sudo kiwi-stack update        # pull, restart, prune
sudo kiwi-stack status
sudo kiwi-stack logs
sudo kiwi-stack vpn-restart   # the VPN client and every container in its namespace
```

`kiwi-stack start` also routes the mesh subnet through the VPN client (through
the WireGuard server on a master), so the host and its containers reach every
other node.

## What a render produces

`output/<host>/` contains:

| File | What |
|---|---|
| `<host>.role.sh` | the role as one script: settings, embedded files (the rendered stack among them), the common library and the role body. Mode 0600, because it holds secrets |
| `<host>.stack/` | module roles: the rendered `docker-compose.yml`, the module configs (nginx.conf, post-rules.txt, gw.sh, start.sh, torrc, Pi-hole's records) and the host units, for review. The script carries a copy |
| `<host>.bu`, `<host>.ign` | CoreOS/uCore: Butane (fcos 1.6.0) and Ignition: admin user, hostname, static network, time zone, update policy, `kiwi-role.service`, uCore autorebase units |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: the preseed, and the files its late command copies in from `/cdrom/kiwi-server` |
| `<host>.iso` | the unattended installer |
| `README.txt` | the same, for that host |

## Toolchain

| Tool | Used for |
|---|---|
| `butane` | Butane → Ignition (`--strict`) |
| `coreos-installer` | downloading and verifying the Fedora CoreOS ISO, `iso customize` |
| `xorriso`, `cpio`, `gzip`, `curl` | rebuilding and downloading the Debian netinst |

These run natively when installed, and otherwise in a small podman or docker
image (`kiwi-server toolchain build`). Inside the container a tool sees the
output and cache directories at the same paths, so nothing else changes.
`--toolchain native` or `--toolchain container` forces one or the other.
