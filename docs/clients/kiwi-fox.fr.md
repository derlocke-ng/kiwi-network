# kiwi-fox

Des identités de navigateur isolées dans Podman rootless.

Chaque profil est une identité persistante : son propre stockage et, en général,
une sortie [kiwi-proxy](kiwi-proxy.md) avec sa gateway scellée et son résolveur
qui bloque les publicités, dans l’un de trois navigateurs. Pour un réseau client,
cela signifie un navigateur qui atteint les consoles web du client par la sortie du
client, et rien d’autre.

- Dépôt : [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Dernière version : **v0.7.1**. Elle figure dans le [catalogue Kiwi](../desktop/catalogs.md), portée utilisateur.
- Les moteurs sont téléchargés, jamais redistribués : Camoufox (MPL-2.0) à l’installation,
  Firefox et Tor Browser sur demande (`kiwi-fox engine fetch`), avec vérification de signature.

| Moteur | Ce que voit une page |
|---|---|
| **Camoufox** (par défaut) | une machine Windows 11 cohérente et ordinaire, avec sa propre région : une empreinte figée et usurpée |
| **Firefox** | Mozilla Firefox d’origine, qui n’usurpe rien : les propres valeurs de cette machine, à travers la même sortie scellée |
| **Tor Browser** | Tor Browser, non modifié, à travers une sortie sur le module tor, avec un circuit par site et les noms `.onion` |

kiwi-fox s’adresse aux personnes qui gèrent plusieurs comptes qui leur appartiennent
ou qu’elles sont autorisées à gérer, et qui ne veulent pas que ces comptes soient
reliés entre eux par l’empreinte du navigateur ou par l’IP.

## Installation { #install }

```bash
kiwi install kiwi-fox      # installe aussi kiwi-proxy ; ou ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # ou torbrowser : avec vérification de signature
```

Il faut Podman rootless et kiwi-proxy, une session Wayland (X11 fonctionne, avec une
frontière plus faible), Python 3.12+, GTK4 + libadwaita, `secret-tool`, et
`gpg`/`gpgv` pour vérifier Firefox et Tor Browser. Avec le pilote NVIDIA
propriétaire, il faut aussi `nvidia-container-toolkit` avec sa spécification CDI.

## Utilisation { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # une sortie, définie une fois, dans kiwi-proxy
kiwi-fox new work --exit client-a     # un profil dessus : la sonde, tire une identité assortie
kiwi-fox new plain --no-proxy         # this machine's own connection, nothing sealed
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # ou l’application
kiwi-fox stop work
kiwi-fox check                        # chaque profil est-il toujours cohérent ?
kiwi-fox selfcheck work               # mesurer ce que voient les pages, puis l’auditer
kiwi-fox-gui                          # "Kiwi Fox" in the app grid
```

`--desktop-entry` place un profil dans la grille d’applications, et les étiquettes
regroupent les profils.

## Profils et sorties { #profiles-and-exits }

Un profil fait référence à une sortie, et les sorties sont partagées : les profils
sur une même sortie partagent sa gateway (un espace de noms, une IP de sortie, un
même ensemble de circuits Tor). Les identités qui ne doivent pas partager une sortie
prennent des sorties différentes. Avec `--no-proxy`, il n’y a pas de gateway : le
conteneur du navigateur a son propre réseau sur la connexion de cette machine, et
rien n’est scellé.

Le conteneur du navigateur rejoint l’espace de noms de la gateway avec toutes les
capabilities retirées sauf `SYS_CHROOT` (le bac à sable propre à Firefox en a
besoin). Il tourne avec `no-new-privileges`, et le moteur est monté en lecture
seule.

## Un profil Camoufox { #a-camoufox-profile }

C’est la machine la plus courante qui soit, car ce sont les valeurs rares que les
détecteurs signalent : un écran 1920×1080, les polices de tout Windows 11 et aucune
autre, et la propre carte graphique de cette machine telle que Firefox sous Windows
la nomme. La région, la langue, le fuseau horaire et les voix suivent la sortie.
Tout peut être modifié ensuite (`kiwi-fox set`, `kiwi-fox webgl`,
`kiwi-fox fonts`), et les modifications ne sont enregistrées que si le résultat
reste cohérent.

## Ce qu’il ne fait pas { #what-it-does-not-do }

Il ne promet pas d’être « indétectable ». Les profils sont isolés pour le stockage,
l’IP et chaque surface que le moteur peut usurper, mais **pas** face aux
identifiants matériels communs à tous les navigateurs : les images que le GPU
dessine réellement et les temps matériels viennent de la vraie machine et sont les
mêmes pour chaque profil qui s’y trouve. Le fichier `docs/detection-notes.md` du
dépôt documente ce qui est mesuré.

Il n’y a pas d’automatisation : pas de bots et pas de création de comptes en masse.
Il sert uniquement à la navigation interactive.
