# kiwi-updater

kiwi-updater installe des applications open source sur votre ordinateur et les
tient à jour. Sa commande s’appelle `kiwi`. Il prend les applications dans des
**catalogues git**. Un catalogue est un dépôt git qui répertorie des
applications, et une application est un dépôt git qui contient un fichier
`kiwi.manifest` et un script `install.sh`. kiwi clone l’application, se place
sur son tag de version le plus récent et lance son script d’installation.
Ensuite, il met l’application à jour en arrière-plan, et il se met à jour
lui-même de la même manière.

Vous n’avez besoin d’aucun compte, et il n’y a ni boutique d’applications ni
éditeur. Un catalogue est un dépôt que vous pouvez lire, dont vous pouvez faire
un fork et auquel vous pouvez envoyer une pull request. Toutes les applications
Kiwi pour le poste de travail s’installent de cette façon.

- Dépôt : [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Dernière version : **v2.5.1**
- **`kiwi`** est l’outil en ligne de commande. **Kiwi Apps** (`kiwi-gui`) est
  l’application de bureau. Vous pouvez y parcourir et rechercher les
  applications, les installer, et lire le script d’installation d’une
  application avant qu’il ne soit exécuté.

## Systèmes pris en charge { #where-it-runs }

kiwi-updater a été conçu pour les Fedora Atomic desktops, et il fonctionne
aujourd’hui aussi sur d’autres distributions Linux. Chaque modification de
kiwi-updater est testée sur les systèmes suivants, avec la suite de tests
complète et une vraie installation :

| Système | Ce qui fonctionne |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | tout |
| Alpine | tout, une fois les outils GNU installés |
| Debian 12, Ubuntu 22.04 (testés, mais pas à chaque modification) | `kiwi` et les applications en ligne de commande. La version de libadwaita de ces systèmes est trop ancienne pour les applications de bureau |

## Installation { #install }

Cette commande installe la partie utilisateur dans votre dossier personnel et la
partie root pour les applications qui ont besoin de root. Votre mot de passe
n’est demandé qu’une seule fois :

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Si vous ne voulez rien en dehors de votre dossier personnel, et jamais de
demande de mot de passe, installez seulement la partie utilisateur :

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

L’installateur vérifie que la version qu’il installe est signée avec la clé qui
sert à signer les versions de kiwi-updater, et il refuse toute version qui ne
l’est pas. Le catalogue Kiwi est enregistré pendant l’installation. Vous pouvez
ensuite lancer :

```bash
kiwi list                    # toutes les applications que vous pouvez installer
kiwi install <app>           # en installer une
kiwi info --installer <app>  # lire son script d'installation avant qu'il ne soit exécuté
kiwi-gui                     # l'application de bureau
```

## Parties root et versions signées { #root-parts-and-signed-releases }

Certaines applications ont besoin de root, par exemple kiwi-killswitch, qui
comprend un démon de pare-feu. Leur partie root est installée par une copie de
kiwi qui appartient à root, et uniquement à partir des sources que root liste
lui-même. Installer ou supprimer une telle application demande toujours votre
mot de passe. Dans le mode par défaut, une mise à jour ne se fait sans mot de
passe que si la version est signée avec la clé que root a enregistrée pour
cette application.

## La documentation complète { #the-full-documentation }

kiwi-updater est documenté dans son propre dépôt :

| Page | Contenu |
|---|---|
| [Installation](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | systèmes pris en charge, paquets par distribution, modes d’installation, désinstallation |
| [Utiliser kiwi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | toutes les commandes, Kiwi Apps, mises à jour en arrière-plan, réglages |
| [Catalogues](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | ajouter des catalogues, `apps.list`, épingler une version, remplacer une entrée d’un catalogue |
| [Sécurité](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | ce qui tourne en root, quand vous saisissez un mot de passe, ce que kiwi vérifie |
| [Écrire une application](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, dépendances, icônes, versions |
| [Versions signées](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | signer les versions de votre application avec `kiwi-release` |
| [Développement](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | tests, CI, publication d’une version de kiwi-updater |

À partir de la prochaine version de kiwi-updater, ces pages apparaîtront aussi
ici, dans le menu, sous kiwi-updater.

Pour publier votre propre application, voir [Catalogues et
publication](catalogs.md).
