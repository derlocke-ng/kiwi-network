# Exploitation

Cette page traite du travail qui vient une fois les machines installées et en
service : vérifier leur état, protéger les secrets, sauvegarder le fichier
fleet et les données des machines, déverrouiller les disques chiffrés, ajuster
la MTU du tunnel et installer un serveur chez netcup. Vous faites tout cela
avec kiwi-server depuis votre propre ordinateur, le *poste d’administration*,
où se trouvent le fichier fleet et les secrets.

## État { #status }

`kiwi-server status` montre comment se portent vos machines, toutes ou
seulement celle que vous nommez :

```bash
kiwi-server status fleet.yaml            # tous les hôtes
kiwi-server status fleet.yaml papaya        # un seul
```

kiwi-server se connecte à chaque machine par SSH et se contente d’y lire des
informations. Chaque machine indique son rôle et sa stack (l’ensemble des
conteneurs et des services qu’elle fait tourner), les éventuels problèmes, par
exemple un rôle en échec ou un conteneur arrêté, ses disques et s’ils sont
chiffrés ou verrouillés, ses sauvegardes, et la durée de validité restante de
ses certificats. Un node de sauvegarde indique aussi sa capacité.
L’application Kiwi Server affiche les mêmes informations sur la page
*Overview* de chaque hôte.

## Secrets { #secrets }

Tout ce qui est secret est stocké dans `secrets/`, le dossier situé à côté du
fichier fleet. Il contient le seed dont sont dérivés tous les mots de passe
générés, l’autorité de certification (CA) propre à votre réseau, les
configurations WireGuard, les clés LUKS des disques chiffrés et les clés d’hôte
SSH. kiwi-server peut garder ce dossier chiffré et ne l’ouvrir que pendant que
vous travaillez :

```bash
kiwi-server secrets init fleet.yaml      # secrets/ devient un seul fichier chiffré avec age
kiwi-server secrets unlock fleet.yaml    # l'ouvrir en mémoire (--for 8h ; 0 le laisse ouvert)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # les mots de passe générés pour un hôte
```

`secrets init` crée le coffre chiffré. Il place une clé dans le trousseau
GNOME (GNOME Keyring) et vous montre une **clé de récupération**. Cette clé de
récupération n’est affichée qu’une seule fois. Tant que le coffre est ouvert,
tout programme qui tourne sous votre compte utilisateur peut le lire.

## Sauvegarder le fichier fleet lui-même { #backing-up-the-fleet-itself }

Le dossier du fichier fleet contient le fichier fleet et `secrets/`, et
kiwi-server le sauvegarde de lui-même. Après chaque génération ou construction
réussie (les deux étapes qui produisent la configuration des hôtes et leurs ISO
d’installation), il chiffre ce dossier (AES-256 avec PBKDF2, 600 000
itérations) et le copie sur les nodes listés dans `backup.hosts`. Chacun de ces
nodes conserve les dix copies les plus récentes. Sur un nouvel ordinateur,
vous récupérez le dossier depuis l’un de ces nodes. Vous pouvez aussi, à tout
moment, en écrire une copie dans le dossier de votre choix :

```bash
kiwi-server restore --from core@lychee.home  # récupérer le dossier du fichier fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # ou une copie dans un dossier, à tout moment
```

## Sauvegarder les données des machines { #backing-up-the-machines-data }

Les données des machines sont sauvegardées avec restic, un logiciel de
sauvegarde. Un node stocke les sauvegardes. Donnez à ce node le module
`backup-server`, qui fait tourner un serveur REST restic. Chaque machine à
sauvegarder reçoit le module `backup`, avec un réglage qui pointe vers ce
serveur :

```yaml
lychee:
  node:
    modules: [vpn-client, reverse-proxy, backup-server]
    backup-server: { clients: [papaya.home, sorbet.home] }
papaya:
  node:
    modules: [vpn-client, reverse-proxy, cloud, vault, portainer, backup]
    backup: { server: https://backup.lychee.home }
```

Chaque nuit à 03:00, ou jusqu’à 15 minutes plus tard, restic envoie au serveur
de sauvegarde, chiffrées, les données que chaque module veut conserver. Une
machine n’a accès qu’à son propre dépôt sur le serveur, et elle peut seulement
y ajouter des données : elle ne peut rien y supprimer. C’est pourquoi la
commande qui supprime les anciens snapshots s’exécute sur le poste
d’administration. Un snapshot est le nom que restic donne à l’état enregistré
lors d’une sauvegarde. La première commande ci-dessous s’utilise sur la
machine elle-même, la seconde sur votre ordinateur :

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # sur la machine
kiwi-server prune fleet.yaml            # garder 7 quotidiens, 4 hebdomadaires, 6 mensuels
```

Une restauration a été testée entre deux nodes, en restaurant les sauvegardes
de papaya sur lychee.

### Prévu pour la prochaine version { #coming-in-the-next-release }

!!! info "Sur la branche `several-servers`"
    Ce travail a été poussé sur les branches `several-servers` de
    kiwi-modules et de kiwi-server, mais il n’est pas encore fusionné ni
    publié. Les serveurs de sauvegarde multiples et la restauration
    automatique ont été testés sur du matériel réel. Le health check du VPN ne
    l’a pas été.

- **Plusieurs serveurs de sauvegarde.** `backup.servers` accepte une liste de
  serveurs, et chaque serveur reçoit sa propre copie complète. Si un serveur
  tombe en panne, seule sa copie est touchée. Une restauration prend la copie
  la plus récente, quel que soit le serveur qui la détient, et
  `kiwi-stack snapshots` liste les snapshots serveur par serveur. Le réglage
  `server`, pour un seul serveur, fonctionne toujours.
- **Une machine reconstruite se restaure elle-même.** Une machine qui vient
  d’être reconstruite trouve sur le serveur des sauvegardes d’elle-même, alors
  qu’elle n’en a fait aucune. Dans ce cas, elle restaure d’elle-même chaque
  module avant de faire sa première sauvegarde, puis sauvegarde comme avant.
  C’est le comportement par défaut, `backup.restore: auto`. Avec `hold`, la
  machine attend que vous lanciez `kiwi-stack restore` ou
  `kiwi-stack backup --new`.
- **Suppression des anciens snapshots à intervalle régulier.**
  `kiwi-server prune fleet.yaml --every week` (ou `day`) installe un timer
  utilisateur systemd sur votre ordinateur, le seul endroit où se trouvent les
  clés qui ont le droit de supprimer. Si une exécution est manquée, elle est
  rattrapée à la connexion suivante. `kiwi-server status` affiche chaque copie
  de sauvegarde et signale un node de sauvegarde dont les anciens snapshots
  n’ont pas été supprimés depuis trois semaines.
- **Une connexion bloquée au fournisseur VPN commercial se rétablit d’elle-même.**
  gluetun, le conteneur du client VPN, reçoit un health check, c’est-à-dire une
  vérification régulière que la connexion fonctionne encore. Si cette
  vérification échoue pendant cinq minutes, le conteneur est tué, et à son
  redémarrage il choisit un autre serveur.

## Disques chiffrés et déverrouillage { #encrypted-disks-and-unlocking }

Un disque chiffré doit être déverrouillé à chaque démarrage de la machine.
Cette section décrit comment chaque système cible (le système d’exploitation
installé sur une machine) chiffre son disque, et comment ce disque peut être
déverrouillé avec ou sans personne sur place.

- **Debian** (`debian.encrypt: true`) est installé avec une clé à usage
  unique, que vous saisissez au premier démarrage. Vous la trouvez dans
  `secrets/luks/<host>.once`. Le premier `apply` la remplace par
  `secrets/luks/<host>.key`, et un master reçoit en plus, à ce moment-là, une
  nouvelle clé de volume. Si vous perdez ce fichier de clé, le disque reste
  verrouillé : veillez donc à ce que le fichier fleet soit sauvegardé.
- **CoreOS / uCore** chiffrent le disque pendant l’installation, au moyen
  d’Ignition, l’outil qui configure une machine CoreOS à son premier
  démarrage. Pour cela, la machine a besoin d’environ 4 Gio de RAM au premier
  démarrage.
- **Les anneaux Tang** permettent aux machines chiffrées de déverrouiller leur
  disque au démarrage sans personne sur place. Tang est un petit serveur
  qu’une machine sollicite par le réseau pour déverrouiller son disque. Un
  node fait tourner le module `tang`, et chaque anneau est un serveur Tang
  avec ses propres clés. Par défaut, il y a un anneau, `infra`, sur le
  port 7500. Le bloc `unlock:` d’un hôte lie son disque à un ou plusieurs
  anneaux et fixe un seuil, c’est-à-dire le nombre d’anneaux qui doivent
  répondre.
- **SSH dans l’initramfs** (`unlock.ssh: true`) vous permet de joindre une
  machine qui attend le déverrouillage de son disque. L’initramfs est le petit
  système qui tourne avant que le disque soit ouvert. Le serveur SSH qu’il
  contient est dropbear sous Debian et dracut-sshd sous CoreOS. Il accepte une
  clé dédiée aux droits restreints, `secrets/unlock_ed25519`, qui ne peut rien
  faire d’autre que lancer le déverrouillage.
- `kiwi-server unlock fleet.yaml <host>` relaie un anneau vers une machine qui
  attend au démarrage : la machine peut ainsi utiliser un anneau qu’elle ne
  peut pas joindre elle-même. Avec `--manual`, la commande transmet
  directement la clé. Un anneau nommé `operator` est servi depuis votre propre
  ordinateur, aussi longtemps qu’il le faut. `vpn-server.unlock_relay` rend un
  anneau joignable à travers le master pour les machines placées derrière un
  NAT.

## MTU du tunnel { #tunnel-mtu }

La MTU est la taille maximale d’un paquet qu’une liaison réseau transporte
d’un seul tenant. WireGuard ajoute ses propres en-têtes à chaque paquet : un
tunnel transporte donc des paquets plus petits que la connexion sur laquelle il
repose, et une connexion mobile des paquets plus petits encore. Un paquet trop
gros pour l’une des liaisons de son trajet est rejeté ou fragmenté, et les
connexions se bloquent. Kiwi règle ce problème de trois façons :

- **Deux réglages.** `wg_mtu` est la MTU de gluetun (le client VPN), des
  configurations clientes délivrées par wg-easy (le serveur WireGuard) et de
  l’interface WireGuard `wg0`. Sa valeur par défaut est **1376**. C’est un
  multiple de 16, parce que WireGuard complète chaque paquet jusqu’au multiple
  de 16 octets suivant. `bridge_mtu` est la MTU du réseau de la stack, qui
  relie les conteneurs d’une machine. Sa valeur par défaut est **1500**.
  `validate` refuse un `wg_mtu` dont le paquet complété, plus 80 octets
  d’en-têtes, ne tient pas dans le bridge. Il refuse aussi toute valeur
  inférieure à 1280, la plus petite MTU avec laquelle IPv6 fonctionne.
- **Le MSS est limité dans les deux sens.** Le MSS est la quantité maximale de
  données que TCP place dans un paquet. wg-easy et le client VPN le limitent
  tous deux à `wg_mtu - 40` (MSS clamping) : TCP n’essaie ainsi jamais un
  segment qui ne pourrait pas passer.
- **TCP trouve de lui-même une taille qui fonctionne.** Le client VPN tourne
  avec `net.ipv4.tcp_mtu_probing=1` et `tcp_base_mss=1024`. Lorsqu’une
  connexion emprunte un chemin qui rejette sans prévenir les gros paquets, TCP
  essaie des paquets plus petits jusqu’à trouver une taille qui passe, au lieu
  de rester bloqué.

### Mesurer un chemin : `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

Pour savoir ce que le chemin vers un node ou un appareil transporte
réellement, mesurez-le :

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # un node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # un appareil de secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # et écrire wg_mtu dans le fichier fleet
```

La mesure envoie des pings à travers le tunnel avec l’indicateur « ne pas
fragmenter » (don’t fragment) : ils ne peuvent donc pas être découpés en
route. Elle les envoie depuis l’intérieur du namespace réseau qui contient le
tunnel. Un namespace réseau est un environnement réseau séparé sur une
machine, comme celui dont dispose un conteneur. Un node est mesuré depuis son
propre client VPN, parce que le pare-feu de ce client rejette les pings
entrants. Un appareil est mesuré depuis le serveur WireGuard. La mesure
commence par un ping ordinaire, puis essaie chaque multiple de 16 à partir de
1280 en montant, et indique la plus grande taille qui arrive **entière**.
Pendant les pings, elle lit les compteurs de réassemblage du noyau. Ainsi, une
réponse fragmentée en route puis réassemblée ne compte pas comme une taille qui
passe.

La mesure vous indique aussi quoi configurer. Pour un **appareil**, il s’agit
de la ligne `MTU =` de sa propre configuration WireGuard, et rien d’autre n’est
touché. Pour un **node**, il s’agit de `wg_mtu` sur ce node et sur son master.
Avec `--write`, la valeur est écrite dans le fichier fleet, et seules ces
lignes sont modifiées. Un cas reste invisible depuis ce côté : un paquet
fragmenté uniquement à l’aller et réassemblé par l’autre extrémité.

Les valeurs par défaut ont été mesurées sur le réseau de test. Un téléphone
sur réseau mobile a besoin de sa propre mesure, car les chemins mobiles sont
souvent en IPv6 uniquement, derrière du 464XLAT avec une encapsulation
imbriquée. Mesurez le téléphone lui-même, et baissez son propre `MTU =` si la
mesure l’indique.

## VPS netcup { #netcup-vpses }

netcup est un hébergeur, et c’est aujourd’hui le seul chez qui kiwi-server
peut installer lui-même un serveur loué (un VPS). Il le fait par l’API du
Server Control Panel de netcup. D’autres hébergeurs sont
[prévus](roadmap.md#more-hosters-and-network-boot), sous forme de plugins.

```bash
kiwi-server vps login fleet.yaml         # connexion par device flow ; le jeton est enregistré dans secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # effacer le serveur et installer l'ISO de l'hôte
```

`vps install` efface le serveur : la commande demande donc confirmation, sauf
si vous passez `--yes`. Elle refuse d’installer dans trois cas : quand l’ISO
contient des secrets de rôle, quand `disk:` désigne le mauvais disque, et quand
un disque CoreOS doit être chiffré sur un serveur qui a moins de 3 500 Mio de
RAM.
