# kiwi-fox

kiwi-fox vous donne un navigateur distinct pour le réseau de chaque client
pour lequel vous travaillez, et pour chaque compte que vous gérez. Le profil de
navigateur d’un client accède aux consoles web de ce client par la connexion
de ce client, et n’a aucun autre moyen de joindre le réseau. Vous n’avez pas
besoin pour cela d’une connexion VPN sur l’hôte.

Chaque profil est une identité persistante. Il a son propre stockage, fait
tourner l’un des trois navigateurs proposés dans un conteneur Podman rootless
(un conteneur qui tourne sous votre propre utilisateur, sans droits root), et
passe en général par un exit [kiwi-proxy](kiwi-proxy.md). Un exit est une
connexion nommée vers un upstream, comme le proxy SOCKS5 d’un client. Pour
chaque exit, kiwi-proxy fait tourner un conteneur gateway. La gateway est un
conteneur dont la seule route mène à cet upstream, et elle contient un
résolveur DNS qui bloque les domaines publicitaires.

- Dépôt : [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Dernière version : **v0.7.1**. Il figure dans le [catalogue Kiwi](../desktop/catalogs.md), en portée utilisateur.
- Les navigateurs, que kiwi-fox appelle des moteurs, sont téléchargés sur
  votre machine et ne sont jamais redistribués. Camoufox (MPL-2.0) est
  téléchargé pendant la mise en place. Firefox et Tor Browser sont téléchargés
  quand vous les demandez (`kiwi-fox engine fetch`), et leurs signatures sont
  vérifiées.

| Moteur | Ce que voit une page |
|---|---|
| **Camoufox** (par défaut) | Une machine Windows 11 ordinaire, avec sa propre région, dont toutes les valeurs sont cohérentes entre elles. Cette empreinte (l’ensemble des valeurs qu’une page peut lire dans un navigateur pour le reconnaître) est falsifiée et ne change pas |
| **Firefox** | Mozilla Firefox non modifié, qui ne falsifie rien. Une page voit les vraies valeurs de cette machine. La connexion passe tout de même par l’exit du profil |
| **Tor Browser** | Tor Browser non modifié, connecté par un exit du module tor. Chaque site reçoit son propre circuit (son propre chemin à travers le réseau Tor), et les noms `.onion` fonctionnent |

kiwi-fox s’adresse aux personnes qui gèrent plusieurs comptes qui leur
appartiennent ou qu’elles sont autorisées à gérer, et qui ne veulent pas que
ces comptes puissent être reliés entre eux par l’empreinte du navigateur ou
par l’adresse IP.

## Installation { #install }

```bash
kiwi install kiwi-fox      # installe aussi kiwi-proxy ; ou ./install.sh install
kiwi-fox setup             # images, un moteur de navigateur d’environ 630 Mo, données DNS ; lance aussi la mise en place de kiwi-proxy
kiwi-fox engine fetch --engine firefox     # ou torbrowser : signature vérifiée
```

kiwi-fox a besoin de Podman rootless, de kiwi-proxy, de Python 3.12+, de GTK4
avec libadwaita et de `secret-tool`. Il est fait pour une session Wayland. X11
fonctionne aussi, mais l’isolation y est plus faible. `gpg`/`gpgv` sont
nécessaires pour vérifier Firefox et Tor Browser. Avec le pilote propriétaire
NVIDIA, kiwi-fox a aussi besoin de `nvidia-container-toolkit` et de sa
spécification CDI.

## Utilisation { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # un exit, défini une fois pour toutes, dans kiwi-proxy
kiwi-fox new work --exit client-a     # un profil qui passe par lui : mesure l’exit, tire une identité qui lui correspond
kiwi-fox new plain --no-proxy         # la connexion propre à cette machine, rien n’est verrouillé
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # ou l’application
kiwi-fox stop work
kiwi-fox check                        # chaque profil est-il toujours cohérent ?
kiwi-fox selfcheck work               # mesurer ce que voient les pages, puis le contrôler
kiwi-fox-gui                          # « Kiwi Fox » dans la grille d’applications
```

Avec `--desktop-entry`, un profil reçoit sa propre entrée dans la grille
d’applications. Les étiquettes (tags) permettent de regrouper des profils.

## Profils et exits { #profiles-and-exits }

Un profil ne possède pas d’exit : il en désigne un, et plusieurs profils
peuvent désigner le même exit. Les profils qui utilisent le même exit
partagent sa gateway, et avec elle un namespace réseau, une adresse IP de
l’exit et un ensemble de circuits Tor. Des identités qui ne doivent pas
partager d’exit ont besoin d’exits différents. Un profil créé avec
`--no-proxy` n’a pas de gateway. Son conteneur de navigateur a son propre
réseau et utilise la connexion propre à cette machine. Dans ce cas, rien n’est
verrouillé : son trafic n’est pas limité à une seule route.

Le conteneur du navigateur rejoint le namespace réseau de la gateway. Toutes
les capabilities Linux lui sont retirées, sauf `SYS_CHROOT`, dont le bac à
sable propre à Firefox a besoin. Le conteneur tourne avec `no-new-privileges`,
et le moteur y est monté en lecture seule.

## Un profil Camoufox { #a-camoufox-profile }

Un profil Camoufox se présente comme la machine la plus courante qui soit,
parce que les systèmes de détection signalent les valeurs rares. Il annonce un
écran de 1920×1080, les polices que possède toute installation de Windows 11 et
aucune autre, et la carte graphique réelle de cette machine, nommée comme
Firefox sous Windows la nomme. La région, la langue, le fuseau horaire et les
voix sont réglés pour correspondre à l’exit. Vous pouvez tout modifier ensuite
avec `kiwi-fox set`, `kiwi-fox webgl` et `kiwi-fox fonts`. Une modification
n’est enregistrée que si le profil reste cohérent, c’est-à-dire si ses valeurs
vont toujours ensemble.

## Ce qu’il ne fait pas { #what-it-does-not-do }

kiwi-fox ne promet pas qu’un profil soit « indétectable ». Les profils sont
séparés les uns des autres par leur stockage, leur adresse IP et toutes les
valeurs que le moteur peut falsifier. Ils ne sont **pas** séparés par les
identifiants qui viennent du matériel et qui sont les mêmes dans tous les
navigateurs. Les images que le GPU dessine réellement et les temps de réponse
du matériel viennent de la vraie machine : ils sont donc les mêmes pour tous
les profils de cette machine. Le fichier `docs/detection-notes.md` du dépôt
documente ce qui est mesuré.

kiwi-fox ne fait aucune automatisation. Il ne fait pas tourner de bots et ne
crée pas de comptes en masse. Il est fait uniquement pour une navigation
interactive.
