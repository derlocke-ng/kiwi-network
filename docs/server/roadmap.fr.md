# Ce qui se prépare

Cette page décrit ce que kiwi-server doit devenir, et quelles parties de ce
projet existent déjà.

!!! info "Conçu, pas encore réalisé"
    Cette page résume la
    [conception du plan de contrôle](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    de kiwi-server, arrêtée en octobre 2026. Rien de ce qui est décrit ici
    n’existe encore, sauf quand une ligne indique *réalisé*. La
    [feuille de route](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    fixe l’ordre des travaux.

Aujourd’hui, kiwi-server est une application de bureau. Le fichier fleet, les secrets
et la CA (l’autorité de certification de votre réseau) sont conservés sur le
poste d’administration, votre propre ordinateur. L’idée est d’en faire un
**service** capable de tourner sur un node. Un réseau pourrait alors être créé
et administré sans poste de travail Linux, depuis un téléphone, et par
plusieurs personnes. Les machines resteront reproductibles à partir du fichier
fleet. Le plan de contrôle est la partie qui détient ce fichier et fait tourner
le générateur, le programme qui transforme le fichier fleet en configuration
pour chaque machine.

## Les couches { #the-layers }

La conception répartit le logiciel en cinq couches.

1. **kiwi-modules** contient les modules et le contrat de génération, qui
   définit comment la configuration d’une machine est générée. *Réalisé.*
2. **kiwi-stack** est la partie qui tourne sur la machine. Son point de départ
   est `kiwi-stack apply`, qui installe une configuration générée sur la
   machine. *Réalisé.*
3. **Le cœur de kiwi-server** gère le fichier fleet, les hôtes, les systèmes
   cibles, les ISO, la CA, l’ajout d’appareils (`enroll`) et `apply`. Comme
   aujourd’hui, il est headless, c’est-à-dire sans interface graphique propre.
   *Réalisé.*
4. **Le module de contrôle** est ce cœur empaqueté dans un conteneur, avec une
   API et une interface web. Il tourne sur un node comme n’importe quel autre
   module.
5. **Les clients** sont les programmes avec lesquels vous utilisez le module
   de contrôle. L’interface web vient en premier. L’application GTK reste, et
   elle dialogue soit avec la CLI locale, soit avec un contrôleur (un module de
   contrôle en fonctionnement) à travers le mesh, le réseau WireGuard privé. La
   CLI reste elle aussi. Toute la logique reste dans le cœur : aucun client n’a
   de logique propre.

## Le node de contrôle { #the-control-node }

Le contrôleur tourne sur un node à domicile, appelé *node de contrôle*. Seuls
les admins peuvent le joindre, et uniquement depuis le mesh. Son disque est
chiffré. Il détient le seed, la clé de la CA, le fichier fleet et toutes les
configurations.

Le **master loué devient un relais remplaçable**. Il fait suivre le trafic du
réseau et ne détient que ce dont il a besoin pour fonctionner : ses clés et ses
pairs WireGuard, ses propres mots de passe et son certificat. Si le master est
perdu, vous appliquez de nouveau sa configuration depuis le node de contrôle. Si c’est le node
de contrôle qui est perdu, vous restaurez la sauvegarde du fichier fleet.

## Utilisateurs { #users }

Un bloc `users:` définit des utilisateurs, chacun avec l’un de deux rôles. Un
**fleet admin** peut tout faire. Un **node admin** est limité à ses propres
hôtes. Il voit l’état, les journaux, les charges de travail et les sauvegardes
de ces hôtes, et il peut ajouter des appareils dans les groupes que le fleet
admin autorise. Il ne voit rien du master, de la CA ni des autres nodes. Pour
se connecter, un utilisateur a besoin d’un mot de passe, et en plus soit d’un
certificat client émis par la CA du réseau, soit de WebAuthn. Chaque
modification est consignée dans un journal d’audit.

## Ajouter une machine au réseau { #joining-a-machine }

Une machine peut rejoindre le réseau de deux façons, et les deux sont
conservées :

- **Une ISO par hôte**, qui contient le rôle de la machine : c’est l’actuel
  `build --offline`. Elle sert aux installations hors ligne.
- **Une ISO d’amorçage générique** par système cible, construite une fois pour
  toutes par la CI et qui ne contient aucun secret. Au premier démarrage, la
  machine récupère son rôle auprès du contrôleur grâce à un **jeton
  d’adhésion** (join token) à usage unique. Une machine installée à la main,
  ou un VPS, rejoint le réseau avec une seule ligne :
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Chaque machine de la famille CoreOS doit faire tourner **une seule image
bootc**, une image de conteneur amorçable, la même pour toutes. La machine
reçoit son rôle au premier démarrage.

## Fédération et multi-saut { #federation-and-multi-hop }

La fédération relie des Kiwi Networks distincts. Des réseaux qui font
confiance à la CA l’un de l’autre et se délèguent mutuellement des noms
deviennent clients l’un de l’autre. Un master a trois modes de sortie, qui
déterminent comment son trafic rejoint Internet. Avec le troisième, le master
d’un réseau envoie son trafic Internet par le master d’un autre réseau. C’est
ce qu’on appelle le **multi-saut** (multi-hop), et le second master ne voit que
le premier. Un administrateur qui fait tourner plusieurs masters de cette
manière dispose de son propre service VPN, avec des masters d’entrée dans un
pays, des masters de sortie dans d’autres pays, et Tor à l’intérieur du
réseau.

## L’orchard { #the-orchard }

L’orchard (“verger” en anglais) est le service prévu pour les personnes qui
font tourner de nombreux masters pour le compte d’autres personnes. Ce sera une
application séparée ou un plugin de kiwi-server. Il crée des VPS par l’API des
hébergeurs et fournit à chaque master son installation et un jeton
d’enregistrement. Il recueille de chaque master un heartbeat, c’est-à-dire un
rapport d’état régulier (version, santé, disque, dernière mise à jour). Il
déploie les mises à jour en déplaçant le tag d’image de chaque canal de mise à
jour.

L’orchard ne peut pas se connecter à un master, lire un fichier fleet ni
modifier un node. Chaque locataire, c’est-à-dire chaque personne dont le master
est géré par quelqu’un d’autre, garde son réseau sur son propre node de contrôle, chez
elle. Le fichier fleet et les clés restent là-bas : l’hébergeur qui fait
tourner la VM du master ne peut donc pas lire les données réseau du locataire.
Le master de chaque locataire tourne dans sa propre VM. L’orchard a besoin d’un
pilote pour les API des hébergeurs, et la prise en charge de netcup par
kiwi-server (`kiwi-server vps`, *réalisé*) en est la première pièce.

## D’autres hébergeurs, et le démarrage par le réseau { #more-hosters-and-network-boot }

*Prévu.* L’objectif est qu’une machine puisse être installée de façon
entièrement automatique, où qu’elle se trouve.

- **Les hébergeurs sous forme de plugins.** La prise en charge de netcup est
  aujourd’hui intégrée. Il est prévu de créer un dépôt séparé pour les API des
  hébergeurs, afin que chacun puisse ajouter AWS, Hetzner et d’autres. Un
  plugin fonctionnerait comme la prise en charge actuelle de netcup : il crée
  ou efface un serveur, y place l’installation et le démarre.
- **Wake-on-LAN et le démarrage PXE** sont prévus pour les machines à
  domicile. Wake-on-LAN allume une machine par le réseau, et PXE lui permet de
  démarrer depuis le réseau. Un node se réveille alors et s’installe lui-même
  par le réseau, sans clé USB.

## Également prévu { #also-on-the-list }

La feuille de route prévoit aussi un master de secours, podman rootless, l’IPv6
de bout en bout, les cartes ARM, des plages de ports et un module de jeux,
ainsi que la restauration des données d’un node à son premier démarrage.
