# kiwi-cli-tools-desktop

kiwi-cli-tools-desktop réunit quatre petits outils en ligne de commande pour un
poste de travail Linux. `torlink` permet de joindre un service sur une autre
machine par Tor, `pweb` partage un dossier en HTTPS, `select-server` vous fait
choisir un hôte SSH dans un menu, et `tethering` ajuste le TTL du trafic des
appareils qui partagent la connexion de la machine.

- Dépôt : [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Dernière version : **v1.2.1**. Il figure dans le [catalogue Kiwi](catalogs.md), en portée utilisateur.

```bash
kiwi install kiwi-cli-tools-desktop   # ou ./install.sh install, dans ~/.local/bin
```

## `torlink` : joindre une machine par Tor { #torlink-reach-a-machine-over-tor }

`torlink` vous permet de joindre n’importe quel service TCP d’une autre
machine, comme SSH, une interface web ou une base de données, à travers le
réseau Tor. C’est un substitut simple à un VPN : aucune des deux machines n’a
besoin d’un port ouvert, il ne faut aucun compte, et il n’y a pas de serveur à
faire tourner. Tor et socat tournent ensemble dans un conteneur Podman
rootless : Podman est donc tout ce dont vous avez besoin.

Une machine qui propose des services est identifiée par son adresse onion,
c’est-à-dire une adresse à l’intérieur du réseau Tor. Sur cette machine, vous
créez un **code d’invitation** pour un pair, c’est-à-dire l’autre partie qui
doit obtenir l’accès. Le pair accepte le code sur l’autre machine. Le code
contient une clé d’autorisation client Tor. Sans cette clé, personne ne peut
voir que le service existe : traitez donc le code comme un mot de passe.

```bash
# machine A : proposer SSH et une interface web à « bob »
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # affiche torlink1:…  (secret !)

# machine B : les utiliser
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH par Tor
torlink connect alice web           # 127.0.0.1:2200 → l’interface web d’alice
torlink ssh-config >> ~/.ssh/config # puis `ssh alice-tor` ; `select-server tor` les liste
```

Chaque invitation est un service onion distinct, qui ne contient que les
services que vous y avez mis. C’est pourquoi `torlink revoke bob` supprime cet
accès définitivement. `torlink ls` affiche vos services, vos pairs et vos
redirections, c’est-à-dire les ports locaux qui mènent aux services d’un pair.
Tor ne transporte que du TCP, et la première connexion prend un moment. Le
port SOCKS du conteneur (19050) n’écoute que sur l’interface de bouclage
(loopback). L’état de `torlink`, y compris vos clés onion, est stocké dans
`~/.local/share/torlink`, et `torlink purge` le supprime.

## `pweb` : partager un dossier en HTTPS { #pweb-share-a-folder-over-https }

`pweb` sert le **répertoire courant** en HTTPS, sur un port libre choisi au
hasard. Servez-vous-en pour faire passer un fichier à une autre machine du même
réseau. Au premier lancement, il crée un certificat autosigné, qu’il réutilise
ensuite. Tant que `pweb` tourne, toutes les machines du réseau local peuvent
accéder au dossier. Lancez-le dans le dossier que vous voulez vraiment
partager, et arrêtez-le avec Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server` : choisir un hôte SSH { #select-server-pick-an-ssh-host }

`select-server` affiche un menu numéroté de tous les alias `Host` concrets de
votre `~/.ssh/config`, c’est-à-dire de tous les alias qui ne sont pas des
motifs génériques. Choisissez-en un, et il s’y connecte. Pour filtrer le menu,
étiquetez vos hôtes : ajoutez un commentaire comme `# tags: work prod` dans le
bloc `Host`, et passez une étiquette sur la ligne de commande :

```
$ select-server work            # uniquement les hôtes étiquetés « work »
$ select-server --tags          # les étiquettes que vous avez
$ select-server -f other.conf   # un autre fichier de configuration
```

## `tethering` : régler le TTL pour les appareils connectés { #tethering-the-ttl-fix }

`tethering` sert quand d’autres appareils utilisent la connexion Internet de
cette machine, ce qu’on appelle le partage de connexion (tethering). Certains
opérateurs mobiles comptent les sauts réseau du trafic, et peuvent ainsi
distinguer les appareils connectés de la machine elle-même. `tethering` règle
le TTL à 64 pour tout le trafic qui arrive par une interface donnée. Pour
l’opérateur, le trafic des appareils connectés ressemble alors à celui de la
machine. L’outil demande sudo et ajoute une règle `iptables` de type mangle.
Cette règle ne survit **pas** à un redémarrage.

```
tethering            # choisir l’interface, poser la règle
tethering --status
tethering --off
```
