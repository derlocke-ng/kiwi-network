# kiwi-server

kiwi-server crée et gère un Kiwi Network. Vous décrivez chaque machine dans un seul
`fleet.yaml`. kiwi-server produit une **ISO d’installation sans intervention** pour
chaque hôte, qui installe Fedora CoreOS, uCore ou Debian puis éteint la machine. Il
**applique** ensuite le rôle via SSH, ce qui transforme la machine en
`kiwi-master` ou en `kiwi-node`. Après cela, il continue de travailler avec la
fleet : il enrôle des clients WireGuard, lit l’état de santé de chaque machine,
conserve les secrets, sauvegarde la fleet et déverrouille les disques chiffrés.

Il a une CLI, `kiwi-server`, et une application GTK4, **Kiwi Server**. Les deux
s’installent dans `~/.local` et n’ont pas besoin de root.

- Dépôt : [derlocke-ng/kiwi-server](https://github.com/derlocke-ng/kiwi-server), GPL-3.0-or-later
- Dernière version : **v2.42.0**. Elle figure dans le [catalogue Kiwi](../desktop/catalogs.md).
- Construit sur [kiwi-modules](single.md) v0.23.0 (les modules et leur moteur de
  rendu) et [kiwi-stack](single.md) v0.5.0 (le côté machine), embarqués et épinglés
  par tag.

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

Ou depuis une copie de travail : `./install.sh install`, puis `kiwi-server doctor`.

Il faut Python 3.9+ avec PyYAML et Jinja2, `openssl` et `ssh`. Le magasin de
secrets a besoin de `age`. Construire des ISO demande `butane`, `coreos-installer`
et `xorriso` (plus `cpio`, `gzip` et `curl` pour Debian). Sur Silverblue ou Bluefin,
construisez-les plutôt sous forme d’une seule image de conteneur au lieu de
superposer des paquets :

```bash
kiwi-server toolchain build     # utilisée automatiquement quand les outils manquent
```

`qrencode` (pour `enroll --qr`), `shellcheck` et `docker compose` sont facultatifs.

## De rien à un réseau en marche { #from-nothing-to-a-running-network }

```bash
kiwi-server init                          # un fleet.yaml commenté
$EDITOR fleet.yaml                        # hôtes, rôles, votre clé SSH, le disque d’installation
kiwi-server secrets init fleet.yaml       # facultatif : secrets/ comme un seul magasin chiffré avec age
kiwi-server validate fleet.yaml

# le master
kiwi-server build fleet.yaml sorbet         # → output/sorbet/sorbet.iso
#   démarrez dessus ; elle installe et éteint la machine ; redémarrez-la
kiwi-server apply fleet.yaml sorbet --ssh core@203.0.113.5

# chaque node : d’abord son client WireGuard, puis le support, puis le rôle
kiwi-server enroll fleet.yaml papaya         # → secrets/papaya.home.conf
kiwi-server build fleet.yaml papaya
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25

# vos propres appareils
kiwi-server enroll fleet.yaml laptop --group devices
kiwi-server status fleet.yaml             # ce que chaque machine rapporte
```

Par défaut, les supports d’installation ne contiennent **aucun des secrets de la
stack** : uniquement le système de base. Le rôle et sa stack arrivent avec
`apply`. Si une machine n’est pas joignable via SSH, `build --offline` place plutôt
tout le rôle et ses secrets sur l’ISO. Gardez une telle ISO hors du magasin d’ISO
d’un hébergeur et supprimez-la après l’installation.

**Pas d’ISO du tout ?** `kiwi-server script fleet.yaml papaya` affiche le script
pour une machine que vous avez installée vous-même (`--offline` pour tout le rôle).

Sur un VPS netcup, `kiwi-server vps install fleet.yaml sorbet` efface le serveur et
installe l’ISO via l’API de netcup.

## Commandes { #commands }

| Commande | Ce qu’elle fait |
|---|---|
| `init [fleet.yaml]` | écrire le fichier fleet d’exemple (`--domain`, par défaut `home`) |
| `validate fleet.yaml [host…]` | le vérifier, en faisant le rendu de chaque stack pour repérer les erreurs de modules |
| `list` / `show fleet.yaml <host>` | les hôtes et ce qui a été généré / la configuration effective d’un hôte, secrets masqués |
| `render fleet.yaml [host…]` | scripts de rôle, stacks et configurations d’installation dans `output/<host>/` |
| `build fleet.yaml [host…]` | le rendu, puis l’ISO : système de base par défaut, `--offline` pour tout le rôle |
| `script fleet.yaml <host>` | le script pour n’importe quelle machine (`--offline` pour tout le rôle) |
| `apply fleet.yaml <host…>` | refaire le rendu, envoyer le rôle via SSH et l’exécuter (`--ssh USER@ADDR`, `--no-run`) |
| `status fleet.yaml [host…]` | ce que rapportent les machines : rôle, stack, problèmes, disques, sauvegardes, certificats |
| `enroll fleet.yaml <host\|name>` | créer ou récupérer un client WireGuard sur le master (`--group`, `--split`, `--qr`, `--address`, `--existing`) |
| `secrets init\|unlock\|lock\|status` | `secrets/` comme un seul fichier chiffré avec age, ouvert en mémoire (`--for 8h`) |
| `secrets show fleet.yaml <host> [setting]` | les mots de passe générés d’un hôte |
| `ca fleet.yaml` | l’autorité de certification de la fleet |
| `mtu fleet.yaml <node\|device\|address>` | mesurer la MTU réelle d’un tunnel et dire quoi régler (`--write`) |
| `openwrt fleet.yaml` | un script qui fait rejoindre le maillage à un routeur OpenWrt ([Routeurs](../network/routers.md)) |
| `backup` / `restore` / `prune` | le répertoire de la fleet vers les nodes et retour ; anciennes sauvegardes de machines supprimées ([Exploitation](operations.md)) |
| `unlock fleet.yaml <host>` | transmettre un anneau Tang à une machine qui attend au démarrage ([Exploitation](operations.md)) |
| `vps login\|list\|probe\|install` | l’API du Server Control Panel de netcup |
| `roles [-v]`, `modules [-v]`, `targets` | ce qui est disponible, avec chaque réglage et sa valeur par défaut |
| `toolchain [status\|build]`, `doctor` | les outils pour les ISO ; vérifier cette machine |

Chaque commande accepte `--porcelain` (JSON), `-o/--output-dir`, `--quiet` et
`-v`. `kiwi-server <command> -h` explique une commande.

## L’application { #the-app }

**Kiwi Server** ouvre votre dernière fleet. La barre latérale contient une vue
d’ensemble, une ligne par hôte, et les valeurs par défaut. L’onglet *Overview* d’un hôte
montre des faits en direct issus de `kiwi-server status` (interrogé une fois par
minute tant que la fenêtre a le focus, en lecture seule via SSH). Son onglet *Settings*
est un formulaire construit à partir des rôles et des modules. *Apply*, *Build* et
*Render* lancent la CLI et affichent sa sortie en continu, et *Build* liste les
disques qu’il va effacer avant de commencer. *Unlock* et *Lock* ouvrent et ferment
le magasin de secrets. L’application écrit du YAML simple, si bien que les
commentaires d’un fichier fleet écrit à la main sont perdus quand elle enregistre.

## Attention { #mind }

!!! danger "Les ISO effacent le disque qu’on leur indique"
    Au démarrage, sans demander. Étiquetez-les. `disk:` est obligatoire pour
    `build` précisément pour cette raison.

- **La sortie contient des secrets** : empreintes de mots de passe, clés WireGuard,
  clés TLS, clés LUKS. Les fichiers sont écrits en 0600 et `output/` est ignoré par
  git. Traitez de la même façon les ISO faites avec `--offline`.
- **Les mots de passe des services sont générés** à partir de `secrets/seed` quand
  vous les omettez du fichier fleet. `validate` avertit si des mots de passe y sont
  écrits. `kiwi-server secrets show` les affiche. Une machine refuse une
  application faite avec une autre graine.
- **Les clés d’hôte SSH** sont enregistrées dans `secrets/known_hosts` au premier
  contact, et une clé modifiée est refusée (après une réinstallation, supprimez la
  ligne).
- **Un script de rôle s’exécute en tant que root.** Lisez `kiwi-server script fleet.yaml <host>
  --offline` avant de faire confiance à un rôle que vous n’avez pas écrit.
- **Un rôle qui échoue le dit.** La machine conserve
  `/var/lib/kiwi-server/role.failed` (l’étape et la commande), et `status` l’affiche.

## État { #status }

La chaîne a été éprouvée sur du matériel en octobre et novembre 2026. Debian, uCore
et Fedora CoreOS ont été démarrés de bout en bout sur deux VPS, un mini PC et une
VM, et un exercice de node mort a reconstruit une machine Debian chiffrée en
environ 14 minutes. Des sauvegardes de nodes ont été restaurées d’un node sur un
autre (de papaya vers lychee), et la MTU du tunnel a été mesurée et ajustée sur des
chemins réels, chemins mobiles compris. La CI fait le rendu de chaque rôle, passe
chaque script à shellcheck, valide chaque configuration Butane, et fige quatre
stacks de référence à l’octet près.

Pas encore éprouvé : la fédération entre réseaux. Tout est en IPv4. L’ISO Debian
est uniquement amd64. Un plan de contrôle prévu (`kiwi-server serve`) est conçu
mais pas construit.

Pour aller plus loin : [Le fichier fleet](fleet.md) · [Rôles](roles.md) ·
[Modules](modules.md) · [Machines](machines.md) · [Exploitation](operations.md) ·
[Une machine sans fleet](single.md)
