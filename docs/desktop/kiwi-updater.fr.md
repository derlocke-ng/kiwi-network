# kiwi-updater

`kiwi` installe et met à jour des applications open source depuis des **catalogues
git** sur Fedora Silverblue, Bluefin et d’autres systèmes ostree. Une application
est un dépôt git avec un `kiwi.manifest` et un `install.sh`. kiwi la clone, extrait
son dernier tag de version, lance son installateur et la tient à jour en
arrière-plan, lui-même compris.

Il n’y a pas de comptes, pas de boutique et pas d’éditeur. Un catalogue est un
dépôt que vous pouvez lire, forker et auquel vous pouvez envoyer une pull request.

- Dépôt : [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Dernière version : **v2.4.0**, une version de sécurité
- **`kiwi`** est la CLI. Elle a besoin de `git`, coreutils, `util-linux` et `awk`,
  tous présents dans l’image de base, plus `ssh-keygen` pour vérifier les
  signatures.
- **Kiwi Apps** (`kiwi-gui`) est l’application GTK4 : recherche, filtres, une vue
  détaillée par application avec son icône, ses captures d’écran et ses
  dépendances. Elle montre l’installateur et le diff d’une mise à jour avant
  d’exécuter l’un ou l’autre, et met vos clics en file d’attente. Ses données
  viennent de la CLI ; les icônes et les captures d’écran sont lues dans les clones
  des applications, si bien que rien n’est téléchargé pour elles.

## Installation { #install }

```bash
# recommandé : portée utilisateur plus la portée système appartenant à root, une seule demande de mot de passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash

# minimal : 100 % niveau utilisateur, ~/.local uniquement, sans root et sans mot de passe, jamais
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal

# aucune action sans mot de passe : chaque changement système demande un mot de passe
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --with-system=manual
```

Le [catalogue Kiwi](catalogs.md) est enregistré par l’installation. Passez
directement à `kiwi list` ou ouvrez **Kiwi Apps**.

Les applications qui ne sont que des fichiers dans votre répertoire personnel (les
outils CLI, ensconce, syncman) sont complètes avec l’installation minimale. Une
application avec une moitié root, comme kiwi-killswitch, a besoin de la portée
système. Sur une installation minimale, `kiwi install kiwi-killswitch` la met en
place sur-le-champ avec un seul mot de passe.

## Commandes { #commands }

```bash
kiwi list [--check]          # chaque application que cette machine connaît
kiwi search vpn              # trouver une application dans chaque catalogue enregistré
kiwi info kiwi-killswitch    # ce que c’est, ce qu’elle installe, si elle a besoin de root
kiwi install <app>           # un nom, ou un --all explicite
kiwi update [<app>]          # tout ce qui a une nouvelle version
kiwi uninstall <app>         # --purge supprime aussi sa configuration
kiwi check                   # code de sortie 10 si quelque chose a une mise à jour

kiwi add <https-url>         # suivre un dépôt directement, sans catalogue
kiwi catalog add|list|remove # gérer les catalogues
kiwi sync                    # actualiser les catalogues maintenant
kiwi self-update
kiwi trust --system <app>    # oublier la clé de signature épinglée pour une application système
```

Avant de lancer quelque chose, et quand quelque chose tourne mal :

```bash
kiwi info --installer <app>  # le script qu’une installation exécuterait, avant qu’il ne s’exécute
kiwi diff <app>              # ce qu’une mise à jour changerait, installateur compris
kiwi pin <app> v1.2.0        # rester là ; kiwi unpin <app> pour suivre à nouveau les versions
kiwi install <app> --dry-run # portée, URL, ref, chemin de l’installateur, et rien d’autre
kiwi doctor                  # verrous périmés, décalage de versions, fichiers de liste invalides, timers
```

## Les versions sont des tags { #releases-are-tags }

Une application suit son dernier **tag de version**, un tag qui correspond à
`^v?[0-9]+(\.[0-9]+){0,3}$` (`v1`, `v1.2`, `1.2.3`, `v1.2.3.4`). Les préversions
et les tags de travail ne passent jamais devant une version. Un dépôt sans tag de
version suit sa branche par défaut. `ref=<tag>` sur une ligne de liste en demande
un précis.

## Dépendances { #dependencies }

`DEPENDS=` dans un manifeste nomme ce dont une application a besoin. Un mot qui est
une application de votre propre catalogue ou de votre liste est installé **en
premier**, dans la même portée, au moment de l’installation.
`kiwi install kiwi-plugin-tor`, par exemple, installe aussi kiwi-proxy. Tout autre
mot est un programme, vérifié avec `command -v`.

## Une application, deux moitiés { #one-app-two-halves }

Certaines applications ne sont qu’un binaire dans `~/.local/bin`. D’autres, comme
un kill switch VPN, sont un démon root **et** une application de bureau **et** une
extension GNOME. Les moitiés s’installent avec des privilèges différents, car
**root ne doit jamais exécuter un fichier que l’utilisateur peut modifier**.
L’application le déclare :

```ini
COMPONENTS=daemon cli gui gnome-extension
SCOPES=user system
ROOT_REASON=installs a root firewall daemon, its D-Bus policy and two systemd units
```

Un catalogue liste cette application une seule fois, et kiwi installe chaque moitié
correctement. Avant de demander votre mot de passe, il affiche le `ROOT_REASON`.

| Élément | Où | Pourquoi |
|---|---|---|
| `kiwi`, Kiwi Apps, applications utilisateur | `~/.local` | pas besoin de root ; survit à un rebase ostree |
| la copie de kiwi propre à root | `/usr/local/bin`, cloné dans `/var/lib/kiwi-updater/repos/` | root n’exécute jamais un fichier que vous pouvez modifier |
| applications système | `/var/lib`, `/etc` | modifiables sur ostree, appartenant à root |
| listes | `~/.config/kiwi-updater/apps.list`, `/etc/kiwi-updater/apps.list` | les entrées propres à une machine l’emportent sur tout catalogue |
| clés de signature épinglées | `/etc/kiwi-updater/signers/<app>` | voir plus bas |

Le `/usr` immuable n’est jamais touché.

## Root, mots de passe et signatures { #root-passwords-and-signatures }

| | Exige root | Demande un mot de passe |
|---|---|---|
| tout ce qui est dans la portée utilisateur | non | non |
| **mettre à jour** une application système | oui | **non**, pour une version signée par la clé que root a épinglée pour cette application. **Oui** pour une version non signée, et toujours en mode `manual` |
| **installer** ou **désinstaller** une application système | oui | oui |

Depuis la 2.4.0 :

- **Versions signées.** Root épingle une clé de signature SSH par application
  système, la première qu’il voit (confiance à la première utilisation). Un tag de
  version signé par cette clé se met à jour sans mot de passe. Une version non
  signée en demande un et indique qu’elle n’a pas pu être vérifiée. Un tag signé
  par une autre clé, ou un tag non signé après des tags signés, est refusé jusqu’à
  ce que vous lanciez `kiwi trust --system <app>`. Cela s’applique à la portée
  système.
- **Root n’installe que les sources qu’il liste** : `/etc/kiwi-updater/apps.list`
  et les catalogues enregistrés pour root. Pour tout le reste, kiwi installe la
  moitié utilisateur et indique le `kiwi add --system <https-url>` à lancer. Kiwi
  Apps propose *Register and Install*.
- **https uniquement.** Les sources `http://` sont refusées partout.

Les mises à jour système sans mot de passe passent par un seul assistant à usage
déterminé, `/usr/local/libexec/kiwi-system-update`. Une règle polkit l’autorise pour
les sessions `wheel` actives, et il n’accepte des noms d’applications que comme une
sélection dans les propres listes de root.

## Mises à jour en arrière-plan { #background-updates }

Il y a un seul timer, et il est à vous : `kiwi-updater.timer` lance
`kiwi update --all` six heures après la dernière exécution (dix minutes après le
démarrage, avec un délai aléatoire). Il met à jour les moitiés utilisateur
directement, et les moitiés système via l’assistant ci-dessus. Il n’y a pas de timer
root. En mode `manual`, les moitiés système attendent votre prochain
`kiwi update` interactif.

## Confiance { #trust }

Installer une application **exécute le `install.sh` de ce dépôt**, et une
application qui déclare la portée système l’exécute **en tant que root**. Les
catalogues sont sélectionnés, pas audités. Ajoutez ceux en qui vous avez confiance,
comme vous ajouteriez un dépôt de paquets, et utilisez `kiwi info --installer`,
`kiwi diff` et `kiwi pin` pour décider en connaissance de cause. Une signature
restreint *qui peut publier*. Elle ne dit rien de *ce que fait ce qui est publié*.

Encore prévu : un registre hébergé de catalogues de confiance
(`kiwi catalog browse`) avec les empreintes des signataires pour chaque entrée.
