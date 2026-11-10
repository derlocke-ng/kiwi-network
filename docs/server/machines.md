# Machines: install, apply, update

This page follows a machine from its entry in the fleet file to a running
system that updates itself. kiwi-server builds an install image that installs
the operating system without anyone at the keyboard. It then sets the machine
up for its role over SSH with the `apply` command. After that the machine
installs its updates by itself and reboots only at the times you allow.

## Targets

A target is the operating system that kiwi-server installs on a machine.

| Target | What gets installed | Install media |
|---|---|---|
| `coreos` | Fedora CoreOS, stable stream | The stock live ISO, customized with the host's Ignition configuration (Butane `fcos` 1.6.0). The install needs no network connection |
| `ucore` | Fedora CoreOS that then switches itself (rebases) to a `ghcr.io/ublue-os/ucore*` image. The images are `ucore-minimal`, `ucore` and `ucore-hci`, also with `-nvidia` / `-zfs`. The rebase works like uCore's own autorebase example | The same as for CoreOS, plus the autorebase units |
| `debian` | Debian stable (trixie), amd64 | The stock netinst image with the preseed (the file with the installer's answers) in its initrd, so that the installer has its answers from the first question on. The host's files are on the image under `/kiwi-server`. The image still boots with both BIOS and UEFI |

On every target the admin user can use sudo without a password. SSH accepts
only keys unless you set `ssh_password_auth: true`.

## Install media

The first command builds the install image (ISO) for one host. The second
command copies it to a USB stick.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- The ISO installs to the disk named in `disk:` **without asking**, which
  erases that disk. When the install is finished, it **powers the machine off**
  (`install.on_done: poweroff`, or `reboot` to restart it instead). Label your
  USB sticks.
- By default the install media contain the **base system only**. This is the
  hostname, the network settings, the admin user with the SSH keys and the
  update policy. The media contain none of the stack's secrets. The machine
  gets its role later, when you run `apply`.
- With `--offline`, the whole role and its secrets are put on the ISO. This is
  meant for a machine that cannot be reached over SSH. Anyone who has that ISO
  has those secrets.
- The live installer lists the machine's disks (`lsblk`) and has a shell, which
  accepts the fleet's console password and SSH keys.

## Apply

`apply` sets a machine up for its role over SSH.

```bash
kiwi-server apply fleet.yaml papaya                         # by name, address or mesh address
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # the first time, by address
```

`apply` first renders the host again, which means that it produces the host's
files from the fleet file anew. It then copies the host's role script over SSH
to `/var/lib/kiwi-server/role.sh`. The role script is the script that sets the
machine up for its role, and `apply` runs it as root. Afterwards `apply` binds
the disk to its Tang rings, which are servers that let an encrypted machine
unlock its disk at boot. On a master it also saves the WireGuard state together
with the fleet's secrets. On an encrypted Debian machine, the first apply
replaces the one-time key that was used for the install.

The SSH connection uses the fleet's own key and checks the machine's host key
against `secrets/known_hosts`. `apply` and `status` can reach a machine by its
name, its static address, the master's public address or its mesh address,
which is the machine's address in the private WireGuard network. They only use
an address whose host key is already on record.

For a role that is built from modules, the role script passes the stack to
`kiwi-stack`. The stack is the set of containers that the machine runs for its
modules. `kiwi-stack` then works through these steps:

1. It installs or enables podman 4.4+ or docker, and it makes sure that the
   service user exists. On Debian, podman comes with `netavark`,
   `aardvark-dns` and `catatonit`.
2. It loads kernel modules and sets sysctls. If the stack has Pi-hole, podman's
   aardvark-dns is moved to port 5533, and the host itself resolves names
   through the stack's Pi-hole. It also adds the mesh to the networks that
   firewalld trusts.
3. It refuses a stack that was rendered from a different seed. The seed is the
   secret from which the fleet's passwords are generated. Otherwise it unpacks
   the stack into `docker_dir`. It installs the quadlets, which are the systemd
   units for the containers, in `/etc/containers/systemd`, and it installs the
   host units. It also removes whatever a module that is no longer in the stack
   had installed.
4. It opens the stack's ports in firewalld or ufw, if one of them is active.
5. It downloads every container image and then starts `kiwi-stack.service`,
   which starts `kiwi-stack.target`.
6. It runs `kiwi-stack verify`, which checks that every container is running.
   If one is not, the apply fails and reports the step that failed.

If you apply the same render again, nothing on the machine is changed. If you
apply a new render, it replaces what has changed. Note that every apply
restarts all containers of the stack, even when nothing has changed.

## First boot

On the first boot, `kiwi-role.service` runs the role script
`/var/lib/kiwi-server/role.sh` once. It starts after the network is up and
waits up to 120 seconds for DNS. The file `role.done` marks the role as
finished, and it is written only when every container is running. If the script
fails, it leaves the file `/var/lib/kiwi-server/role.failed`, which names the
step and the command that failed, and the script is run again on the next boot.
The log is `/var/log/kiwi-server-role.log`. On uCore the role script waits
until the machine runs the signed uCore image. To run the script again by hand,
use `sudo bash /var/lib/kiwi-server/role.sh --force`.

## Updates

Machines install their operating system updates continuously. The **reboot**
that activates the updates only happens inside the time window you set with
`updates.days`, `time` and `length_minutes`, in local time.

| Target | Installs updates | Reboots |
|---|---|---|
| `coreos` | Zincati, continuously | only in the window (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` downloads and prepares (stages) them | `kiwi-staged-reboot.timer` in the window |
| `debian` | unattended-upgrades, daily | `kiwi-reboot-if-required.timer` in the window, if an update requires a reboot |

`updates.days: []` allows the reboot on any day, and `updates.enabled: false`
turns the updates and the reboots off. An encrypted machine does not reboot by
itself if it needs a Tang ring that someone has to forward to it by hand. It
would otherwise wait at boot until someone unlocked it.

The containers are updated on their own schedule. Once a week, on Sunday at
00:00, `kiwi-stack update` runs `podman auto-update`, as long as
`auto_update: registry` is set. The VPN client is restarted every day at 07:00,
which gives it a new exit address. The exit address is the public address
that websites see when traffic comes out of the VPN.

## On the machine: `kiwi-stack`

`kiwi-stack` is the command that you run on the machine itself to look at the
stack and to control it.

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

The stack's files are in `docker_dir` (by default `/home/user/docker`), and its
settings are in `/etc/kiwi-server/stack.env`. The systemd units are
`kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` and
`kiwi-stack-update.timer`, plus any units that a module adds.

## What a render produces

A render is what kiwi-server produces from the fleet file for one host. It is
written to `output/<host>/`, which then contains these files.

| File | What |
|---|---|
| `<host>.role.sh` | The role as a single script. It contains the settings, the embedded stack, the kiwi-stack command and library, and the role body. The file has mode 0600 |
| `<host>.stack/` | The stack bundle, so that you can review it. It contains `docker-compose.yml`, `quadlets/`, the modules' configuration files, the host units and `stack.sh`. You can also install it by hand with `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | On CoreOS and uCore, the Butane and Ignition configuration |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | On Debian, the preseed file and the files that it copies onto the machine |
| `<host>.iso` | The install image, which installs without anyone at the keyboard |
