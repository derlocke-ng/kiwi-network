# Catalogues et publication d’applications

## Le catalogue Kiwi { #the-kiwi-catalog }

[derlocke-ng/kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) est le
catalogue d’applications du Kiwi Network. L’installation de kiwi-updater
l’enregistre, et
`kiwi catalog add https://github.com/derlocke-ng/kiwi-catalog.git` l’enregistre
à la main.

| Application | Version | Portées | Ce que c’est |
|---|---|---|---|
| [kiwi-updater](kiwi-updater.md) | v2.4.0 | utilisateur | le gestionnaire de mises à jour lui-même |
| [kiwi-killswitch](kiwi-killswitch.md) | v0.2.3 | utilisateur + système | kill switch VPN pour GNOME qui se ferme en cas de panne |
| [ensconce](ensconce.md) | v2.5.0 | utilisateur | configuration post-installation pour Bluefin-DX |
| [kiwi-cli-tools-desktop](cli-tools.md) | v1.2.1 | utilisateur | `pweb`, `select-server`, `tethering`, `torlink` |
| [kiwi-proxy](../clients/kiwi-proxy.md) | v0.7.3 | utilisateur | sorties SOCKS5/VPN scellées dans Podman rootless |
| [kiwi-fox](../clients/kiwi-fox.md) | v0.7.1 | utilisateur | identités de navigateur isolées sur des sorties kiwi-proxy |
| [kiwi-custodia](../clients/kiwi-custodia.md) | v0.2.3 | utilisateur | box de distributions dont le trafic ne sort que par une sortie |
| [kiwi-server](../server/index.md) | v2.42.0 | utilisateur | construire et faire tourner votre propre réseau |
| [syncman](syncman.md) | v0.4.1 | utilisateur | synchronisation bidirectionnelle de dossiers |
| [gnome-monitor](gnome-monitor.md) | v0.3.2 | utilisateur | dispositions d’écrans pour GNOME |
| [kiwi-plugin-tor](../clients/providers.md) | v0.3.0 | utilisateur | fournisseur kiwi-proxy : Tor |
| [kiwi-plugin-vpn](../clients/providers.md) | v0.2.2 | utilisateur | fournisseur kiwi-proxy : un VPN via gluetun |
| [kiwi-plugin-9proxy](../clients/providers.md) | v0.2.0 | utilisateur | fournisseur kiwi-proxy : 9proxy |
| [kiwi-plugin-myst](../clients/providers.md) | v0.5.2 | utilisateur | fournisseur kiwi-proxy : Mysterium |

kiwi synchronise le catalogue avant chaque vérification et chaque mise à jour, si
bien que gérer une flotte de postes de bureau, ce n’est que du git :

- **ajouter une application** : ajoutez son URL à `apps.list` et faites un commit ;
- **épingler ou revenir en arrière** : ajoutez `ref=<tag>` à sa ligne (sur une seule
  machine, `kiwi pin <app> <tag>` fait la même chose) ;
- **la retirer** : supprimez la ligne (les copies installées restent jusqu’à ce que
  vous les désinstalliez).

## Votre propre catalogue { #your-own-catalog }

Un catalogue est un dépôt git avec un `apps.list` et, en option, un
`catalog.manifest` qui le décrit :

```ini
# catalog.manifest
NAME=my-catalog
DESCRIPTION=What these apps are for
HOMEPAGE=https://…
MAINTAINER=you
```

```
# apps.list : une ligne par application, même quand elle a une moitié root et une moitié utilisateur
https://github.com/derlocke-ng/kiwi-updater.git
https://github.com/you/your-tool.git ref=v1.2.0
```

| Option | Signification |
|---|---|
| `branch=<name>` | suivre une branche plutôt que les tags de version |
| `ref=<tag>` | épingler une version exacte |
| `scope=user\|system` | n’installer que cette moitié sur les machines qui utilisent cette liste. C’est un *filtre*, pas une déclaration |

La liste propre à une machine (`~/.config/kiwi-updater/apps.list`, ou
`/etc/kiwi-updater/apps.list` pour root) l’emporte toujours sur un catalogue.
`kiwi add <url>` y ajoute une ligne.

## Publier une application { #publishing-an-app }

Placez un `kiwi.manifest` et un `install.sh` à la racine de votre dépôt. Des modèles
se trouvent dans [`templates/`](https://github.com/derlocke-ng/kiwi-updater/tree/main/templates)
de kiwi-updater.

```ini
NAME=my-tool
DESCRIPTION=Short description
# COMPONENTS: cli gui daemon service gnome-extension config module
COMPONENTS=cli
# SCOPES: user, system, or both
SCOPES=user
VERSION=0.1.0
HOMEPAGE=https://…
LICENSE=GPL-3.0-or-later
ICON=data/my-tool.svg
INSTALLER=install.sh
```

Autres clés : `AUTHOR`, `CATEGORY`, `TAGS`, `SCREENSHOTS`, `ABOUT` (un fichier que
Kiwi Apps affiche), `DEPENDS` et, pour tout ce qui a une moitié système,
`ROOT_REASON`. `ICON=` est un SVG ou un PNG d’au plus 1 Mio dans le dépôt. La
plupart des applications Kiwi prennent la leur dans [kiwi-icons](../project/brand.md).

!!! warning "Les commentaires vont sur leur propre ligne"
    Une valeur court jusqu’à la fin de la ligne. `COMPONENTS=cli  # … gui …` fait du
    commentaire une partie de la valeur, et l’application est alors traitée comme
    ayant une interface graphique.

kiwi exécute votre installateur une fois **par portée déclarée**, avec :

| Variable | Valeur |
|---|---|
| `KIWI_SCOPE` | `user` ou `system` |
| `KIWI_PREFIX` | `~/.local` ou `/usr/local` |
| `KIWI_APP_DIR` | chemin absolu du clone |
| `KIWI_ACTION` | `install`, `update` ou `uninstall` |
| `KIWI_GUI` | `0` sur une machine sans écran, ou avec `--cli-only` |
| `KIWI_PURGE` | `1` quand l’utilisateur a demandé `--purge` |
| `PATH` | `$KIWI_PREFIX/bin` en premier ; un chemin système fixe pour la portée système |

Un installateur à double portée se branche sur `KIWI_SCOPE` et ne fait que cette
moitié à chaque fois. Sans `--purge`, laissez la configuration de l’utilisateur là
où elle est.

**Publiez une version avec un tag signé**, pour qu’une moitié système se mette à
jour sans mot de passe :

```bash
git config gpg.format ssh            # signer avec votre clé SSH
git tag -s v1.3.0 -m v1.3.0 && git push origin v1.3.0
```

Le `templates/release.yml` de kiwi-updater ne publie une release GitHub que pour un
tag signé par une clé figurant dans `.github/allowed_signers`, et ne crée jamais de
tags lui-même. Ouvrez ensuite une pull request qui ajoute votre URL au catalogue.
Tout ce qui est open source et réellement utilisable sans compte, sans abonnement
et sans traqueur est bienvenu.

## Confiance { #trust }

Le catalogue est **sélectionné, pas audité**. Y figurer signifie que quelqu’un a
jugé que l’application valait la peine, pas que son code a été relu. Lisez
`kiwi info <app>` avant d’installer quelque chose que vous ne connaissez pas déjà,
et `kiwi info --installer <app>` pour voir exactement ce qui va s’exécuter.
