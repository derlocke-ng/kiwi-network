# kiwi-cli-tools-desktop

Quatre petits utilitaires en ligne de commande pour un bureau Linux.

- Dépôt : [derlocke-ng/kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop), GPL-3.0-or-later
- Dernière version : **v1.2.1**. Elle figure dans le [catalogue Kiwi](catalogs.md), portée utilisateur.

```bash
kiwi install kiwi-cli-tools-desktop   # ou ./install.sh install, dans ~/.local/bin
```

## `torlink` : atteindre une machine via Tor { #torlink-reach-a-machine-over-tor }

Un VPN du pauvre : atteindre n’importe quel service TCP (SSH, une interface web,
une base de données) sur une autre machine via Tor, sans port ouvert, sans compte
et sans serveur. Tor et socat tournent dans un seul conteneur Podman rootless, donc
Podman est tout ce qu’il vous faut.

Une adresse onion est l’identité. Le côté qui propose crée un **code
d’invitation** pour un pair, et l’autre côté l’accepte. Le code contient une clé
d’autorisation client Tor, si bien que le service est invisible pour quiconque ne
l’a pas : traitez le code comme un mot de passe.

```bash
# machine A : proposer SSH et une interface web à "bob"
torlink add-service ssh 22
torlink add-service web 8080
torlink invite bob ssh web          # affiche torlink1:…  (secret !)

# machine B : les utiliser
torlink accept torlink1:… alice
torlink up
torlink ssh alice                   # SSH via Tor
torlink connect alice web           # 127.0.0.1:2200 → alice's web UI
torlink ssh-config >> ~/.ssh/config # then `ssh alice-tor`; `select-server tor` lists them
```

Chaque invitation est son propre service onion avec uniquement les services que
vous avez listés, si bien que `torlink revoke bob` retire cet accès pour de bon.
`torlink ls` montre les services, les pairs et les redirections. Tor ne fait que du
TCP, et la première connexion prend un moment. Le port SOCKS du conteneur (19050)
n’écoute que sur la boucle locale. L’état, y compris vos clés onion, se trouve dans
`~/.local/share/torlink`, et `torlink purge` le supprime.

## `pweb` : partager un dossier en HTTPS { #pweb-share-a-folder-over-https }

Sert le **répertoire courant** en HTTPS sur un port libre aléatoire, pour passer un
fichier à une autre machine du même réseau. Un certificat auto-signé est créé au
premier lancement et réutilisé ensuite. Il sert tout le LAN : lancez-le donc dans le
dossier que vous voulez partager et arrêtez-le avec Ctrl+C.

```
$ cd ~/Downloads && pweb
serving /home/you/Downloads
on https://yourhost:40123  (also https://localhost:40123)
```

## `select-server` : choisir un hôte SSH { #select-server-pick-an-ssh-host }

Un menu numéroté de chaque alias `Host` concret de votre `~/.ssh/config`. Choisissez
en un et il s’y connecte. Étiquetez les hôtes avec un commentaire `# tags: work prod`
dans le bloc `Host` pour filtrer :

```
$ select-server work            # only hosts tagged "work"
$ select-server --tags          # les étiquettes que vous avez
$ select-server -f other.conf   # un autre fichier de configuration
```

## `tethering` : le correctif TTL { #tethering-the-ttl-fix }

Fixe un TTL de 64 sur le trafic qui arrive d’une interface, si bien que les
appareils partagés via cette machine ressemblent au trafic propre de la machine
pour un opérateur qui compte les sauts. Il demande sudo, ajoute une règle
`iptables` mangle, et la règle ne survit **pas** à un redémarrage.

```
tethering            # choisir l’interface, poser la règle
tethering --status
tethering --off
```
