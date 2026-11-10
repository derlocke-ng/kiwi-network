# kiwi-custodia

Des conteneurs de distributions dont chaque octet sort par une sortie
[kiwi-proxy](kiwi-proxy.md). *Pensez à distrobox, avec le réseau sous bonne
garde.*

- Dépôt : [derlocke-ng/kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia), GPL-3.0-or-later
- Dernière version : **v0.2.3**. Elle figure dans le [catalogue Kiwi](../desktop/catalogs.md), portée utilisateur.
- Une CLI (`kiwi-custodia`) et une application GTK4 (**Kiwi Custodia**)

Une **box** est une distribution Linux dans un conteneur Podman rootless, avec son
propre répertoire personnel, reliée à la gateway scellée d’une sortie. Installez-y
ce que vous voulez avec son gestionnaire de paquets, lancez ses applications de
bureau sur votre bureau et placez-les dans la grille d’applications. La box n’a
aucune route hormis la sortie : ni pour `dnf`, ni pour un client de jeu, ni pour un
binaire statique qui n’a jamais entendu parler de `$ALL_PROXY`. Si la sortie
disparaît, la box n’a plus aucune route.

Une box par réseau client est donc une façon propre de travailler : les outils, les
clés et l’historique du shell du client A dans une box, ceux du client B dans une
autre, chacune n’atteignant que son propre client.

## Installation { #install }

```bash
kiwi install kiwi-custodia   # installe aussi kiwi-proxy ; ou ./install.sh install
kiwi-custodia setup          # the tunnel image, plus kiwi-proxy's gateway image and DNS data
```

Il faut Podman rootless avec `catatonit`, kiwi-proxy, une session Wayland,
Python 3.12+ avec pydantic, GTK4 + libadwaita pour l’application, et `/dev/net/tun`
utilisable par des conteneurs rootless. Les images des distributions sont
téléchargées au premier démarrage d’une box. Relancez `kiwi-custodia setup` après
une mise à jour.

## Utilisation { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080       # une sortie, définie une fois, dans kiwi-proxy
kiwi-custodia new work --exit client-a --distro fedora     # une box dessus ; le premier démarrage installe une base
kiwi-custodia enter work                                   # un shell dedans : sudo dnf install …
kiwi-custodia run work -- firefox                          # une commande dedans
kiwi-custodia check work                                   # ce que le monde voit depuis l’intérieur
kiwi-custodia apps work                                    # les applications de bureau qu’elle contient
kiwi-custodia export work firefox                          # "Firefox (work)" in the app grid
kiwi-custodia stop work
kiwi-custodia reset work                                   # retour à l’image de base ; le répertoire personnel reste
kiwi-custodia-gui
```

Distributions : `fedora` (par défaut), `fedora-toolbox`, `ubuntu`,
`ubuntu-toolbox`, `debian`, `debian-toolbox`, `kali`, `arch`, `arch-toolbox`,
`opensuse`, `rocky`, `alpine`, ou `custom` avec `--image`.

## Comment une box est construite { #how-a-box-is-built }

Trois conteneurs partagent un même espace de noms réseau : la **gateway** de
kiwi-proxy, un **sidecar de tunnel** (tun2socks sur un périphérique TUN qui devient
la route par défaut) et la **box** elle-même. Tout le trafic sort par le TUN vers le
SOCKS5 de la sortie, si bien que les programmes qui ignorent les réglages de proxy
sont couverts aussi.

- La box tourne sous votre utilisateur, avec le même uid et `sudo` sans mot de
  passe. Son répertoire personnel est `~/.local/share/kiwi-custodia/boxes/<id>/home`,
  un par box plutôt que votre vrai répertoire personnel : deux box, ce sont deux
  identités.
- Les modifications faites dans une box sont conservées dans un instantané propre à
  la box quand elle s’arrête, et `reset` revient à l’image de base.
- Wayland, X11 (via Xwayland), PipeWire, le bus de session et `/dev/dri` sont
  transmis, si bien que les applications de bureau et les jeux fonctionnent.
- Le DNS passe par le résolveur de la gateway (avec blocage des publicités), ou par
  l’amont sur une sortie en DNS distant.

## Ce que ce n’est pas { #what-it-is-not }

Une box est **une garde réseau, pas un bac à sable vis-à-vis de votre bureau**.
Comme distrobox, elle reçoit votre affichage et votre bus de session, si bien qu’un
programme dans la box peut afficher des fenêtres, lire le presse-papiers et utiliser
les portails. Ce qu’elle ne peut pas faire, c’est atteindre le réseau autrement que
par sa sortie. L’UDP n’a aucune issue (pas de QUIC, pas de média WebRTC), et l’IPv6
n’a pas de route.

Les box qui ne doivent pas partager une sortie prennent des sorties différentes.
