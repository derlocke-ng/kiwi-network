# Travailler dans les réseaux de nombreux clients

Si vous travaillez à distance pour de nombreux clients, il vous faut en
général une connexion VPN ou SOCKS distincte pour accéder au réseau de chacun.
Dix clients, cela fait dix connexions. Les faire toutes tourner sur l’hôte pose
des problèmes : dix tunnels sont actifs en même temps, leurs routes entrent en
conflit, et le trafic destiné au réseau d’un client peut atterrir dans celui
d’un autre.

Les applications Kiwi du poste de travail vous permettent de travailler dans
le réseau de chaque client de façon isolée. L’hôte n’est pas encombré de
tunnels et de routes, et vous n’avez pas dix connexions VPN actives en même temps.
Chaque connexion est placée dans son propre conteneur, et la seule route qui
sort de ce conteneur mène à ce client-là. Une telle connexion s’appelle un
**exit**. Vos outils tournent dans un conteneur ou un profil de navigateur qui
passe par l’exit dont il a besoin, et rien d’autre ne change sur l’hôte.

| Application | Ce qu’elle fait |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Le moteur sur lequel reposent les autres applications. Un **exit** est une connexion vers un upstream, enregistrée sous un nom. L’upstream est le proxy auquel votre trafic est envoyé : soit un proxy SOCKS5 qu’on vous a fourni, soit un proxy créé par un module fournisseur. Quand vous démarrez un exit, kiwi-proxy crée pour lui une **gateway**. La gateway est un namespace réseau (une pile réseau séparée, avec ses propres routes et son propre pare-feu) dont la seule route mène à cet upstream. Les programmes de l’hôte peuvent utiliser un exit par un port SOCKS5 local |
| [**kiwi-custodia**](kiwi-custodia.md) | **Des distributions Linux dans des box qui passent par un exit.** Une box kiwi-custodia est un conteneur rootless (qui tourne sans droits root) contenant Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky ou Alpine, avec son propre dossier personnel. *Tout* le trafic réseau de la box passe par l’exit, y compris celui des gestionnaires de paquets, des jeux et des programmes liés statiquement qui ignorent les réglages de proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Des profils de navigateur qui passent par un exit.** Chaque profil fait tourner Camoufox, Firefox ou Tor Browser et a son propre stockage |
| [**Modules fournisseurs**](providers.md) | Des modules qui créent des exits par Tor, par un VPN (avec gluetun), par 9proxy ou par Mysterium. Tor et Mysterium sont un moyen rapide d’obtenir davantage d’adresses IP, ce qui est utile pour les tests |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Comment les exits restent séparés { #how-it-stays-clean }

- **Une gateway est fail-closed** : une panne coupe le trafic et ne lui ouvre
  jamais un autre chemin. Le pare-feu d’une gateway rejette tout ce qui n’est
  pas destiné à son unique upstream. Si la gateway s’arrête, tout ce qui
  passait par elle n’a plus de route. Aucun programme n’a besoin de remarquer
  la panne et d’y réagir : sans la gateway, il n’y a tout simplement pas de
  route.
- **Seul ce que vous utilisez tourne.** Quand une box ou un navigateur démarre
  une gateway, celle-ci est supprimée dès que la dernière box ou le dernier
  navigateur qui l’utilisait s’est arrêté. Seuls les exits que vous démarrez
  vous-même avec `kiwi-proxy up` restent actifs.
- **Les clients restent séparés.** Les box et les navigateurs qui utilisent le
  même exit le partagent : ils ont la même adresse IP et le même namespace
  réseau. Des clients qui ne doivent pas se voir reçoivent des exits
  différents. Chaque box a aussi son propre dossier personnel : les clés SSH et
  les profils de navigateur d’un client ne sont donc pas accessibles dans la
  box d’un autre client.
- **Pas de droits root, pas de routes sur l’hôte.** Tout tourne dans Podman
  rootless, qui fait tourner les conteneurs sous votre propre utilisateur. Le
  réseau de l’hôte n’est pas modifié.
- **Les requêtes DNS passent elles aussi par l’exit.** Par défaut, les noms
  sont résolus en DNS over HTTPS (DoH) à travers l’exit, et des listes de
  domaines publicitaires sont bloquées. Pour résoudre les **noms d’hôte
  internes** d’un client, utilisez plutôt `--dns remote` : les noms sont alors
  transmis du côté du client et résolus là-bas. Tor et les noms `.onion` ont
  eux aussi besoin de ce mode.

## Limites { #limits }

Ces limites sont indiquées dans les dépôts :

- **Uniquement TCP et uniquement IPv4.** UDP n’est pas transmis, donc QUIC et
  les flux média de WebRTC ne fonctionnent pas. Il n’y a pas de route pour
  IPv6.
- **Une seule configuration VPN par machine.** Le module fournisseur VPN n’a
  qu’une configuration gluetun, avec un seul `vpn.json` et une seule
  configuration WireGuard personnalisée. Ses exits ne diffèrent que par le pays
  du serveur. Si vous avez besoin en même temps des VPN propres à plusieurs
  clients, la solution actuelle est un point d’accès SOCKS5 par client.
- **Une box restreint le réseau, mais ce n’est pas un bac à sable.** Comme un
  conteneur distrobox, elle partage votre affichage, votre bus de session et
  votre presse-papiers. Ce qu’elle ne peut pas faire, c’est accéder au réseau
  autrement que par son exit.
- **Mysterium :** une identité ne peut avoir qu’une connexion à la fois.

## Pour commencer { #get-started }

Les commandes suivantes installent les applications, enregistrent le proxy
SOCKS5 d’un client comme exit, et ouvrent un shell dans une box Fedora qui
passe par cet exit :

```bash
kiwi install kiwi-custodia            # installe aussi kiwi-proxy
kiwi-custodia setup                   # images et données DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # un shell qui ne joint le réseau que par le SOCKS5 du client A
```
