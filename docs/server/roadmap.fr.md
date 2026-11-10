# Où cela va

!!! info "Conçu, pas construit"
    Cette page résume la
    [conception du plan de contrôle](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    de kiwi-server, arrêtée en octobre 2026. Sauf si une ligne indique *construit*,
    rien de tout cela n’existe encore. La
    [feuille de route](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    en suit l’ordre.

Aujourd’hui, kiwi-server est un outil de bureau : le fichier fleet, les secrets et
l’autorité de certification se trouvent sur la machine de l’opérateur. Le projet
est d’en faire un **service** qui peut tourner sur un node, pour qu’un réseau
puisse être créé et géré sans bureau Linux, depuis un téléphone, et par plus d’une
personne. Les machines restent reproductibles à partir du fichier fleet. Le plan de
contrôle n’est que ce qui détient ce fichier et fait tourner le moteur de rendu.

## Les couches { #the-layers }

1. **kiwi-modules** : les modules et le contrat de rendu pour une machine.
   *Construit.*
2. **kiwi-stack** : le côté machine, à partir de `kiwi-stack apply`. *Construit.*
3. **Le cœur de kiwi-server** : la fleet, les hôtes, les cibles, les ISO,
   l’autorité de certification, l’enrôlement et l’application, sans interface graphique comme
   aujourd’hui. *Construit.*
4. **Le module de contrôle** : le cœur sous forme de conteneur, avec une API et une
   interface web, qui tourne comme module sur un node comme n’importe quel autre.
5. **Les clients** : l’interface web d’abord. L’application GTK reste et parle à la
   CLI locale ou à un contrôleur via le maillage, et la CLI reste aussi. Aucune
   interface ne développe de logique propre.

## Le node de contrôle { #the-control-node }

Le contrôleur tourne sur un node à la maison (le *node de contrôle*), joignable
depuis le maillage par les administrateurs uniquement, sur un disque chiffré. Il
détient la graine, la clé de l’autorité de certification, le fichier fleet et
chaque configuration.

Le **master loué devient une infrastructure de relais remplaçable**. Il ne détient
que ce dont il a besoin pour tourner : ses clés et ses pairs WireGuard, ses propres
mots de passe et son certificat. Le perdre coûte une nouvelle application depuis
le node de contrôle. Perdre le node de contrôle coûte une restauration de la
sauvegarde de la fleet.

## Utilisateurs { #users }

Un bloc `users:` avec deux rôles : un **administrateur de la fleet** qui peut tout
faire, et des **administrateurs de nodes** liés à leurs propres hôtes. Un
administrateur de nodes voit l’état, les journaux, les charges de travail et les
sauvegardes de ces hôtes, et enrôle des appareils dans les groupes que
l’administrateur de la fleet autorise, mais ne voit rien du master, de l’autorité
de certification ni des autres nodes. La connexion se fait par un mot de passe plus
un certificat client de l’autorité de certification de la fleet ou WebAuthn, et
chaque modification va dans un journal d’audit.

## Faire rejoindre une machine { #joining-a-machine }

Les deux voies restent :

- **Une ISO par hôte** avec son rôle (le `build --offline` d’aujourd’hui), pour
  les installations hors ligne.
- **Une ISO d’amorçage générique** par cible, construite une fois par la CI et ne
  contenant aucun secret. Au premier démarrage, elle récupère son rôle auprès du
  contrôleur avec un **jeton d’adhésion** à usage unique. Une machine installée à la
  main ou un VPS rejoint avec une seule ligne :
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Chaque machine de la lignée CoreOS est censée faire tourner **une seule image
bootc**, le rôle arrivant au premier démarrage.

## Fédération et multi-saut { #federation-and-multi-hop }

Des réseaux qui font confiance à l’autorité de certification l’un de l’autre et se
délèguent mutuellement des noms deviennent clients l’un de l’autre. Avec le
troisième mode de sortie, le master d’un réseau peut sortir vers Internet par celui
d’un autre : le **multi-saut**, où le second master ne voit que le premier.
Plusieurs masters gérés par un même opérateur forment alors un service VPN à soi :
des masters d’entrée dans un pays, des masters de sortie dans d’autres, Tor à
l’intérieur.

## Le verger { #the-orchard }

Le verger s’adresse aux personnes qui gèrent de nombreux masters pour d’autres.
C’est une application séparée ou un plugin de kiwi-server qui crée des VPS via les
API des hébergeurs, remet à chaque master son installation et un jeton
d’enregistrement, collecte un signal de vie de chaque master (version, santé,
disque, dernière mise à jour), et déploie les mises à jour en déplaçant des tags
d’images par canal.

Il ne peut pas se connecter à un master, lire une fleet ni toucher un node. Le node
de contrôle de chaque locataire, à la maison, garde son réseau. L’hébergeur du
master ne peut pas le lire, et fait tourner une VM par locataire. La prise en
charge de netcup dans kiwi-server (`kiwi-server
vps`, *construit*) est la première pièce de son pilote d’hébergeur.

## Également sur la liste { #also-on-the-list }

Un master de secours, podman rootless, IPv6 de bout en bout, les cartes ARM, les
plages de ports et un module de jeux, et une restauration des données d’un node au
premier démarrage.
