# One machine, without a fleet

kiwi-server is built from two smaller tools, and you can use them on their own:

| Repository | What it is |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | The modules and their renderer: **one machine file in, a stack bundle out**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | The machine side: the `kiwi-stack` command and library that put a bundle onto CoreOS, uCore or Debian and keep it running. v0.5.0, GPL-3.0-or-later |

Use them when you want a stack on one machine without the rest: a node you set
up by hand, a module you are developing, or a machine that renders its own
stack. kiwi-server vendors both, pinned by tag. A machine set up either way ends
up identical, and both derive the same secrets from the same seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Render a machine

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # edit: TLS files, the WireGuard config
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

It needs Python 3 with PyYAML and Jinja2. `kiwi-modules modules -v` lists every
module and setting, and `kiwi-modules profiles` lists the roles and their
presets.

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

kiwi-modules has no certificate authority of its own, so a standalone render
needs the TLS certificate and key files. The WireGuard config is found at
`secrets/<hostname>.conf` when the machine file names none.

## Put it on the machine

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack and its library
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

It needs bash and systemd, plus podman 4.4+ with catatonit (or docker with
the compose plugin), whichever the bundle's `runtime` is. On Debian it installs
podman itself.

`apply` does what a kiwi-server role does with a stack (see
[Machines](machines.md#apply)), except setting the hostname and time zone. It is
repeatable: the same bundle again changes nothing. There is no rollback. Data
comes back with `kiwi-stack restore` from the backup module, and an older
configuration by applying an older bundle.

On the machine, the names still say `kiwi-server` (`/etc/kiwi-server/stack.env`,
`/var/lib/kiwi-server/`), by design: they are the contract between the two.
