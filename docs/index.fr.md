---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Votre propre réseau privé : un master à l’entrée, des nodes derrière lui, chaque machine à vous. Construit à partir d’un seul fichier, avec une seule porte vers Internet.</p>

[Comment ça marche](network/index.md){ .md-button .md-button--primary }
[En construire un](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Le réseau</strong>
<span>Un master, de nombreux nodes, un seul maillage WireGuard. Des groupes de clients, une sortie à double saut, un DNS et des certificats à vous.</span>
<em>Comment ça marche →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Le fichier fleet, les ISO d’installation, l’application via SSH, l’enrôlement, les sauvegardes, le déverrouillage. CLI et application GTK.</span>
<em>Construire un réseau →</em>
</a>

<a href="server/modules/">
<strong>Modules</strong>
<span>Les 20 : WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, sauvegardes, Tang, Immich, Paperless-ngx et d’autres.</span>
<em>Ce qu’un node peut être →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>kiwi-framework : marchés ouverts, fils, messagerie et partage sur nostr, scellés dans le navigateur. Armory est le premier.</span>
<em>Des hubs, pas des plateformes →</em>
</a>

<a href="desktop/">
<strong>Le bureau</strong>
<span>kiwi-updater et les applications pour Fedora Atomic : kill switch, sorties scellées pour les réseaux clients, installation, synchronisation.</span>
<em>Des applications depuis git →</em>
</a>

<a href="project/status/">
<strong>État</strong>
<span>Chaque dépôt, sa version et ses lacunes connues, décrits tels qu’ils sont.</span>
<em>Où en sont les choses →</em>
</a>

</div>

## Les machines { #the-machines }

| Rôle | Ce que devient la machine |
|---|---|
| `master` | l’entrée : WireGuard, une sortie à double saut ou directe, Pi-hole, Tor, les pages d’administration et, en option, un relais nostr et un hub |
| `node` · `gateway` | un LAN à travers le VPN, avec Pi-hole comme DNS et DHCP, une station de téléchargement et SFTP |
| `node` · `cloud` | Nextcloud avec Collabora, et Vaultwarden |
| `node` · `minimal` | le tunnel et nginx, pour les modules de votre choix : sauvegardes, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | uniquement le système de base |

Les masters portent des noms de desserts aux fruits (sorbet, crumble, compote), et les
nodes des noms de fruits (papaya, lychee, quince). Le master est la seule machine qui
doit être joignable depuis Internet et, par défaut, il publie un seul port : WireGuard,
UDP 51820.

```bash
kiwi install kiwi-server            # ou depuis un clone : ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # une ISO sans intervention par machine
kiwi-server apply fleet.yaml papaya # le rôle, via SSH
```
