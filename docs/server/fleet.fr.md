# Le fichier fleet

`fleet.yaml` décrit chaque machine que kiwi-server construit. Il a deux clés :
`defaults`, qui s’applique à chaque hôte, et `hosts`, avec une entrée par machine.
Tout ce qu’un hôte règle remplace les valeurs par défaut. `kiwi-server init` écrit
un point de départ commenté, et la référence complète est
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Un hôte a une **cible** (target : ce qui est installé) et un **rôle** (role : ce
qu’il devient) :

- `target` : `coreos`, `ucore` (par défaut) ou `debian`. Voir [Machines](machines.md).
- `role` : `bare` (par défaut), `master` ou `node`. Voir [Rôles](roles.md).

## Exemple { #example }

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya devient papaya.home ; les services sont cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # EFFACÉ par l’ISO sans demander
  admin:
    user: core
    ssh_keys: [~/.ssh/id_ed25519.pub]
  updates: { enabled: true, days: [Sun], time: "03:30", length_minutes: 90 }
  install: { on_done: poweroff }
  tls: { auto: true, ca_dir: secrets/ca, name_constraints: [home] }
  debian: { release: trixie, partitioning: lvm }

hosts:
  sorbet:                              # le master, un VPS Debian
    role: master
    target: debian
    disk: /dev/vda
    master:
      vpn-client:
        vpn_provider: mullvad
        wireguard_private_key: "<from your Mullvad WireGuard config>"
        wireguard_addresses: 10.66.1.2/32
        server_countries: Germany
      vpn-server:
        wg_host: vpn.example.org     # ce à quoi se connectent les clients et les nodes

  lychee:                                # un node gateway
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # le côté LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # un node cloud sur uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # pour le premier compte ; désactivez-le ensuite
```

Il n’y a aucun mot de passe de service dedans. Chaque mot de passe que vous omettez
est généré à partir de `secrets/seed`, et
`kiwi-server secrets show fleet.yaml papaya` les affiche. Les configurations
WireGuard des nodes n’y sont pas non plus nommées : `kiwi-server enroll` écrit
`secrets/<hostname>.conf`, que chaque node trouve tout seul, et l’adresse de
maillage du node y est lue.

## Valeurs par défaut { #defaults }

| Clé | Par défaut |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | aucune ; obligatoire pour `build`, doit commencer par `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false` ; donnez un `password_hash` pour la console |
| `network` | `dhcp: true` ; statique avec `address` (CIDR), `gateway`, `dns`, ou un `iprange` qui attribue les adresses dans l’ordre du fichier |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (ou `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | les anneaux Tang auxquels lier le disque (voir [Exploitation](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | où le répertoire de la fleet est sauvegardé (`hosts: []`, `keep: 10`) |
| `vps` | `server:` un id, un nom ou un surnom de serveur netcup |

## Comment les réglages se combinent { #how-settings-combine }

- Les hôtes remplacent les valeurs par défaut **clé par clé**. Les listes
  `admin.ssh_keys`, `debian.packages`, `debian.kernel_arguments` et les listes
  `coreos.*` s’*ajoutent* au contraire aux valeurs par défaut.
- Un rôle à modules garde ses réglages dans un bloc qui porte le nom du rôle
  (`master:`, `node:`) : d’abord les **réglages de la stack**, puis **un bloc par
  module**.
- `modules:` dans ce bloc **remplace** la liste de modules du preset. Les modules
  obligatoires sont ajoutés d’eux-mêmes.
- Les **réglages de fichiers** (certificats, configurations) sont des chemins
  relatifs au fichier fleet. Leur contenu est intégré au script de rôle de l’hôte.
- Un réglage donné sans valeur signifie la valeur par défaut. Une clé mal
  orthographiée est une erreur, accompagnée d’une suggestion.

## Réglages de la stack { #stack-settings }

| Réglage | Par défaut | Remarques |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` ou `minimal` |
| `runtime` | `podman` | quadlets podman ; `docker` lance docker compose |
| `auto_update` | `registry` | `podman auto-update` hebdomadaire ; `off` : les images changent avec une application |
| `docker_dir` | `/home/user/docker` | la stack et ses données |
| `service_user` | l’utilisateur admin | possède les répertoires de données |
| `vpn_ip` | depuis la configuration WireGuard | l’adresse de maillage de la machine |
| `master_ip` | depuis la fleet | l’adresse de maillage du master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | à mesurer avec `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | depuis la route par défaut | l’interface LAN |
| `daily_vpn_restart` | `07:00` | vide : jamais |
| `weekly_update` | `Sun *-*-* 00:00` | vide : jamais |

`kiwi-server roles -v` et `kiwi-server modules -v` listent chaque réglage avec sa
valeur par défaut.

## Vérifier ce que vous avez écrit { #checking-what-you-wrote }

```bash
kiwi-server validate fleet.yaml          # erreurs et avertissements
kiwi-server show fleet.yaml papaya          # one host's effective config, secrets masked
```

kiwi-server vérifie aussi le domaine : `.local` est refusé, `.lan` et les domaines
de premier niveau publics reçoivent un avertissement (voir
[DNS](../network/dns.md#names-servicehostnamehome)).

## Reprendre une machine v1 { #taking-over-a-v1-machine }

Une machine qui faisait tourner l’une des anciennes stacks v1 peut être reprise
sans perte de données. Le runtime par défaut est désormais podman, et le script de
rôle n’arrête pas les conteneurs docker. Donc, soit vous réglez `runtime: docker`,
soit vous arrêtez d’abord l’ancienne stack. Réglez ensuite `docker_subnet` sur ce
qu’utilisait l’ancienne stack, et renommez les répertoires de données selon les
noms des modules (`kmvpn-server` → `km-vpn-server`, `knvault` → `kn-vault`, …).
Les conteneurs gardent leurs adresses et wg-easy garde ses pairs.
