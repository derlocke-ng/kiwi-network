# Rôles

Un rôle est ce que devient une machine. Chaque rôle fonctionne sur les trois
cibles.

| Rôle | Ce que devient la machine | Modules |
|---|---|---|
| `bare` | le système de base : utilisateur admin, SSH, mises à jour automatiques | aucun |
| `master` | le **kiwi-master** : point d’entrée WireGuard avec le double saut, Pi-hole, Tor et les pages d’administration | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | un **kiwi-node** qui route un LAN à travers le VPN, avec Pi-hole, relais DHCP, une station de téléchargement et SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | un **kiwi-node** avec Nextcloud et Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | un **kiwi-node** à remplir avec les modules de votre choix | `vpn-client`, `reverse-proxy` |

`node-gw` et `node-cloud` fonctionnent toujours comme noms pour les presets
`gateway` et `cloud`.

Les rôles à modules produisent une **stack** : des quadlets podman par défaut
(docker compose avec `runtime: docker`), que `kiwi-stack` démarre et maintient en
marche. Voir [Modules](modules.md).

## `master` { #master }

Le preset modifie ces valeurs par défaut des modules :

- `vpn-client` : `vpn_provider: mullvad`, `mss_clamp: true`
- `dns` : `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` et `reverse-proxy` : `network_mode: vpn-server`

Pi-hole, Tor et nginx vivent donc dans l’espace de noms réseau du serveur WireGuard
et répondent à l’adresse de maillage du master. Les conteneurs s’appellent `km-…`
sur le réseau `knet-master` (`172.64.0.0/24`).

Un master peut ajouter `nostr-relay` et `hub` (un [hub pour les personnes](../people/hubs.md)),
`portainer` et `backup` à ses `modules:`. Le relais et le hub ne tournent que sur
des masters.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

Le preset choisit la liste de modules. `modules:` la remplace, et les modules
obligatoires s’ajoutent d’eux-mêmes. Les conteneurs s’appellent `kn-…` sur le
réseau `knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee fait tourner le module backup-server
```

Le preset gateway active la page web propre à Pi-hole (`expose_web_ui: true`) sur
`127.0.0.1:8080`. Le reverse proxy la sert de toute façon en TLS sur
`pihole.<hostname>`.

## Écrire un rôle { #writing-a-role }

Un rôle est un répertoire `roles/<name>/` avec un `role.yaml` et un `apply.sh`. Un
rôle à modules liste ses modules et inclut les réglages de stack partagés, et son
`apply.sh` tient en un appel :

```yaml
name: node-media
title: kiwi-node (media)
targets: [coreos, ucore, debian]
node_type: node
modules: [vpn-client, reverse-proxy, downloader, portainer]
settings_include: [common/stack]
module_defaults:
  downloader: { jdownloader: false }
```

```bash
ks_role_apply() { ks_stack_apply; }
```

Un rôle sans modules fait son propre travail dans `ks_role_apply()`, en utilisant
la bibliothèque `roles/common/lib.sh` (qui vient de kiwi-stack). Les réglages de
`role.yaml` deviennent `KS_ROLE_<KEY>`. Le script s’exécute en tant que root avec
`set -euo pipefail`. Les tests font le rendu de chaque rôle de l’arborescence et le
passent à shellcheck.
