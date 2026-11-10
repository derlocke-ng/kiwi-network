# ensconce

ensconce configure à votre place une installation toute fraîche de
[Bluefin-DX](https://projectbluefin.io/) : vous n’avez plus à régler chaque
nouvelle machine à la main. Vous décrivez votre poste de travail dans de
simples fichiers de listes, et ensconce fait de l’installation neuve exactement
ce poste. Il s’occupe des paquets superposés, des Flatpaks, des extensions
GNOME, de la synchronisation Nextcloud, d’une configuration SSH synchronisée
entre vos machines, des réglages du bureau et de l’écran de connexion, et de
vos applications Kiwi. Les paquets superposés (layered packages) sont des
paquets RPM ajoutés par-dessus l’image du système. La configuration est
modulaire : elle se compose d’étapes distinctes, que vous pouvez lancer ou
sauter.

- Dépôt : [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce).
  D’après son manifeste, la licence est GPL-3.0-or-later. Le README indique
  GPL-3.0.
- Dernière version : **v2.5.0**. Il figure dans le [catalogue Kiwi](catalogs.md)
  et s’installe dans la portée utilisateur, c’est-à-dire dans votre dossier
  personnel.

```bash
kiwi install ensconce
ensconce --init          # créer ~/.config/ensconce à partir des exemples
ensconce                 # lancer la configuration
```

Vous pouvez aussi le lancer depuis un clone du dépôt : lancez
`./ensconce.sh --init`, modifiez les fichiers de `config/`, puis lancez
`./ensconce.sh`.

## Étapes { #steps }

La configuration est découpée en étapes. Chaque étape est un script du
répertoire `steps/`, et les étapes s’exécutent dans cet ordre :

| # | Étape | Rôle |
|---|---|---|
| 01 | `rebase` | fait passer le système sur Bluefin-DX |
| 02 | `ujust` | met en place les groupes de développement et les outils en ligne de commande |
| 03 | `repos` | ajoute des dépôts RPM |
| 04 | `packages` | ajoute des paquets RPM superposés |
| 05 | `flatpaks` | installe des applications Flatpak. `FLATPAK_LANGUAGES` choisit les langues de leurs traductions |
| 06 | `overrides` | définit des dérogations aux permissions Flatpak |
| 07 | `extensions` | installe des extensions GNOME Shell |
| 08 | `cacert` | installe des certificats de CA personnalisés |
| 09 | `nextcloud` | prépare la configuration de la synchronisation de dossiers Nextcloud |
| 10 | `dconf` | applique les réglages du bureau GNOME |
| 11 | `gdm` | configure l’écran de connexion |
| 12 | `ssh` | met en place la configuration SSH synchronisée, avec Bitwarden ou GNOME comme agent SSH |
| 13 | `kiwi` | installe kiwi-updater de la façon choisie par `KIWI_INSTALL=recommended\|manual\|minimal`, puis chaque application de `kiwi-apps.list` |
| 14 | `sysctl` | installe les fichiers de réglages du noyau de `sysctl.d/`. Un fichier d’exemple limite la quantité de données pas encore écrites que le noyau garde en mémoire, ce qui aide avec les SSD lents |
| 15 | `power` | avec `SYSTEM_SLEEP=off`, masque les cibles de mise en veille, pour que la machine ne puisse pas se mettre en veille |

Avant de commencer, ensconce vérifie l’environnement : le système doit être une
image Bluefin, et `rpm-ostree`, `flatpak`, `dconf`, `jq` et `curl` doivent être
disponibles. ensconce enregistre sa progression, si bien qu’après un
redémarrage il reprend là où il s’était arrêté. Il empêche la machine de se
mettre en veille pendant toute l’exécution, puis rétablit vos réglages
d’alimentation.

Ces options pilotent une exécution :

```bash
ensconce --dry-run                  # aperçu sans rien modifier
ensconce --skip rebase,ujust        # sauter des étapes
ensconce --only extensions,dconf    # ne lancer que celles-ci
ensconce --status | --list-steps | --reset
ensconce --log [file]               # enregistrer la sortie
ensconce --config-dir               # afficher le répertoire de configuration utilisé
```

## Configuration { #configuration }

ensconce cherche son répertoire de configuration à quatre endroits et prend le
premier qui existe : d’abord `$ENSCONCE_CONFIG`, puis `~/.config/ensconce/`,
utilisé quand ensconce a été installé avec kiwi, puis `config/` dans un clone,
et enfin `config.example/`. Quand il utilise `config.example/`, il affiche un
avertissement.

| Fichier / répertoire | Rôle |
|---|---|
| `settings.sh` | les URL des serveurs, et les interrupteurs pour SSH, kiwi-updater, les langues Flatpak et la mise en veille |
| `packages.list`, `flatpaks.list`, `extensions.list` | les paquets, Flatpaks et extensions GNOME à installer, un par ligne |
| `kiwi-apps.list` | les applications Kiwi à installer |
| `repos.d/`, `flatpak-overrides/` | des fichiers de dépôts, et des dérogations pour certaines applications, au format propre à Flatpak |
| `nextcloud/folders.list` | les dossiers à synchroniser, sous la forme `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | ce qui est exclu de la synchronisation, pour tous les dossiers et pour certains dossiers qui portent une étiquette |
| `certs/` | des certificats de CA (`.pem`), par exemple le `kiwiCA.pem` de votre réseau |
| `sysctl.d/` | les réglages du noyau |
| `dconf-settings.ini`, `gtk3-bookmarks` | les réglages GNOME et les signets de Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | les réglages de l’écran de connexion et la disposition des écrans qu’il utilise |

Une étiquette dans `nextcloud/folders.list` donne à un dossier ses propres
exclusions. Par exemple, l’étiquette `browser` place `exclude.d/browser.lst`
dans ce dossier. Les bases de données d’un profil de navigateur ne sont alors
pas synchronisées, parce que la synchronisation risquerait de les corrompre,
alors que `user.js` l’est toujours.

## Cloner une machine { #cloning-a-machine }

`--export` fait l’inverse des étapes : il lit le système en marche et en tire
un répertoire de configuration ensconce. Vous pouvez ensuite configurer une
nouvelle machine avec ce répertoire :

```bash
ensconce --export ./my-setup        # sur la machine déjà configurée
ensconce --init                     # sur la nouvelle
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

L’export ne contient que ce que vous avez ajouté au système. Il liste les
paquets que vous avez demandés, et non toute l’image. Il ne liste que les
extensions qui viennent réellement d’extensions.gnome.org. Il contient vos
propres fichiers de dépôts, et une sélection de branches dconf au lieu d’un
export complet. Considérez l’export comme un point de départ. `certs/` et
`nextcloud/` peuvent contenir des données privées.

ensconce est une application de **portée utilisateur**. Les étapes qui ont
besoin de root le demandent elles-mêmes. Pour ajouter votre propre étape, créez
un fichier `steps/NN-<name>.sh` contenant une fonction `step_<name>()`.
