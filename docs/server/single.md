# One machine, without a fleet

kiwi-server manages a whole fleet of machines. If you only want to run a stack
on a single machine, you do not need it. A stack is the set of containers and
services that a machine runs. kiwi-server is built from two smaller tools, and
you can use them on their own:

| Repository | What it is |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | The modules and their renderer. It reads **one machine file and writes a stack bundle**, a directory with the rendered configuration of the machine's stack. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | The part that runs on the machine. It consists of the `kiwi-stack` command and a library, which put a bundle onto a CoreOS, uCore or Debian machine and keep it running. v0.5.0, GPL-3.0-or-later |

Use the two tools when you want a stack on one machine without the rest of
kiwi-server. Examples are a node that you set up by hand, a module that you
are developing, or a machine that renders its own stack. kiwi-server contains
a copy of both tools, each pinned to a release tag. A machine ends up
identical whether you set it up with kiwi-server or with the two tools, and
both ways derive the same secrets from the same seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Render a machine

The commands below install kiwi-modules, create a seed and render the example
machine file into a bundle. The last line copies the bundle to the machine and
applies it there.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # edit: TLS files, the WireGuard config
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules needs Python 3 with PyYAML and Jinja2. `kiwi-modules modules -v`
lists every module and setting, and `kiwi-modules profiles` lists the roles
and their presets.

A machine file describes one machine, as in this example:

```yaml
# a cloud node
name: sh3
domain: home
target: ucore
timezone: Europe/Berlin
admin: { user: core }
role: node
node:
  preset: cloud
  cloud: { collabora: true, talk: true }
  reverse-proxy:
    tls_fullchain: secrets/sh3-fullchain.pem
    tls_privkey: secrets/sh3-privkey.pem
dns_records:                    # the network's names
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # trusted inside the containers and on the host
seed: secrets/seed              # generated passwords derive from it
```

kiwi-modules has no certificate authority of its own. When you render a
machine without kiwi-server, you therefore have to provide the TLS certificate
and key files yourself. If the machine file names no WireGuard config,
kiwi-modules looks for it at `secrets/<hostname>.conf`.

## Put it on the machine

On the machine, install kiwi-stack and apply the bundle:

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack and its library
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack needs bash and systemd. It also needs the container runtime that
the bundle's `runtime` names, which is either podman 4.4+ with catatonit or
docker with the compose plugin. On Debian, kiwi-stack installs podman itself.

`apply` does the same with a stack as a kiwi-server role does (see
[Machines](machines.md#apply)), except that it does not set the hostname and
the time zone. You can repeat it, and applying the same bundle again changes
nothing. There is no rollback. To get data back, use `kiwi-stack restore` from
the backup module. To get an older configuration back, apply an older bundle.

Some names on the machine still say `kiwi-server`, for example
`/etc/kiwi-server/stack.env` and `/var/lib/kiwi-server/`. This is deliberate:
the Kiwi tools rely on these names, so they are not renamed.
