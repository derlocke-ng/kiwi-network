# kiwi-server

kiwi-server est l’outil qui crée et administre un Kiwi Network. Vous décrivez
toutes vos machines dans un seul fichier, `fleet.yaml`, et kiwi-server les met
en place à partir de ce fichier. Vous n’avez donc pas à installer et configurer
chaque machine à la main.

Pour chaque hôte, kiwi-server produit une **ISO d’installation automatique**.
C’est une image d’installation qui installe Fedora CoreOS, uCore ou Debian sans
poser la moindre question, puis éteint la machine. kiwi-server **applique**
ensuite par SSH le rôle de la machine, ce qui en fait un `kiwi-master` ou un
`kiwi-node`. Par la suite, il continue de s’occuper de l’ensemble de vos
machines : il ajoute des clients WireGuard au réseau, relève l’état de chaque
machine, garde les secrets, sauvegarde le fichier fleet et ses secrets, et déverrouille les
disques chiffrés.

kiwi-server existe sous forme d’outil en ligne de commande (CLI),
`kiwi-server`, et d’application GTK4, **Kiwi Server**. Les deux s’installent
dans `~/.local` et n’ont pas besoin des droits root.

- Dépôt : [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Dernière version : **v2.42.0**. Elle est disponible dans le [catalogue Kiwi](../desktop/catalogs.md).
- kiwi-server s’appuie sur [kiwi-modules](single.md) v0.23.0, qui contient les
  modules et le programme qui génère leurs fichiers, et sur
  [kiwi-stack](single.md) v0.5.0, la partie qui tourne sur chaque machine. Une
  copie de chacun des deux est incluse dans kiwi-server (vendoring), épinglée
  sur un tag.

```
fleet.yaml + secrets/
   │  kiwi-server: merge defaults, work out DNS records, the master's mesh address,
   │  LAN neighbours, and a certificate from the fleet CA per host
   ▼
kiwi-modules renders each host's stack  →  compose file, podman quadlets, configs, units
   │
   ├─ build ─▶ <host>.iso      base system only: hostname, network, admin user, updates;
   │                            installs to the named disk WITHOUT ASKING, then powers off
   └─ apply ─▶ over SSH        role script + stack → kiwi-stack starts and verifies it
```

## Installation { #install }

```bash
kiwi install kiwi-server        # avec kiwi-updater
```

Vous pouvez aussi l’installer depuis une copie locale du dépôt : lancez
`./install.sh install`, puis `kiwi-server doctor`.

kiwi-server a besoin de Python 3.9+ avec PyYAML et Jinja2, ainsi que des
programmes `openssl` et `ssh`. Le coffre à secrets a besoin de `age`. Pour
construire des ISO, il vous faut `butane`, `coreos-installer` et `xorriso`, et
pour Debian également `cpio`, `gzip` et `curl`. Sous Silverblue ou Bluefin,
n’ajoutez pas ces paquets au système (layering). Construisez plutôt les outils
ISO sous la forme d’une seule image de conteneur :

```bash
kiwi-server toolchain build     # utilisée automatiquement quand les outils manquent
```

`qrencode` (pour `enroll --qr`), `shellcheck` et `docker compose` sont
facultatifs.

## De zéro à un réseau qui tourne { #from-nothing-to-a-running-network }

Les commandes ci-dessous vous mènent d’un dossier vide à un réseau en
fonctionnement, avec un master, un node et vos propres appareils :

```bash
kiwi-server init                          # un fleet.yaml commenté
$EDITOR fleet.yaml                        # hôtes, rôles, votre clé SSH, le disque d'installation
kiwi-server secrets init fleet.yaml       # facultatif : secrets/ dans un seul coffre chiffré avec age
kiwi-server validate fleet.yaml

# le master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   démarrez dessus ; il s'installe et s'éteint ; rallumez-le
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# chaque node : d'abord son client WireGuard, puis le support d'installation, puis le rôle
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# vos propres appareils
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # ce que signale chaque machine
```

Par défaut, une ISO d’installation ne contient **aucun des secrets de la
stack**. Elle ne contient que le système de base : le rôle et sa stack sont
envoyés ensuite à la machine par `apply`. Si une machine n’est pas joignable
par SSH, `build --offline` met au contraire tout le rôle et ses secrets sur
l’ISO. Ne téléversez pas une telle ISO dans l’espace de stockage d’ISO d’un
hébergeur, et supprimez-la après l’installation.

**Si vous ne voulez pas utiliser d’ISO du tout,**
`kiwi-server script fleet.yaml papaya` affiche le script destiné à une machine
que vous avez installée vous-même. Avec `--offline`, ce script contient tout le
rôle.

Sur un VPS de netcup, `kiwi-server vps install fleet.yaml sorbet` efface le
serveur et installe l’ISO par l’API de netcup : personne n’a besoin de se
mettre devant une console. netcup est pour l’instant le seul hébergeur pris en
charge. D’autres sont [prévus](roadmap.md#more-hosters-and-network-boot).

## Commandes { #commands }

| Commande | Ce qu’elle fait |
|---|---|
| `init [fleet.yaml]` | Écrit le fichier fleet d’exemple. `--domain` fixe le domaine, `home` par défaut. |
| `validate fleet.yaml [host…]` | Vérifie le fichier fleet. Elle génère chaque stack, afin de détecter aussi les erreurs dans les modules. |
| `list` / `show fleet.yaml <host>` | La première liste les hôtes et ce qui a été généré pour eux. La seconde affiche la configuration effective d’un hôte, secrets masqués. |
| `render fleet.yaml [host…]` | Écrit les scripts de rôle, les stacks et les configurations d’installation dans `output/<host>/`. |
| `build fleet.yaml [host…]` | Génère les fichiers, puis construit l’ISO. Par défaut, l’ISO ne contient que le système de base ; avec `--offline`, elle contient tout le rôle. |
| `script fleet.yaml <host>` | Affiche le script pour n’importe quelle machine. Avec `--offline`, le script contient tout le rôle. |
| `apply fleet.yaml <host…>` | Génère de nouveau les fichiers, envoie le rôle à la machine par SSH et l’y exécute (`--ssh USER@ADDR`, `--no-run`). |
| `status fleet.yaml [host…]` | Affiche ce que signalent les machines : rôle, stack, problèmes, disques, sauvegardes et certificats. |
| `enroll fleet.yaml <host\|name>` | Crée un client WireGuard sur le master, ou récupère un client qui existe déjà (`--group`, `--split`, `--qr`, `--address`, `--existing`). |
| `secrets init\|unlock\|lock\|status` | Gère `secrets/` sous la forme d’un seul fichier chiffré avec age, ouvert en mémoire quand vous le déverrouillez (`--for 8h`). |
| `secrets show fleet.yaml <host> [setting]` | Affiche les mots de passe générés pour un hôte. |
| `ca fleet.yaml` | Affiche la CA de votre réseau. |
| `mtu fleet.yaml <node\|device\|address>` | Mesure la MTU réelle d’un tunnel et indique la valeur à configurer (`--write`). |
| `openwrt fleet.yaml` | Écrit un script qui relie un routeur OpenWrt au mesh ([Routeurs](../network/routers.md)). |
| `backup` / `restore` / `prune` | Sauvegarde le dossier du fichier fleet sur des nodes, le restaure depuis ces nodes, et supprime les anciens snapshots des sauvegardes des machines ([Exploitation](operations.md)). |
| `unlock fleet.yaml <host>` | Relaie un anneau Tang vers une machine qui attend, au démarrage, le déverrouillage de son disque chiffré ([Exploitation](operations.md)). |
| `vps login\|list\|probe\|install` | Utilise l’API du Server Control Panel de netcup. |
| `roles [-v]`, `modules [-v]`, `targets` | Affiche ce qui est disponible, avec chaque réglage et sa valeur par défaut. |
| `toolchain [status\|build]`, `doctor` | Gère les outils ISO et vérifie l’ordinateur sur lequel vous travaillez. |

Toutes les commandes acceptent `--porcelain` (sortie en JSON),
`-o/--output-dir`, `--quiet` et `-v`. `kiwi-server <command> -h` explique une
commande précise.

## L’application { #the-app }

L’application **Kiwi Server** ouvre le dernier fichier fleet sur lequel vous
avez travaillé. Sa barre latérale contient une vue d’ensemble, une ligne par
hôte et les valeurs par défaut. La page *Overview* d’un hôte affiche les
informations actuelles de `kiwi-server status`. L’application les récupère une
fois par minute tant que la fenêtre est active, par SSH et en lecture seule. La
page *Settings* d’un hôte est un formulaire construit à partir des rôles et des
modules. *Apply*, *Build* et *Render* lancent l’outil en ligne de commande et
affichent sa sortie au fur et à mesure. Avant de démarrer, *Build* liste les
disques qu’il va effacer. *Unlock* et *Lock* ouvrent et ferment le coffre à
secrets. L’application écrit du YAML brut : quand elle enregistre un fichier
fleet que vous avez écrit à la main, les commentaires qu’il contenait sont
perdus.

## Points à garder en tête { #mind }

!!! danger "Les ISO effacent le disque qui leur a été indiqué"
    Dès qu’une machine démarre sur une ISO d’installation, celle-ci efface le
    disque pour lequel elle a été construite, sans rien demander. Étiquetez vos
    ISO. C’est précisément pour cette raison que `build` exige le réglage
    `disk:`.

- **La sortie contient des secrets** : empreintes de mots de passe, clés
  WireGuard, clés TLS et clés LUKS. Les fichiers sont écrits avec les droits
  0600, et `output/` est ignoré par git. Traitez les ISO créées avec
  `--offline` avec le même soin.
- **Les mots de passe des services sont générés** à partir de `secrets/seed`
  si vous ne les indiquez pas dans le fichier fleet. `validate` vous avertit
  des mots de passe écrits en clair dans le fichier fleet, et
  `kiwi-server secrets show` affiche ceux qui ont été générés. Une machine
  refuse un `apply` préparé avec un autre seed.
- **Les clés d’hôte SSH** sont enregistrées dans `secrets/known_hosts` la
  première fois que kiwi-server se connecte à une machine. Si la clé d’une
  machine change par la suite, la connexion est refusée. Après avoir réinstallé
  une machine, supprimez sa ligne dans ce fichier.
- **Un script de rôle s’exécute en root.** Avant de faire confiance à un rôle
  que vous n’avez pas écrit, lisez la sortie de `kiwi-server script fleet.yaml <host>
  --offline`.
- **L’échec d’un rôle est signalé.** La machine conserve le fichier
  `/var/lib/kiwi-server/role.failed`, qui indique l’étape et la commande qui
  ont échoué, et `status` l’affiche.

## État { #status }

L’ensemble du processus, du fichier fleet jusqu’à une machine en
fonctionnement, a été testé sur du matériel réel en octobre et novembre 2026.
Debian, uCore et Fedora CoreOS l’ont parcouru en entier sur deux VPS, un mini
PC et une machine virtuelle. Lors d’un exercice qui simulait la panne
définitive d’un node, une machine Debian chiffrée a été reconstruite en
14 minutes environ. Les sauvegardes d’un node ont été restaurées sur un autre
node (de papaya vers lychee). La MTU du tunnel a été mesurée et ajustée sur de
vraies connexions, y compris mobiles. Les tests automatisés (CI) génèrent
chaque rôle, passent chaque script à shellcheck et valident chaque
configuration Butane. Ils comparent aussi, octet par octet, quatre stacks de
référence (les golden stacks) avec leur sortie enregistrée.

La fédération entre réseaux n’a pas encore été testée. Tout fonctionne
uniquement en IPv4. L’ISO Debian n’existe que pour amd64. Un plan de contrôle
(`kiwi-server serve`) est prévu et conçu, mais pas encore réalisé.

Pour aller plus loin : [Le fichier fleet](fleet.md) · [Rôles](roles.md) ·
[Modules](modules.md) · [Machines](machines.md) ·
[Exploitation](operations.md) · [Une machine sans fichier fleet](single.md)
