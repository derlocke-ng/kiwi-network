# kiwi-custodia

kiwi-custodia vous donne un environnement Linux distinct pour le réseau de
chaque client pour lequel vous travaillez. Chaque environnement est un
conteneur qui contient la distribution Linux de votre choix, et tout son trafic
réseau passe par un exit [kiwi-proxy](kiwi-proxy.md). Un exit est une
connexion nommée vers un upstream, par exemple le proxy SOCKS5 qui donne accès
au réseau d’un client. Vous pouvez ainsi travailler pour dix clients sans avoir
dix connexions VPN sur l’hôte, et les outils et les clés de chaque client
restent dans l’environnement de ce client. *Si vous connaissez distrobox, c’est
la même idée, à ceci près que le conteneur ne peut accéder au réseau que par
son exit.*

- Dépôt : [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Dernière version : **v0.2.3**. Il figure dans le [catalogue Kiwi](../desktop/catalogs.md), en portée utilisateur.
- Il comprend un outil en ligne de commande (`kiwi-custodia`) et une application GTK4 (**Kiwi Custodia**).

Une **box** kiwi-custodia, c’est une distribution Linux dans un conteneur
Podman rootless, c’est-à-dire un conteneur qui tourne sous votre propre
utilisateur, sans droits root. La box a son propre dossier personnel et elle
est rattachée à la gateway d’un exit. La gateway est le conteneur que
kiwi-proxy démarre pour un exit, et la seule route qui en sort mène à
l’upstream de l’exit. Dans la box, vous pouvez installer ce que vous voulez
avec le gestionnaire de paquets de la distribution. Ses applications de bureau
s’ouvrent sur votre bureau, et vous pouvez les ajouter à la grille
d’applications. La box n’a pas d’autre route que l’exit, et cela vaut pour
chaque programme qu’elle contient : pour `dnf`, pour un client de jeu, et pour
un programme lié statiquement qui ignore `$ALL_PROXY`. Si l’exit s’arrête, la
box n’a plus aucune route.

C’est pourquoi une box par réseau de client est une bonne façon de travailler.
Les outils, les clés et l’historique du shell du client A sont dans une box,
ceux du client B dans une autre, et chaque box ne peut joindre que son propre
client.

## Installation { #install }

```bash
kiwi install kiwi-custodia   # installe aussi kiwi-proxy ; ou ./install.sh install
kiwi-custodia setup          # l’image du tunnel, plus l’image de gateway et les données DNS de kiwi-proxy
```

kiwi-custodia a besoin de Podman rootless avec `catatonit`, de kiwi-proxy,
d’une session Wayland et de Python 3.12+ avec pydantic. L’application a besoin
de GTK4 et de libadwaita. Les conteneurs rootless doivent aussi pouvoir
utiliser `/dev/net/tun`. Les images des distributions ne sont pas
téléchargées pendant la mise en place : une image est téléchargée la première
fois qu’une box qui l’utilise démarre. Après une mise à jour, relancez
`kiwi-custodia setup`.

## Utilisation { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # un exit, défini une fois pour toutes, dans kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # une box qui passe par lui ; le premier démarrage installe une base
kiwi-custodia enter work                                   # un shell dans la box : sudo dnf install …
kiwi-custodia run work -- firefox                          # une seule commande dans la box
kiwi-custodia check work                                   # ce que le monde voit depuis l’intérieur
kiwi-custodia apps work                                    # les applications de bureau qu’elle contient
kiwi-custodia export work firefox                          # « Firefox (work) » dans la grille d’applications
kiwi-custodia stop work
kiwi-custodia reset work                                   # retour à l’image de base ; le dossier personnel reste
kiwi-custodia-gui
```

Les distributions disponibles sont `fedora` (par défaut), `fedora-toolbox`,
`ubuntu`, `ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`,
`arch-toolbox`, `opensuse`, `rocky` et `alpine`. Vous pouvez aussi choisir
`custom` et indiquer vous-même une image avec `--image`.

## Comment une box est construite { #how-a-box-is-built }

Une box en marche se compose de trois conteneurs qui partagent un même
namespace réseau : ils ont les mêmes interfaces réseau, les mêmes routes et les
mêmes règles de pare-feu. Le premier est la **gateway** de kiwi-proxy. Le
deuxième est un **sidecar de tunnel**, un conteneur auxiliaire qui fait tourner
tun2socks sur un périphérique TUN. Un périphérique TUN est une interface réseau
virtuelle, qui devient ici la route par défaut. Le troisième conteneur est la
**box** elle-même. Tout le trafic de la box entre dans le périphérique TUN et
va de là au proxy SOCKS5 de l’exit. Comme cela passe par la route par défaut
et non par des réglages de proxy, les programmes qui ignorent ces réglages sont
couverts eux aussi.

- La box tourne sous votre utilisateur, avec le même uid, et `sudo` y
  fonctionne sans mot de passe. Son dossier personnel est
  `~/.local/share/kiwi-custodia/boxes/<id>/home`. Chaque box a son propre
  dossier personnel et n’utilise pas le vôtre : deux box sont donc deux
  identités séparées.
- Quand une box s’arrête, les modifications faites à l’intérieur sont
  enregistrées dans un snapshot propre à cette box. `reset` ramène la box à
  l’image de base.
- Wayland, X11 (par Xwayland), PipeWire, le bus de session et `/dev/dri` sont
  mis à disposition dans la box, pour que les applications de bureau et les
  jeux fonctionnent.
- Les requêtes DNS reçoivent leur réponse du résolveur de la gateway, qui
  bloque aussi les domaines publicitaires. Sur un exit qui utilise le DNS
  distant, c’est l’upstream qui résout les noms.

## Ce que ce n’est pas { #what-it-is-not }

Une box **restreint le réseau. Ce n’est pas un bac à sable qui protège votre
bureau des programmes qu’elle contient.** Comme un conteneur distrobox, la box
a accès à votre affichage et à votre bus de session. Un programme dans la box
peut donc afficher des fenêtres, lire le presse-papiers et utiliser les
portails du bureau. Ce qu’il ne peut pas faire, c’est accéder au réseau
autrement que par son exit. UDP n’est pas transmis, donc QUIC et les flux
média de WebRTC ne fonctionnent pas, et il n’y a pas de route pour IPv6.

Les box qui utilisent le même exit le partagent. Des box qui doivent rester
séparées les unes des autres ont besoin d’exits différents.
