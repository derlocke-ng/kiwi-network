# Le poste de travail

Côté poste de travail, Kiwi Network, c’est l’ordinateur sur lequel vous
travaillez : un poste Linux qui se configure automatiquement et qui reçoit ses
applications de catalogues git. Un catalogue est un dépôt git qui répertorie
des applications. Vous n’avez pas à configurer la machine à la main, et vous
pouvez configurer la suivante exactement de la même façon.

Les outils Kiwi pour le poste de travail sont faits pour les **Fedora Atomic
desktops** : Fedora Silverblue et [Bluefin](https://projectbluefin.io/), en
particulier Bluefin-DX. Ces systèmes sont installés et mis à jour d’un bloc,
sous la forme d’une image complète. Leur répertoire `/usr` est immuable,
c’est-à-dire qu’on ne peut pas le modifier, et l’on peut facilement revenir
sur une mise à jour. Il n’existe pas d’image Kiwi particulière : vous installez une
image Silverblue ou Bluefin standard, et vous y ajoutez trois choses.

1. **[kiwi-updater](kiwi-updater.md)** installe des applications depuis des
   catalogues git et les tient à jour. Il installe tout dans votre dossier
   personnel. Seule une application qui a besoin de root reçoit en plus une
   partie qui appartient à root. kiwi-updater se met aussi à jour lui-même.
2. **[ensconce](ensconce.md)** configure une installation toute fraîche de
   Bluefin-DX. Vous décrivez votre configuration dans de simples fichiers de
   listes, et ensconce l’applique : paquets, Flatpaks, extensions GNOME,
   synchronisation Nextcloud, SSH, réglages sysctl et d’alimentation, écran de
   connexion et applications Kiwi. Avec `--export`, il écrit la configuration
   d’une machine existante dans ces mêmes fichiers, ce qui vous permet de
   cloner cette machine.
3. **Les applications**, que vous installez depuis le
   [catalogue Kiwi](catalogs.md) :

| Application | Ce qu’elle fait |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Un kill switch VPN pour GNOME. Il est fail-closed : tant que le VPN n’est pas actif, tout le trafic reste bloqué |
| [Réseaux de clients](../clients/index.md) : kiwi-proxy, kiwi-custodia, kiwi-fox | Un exit pour chaque point d’accès VPN ou SOCKS. Un exit est un conteneur isolé qui ne peut joindre que ce seul point d’accès. Des box de distributions Linux et des navigateurs peuvent passer par un exit, et tout leur trafic l’emprunte alors |
| [kiwi-server](../server/index.md) | L’outil avec lequel vous construisez et faites tourner votre propre réseau |
| [gnome-monitor](gnome-monitor.md) | Enregistre des dispositions d’écrans et passe de l’une à l’autre. Il éteint et rallume aussi des écrans un par un |
| [syncman](syncman.md) | Synchronise des dossiers dans les deux sens, par exemple les parties enregistrées de vos jeux. La synchronisation tourne sous forme de services utilisateur |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Cette section décrit aussi [kiwi-gen](kiwi-gen.md), un gestionnaire de clés et
de certificats qui tourne dans le navigateur et fonctionne hors ligne.

## Depuis une installation neuve { #from-a-fresh-install }

Ces commandes vous mènent d’un système fraîchement installé à un poste de
travail équipé des applications Kiwi :

```bash
# 1. kiwi-updater : portées utilisateur et système, une seule demande de mot de passe ; le catalogue Kiwi est inclus
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configurer la machine
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. les applications que vous voulez (ou listez-les dans le kiwi-apps.list d’ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

Vous pouvez aussi installer des applications sans passer par le terminal :
**Kiwi Apps** (`kiwi-gui`), dans la grille d’applications, installe une
application en un clic.

## Rejoindre votre réseau { #joining-your-network }

Un poste de travail rejoint le mesh comme n’importe quel autre appareil. Le
mesh est le réseau WireGuard privé qui relie vos serveurs et vos appareils. La
commande `kiwi-server enroll fleet.yaml laptop --group devices` écrit un
fichier de configuration WireGuard, que vous importez dans les Paramètres de
GNOME. Importez aussi l’autorité de certification (CA) de votre réseau,
`kiwiCA.pem`, pour que le poste fasse confiance aux certificats HTTPS des noms
de votre réseau. ensconce installe pour tout le système chaque fichier `.pem`
de son répertoire `certs/`.

[kiwi-killswitch](kiwi-killswitch.md) protège ensuite cette connexion et
maintient la machine fail-closed : le trafic qui ne passe pas par la connexion
est bloqué, y compris quand la connexion est coupée. Chez vous, il se peut
qu’un node passerelle de votre réseau local fasse déjà passer votre trafic par
un tunnel. Avec le réglage *trusted kiwi-nodes*, le kill switch accepte un tel
node passerelle à la place du tunnel.
