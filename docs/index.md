---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Your own private network: a master at the gate, nodes behind it, every machine yours. Built from one file, with one door to the Internet.</p>

[How it works](network/index.md){ .md-button .md-button--primary }
[Build one](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>The network</strong>
<span>One master, many nodes, one WireGuard mesh. Client groups, a double-hop exit, DNS and certificates of your own.</span>
<em>How it works →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>The fleet file, install ISOs, apply over SSH, enrolment, backups, unlocking. CLI and GTK app.</span>
<em>Build a network →</em>
</a>

<a href="server/modules/">
<strong>Modules</strong>
<span>All 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, backups, Tang, Immich, Paperless-ngx and more.</span>
<em>What a node can be →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>kiwi-framework: open markets, feeds, chat and sharing on nostr, sealed in the browser. Armory is the first.</span>
<em>Hubs, not platforms →</em>
</a>

<a href="desktop/">
<strong>The desktop</strong>
<span>kiwi-updater and the apps for Fedora Atomic: kill switch, sealed exits for client networks, setup, sync.</span>
<em>Apps from git →</em>
</a>

<a href="project/status/">
<strong>Status</strong>
<span>Every repository, its release and its known gaps, described as they are.</span>
<em>Where things stand →</em>
</a>

</div>

## The idea

Kiwi Network is a fully automated Linux environment to live and work in:
secure, sound and safe for a harsh online life. Your machines look after
themselves.

- **They install themselves.** An unattended ISO per machine, or straight onto
  a rented server through the hoster's API (netcup today, more
  [planned](server/roadmap.md#more-hosters-and-network-boot)).
- **They keep themselves current.** Updates install continuously, and reboots
  wait for the window you set.
- **They back themselves up.** Every night, encrypted and append-only, to
  backup nodes of your own. The fleet file and its secrets are backed up too.
- **They get back up.** Encrypted disks unlock through Tang, or remotely when
  something is wrong, and a rebuilt machine comes back from the fleet file and
  its backup.

## The machines

| Role | What the machine becomes |
|---|---|
| `master` | the gate: WireGuard, a double-hop or direct exit, Pi-hole, Tor, the admin pages, and optionally a nostr relay and a hub |
| `node` · `gateway` | a LAN through the VPN, with Pi-hole as DNS and DHCP, a download station and SFTP |
| `node` · `cloud` | Nextcloud with Collabora, and Vaultwarden |
| `node` · `minimal` | the tunnel and nginx, for modules of your choice: backups, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | just the base system |

Masters are named after fruit dishes (sorbet, crumble, compote), and nodes after
fruits (papaya, lychee, quince). The master is the only machine that has to be
reachable from the Internet, and by default it publishes one port: WireGuard,
UDP 51820.

```bash
kiwi install kiwi-server            # or from a clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # an unattended ISO per machine
kiwi-server apply fleet.yaml papaya # the role, over SSH
```
