# ensconce

Configuration post-installation modulaire pour [Bluefin-DX](https://projectbluefin.io/).
ensconce transforme une installation neuve de Bluefin en votre poste de travail
configuré, à partir de simples fichiers de listes : paquets superposés, Flatpaks,
extensions GNOME, synchronisation Nextcloud, une configuration SSH synchronisée,
réglages du bureau et de l’écran de connexion, et vos applications Kiwi.

- Dépôt : [derlocke-ng/ensconce](https://github.com/derlocke-ng/ensconce),
  GPL-3.0-or-later (son manifeste ; le README indique GPL-3.0)
- Dernière version : **v2.5.0**. Elle figure dans le [catalogue Kiwi](catalogs.md), portée utilisateur.

```bash
kiwi install ensconce
ensconce --init          # créer ~/.config/ensconce à partir des exemples
ensconce                 # lancer la configuration
```

Ou depuis un clone : `./ensconce.sh --init`, modifiez `config/`, puis `./ensconce.sh`.

## Étapes { #steps }

Chaque phase est un script dans `steps/`, exécuté dans l’ordre :

| # | Étape | Fait |
|---|---|---|
| 01 | `rebase` | passer à Bluefin-DX |
| 02 | `ujust` | groupes de développeur et outils CLI |
| 03 | `repos` | ajouter des dépôts RPM |
| 04 | `packages` | superposer des paquets RPM |
| 05 | `flatpaks` | installer des applications Flatpak (`FLATPAK_LANGUAGES` choisit leurs traductions) |
| 06 | `overrides` | surcharges des permissions Flatpak |
| 07 | `extensions` | extensions GNOME Shell |
| 08 | `cacert` | certificats d’autorité personnalisés |
| 09 | `nextcloud` | préconfigurer la synchronisation de dossiers Nextcloud |
| 10 | `dconf` | réglages du bureau GNOME |
| 11 | `gdm` | l’écran de connexion |
| 12 | `ssh` | une configuration SSH synchronisée, avec Bitwarden ou GNOME comme agent SSH |
| 13 | `kiwi` | installer kiwi-updater (`KIWI_INSTALL=recommended\|manual\|minimal`) et chaque application de `kiwi-apps.list` |
| 14 | `sysctl` | fichiers complémentaires de `sysctl.d/` (un exemple plafonne l’écriture différée des pages modifiées pour les SSD lents) |
| 15 | `power` | `SYSTEM_SLEEP=off` masque les cibles de mise en veille |

ensconce vérifie d’abord l’environnement (une image Bluefin, `rpm-ostree`,
`flatpak`, `dconf`, `jq`, `curl`). Il enregistre sa progression et reprend après
les redémarrages, et garde la machine éveillée pendant toute l’exécution, puis
restaure vos réglages d’alimentation.

```bash
ensconce --dry-run                  # aperçu sans rien modifier
ensconce --skip rebase,ujust        # sauter des étapes
ensconce --only extensions,dconf    # n’exécuter que celles-ci
ensconce --status | --list-steps | --reset
ensconce --log [file]               # enregistrer la sortie
ensconce --config-dir               # afficher le répertoire de configuration actif
```

## Configuration { #configuration }

Le répertoire de configuration est le premier qui existe parmi : `$ENSCONCE_CONFIG`,
`~/.config/ensconce/` (installé via kiwi), `config/` dans un clone, et
`config.example/` (avec un avertissement).

| Fichier / répertoire | Rôle |
|---|---|
| `settings.sh` | URL de serveurs et interrupteurs : SSH, kiwi-updater, langues Flatpak, veille |
| `packages.list`, `flatpaks.list`, `extensions.list` | un élément par ligne |
| `kiwi-apps.list` | les applications Kiwi à installer |
| `repos.d/`, `flatpak-overrides/` | fichiers de dépôts ; surcharges par application dans le format propre à Flatpak |
| `nextcloud/folders.list` | dossiers synchronisés sous la forme `localPath\|remotePath[\|tags]` |
| `nextcloud/exclude.lst`, `exclude.d/` | exclusions de synchronisation globales et par dossier (étiquetées) |
| `certs/` | certificats d’autorité (`.pem`), par exemple le `kiwiCA.pem` de votre fleet |
| `sysctl.d/` | réglages du noyau |
| `dconf-settings.ini`, `gtk3-bookmarks` | réglages GNOME, signets de Nautilus |
| `gdm/dconf.d/`, `gdm/monitors.xml` | les réglages et la disposition d’écrans de l’écran de connexion |

Une étiquette d’exclusion par dossier comme `browser` place `exclude.d/browser.lst`
dans ce dossier, ce qui empêche les bases de données d’un profil de navigateur
d’être synchronisées (et corrompues) alors que `user.js` est toujours synchronisé.

## Cloner une machine { #cloning-a-machine }

`--export` lit le système en marche et écrit une arborescence de configuration
ensconce, l’inverse des étapes :

```bash
ensconce --export ./my-setup        # sur la machine configurée
ensconce --init                     # sur la nouvelle
cp -rT ./my-setup "$(ensconce --config-dir)"
ensconce --dry-run && ensconce
```

Il ne capture que ce que vous avez ajouté : les paquets demandés plutôt que toute
l’image, les extensions qui viennent réellement d’extensions.gnome.org, vos propres
fichiers de dépôts, et des sous-arbres dconf choisis plutôt qu’un export complet.
Traitez-le comme un point de départ. `certs/` et `nextcloud/` peuvent contenir des
éléments privés.

ensconce est une application de **portée utilisateur**. Les étapes qui ont besoin de
root le demandent elles-mêmes. Ajoutez votre propre étape sous la forme
`steps/NN-<name>.sh` avec une fonction `step_<name>()`.
