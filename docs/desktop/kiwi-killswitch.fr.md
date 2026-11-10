# kiwi-killswitch

kiwi-killswitch est un **kill switch VPN** pour GNOME, sur Fedora Silverblue
et Bluefin. Un kill switch garantit que votre ordinateur n’envoie aucun trafic
en dehors du VPN, par exemple quand la connexion VPN tombe ou quand vous
changez de réseau. Celui-ci est **fail-closed** : le pare-feu bloque tout ce
qui n’est pas explicitement autorisé, si bien qu’en cas de panne le trafic est
bloqué au lieu de passer.

Le pare-feu est géré par un seul démon qui tourne en root. Vous le commandez
par un interrupteur dans les réglages rapides de GNOME, par une application
GTK4 ou par un outil en ligne de commande (CLI). Ces trois interfaces
transmettent leurs demandes au démon par le bus système D-Bus, et elles ne
demandent jamais de mot de passe.

Il protège **une seule** connexion VPN à la fois, WireGuard ou OpenVPN. Il
n’établit pas la connexion VPN à votre place : vous lancez vos connexions dans
les Paramètres de GNOME, et le kill switch règle son pare-feu sur la connexion
réellement active, pour qu’aucun trafic ne puisse sortir de l’ordinateur en
dehors de celle-ci.

- Dépôt : [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Dernière version : **v0.2.3**. Il figure dans le [catalogue Kiwi](catalogs.md)
  et a deux portées, utilisateur + système : une moitié est installée dans
  votre dossier personnel, l’autre appartient à root.
- Il fonctionne avec GNOME Shell 45 à 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Une extension GNOME tourne dans un processus sans droits root. Elle ne peut
pas modifier le pare-feu, et elle ne doit pas le pouvoir. C’est pourquoi tout
le blocage est fait par le démon, et l’interface ne fait que lui transmettre
des demandes.

## Ce qu’il fait { #what-it-does }

- **Il est fail-closed.** Le pare-feu applique `policy drop` au trafic
  sortant, entrant et transféré, en IPv4 comme en IPv6 : tout paquet est
  rejeté, sauf si une règle l’autorise. Un nouveau jeu de règles remplace
  l’ancien en une seule opération atomique. Le trafic ne peut sortir que par le
  tunnel protégé. Si le VPN tombe, si vous redémarrez ou si vous passez du
  Wi-Fi au partage de connexion, tout reste bloqué jusqu’à ce qu’un chemin
  autorisé soit de nouveau disponible.
- **Les nouvelles interfaces réseau sont bloquées.** Si vous branchez un
  partage de connexion USB ou activez le Wi-Fi pendant que le kill switch est
  armé, c’est-à-dire activé, la nouvelle interface est bloquée par défaut.
  Elle n’est pas autorisée du simple fait qu’aucune règle ne la mentionne.
- **Il y a trois niveaux de filtrage.** *Standard* filtre le trafic sortant et
  entrant. *Strict*, le niveau par défaut, filtre en plus le trafic
  **transféré**. C’est nécessaire parce que les conteneurs, les machines
  virtuelles et Waydroid font passer leur trafic par l’hôte, et que les paquets
  transférés ne passent jamais par le hook output. *Paranoid* ajoute une
  chaîne **netdev egress** sur chaque carte réseau (NIC). C’est la seule
  couche qui voit le trafic des sockets bruts.
- **Les requêtes DNS ne peuvent pas contourner le tunnel.** Vous choisissez
  quel résolveur DNS est utilisé pendant que le kill switch est armé : vous
  pouvez envoyer les requêtes DNS par le VPN, utiliser le résolveur du réseau
  sur lequel vous êtes, ou un résolveur que vous choisissez vous-même. Le
  résolveur du réseau n’est utilisé que sur le réseau d’un kiwi-node de
  confiance. Le kill switch applique votre choix par les réglages par lien de
  systemd-resolved. Par précaution supplémentaire, une règle nftables rejette
  toute autre requête DNS.
- **Pour un serveur VPN désigné par un nom d’hôte, le démon ne se fie pas au
  DNS ordinaire.** Il résout lui-même le nom d’hôte du serveur VPN. Il utilise
  pour cela le DNS-over-HTTPS, se connecte à une adresse IP épinglée (fixe) et
  vérifie le certificat. Il met chaque réponse en cache.
- **Vous choisissez une connexion, puis vous appliquez.** Les modifications
  sont d’abord mises en attente et ne prennent effet que quand vous les
  appliquez. Vous pouvez donc passer de « LAN domestique + kiwi-node »
  à « partage de connexion + VPN » *alors que vous êtes déjà sur le
  partage de connexion*. Au moment où vous appliquez, toutes les modifications
  sont faites en une seule transaction atomique, et le kill switch n’est
  désarmé à aucun moment entre les deux.
- **kiwi-nodes de confiance.** Il se peut que votre réseau ait une passerelle
  qui fait déjà passer votre trafic par un tunnel. Dans un Kiwi Network, c’est
  un [node passerelle](../server/roles.md#node). Sur son propre réseau, une
  telle passerelle peut remplacer le VPN. Le kill switch la reconnaît à son
  adresse IP **et** à son adresse MAC. C’est à vous d’activer cette option : le
  kill switch ne décide jamais de lui-même qu’une passerelle est de confiance.
- **Un seul VPN peut se connecter.** Seul le serveur de la connexion choisie
  est joignable. Tout autre tunnel que vous lancez ne peut pas se connecter, et
  l’interface indique lequel.
- **Les règles restent en place.** Elles sont toujours là après un
  redémarrage, après une déconnexion suivie d’une reconnexion, et après un
  redémarrage de NetworkManager. Une unité distincte charge des règles de
  blocage *avant que le réseau ne soit activé*.

## Installation { #install }

kiwi-killswitch a besoin de `nftables`, `NetworkManager` et `python3-gobject`,
et pour WireGuard de `wireguard-tools`. Tous sont présents sur Silverblue et
Bluefin. Rien n’est écrit dans le répertoire immuable `/usr`. Votre utilisateur
doit faire partie du groupe `wheel`.

```bash
kiwi install kiwi-killswitch   # les deux moitiés ; met en place la portée système de kiwi si besoin
```

Vous pouvez aussi l’installer depuis un clone du dépôt. Lancez d’abord
`sudo ./install.sh install`, qui installe le démon, la CLI, la politique D-Bus
et les unités systemd. Lancez ensuite `./install.sh install`, qui installe
l’extension GNOME et l’application de réglages. Déconnectez-vous puis
reconnectez-vous pour que GNOME charge l’extension. À la désinstallation, le
kill switch est d’abord désarmé : la désinstallation ne peut donc pas vous
laisser avec un réseau bloqué.

## Utilisation { #use }

Ouvrez **Quick Settings → Kill Switch**, dans les réglages rapides de GNOME,
pour armer et désarmer le kill switch et choisir quel VPN est protégé. Pour
tout le reste, ouvrez **Kiwi Kill Switch** dans la grille d’applications. La
CLI propose ces commandes :

```bash
kiwi-killswitch status                   # ce qui est appliqué en ce moment
kiwi-killswitch list                     # les connexions VPN que NetworkManager connaît
kiwi-killswitch vpn <name>               # préparer le choix de celle qui est protégée
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # une seule transaction atomique
kiwi-killswitch arm                      # ou : arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # ce qui est préparé ; revert l’annule
```

!!! warning "Armer le kill switch par SSH"
    Quand vous armez le kill switch, une session SSH venant d’un sous-réseau
    qui ne figure pas dans `mgmt_subnets` est coupée. C’est le comportement
    normal d’un kill switch. Si vous travaillez par SSH, réglez d’abord ces
    valeurs :
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Dépannage.** La CLI n’a pas besoin du réseau : une console texte (TTY)
suffit toujours pour lancer `kiwi-killswitch disarm`. Si le démon lui-même a
disparu, supprimez ses tables de pare-feu avec
`sudo nft delete table inet kiwi_ks` et
`sudo nft delete table netdev kiwi_ks_egress`.

**Machines virtuelles.** Une machine virtuelle en mode pont (bridge) ne fait
jamais passer son trafic par l’hôte : le kill switch ne la concerne donc pas.
Évitez alors `paranoid`, car ce niveau filtre au niveau de la carte réseau
physique. Une machine virtuelle en NAT fait passer son trafic par l’hôte. Avec
`strict`, ce trafic sort par le tunnel et il est bloqué quand le tunnel est
coupé. Ajoutez le sous-réseau de la machine virtuelle à `mgmt_subnets`, pour
que ses requêtes DHCP et DNS parviennent à l’hôte. Le tableau montre ce
qu’autorise chaque réglage :

| Réglage | Sortant | Entrant | Exclu du tunnel |
|---|---|---|---|
| `allow_lan` | oui (auto) | non | non |
| `bypass_subnets` | oui | non | non |
| `mgmt_subnets` | oui | oui | oui |

**Vérifier qu’il fonctionne.** Armez le kill switch, puis coupez le VPN avec
`nmcli connection down …`. À ce moment, `curl --max-time 5 ifconfig.me` doit
**expirer sans réponse**. La commande ne doit pas afficher votre véritable
adresse IP. Ne jugez pas le résultat en comparant les adresses IP publiques
que vous voyez. Pour prouver que le trafic passe par le tunnel, lancez
`wg show <iface> transfer` ou `ip route get 1.1.1.1`.

## Autres pare-feu et limites connues { #coexistence-and-known-limits }

- **firewalld peut rester actif.** Ses chaînes ont la priorité 10, celles du
  kill switch la priorité −10.
- Ne faites **pas** tourner kiwi-killswitch en même temps qu’un autre kill
  switch qui rejette le trafic sortant dans sa propre table.
- Ne touchez pas à `nftables.service` si vous ne l’utilisez pas. Quand ce
  service s’arrête, il supprime toutes les tables nftables. Le démon recharge
  ses règles en quelques secondes, mais pendant ces quelques secondes les
  règles manquent, et il n’y a aucune raison de provoquer cela.
- Un VPN dont le serveur est indiqué par un **nom d’hôte** ne peut pas se
  reconnecter pendant que le kill switch est armé, sauf si le DNS est réglé
  sur *a resolver I choose* (un résolveur que vous choisissez). En effet,
  NetworkManager et OpenVPN résolvent le nom par le résolveur du système, et
  celui-ci est bloqué tant qu’aucun tunnel n’est actif. Les connexions dont le
  serveur est indiqué par une adresse IP ne sont pas concernées.
- **Un résolveur que vous choisissez est joignable en dehors du tunnel**
  pendant que le tunnel est coupé. Activez le DNS-over-TLS pour ce résolveur.
- **Un node de confiance enregistré sans adresse MAC** est reconnu à sa seule
  adresse de passerelle.
- **Le pilotage sans mot de passe** passe par la politique D-Bus du groupe
  `wheel`. Cela veut dire aussi que n’importe quel programme qui tourne sous
  votre utilisateur peut désactiver le kill switch sans vous le demander.
- Il empêche les fuites au niveau du réseau. Ce n’est ni Tails ni Whonix. Il ne
  fait rien contre l’empreinte du navigateur (fingerprinting), contre WebRTC,
  ni contre une application qui envoie des données à son éditeur à travers le
  tunnel.
- C’est un outil personnel, qui n’a pas fait l’objet d’un audit indépendant.
  `tests/run.sh` teste le vrai démon avec de vraies règles nftables. Chaque
  groupe de tests tourne dans son propre namespace, et les tests n’ont pas
  besoin de root.
- Ses tags de version ne sont pas encore signés. Avec kiwi-updater 2.4, sa
  moitié root vous demande donc votre mot de passe à chaque mise à jour.

kiwi-killswitch reprend trois outils antérieurs du même auteur. L’ordre de
démarrage vient de `gnome-vpn-killswitch`, la détection de la passerelle de
`kiwi-vpn-monitor`, et l’architecture du démon de `nova-killswitch`.
