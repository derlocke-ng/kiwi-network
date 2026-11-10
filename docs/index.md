---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">An open-source Linux environment that you run yourself: your servers, your devices and your desktop, connected in one private network. It installs itself, keeps itself up to date, makes a backup every night and can be rebuilt when something breaks.</p>

[How it works](network/index.md){ .md-button .md-button--primary }
[Set one up](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>The network</strong>
<span>Your servers and devices in one private WireGuard network. One server is visible from the Internet, and the others stay at home.</span>
<em>How it works →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>The tool that builds and runs the network: one file for all machines, automatic installation, backups and unlocking.</span>
<em>Set up a network →</em>
</a>

<a href="server/modules/">
<strong>Modules</strong>
<span>The 20 services a machine can run, from WireGuard and Pi-hole to Nextcloud, Vaultwarden, backups and Immich.</span>
<em>What a node can run →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>With kiwi-framework a community runs its own hub, with an open marketplace, a feed and chat, and no central platform.</span>
<em>Community hubs →</em>
</a>

<a href="desktop/">
<strong>The desktop</strong>
<span>A Fedora Atomic workstation with apps from git: a VPN kill switch, isolated connections for client networks, setup and sync.</span>
<em>Desktop apps →</em>
</a>

<a href="project/status/">
<strong>Status</strong>
<span>Every repository with its current release and what is still missing.</span>
<em>Current state →</em>
</a>

</div>

## The idea

The Internet is a rough place, and looking after your own servers is work that
never ends. Kiwi Network does that work for you. You describe your machines in
one file, and the routine jobs run automatically. Break-ins, failed disks and
lost machines are planned for from the start.

- **Automatic installation.** Every machine is installed without anyone at the
  keyboard: from its own install image, or directly on a rented server through
  the hosting provider's API. netcup is supported today, and more providers are
  [planned](server/roadmap.md#more-hosters-and-network-boot).
- **Automatic updates.** Updates are installed automatically. A machine only
  restarts during the hours you have allowed.
- **A backup every night.** Each machine sends an encrypted backup to a backup
  server of your own. It can add to its backups but cannot delete them, so an
  intruder cannot wipe them. The fleet file and its secrets are backed up too.
- **Recovery when it matters.** Disks are encrypted. Machines unlock them on
  their own when they start, or you unlock them from a distance. A machine that
  has to be rebuilt gets its setup from the fleet file and its data from the
  backup.

## The machines

Every machine has a role, which decides what it does in the network.

| Role | What the machine does |
|---|---|
| `master` | The only machine that can be reached from the Internet. It runs the WireGuard server, sends outgoing traffic through a VPN provider or directly, and provides DNS with Pi-hole, Tor and the admin pages. It can also run a nostr relay and a hub. |
| `node` · `gateway` | Sends a home or office network through the VPN, with Pi-hole as its DNS and DHCP server, a download station and SFTP. |
| `node` · `cloud` | Runs Nextcloud with Collabora, and Vaultwarden. |
| `node` · `minimal` | Has only the connection to the network and nginx. You add the modules you want, for example backups, Tang, Immich, Paperless-ngx or OpenCloud. |
| `bare` | Has only the base system. |

Masters are named after fruit dishes (sorbet, crumble, compote), and nodes after
fruits (papaya, lychee, quince). The master is the only machine that has to be
reachable from the Internet. By default it has one open port: WireGuard, on UDP
51820.

```bash
kiwi install kiwi-server            # or from a clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # an unattended ISO per machine
kiwi-server apply fleet.yaml papaya # the role, over SSH
```
