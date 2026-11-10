# Machines: install, apply, update

## Targets

| Target | What gets installed | Install media |
|---|---|---|
| `coreos` | Fedora CoreOS, stable stream | the stock live ISO, customized with the host's Ignition (Butane `fcos` 1.6.0); no network needed for the install |
| `ucore` | Fedora CoreOS that rebases itself onto a `ghcr.io/ublue-os/ucore*` image (`ucore-minimal`, `ucore`, `ucore-hci`, with `-nvidia` / `-zfs`), like uCore's own autorebase example | as for CoreOS, plus the autorebase units |
| `debian` | Debian stable (trixie), amd64 | the stock netinst with the preseed in its initrd, so it answers from the first question on, and the host's files under `/kiwi-server`; BIOS and UEFI boot kept |

The admin user gets passwordless sudo everywhere. SSH takes keys only unless you
set `ssh_password_auth: true`.

## Install media

```bash
kiwi-server build fleet.yaml gate      # → output/gate/gate.iso
sudo dd if=output/gate/gate.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- An ISO installs to `disk:` **without asking** and then **powers the machine
  off** (`install.on_done: poweroff`, or `reboot`). Label your sticks.
- By default the media carry the **base system only**: hostname, network, admin
  user and keys, update policy. None of the stack's secrets are on them. The
  role comes later with `apply`.
- `--offline` puts the whole role and its secrets on the ISO, for a machine that
  SSH cannot reach. Whoever holds that ISO holds those secrets.
- The live installer shows the disks (`lsblk`) and has a shell with the fleet's
  console password and keys.

## Apply

```bash
kiwi-server apply fleet.yaml sh3                         # by name, address or mesh address
kiwi-server apply fleet.yaml sh3 --ssh core@192.168.1.25 # the first time, by address
```

`apply` re-renders the host and sends its role script over SSH to
`/var/lib/kiwi-server/role.sh`. It runs the script as root, then binds the disk
to its Tang rings and, on a master, saves the WireGuard state with the fleet's
secrets. On an encrypted Debian machine, the first apply replaces the one-time
install key. SSH uses the fleet's own key and checks host keys against
`secrets/known_hosts`. `apply` and `status` find a machine by its name, static
address, the master's public address or its mesh address, but only addresses
whose host key is on record.

For a module role, the script hands the stack to `kiwi-stack`:

1. It installs or enables podman 4.4+ (on Debian with `netavark`,
   `aardvark-dns` and `catatonit`) or docker, and the service user.
2. It loads kernel modules and sets sysctls. With Pi-hole, aardvark-dns moves to
   port 5533 and the host resolves through the stack's Pi-hole. It also trusts
   the mesh in firewalld.
3. It refuses a stack rendered from a different seed. It unpacks the stack into
   `docker_dir`, installs the quadlets in `/etc/containers/systemd` and the host
   units, and removes what a module that left had installed.
4. It opens the stack's ports in firewalld or ufw, if one of them is active.
5. It pulls every image, then starts `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. It runs `kiwi-stack verify`: every container must be running, or the apply
   fails and says which step failed.

Applying the same render again changes nothing, and a new render replaces what
changed. A re-apply does restart every container of the stack.

## First boot

`kiwi-role.service` runs `/var/lib/kiwi-server/role.sh` once, after the
network is up (waiting up to 120 seconds for DNS). `role.done` is written only
once every container runs. A failure leaves `/var/lib/kiwi-server/role.failed`
(the step and the command) and is retried on the next boot. The log is
`/var/log/kiwi-server-role.log`. On uCore the role waits until the image is
signed. `sudo bash /var/lib/kiwi-server/role.sh --force` runs it again.

## Updates

Updates install continuously. The **reboot** into them only happens inside your
window (`updates.days`, `time`, `length_minutes`, local time):

| Target | Installs updates | Reboots |
|---|---|---|
| `coreos` | Zincati, continuously | only in the window (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` stages them | `kiwi-staged-reboot.timer` in the window |
| `debian` | unattended-upgrades, daily | `kiwi-reboot-if-required.timer` in the window, when one is required |

`updates.days: []` means any day, and `updates.enabled: false` turns it all
off. An encrypted machine whose Tang ring has to be forwarded in does not
reboot by itself.

The containers have their own schedule: a weekly `kiwi-stack update` (Sunday
00:00) runs `podman auto-update` while `auto_update: registry` is set. A daily
restart of the VPN client at 07:00 gives a fresh exit address.

## On the machine: `kiwi-stack`

```bash
sudo kiwi-stack status          # containers, host units, verify
sudo kiwi-stack verify          # every container running?
sudo kiwi-stack logs [service]  # from the journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # the VPN client and every container in its namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # with the backup module
sudo kiwi-stack apply DIR       # a stack bundle, without a role script
```

The stack lives in `docker_dir` (default `/home/user/docker`), and its settings
in `/etc/kiwi-server/stack.env`. The units are `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` and `kiwi-stack-update.timer`, plus any a module
adds.

## What a render produces

`output/<host>/` contains:

| File | What |
|---|---|
| `<host>.role.sh` | the role as one script: settings, the stack (embedded), the kiwi-stack command and library, and the role body. Mode 0600 |
| `<host>.stack/` | the stack bundle, for review: `docker-compose.yml`, `quadlets/`, module configs, host units and `stack.sh`. `kiwi-stack apply` can install it by hand |
| `<host>.bu`, `<host>.ign` | CoreOS and uCore: Butane and Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian: the preseed and the files it copies in |
| `<host>.iso` | the unattended installer |
