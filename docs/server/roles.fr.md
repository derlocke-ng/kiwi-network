# Rôles

Le rôle d’une machine détermine à quoi elle sert dans votre Kiwi Network. Vous
attribuez un rôle à chaque hôte dans le fichier fleet, et kiwi-server configure
la machine en conséquence. Une machine peut être un simple système de base, le
master auquel se connectent tous les appareils et tous les nodes, ou un node
qui fait tourner vos services. Chaque rôle fonctionne sur les trois systèmes
cibles, c’est-à-dire les trois systèmes d’exploitation que kiwi-server sait
installer.

| Rôle | Ce que devient la machine | Modules |
|---|---|---|
| `bare` | Uniquement le système de base, avec un utilisateur admin, SSH et les mises à jour automatiques | aucun |
| `master` | Le **kiwi-master**. C’est le point d’entrée WireGuard du réseau, et il fait passer le trafic Internet du réseau par un VPN commercial (le double saut). Il fait aussi tourner Pi-hole, pour un DNS qui bloque les publicités, ainsi que Tor et les pages d’administration | `vpn-client`, `vpn-server`, `dns`, `tor`, `reverse-proxy` |
| `node`, preset `gateway` | Un **kiwi-node** qui fait passer le trafic d’un réseau local (LAN) par le VPN. Il fait aussi tourner Pi-hole, un relais DHCP, une station de téléchargement et SFTP | `vpn-client`, `dns`, `dhcp-relay`, `reverse-proxy`, `downloader`, `gateway`, `portainer`, `sftp` |
| `node`, preset `cloud` | Un **kiwi-node** qui fait tourner Nextcloud et Vaultwarden | `vpn-client`, `reverse-proxy`, `cloud`, `vault`, `portainer` |
| `node`, preset `minimal` | Un **kiwi-node** avec seulement les deux modules de base, auxquels vous ajoutez les modules de votre choix | `vpn-client`, `reverse-proxy` |

Le rôle `node` se décline en presets. Un preset est une liste de modules prête
à l’emploi. Les anciens noms de rôles `node-gw` et `node-cloud` fonctionnent
toujours et correspondent aux presets `gateway` et `cloud`.

Les rôles `master` et `node` sont construits à partir de modules, chaque module
étant un service. kiwi-server transforme les modules d’un hôte en une
**stack**, c’est-à-dire l’ensemble des conteneurs que fait tourner la machine.
Par défaut, la stack se compose de quadlets podman, des unités systemd qui
font tourner des conteneurs. Avec `runtime: docker`, c’est docker compose qui
la fait tourner. Sur la machine, `kiwi-stack` démarre la stack et la maintient
en marche. Voir [Modules](modules.md).

## `master` { #master }

Le rôle `master` modifie les valeurs par défaut suivantes des modules :

- `vpn-client` : `vpn_provider: mullvad`, `mss_clamp: true`
- `dns` : `network_mode: vpn-server`, `mullvad_socks: true`
- `tor` et `reverse-proxy` : `network_mode: vpn-server`

Avec ces réglages, Pi-hole, Tor et nginx partagent le namespace réseau du
serveur WireGuard. Un namespace réseau est l’ensemble des interfaces et des
adresses réseau que voit un conteneur. Les trois services sont donc
joignables à l’adresse mesh du master, c’est-à-dire son adresse dans le réseau
WireGuard privé. Sur un master, les conteneurs s’appellent `km-…` et sont
rattachés au réseau `knet-master` (`172.64.0.0/24`).

Un master peut aussi faire tourner `nostr-relay` et `hub` (pour un
[hub communautaire](../people/hubs.md)), ainsi que `portainer` et
`backup`. Pour les utiliser, ajoutez-les à la liste `modules:` du master. Le
relais et le hub ne tournent que sur un master.

```yaml
sorbet:
  role: master
  master:
    modules: [vpn-client, vpn-server, dns, tor, reverse-proxy, nostr-relay, hub]
```

## `node` { #node }

C’est le preset qui détermine les modules que fait tourner un node. Si vous
écrivez votre propre liste `modules:`, elle remplace celle du preset, et les
modules dont dépendent les modules listés sont ajoutés automatiquement. Sur un
node, les conteneurs s’appellent `kn-…` et sont rattachés au réseau
`knet-node` (`172.128.0.0/24`).

```yaml
papaya:
  role: node
  node:
    preset: cloud
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }   # lychee fait tourner le module backup-server
```

Le preset gateway rend aussi accessible la page web propre à Pi-hole, à
l’adresse `127.0.0.1:8080` sur le node (`expose_web_ui: true`). Que ce réglage
soit activé ou non, le reverse proxy sert cette page en TLS sous le nom
`pihole.<hostname>`.

## Écrire un rôle { #writing-a-role }

Vous pouvez écrire votre propre rôle. Un rôle est un dossier `roles/<name>/`
qui contient un `role.yaml` et un `apply.sh`. Un rôle construit à partir de
modules liste ses modules dans `role.yaml` et inclut les réglages communs de la
stack. Son `apply.sh` se réduit alors à un seul appel.

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

Un rôle sans modules fait lui-même son travail dans `ks_role_apply()`. Il peut
utiliser la bibliothèque `roles/common/lib.sh`, qui vient de kiwi-stack. Les
réglages déclarés dans `role.yaml` sont disponibles dans le script sous forme
de variables nommées `KS_ROLE_<KEY>`. Le script s’exécute en root avec
`set -euo pipefail`. Les tests du projet génèrent chaque rôle de
l’arborescence et le passent à shellcheck.
