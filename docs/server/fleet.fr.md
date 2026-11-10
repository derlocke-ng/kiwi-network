# Le fichier fleet

Le fichier fleet, `fleet.yaml`, est l’endroit où vous décrivez toutes les
machines de votre Kiwi Network. Pour chaque machine, il indique le système
d’exploitation à installer, l’usage de la machine et la configuration de ses
services. kiwi-server construit chaque machine à partir de cette description :
vous notez une fois ce que vous voulez, et vous n’avez aucune machine à
configurer à la main.

Le fichier comporte deux clés. `defaults` contient les réglages qui
s’appliquent à tous les hôtes, et `hosts` contient une entrée par machine. Un
réglage indiqué dans l’entrée d’un hôte remplace le même réglage des valeurs
par défaut. `kiwi-server init` écrit un fichier commenté dont vous pouvez
partir, et la référence complète se trouve dans
[examples/fleet.yaml](https://github.com/derlocke-ng/kiwi-server/blob/main/examples/fleet.yaml).

Chaque hôte a un **système cible** (`target`), c’est-à-dire le système
d’exploitation qui sera installé, et un **rôle**, c’est-à-dire la fonction que
la machine remplit ensuite.

- `target` vaut `coreos`, `ucore` (par défaut) ou `debian`. Voir [Machines](machines.md).
- `role` vaut `bare` (par défaut), `master` ou `node`. Voir [Rôles](roles.md).

## Exemple { #example }

Ce fichier fleet décrit trois machines. La première est le master, installé
sur un VPS Debian (un serveur virtuel loué) : c’est la machine à laquelle
toutes les autres se connectent. La deuxième est un node passerelle, qui fait passer le
trafic d’un réseau local par le VPN. La troisième est un node cloud, qui fait
tourner Nextcloud et Vaultwarden.

```yaml
defaults:
  target: ucore
  role: bare
  domain: home                       # papaya devient papaya.home ; les services sont cloud.papaya.home …
  timezone: Europe/Berlin
  disk: /dev/sda                     # EFFACÉ par l'ISO sans demander
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
        wg_host: vpn.example.org     # l'adresse à laquelle se connectent les clients et les nodes

  lychee:                                # un node passerelle
    role: node
    node:
      preset: gateway
      pub_iface: eth0                # le côté LAN
      downloader: { download_dir: /mnt/data/downloads }

  papaya:                               # un node cloud sous uCore HCI
    role: node
    ucore: { image: ghcr.io/ublue-os/ucore-hci:stable }
    node:
      preset: cloud
      vpn_ip: 10.8.0.25
      cloud: { nextcloud_datadir: /mnt/nvme_2tb/docker/knnc-data, memory_limit: 8192M }
      vault: { signups_allowed: true }   # pour le premier compte ; désactivez-le ensuite
```

L’exemple ne contient aucun mot de passe de service. kiwi-server génère tous
les mots de passe que vous n’indiquez pas, à partir du seed qui se trouve dans
`secrets/seed`, et `kiwi-server secrets show fleet.yaml papaya` affiche les
mots de passe de cet hôte.

L’exemple ne mentionne pas non plus les fichiers de configuration WireGuard des
nodes. `kiwi-server enroll` écrit la configuration d’un node dans
`secrets/<hostname>.conf`, et le client VPN du node l’y trouve sans qu’aucune
entrée soit nécessaire dans le fichier fleet. L’adresse mesh du node est lue dans ce même
fichier. Le mesh est le réseau WireGuard privé qui relie toutes vos machines,
et l’adresse mesh est l’adresse d’une machine dans ce réseau.

## Valeurs par défaut { #defaults }

Si une clé n’est définie ni dans votre bloc `defaults` ni dans un hôte,
kiwi-server utilise la valeur intégrée indiquée dans ce tableau.

| Clé | Valeur par défaut |
|---|---|
| `target` / `role` / `domain` | `ucore` / `bare` / `home` |
| `timezone` / `locale` / `keyboard` | `UTC` / `en_US.UTF-8` / `us` |
| `disk` | Aucune valeur par défaut. `build` en a besoin, et la valeur doit commencer par `/dev/` |
| `admin` | `user: core`, `ssh_keys: []`, `ssh_password_auth: false`. Définissez un `password_hash` si vous voulez vous connecter sur la console |
| `network` | `dhcp: true`. Pour une adresse statique, définissez `address` (en notation CIDR), `gateway` et `dns`. Ou bien définissez un `iprange`, dans lequel les hôtes reçoivent leurs adresses dans l’ordre où ils apparaissent dans le fichier |
| `updates` | `enabled: true`, `days: [Sun]`, `time: "03:30"`, `length_minutes: 90` |
| `install` | `on_done: poweroff` (ou `reboot`) |
| `tls` | `auto: true`, `ca_dir: secrets/ca`, `name_constraints: []` |
| `debian` | `release: trixie`, `partitioning: lvm` (`regular`, `lvm`, `crypto`), `encrypt: false` |
| `ucore` | `image: ghcr.io/ublue-os/ucore:stable` |
| `unlock` | Les anneaux Tang auxquels le disque est lié. Un anneau est un serveur Tang, qui permet à une machine chiffrée de déverrouiller son disque au démarrage (voir [Exploitation](operations.md#encrypted-disks-and-unlocking)) |
| `backup` | Les hôtes sur lesquels le dossier du fichier fleet est sauvegardé, et le nombre de sauvegardes conservées (`hosts: []`, `keep: 10`) |
| `vps` | `server:` l’identifiant, le nom ou le surnom d’un serveur netcup |

## Comment les réglages se combinent { #how-settings-combine }

- Un hôte remplace les valeurs par défaut **clé par clé** : il lui suffit donc
  de nommer les clés qui diffèrent. Les listes `admin.ssh_keys`,
  `debian.packages`, `debian.kernel_arguments` et les listes `coreos.*` font
  exception. Les entrées qu’un hôte met dans ces listes *s’ajoutent* à celles
  des valeurs par défaut au lieu de les remplacer.
- Les rôles construits à partir de modules, `master` et `node`, regroupent
  leurs réglages dans un bloc qui porte le nom du rôle (`master:` ou `node:`).
  Ce bloc contient d’abord les **réglages de la stack**, puis **un bloc par
  module**. La stack est l’ensemble des conteneurs qu’une machine fait tourner
  pour ses modules, et les réglages de la stack s’appliquent à tous ces
  conteneurs.
- Une liste `modules:` dans ce bloc **remplace** la liste de modules du preset.
  Un preset est une liste de modules prête à l’emploi. Les modules dont
  dépendent les modules listés sont ajoutés automatiquement.
- **Les réglages de type fichier**, par exemple des certificats ou des fichiers
  de configuration, s’indiquent par un chemin relatif au fichier fleet.
  kiwi-server copie le contenu de ces fichiers dans le script de rôle de
  l’hôte, c’est-à-dire le script qui configure la machine pour son rôle.
- Un réglage écrit sans valeur prend sa valeur par défaut. Si vous faites une
  faute de frappe dans une clé, kiwi-server signale une erreur et propose la
  clé que vous vouliez sans doute écrire.

## Réglages de la stack { #stack-settings }

Les réglages de la stack s’appliquent à toute la stack d’une machine. Vous les
écrivez directement dans le bloc du rôle.

| Réglage | Par défaut | Remarques |
|---|---|---|
| `preset` (node) | `gateway` | `gateway`, `cloud` ou `minimal` |
| `runtime` | `podman` | `podman` fait tourner les conteneurs sous forme de quadlets podman, c’est-à-dire d’unités systemd pour conteneurs. `docker` utilise docker compose |
| `auto_update` | `registry` | `registry` lance `podman auto-update` une fois par semaine. Avec `off`, les images des conteneurs ne changent que lorsque vous appliquez de nouveau la configuration de l’hôte |
| `docker_dir` | `/home/user/docker` | le dossier qui contient la stack et ses données |
| `service_user` | l’utilisateur admin | l’utilisateur propriétaire des dossiers de données |
| `vpn_ip` | d’après la configuration WireGuard | l’adresse mesh de la machine |
| `master_ip` | d’après le fichier fleet | l’adresse mesh du master |
| `mesh_subnet` | `10.8.0.0/16` | |
| `wg_mtu` / `bridge_mtu` | `1376` / `1500` | vous pouvez les mesurer avec `kiwi-server mtu` |
| `docker_subnet` | `172.64.0.0/24` master, `172.128.0.0/24` node | |
| `pub_iface` | d’après la route par défaut | l’interface réseau côté LAN |
| `daily_vpn_restart` | `07:00` | une valeur vide désactive le redémarrage quotidien |
| `weekly_update` | `Sun *-*-* 00:00` | une valeur vide désactive la mise à jour hebdomadaire |

`kiwi-server roles -v` et `kiwi-server modules -v` listent chaque réglage avec
sa valeur par défaut.

## Vérifier ce que vous avez écrit { #checking-what-you-wrote }

kiwi-server peut vérifier le fichier fleet pour vous et montrer ce qu’il en
déduit pour un hôte donné.

```bash
kiwi-server validate fleet.yaml          # erreurs et avertissements
kiwi-server show fleet.yaml papaya          # la configuration effective d'un hôte, secrets masqués
```

kiwi-server vérifie aussi le domaine. Il refuse `.local` et émet un
avertissement pour `.lan` et pour les domaines de premier niveau publics (voir
[DNS](../network/dns.md#names-servicehostnamehome)).

## Reprendre une machine v1 { #taking-over-a-v1-machine }

Vous pouvez intégrer à votre réseau une machine qui faisait tourner l’une des
anciennes stacks v1, sans perdre ses données. Le moteur de conteneurs par défaut
est désormais podman, et le script de rôle n’arrête pas les conteneurs docker qui
tournent encore. Il faut donc soit définir `runtime: docker`, soit arrêter
d’abord l’ancienne stack. Ensuite, donnez à `docker_subnet` le sous-réseau
qu’utilisait l’ancienne stack, et renommez les dossiers de données selon les
nouveaux noms de modules (`kmvpn-server` → `km-vpn-server`,
`knvault` → `kn-vault`, …). Les conteneurs gardent alors leurs adresses, et
wg-easy conserve ses pairs.
