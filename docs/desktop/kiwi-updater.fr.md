# kiwi-updater

kiwi-updater installe des applications open source sur votre poste de travail
et les tient à jour. Sa commande s’appelle `kiwi`. Il prend les applications
dans des **catalogues git** et fonctionne sur Fedora Silverblue, Bluefin et
d’autres systèmes ostree. Un catalogue est un dépôt git qui répertorie des
applications. Une application est un dépôt git qui contient un fichier
`kiwi.manifest` et un script `install.sh`. kiwi clone le dépôt de
l’application, se place sur son dernier tag de version et lance son script
d’installation. Ensuite, il met l’application à jour en arrière-plan, et il se
met à jour lui-même de la même manière.

Vous n’avez besoin d’aucun compte, et il n’y a ni boutique d’applications ni
éditeur. Un catalogue est un dépôt que vous pouvez lire, dont vous pouvez
faire un fork et auquel vous pouvez envoyer une pull request.

- Dépôt : [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Dernière version : **v2.4.0**, une version de sécurité
- **`kiwi`** est l’outil en ligne de commande (CLI). Il a besoin de `git`, des
  coreutils, de `util-linux` et de `awk`, qui font tous partie de l’image de
  base. Pour vérifier les signatures, il lui faut aussi `ssh-keygen`.
- **Kiwi Apps** (`kiwi-gui`) est l’application de bureau, écrite avec GTK4.
  Vous pouvez y chercher et filtrer les applications, et chacune a une vue
  détaillée avec son icône, ses captures d’écran et ses dépendances. Kiwi Apps
  vous montre le script d’installation avant d’installer une application, et
  ce que change une mise à jour avant de l’appliquer. Si vous cliquez sur
  plusieurs actions à la suite, elles sont mises en file d’attente. Kiwi Apps
  obtient ses données par la CLI. Les icônes et les captures d’écran sont lues
  dans les clones locaux des applications : rien n’est téléchargé pour les
  afficher.

## Installation { #install }

kiwi travaille avec deux portées. La portée utilisateur, c’est tout ce qui se
trouve dans votre dossier personnel, et elle n’a jamais besoin de root. La
portée système est une partie qui appartient à root, pour les applications qui
ont besoin de root. À l’installation, vous choisissez quelle part de la portée
système vous voulez :

```bash
# recommandé : portée utilisateur plus la portée système détenue par root, une seule demande de mot de passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimal : 100 % au niveau utilisateur, uniquement ~/.local, jamais de root ni de mot de passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# aucune action sans mot de passe : chaque modification du système demande le mot de passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

L’installation enregistre le [catalogue Kiwi](catalogs.md) : vous pouvez donc
lancer `kiwi list` ou ouvrir **Kiwi Apps** tout de suite.

Certaines applications ne sont faites que de fichiers dans votre dossier
personnel, par exemple les outils en ligne de commande, ensconce et syncman.
Elles fonctionnent entièrement avec l’installation minimale. Une application
dont une moitié tourne en root, comme kiwi-killswitch, a besoin de la portée
système. Sur une installation minimale, `kiwi install kiwi-killswitch` met en
place la portée système à ce moment-là et vous demande votre mot de passe une
fois.

## Commandes { #commands }

```bash
kiwi list [--check]          # toutes les applications que cette machine connaît
kiwi search vpn              # chercher une application dans tous les catalogues enregistrés
kiwi info kiwi-killswitch    # ce que c’est, ce qu’elle installe, si elle a besoin de root
kiwi install <app>           # un nom, ou explicitement --all
kiwi update [<app>]          # tout ce qui a une nouvelle version
kiwi uninstall <app>         # --purge supprime aussi sa configuration
kiwi check                   # code de retour 10 s’il y a une mise à jour

kiwi add <https-url>         # suivre directement un dépôt, sans catalogue
kiwi catalog add|list|remove # gérer les catalogues
kiwi sync                    # actualiser les catalogues maintenant
kiwi self-update
kiwi trust --system <app>    # oublier la clé de signature épinglée pour une application système
```

Les commandes suivantes vous montrent ce qu’une application va faire avant
que vous la lanciez, et elles aident quand quelque chose ne va pas :

```bash
kiwi info --installer <app>  # le script qu’une installation lancerait, avant qu’il ne tourne
kiwi diff <app>              # ce qu’une mise à jour changerait, script d’installation compris
kiwi pin <app> v1.2.0        # rester sur cette version ; kiwi unpin <app> pour suivre de nouveau les versions
kiwi install <app> --dry-run # portée, URL, ref, chemin du script d’installation, et rien d’autre
kiwi doctor                  # verrous périmés, versions incohérentes, fichiers de liste invalides, timers
```

## Les versions sont des tags { #releases-are-tags }

kiwi utilise les tags git comme versions. Une application suit son dernier
**tag de version**. Un tag de version est un tag qui correspond à
`^v?[0-9]+(\.[0-9]+){0,3}$`, par exemple `v1`, `v1.2`, `1.2.3` ou `v1.2.3.4`.
Les tags de préversion et les tags temporaires ne correspondent pas : ils ne
sont donc jamais pris pour une version. Un dépôt sans tag de version suit sa
branche par défaut. Pour demander une version précise, ajoutez `ref=<tag>` à la
ligne de l’application dans une liste.

## Dépendances { #dependencies }

La ligne `DEPENDS=` d’un manifeste indique ce dont une application a besoin.
Si un mot de cette ligne est le nom d’une application de votre propre
catalogue ou de votre liste, kiwi installe cette application **d’abord**, dans
la même portée, au moment où vous installez celle qui en a besoin. Par
exemple, `kiwi install kiwi-plugin-tor` installe aussi kiwi-proxy. Tout autre
mot est considéré comme le nom d’un programme, et kiwi vérifie avec
`command -v` que ce programme est présent.

## Une application, deux moitiés { #one-app-two-halves }

Certaines applications ne sont qu’un programme dans `~/.local/bin`. D’autres,
comme un kill switch VPN, se composent d’un démon qui tourne en root **et**
d’une application de bureau **et** d’une extension GNOME. Une telle
application a deux moitiés, une moitié utilisateur et une moitié système, qui
sont installées avec des droits différents. La raison en est simple : **root
ne doit jamais exécuter un fichier que l’utilisateur peut modifier**.
L’application déclare ses composants et ses portées dans son manifeste :

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Un catalogue ne liste une telle application qu’une fois, et kiwi installe
chaque moitié dans la bonne portée. Avant de vous demander votre mot de passe,
kiwi vous montre le `ROOT_REASON`.

| Élément | Emplacement | Raison |
|---|---|---|
| `kiwi`, Kiwi Apps, applications utilisateur | `~/.local` | n’a pas besoin de root, et est conservé quand le système passe (rebase) sur une autre image ostree |
| la copie de kiwi propre à root | `/usr/local/bin`, cloné dans `/var/lib/kiwi-updater/repos/` | root n’exécute jamais un fichier que vous pouvez modifier |
| applications système | `/var/lib`, `/etc` | ces répertoires sont modifiables sur les systèmes ostree et appartiennent à root |
| listes | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | les entrées de la liste propre à une machine l’emportent sur tous les catalogues |
| clés de signature épinglées | `/etc/kiwi-updater/signers/<app>` | voir la section suivante |

kiwi ne modifie jamais rien dans le répertoire immuable `/usr`.

## Root, mots de passe et signatures { #root-passwords-and-signatures }

Le tableau indique quelles actions ont besoin de root et lesquelles demandent
un mot de passe.

| | Besoin de root | Demande un mot de passe |
|---|---|---|
| tout ce qui relève de la portée utilisateur | non | non |
| **mettre à jour** une application système | oui | **non**, si la version est signée avec la clé que root a épinglée pour cette application. **Oui**, si la version n’est pas signée, et toujours en mode `manual` |
| **installer** ou **désinstaller** une application système | oui | oui |

Depuis la version 2.4.0, ces règles s’appliquent :

- **Versions signées.** Pour chaque application système, root épingle une clé
  de signature SSH. Épingler une clé, c’est la retenir et n’accepter qu’elle à
  partir de ce moment-là. Root épingle la première clé qu’il voit pour
  l’application : c’est ce qu’on appelle la confiance au premier usage (trust on first use).
  Si un tag de version est signé avec la clé épinglée, la mise à jour
  s’installe sans mot de passe. Si une version n’est pas signée, kiwi vous
  demande votre mot de passe et vous indique qu’il n’a pas pu vérifier la
  version. kiwi refuse un tag signé avec une autre clé, et il refuse un tag non
  signé quand les tags précédents étaient signés. Il continue de les refuser
  jusqu’à ce que vous lanciez `kiwi trust --system <app>`. Ces règles
  s’appliquent à la portée système.
- **Root n’installe qu’à partir des sources qu’il liste lui-même.** Ces
  sources sont `/etc/kiwi-updater/apps.list` et les catalogues enregistrés
  pour root. Si une application vient d’une autre source, kiwi n’installe que
  la moitié utilisateur et vous indique la commande
  `kiwi add --system <https-url>` à lancer. Dans ce cas, Kiwi Apps propose le
  bouton *Register and Install*, qui enregistre la source puis installe
  l’application.
- **Uniquement https.** kiwi refuse partout les sources en `http://`.

Les mises à jour système sans mot de passe passent par un seul programme
auxiliaire, `/usr/local/libexec/kiwi-system-update`, qui ne sert qu’à cela.
Une règle polkit permet aux utilisateurs du groupe `wheel` de le lancer quand
leur session est active. Ce programme n’accepte que des noms d’applications,
et un nom ne peut désigner qu’une application figurant dans les listes propres
à root.

## Mises à jour en arrière-plan { #background-updates }

Les mises à jour en arrière-plan reposent sur un seul timer systemd, et c’est
un timer utilisateur : il tourne sous votre utilisateur, pas en root.
`kiwi-updater.timer` lance `kiwi update --all` six heures après la dernière
exécution, et dix minutes après le démarrage, avec un léger délai aléatoire.
Cette exécution met à jour directement les moitiés utilisateur, et les moitiés
système par le programme auxiliaire décrit plus haut. Il n’y a pas de timer
root. En mode `manual`, le timer ne met pas à jour les moitiés système : elles
attendent que vous lanciez `kiwi update` vous-même.

## Confiance { #trust }

Quand vous installez une application, kiwi **exécute le `install.sh` du dépôt
de cette application**. Si l’application déclare la portée système, kiwi
exécute ce script **en root**. Les catalogues sont sélectionnés, pas audités :
quelqu’un a choisi les applications, ce qui ne veut pas dire que leur code a
été relu. N’ajoutez que des catalogues auxquels vous faites confiance, comme vous
le feriez pour un dépôt de paquets. Servez-vous de `kiwi info --installer`,
`kiwi diff` et `kiwi pin` pour voir ce que fait une application avant de vous
décider. Une signature limite *qui peut publier* une version. Elle ne dit rien
de *ce que fait la version publiée*.

Une chose est encore prévue : un registre hébergé de catalogues de confiance,
avec la commande `kiwi catalog browse` et les empreintes des signataires de
chaque entrée.
