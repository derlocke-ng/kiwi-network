# Exploitation

Le travail au quotidien sur une fleet en marche, entièrement depuis la machine de
l’opérateur.

## État { #status }

```bash
kiwi-server status fleet.yaml            # chaque hôte
kiwi-server status fleet.yaml papaya        # un seul
```

Chaque machine fait son rapport via SSH (en lecture seule) : son rôle, sa stack,
les problèmes (un rôle en échec, un conteneur arrêté), ses disques et s’ils sont
chiffrés ou verrouillés, ses sauvegardes, et le temps qu’il reste à ses
certificats. Un node de sauvegarde indique aussi sa capacité. L’application Kiwi
Server montre la même chose dans l’onglet *Overview* de chaque hôte.

## Secrets { #secrets }

Tout ce qui est secret se trouve dans `secrets/`, à côté du fichier fleet : la
graine dont dérive chaque mot de passe généré, l’autorité de certification de la
fleet, les configurations WireGuard, les clés LUKS et les clés d’hôte SSH.

```bash
kiwi-server secrets init fleet.yaml      # secrets/ devient un seul fichier chiffré avec age
kiwi-server secrets unlock fleet.yaml    # l’ouvrir en mémoire (--for 8h ; 0 le garde ouvert)
kiwi-server secrets lock fleet.yaml
kiwi-server secrets status fleet.yaml
kiwi-server secrets show fleet.yaml papaya [setting]   # a host's generated passwords
```

`secrets init` conserve une clé dans le trousseau GNOME et affiche une **clé de
récupération** une seule fois. Tant que le magasin est ouvert, tout ce qui tourne
sous votre utilisateur peut le lire.

## Sauvegarder la fleet elle-même { #backing-up-the-fleet-itself }

Après chaque rendu ou construction réussi, le répertoire de la fleet est chiffré
(AES-256 avec PBKDF2, 600 000 itérations) et copié vers les nodes listés dans
`backup.hosts`, qui gardent les dix plus récents. Sur une machine neuve :

```bash
kiwi-server restore --from core@lychee.home  # récupérer le répertoire de la fleet
kiwi-server backup fleet.yaml --local /mnt/usb   # ou une copie vers un répertoire, à tout moment
```

## Sauvegarder les données des machines { #backing-up-the-machines-data }

Donnez à un node le module `backup-server` (un serveur REST restic), et à chaque
machine à sauvegarder le module `backup`, qui pointe vers lui :

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

Chaque nuit à 03:00 (dans les 15 minutes qui suivent), restic envoie, chiffré, ce
que chaque module demande de conserver. Chaque machine ne peut atteindre que son
propre dépôt, et seulement y ajouter. La suppression des anciens instantanés se
lance donc depuis la machine de l’opérateur :

```bash
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # sur la machine
kiwi-server prune fleet.yaml            # garder 7 quotidiens, 4 hebdomadaires, 6 mensuels
```

Une restauration a été testée de node à node : les sauvegardes de papaya sur
lychee.

### Dans la prochaine version { #coming-in-the-next-release }

!!! info "Sur la branche `several-servers`"
    Ce travail est poussé sur les branches `several-servers` de kiwi-modules et de
    kiwi-server, mais il n’est pas encore fusionné ni publié. Les serveurs
    multiples et la restauration automatique ont été testés sur du matériel. Le
    contrôle de santé du VPN ne l’a pas été.

- **Plusieurs serveurs de sauvegarde.** `backup.servers` accepte une liste, et
  chaque serveur reçoit sa propre copie complète. Si un serveur tombe en panne,
  seule sa copie manque. Une restauration prend la copie la plus récente sur le
  serveur qui l’a, et `kiwi-stack snapshots` les liste serveur par serveur. Le
  réglage unique `server` fonctionne toujours.
- **Une machine reconstruite se restaure elle-même.** Si une machine se trouve dans
  les sauvegardes mais n’en a fait aucune (une reconstruction), elle restaure
  d’elle-même chaque module avant sa première sauvegarde, puis sauvegarde comme
  avant (`backup.restore:
  auto`, par défaut). Avec `hold`, elle attend `kiwi-stack restore` ou
  `kiwi-stack backup --new`.
- **L’élagage sur un timer.** `kiwi-server prune fleet.yaml --every week` (ou
  `day`) installe un timer utilisateur systemd sur votre ordinateur, le seul
  endroit qui détient les clés autorisées à supprimer. Une exécution manquée a lieu
  à la connexion suivante. `kiwi-server status` montre chaque copie de sauvegarde,
  et avertit quand un node de sauvegarde n’a pas été élagué depuis trois semaines.
- **Une sortie commerciale bloquée repart de zéro.** gluetun reçoit un contrôle de
  santé. Après cinq minutes en mauvaise santé, le conteneur est tué, et son
  prochain démarrage choisit un autre serveur.

## Disques chiffrés et déverrouillage { #encrypted-disks-and-unlocking }

- **Debian** (`debian.encrypt: true`) s’installe avec une clé à usage unique que
  vous tapez au premier démarrage (`secrets/luks/<host>.once`). Le premier `apply`
  la remplace par `secrets/luks/<host>.key`, et un master reçoit aussi une nouvelle
  clé de volume. Perdre ce fichier de clé verrouille le disque : gardez donc la
  fleet sauvegardée.
- **CoreOS / uCore** chiffrent à l’installation via Ignition (avec environ 4 Gio de
  RAM au premier démarrage).
- **Les anneaux Tang** permettent aux machines chiffrées de se déverrouiller au
  démarrage sans personne sur place. Un node fait tourner le module `tang` (chaque
  anneau est un serveur Tang avec ses propres clés, `infra` sur le port 7500 par
  défaut), et le bloc `unlock:` d’un hôte lie son disque à des anneaux avec un
  seuil.
- **SSH dans l’initramfs** (`unlock.ssh: true` : dropbear sous Debian, dracut-sshd
  sous CoreOS) utilise sa propre clé restreinte, `secrets/unlock_ed25519`, qui ne
  peut que lancer le déverrouillage.
- `kiwi-server unlock fleet.yaml <host>` transmet un anneau à une machine qui
  attend au démarrage, et `--manual` remet la clé elle-même. Un anneau `operator`
  est servi depuis votre propre machine tant qu’on en a besoin.
  `vpn-server.unlock_relay` atteint les machines derrière un NAT.

## MTU du tunnel { #tunnel-mtu }

WireGuard ajoute ses propres en-têtes, si bien qu’un tunnel transporte des paquets
plus petits que la ligne qui est en dessous, et un chemin mobile des paquets plus
petits encore. Un paquet trop gros pour un lien en chemin est rejeté ou fragmenté,
et les connexions se bloquent. Kiwi gère cela en trois couches :

- **Deux réglages.** `wg_mtu` (par défaut **1376**, un multiple de 16 car
  WireGuard complète à 16) est la MTU de gluetun, des configurations client de
  wg-easy et de `wg0`. `bridge_mtu` (par défaut **1500**) est la MTU du réseau de
  la stack. `validate` refuse un `wg_mtu` dont le paquet complété plus 80 octets
  d’en-têtes ne tient pas dans le pont, et toute valeur inférieure à 1280, le
  minimum avec lequel IPv6 fonctionne.
- **La MSS est limitée dans les deux sens** à `wg_mtu - 40`, dans wg-easy et dans
  le client VPN, si bien que TCP ne tente jamais un segment qui ne peut pas passer.
- **TCP sonde de lui-même.** Le client VPN tourne avec
  `net.ipv4.tcp_mtu_probing=1` et `tcp_base_mss=1024`, si bien qu’une connexion
  qui tombe sur un chemin rejetant silencieusement les gros paquets trouve une
  taille qui fonctionne au lieu de rester bloquée.

### Mesurer un chemin : `kiwi-server mtu` { #measuring-a-path-kiwi-server-mtu }

```bash
kiwi-server mtu fleet.yaml papaya --ssh core@<address>   # un node
kiwi-server mtu fleet.yaml phone --ssh core@<master>     # un appareil de secrets/devices/
kiwi-server mtu fleet.yaml papaya --write                # et écrire wg_mtu dans le fichier fleet
```

La sonde envoie des pings sans fragmentation à travers le tunnel, depuis
l’intérieur de l’espace de noms qui le contient. Elle mesure un node depuis son
propre client VPN (dont le pare-feu rejette les pings entrants), et un appareil
depuis le serveur WireGuard. Elle commence par un ping ordinaire, puis essaie
chaque multiple de 16 à partir de 1280 en montant, et indique le plus grand qui
arrive **entier**. Pendant qu’elle envoie les pings, elle lit les compteurs de
réassemblage du noyau, si bien qu’une réponse fragmentée en chemin puis
réassemblée ne compte pas comme passant.

Elle dit aussi quoi régler. Pour un **appareil**, c’est le `MTU =` propre à
l’appareil dans sa configuration WireGuard, et personne d’autre n’est concerné.
Pour un **node**, c’est `wg_mtu` sur ce node et sur son master, que `--write` écrit
dans le fichier fleet (en ne modifiant que ces lignes). Un paquet qui n’est
fragmenté que dans le sens sortant et réassemblé par l’autre extrémité ne peut pas
être vu depuis cette extrémité-ci.

Les valeurs par défaut ont été mesurées sur la fleet de test. Pour un téléphone sur
données mobiles, où les chemins sont souvent uniquement IPv6 derrière 464XLAT avec
une encapsulation imbriquée, mesurez le téléphone lui-même et baissez son propre
`MTU =` si la sonde l’indique.

## VPS netcup { #netcup-vpses }

```bash
kiwi-server vps login fleet.yaml         # connexion par device flow ; le jeton va dans secrets/
kiwi-server vps list fleet.yaml
kiwi-server vps install fleet.yaml sorbet  # wipe the server and install the host's ISO
```

`vps install` demande d’abord confirmation, sauf si vous passez `--yes`. Il refuse
une ISO qui contient des secrets de rôle, un `disk:` erroné, et le chiffrement de
disque CoreOS avec moins de 3500 Mio de RAM.
