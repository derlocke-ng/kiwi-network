# Catalogues et publication d’applications

Un catalogue est une liste d’applications que kiwi-updater peut installer.
C’est un dépôt git : vous pouvez donc le lire, le copier et y proposer des
modifications. Cette page présente le catalogue Kiwi, montre comment créer
votre propre catalogue, par exemple pour tous les postes de travail dont vous
vous occupez, et explique comment publier une application pour que d’autres
puissent l’installer avec kiwi.

## Le catalogue Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) est le
catalogue d’applications de Kiwi Network. Il est enregistré automatiquement
quand vous installez kiwi-updater. Pour l’enregistrer à la main, lancez
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git`.

Le tableau liste les applications du catalogue. La colonne *Portées* indique
où une application est installée. La portée utilisateur, c’est votre dossier
personnel. La portée système, c’est une partie qui appartient à root.

| Application | Version | Portées | Ce que c’est |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | utilisateur | le gestionnaire de mises à jour lui-même |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | utilisateur + système | kill switch VPN pour GNOME. Il est fail-closed : tant que le VPN n’est pas actif, tout le trafic reste bloqué |
| [ensconce](ensconce.md) | v2.5.0 | utilisateur | configure une installation toute fraîche de Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | utilisateur | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | utilisateur | des exits pour les connexions SOCKS5 et VPN. Un exit est un conteneur isolé dans Podman rootless |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | utilisateur | des identités de navigateur isolées qui passent par des exits kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | utilisateur | des box (des conteneurs contenant une distribution Linux) dont le trafic passe uniquement par un exit |
| [kiwi-server](../server/index.md) | v2.42.0 | utilisateur | l’outil avec lequel vous construisez et faites tourner votre propre réseau |
| [syncman](syncman.md) | v0.4.1 | utilisateur | synchronise des dossiers dans les deux sens |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | utilisateur | enregistre des dispositions d’écrans dans GNOME et passe de l’une à l’autre |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | utilisateur | module fournisseur pour kiwi-proxy : Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | utilisateur | module fournisseur pour kiwi-proxy : un VPN via gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | utilisateur | module fournisseur pour kiwi-proxy : 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | utilisateur | module fournisseur pour kiwi-proxy : Mysterium |

kiwi récupère la version actuelle du catalogue avant chaque vérification et
chaque mise à jour. Vous pouvez donc gérer les applications de tout un parc de
postes de travail avec git, sans rien d’autre :

- **Pour ajouter une application**, ajoutez son URL à `apps.list` et faites
  un commit.
- **Pour épingler une application à une version ou revenir à une version
  antérieure**, ajoutez `ref=<tag>` à la fin de sa ligne. Sur une seule
  machine, `kiwi pin <app> <tag>` fait la même chose.
- **Pour retirer une application**, supprimez sa ligne. Les copies déjà
  installées le restent jusqu’à ce que vous les désinstalliez.

## Votre propre catalogue { #your-own-catalog }

Un catalogue est un dépôt git qui contient un fichier `apps.list`. Il peut
aussi contenir un fichier `catalog.manifest`, dans lequel le catalogue se
décrit lui-même :

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list : une ligne par application, même si elle a une moitié root et une moitié utilisateur
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

Une ligne de `apps.list` peut porter ces options après l’URL :

| Option | Signification |
|---|---|
| `branch=<name>` | suivre une branche au lieu des tags de version |
| `ref=<tag>` | rester exactement sur cette version |
| `scope=user\|system` | n’installer que cette moitié de l’application sur les machines qui utilisent cette liste. Cette option est un *filtre* : elle ne déclare pas quelles portées l’application possède |

Chaque machine a aussi sa propre liste :
`~/.config/kiwi-updater/apps.list` pour votre utilisateur et
`/etc/kiwi-updater/apps.list` pour root. Une entrée de la liste propre à la
machine l’emporte toujours sur un catalogue. `kiwi add <url>` ajoute une ligne
à cette liste.

## Publier une application { #publishing-an-app }

Pour publier une application, placez un fichier `kiwi.manifest` et un script
`install.sh` à la racine de votre dépôt. Vous trouverez des modèles dans le
répertoire
[`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
de kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, ou les deux
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Un manifeste peut comporter d’autres clés : `AUTHOR`, `CATEGORY`, `TAGS`,
`SCREENSHOTS`, `ABOUT` (un fichier que Kiwi Apps affiche), `DEPENDS` et
`ROOT_REASON`. Toute application qui a une moitié système doit avoir un
`ROOT_REASON`. `ICON=` désigne un fichier SVG ou PNG d’au plus 1 Mio, situé
dans le dépôt. La plupart des applications Kiwi prennent leur icône dans
[kiwi-icons](../project/brand.md).

!!! warning "Mettez les commentaires sur une ligne à part"
    Une valeur s’étend jusqu’à la fin de sa ligne. Si vous écrivez
    `COMPONENTS=cli  # … gui …`, le commentaire fait partie de la valeur, et
    kiwi considère alors que l’application a une interface graphique.

kiwi lance votre script d’installation une fois **pour chaque portée que
l’application déclare**. Il lui fournit ces variables :

| Variable | Valeur |
|---|---|
| `KIWI_SCOPE` | `user` ou `system` |
| `KIWI_PREFIX` | `~/.local` ou `/usr/local` |
| `KIWI_APP_DIR` | chemin absolu du clone |
| `KIWI_ACTION` | `install`, `update` ou `uninstall` |
| `KIWI_GUI` | `0` sur une machine sans bureau graphique, ou avec `--cli-only` |
| `KIWI_PURGE` | `1` quand l’utilisateur a demandé `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` passe en premier. La portée système reçoit un chemin système fixe |

Le script d’installation d’une application qui a les deux portées doit
vérifier `KIWI_SCOPE` et, à chaque exécution, ne faire que le travail de la
moitié concernée. Si l’utilisateur n’a pas demandé `--purge`, laissez sa
configuration en place.

**Publiez chaque version sous forme de tag signé.** C’est la condition pour
qu’une moitié système puisse être mise à jour sans mot de passe :

```bash
git config gpg.format ssh            # signer avec votre clé SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

kiwi-updater fournit un workflow de publication, `templates/release.yml`. Il
ne publie une version sur GitHub que pour un tag signé avec une clé listée dans
`.github/allowed_signers`, et il ne crée jamais de tag lui-même. Pour finir,
ouvrez une pull request qui ajoute votre URL au catalogue. Toute application
est la bienvenue si elle est open source et réellement utilisable sans compte,
sans abonnement et sans pisteur.

## Confiance { #trust }

Le catalogue est **sélectionné, pas audité**. Une application y figure parce
que quelqu’un a jugé qu’elle en valait la peine. Cela ne veut pas dire que son
code a été relu. Avant d’installer une application que vous ne connaissez pas,
lisez la sortie de `kiwi info <app>`. Lancez `kiwi info --installer <app>` pour
voir exactement ce qui va s’exécuter.
