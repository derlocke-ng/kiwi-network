# Travailler avec de nombreux réseaux clients

Dix clients à distance, c’est souvent dix VPN ou points d’accès SOCKS, un pour
atteindre le réseau de chaque client. Les faire tous tourner sur l’hôte tourne au
chaos : dix tunnels à la fois, des routes qui se battent, et un réseau qui fuit dans
le suivant. Les applications de bureau Kiwi donnent plutôt à chacun une **sortie
scellée** : un conteneur dont la seule route est cet amont-là. Vos outils rejoignent
la sortie dont ils ont besoin, et rien d’autre ne change sur l’hôte.

| Application | Ce qu’elle fait |
|---|---|
| [**kiwi-proxy**](kiwi-proxy.md) | Le moteur. Une **sortie** est un amont désigné par un nom : un SOCKS5 qu’on vous a fourni, ou un que produit un module de fournisseur. La démarrer crée une **gateway**, un espace de noms réseau dont la seule route est cet amont. Les applications de l’hôte peuvent l’utiliser comme port SOCKS5 local |
| [**kiwi-custodia**](kiwi-custodia.md) | **Des box de distributions sur une sortie** : Fedora, Ubuntu, Debian, Kali, Arch, openSUSE, Rocky ou Alpine dans un conteneur rootless avec son propre répertoire personnel. *Tout* ce qui est dans la box sort par la sortie : gestionnaires de paquets, jeux, binaires statiques qui n’ont jamais entendu parler d’un proxy |
| [**kiwi-fox**](kiwi-fox.md) | **Des profils de navigateur sur une sortie** : Camoufox, Firefox ou Tor Browser, chaque profil avec son propre stockage |
| [**Modules de fournisseurs**](providers.md) | Des sorties via Tor, un VPN (gluetun), 9proxy ou Mysterium. Tor et Mysterium sont le moyen rapide d’obtenir plus d’IP de sortie, pratique pour les tests |

```
 client A: socks5://…  ─┐                                   ┌─ box "client-a" (Fedora: ssh, ansible, dnf …)
 client B: socks5://…  ─┼─ kiwi-proxy exits ─▶ gateways ───┼─ browser profile "client-b"
 Tor / Mysterium / VPN ─┘   one per upstream   only route   └─ curl, mail, any app: socks5h://127.0.0.1:1082
                                               is the exit
```

## Comment tout reste propre { #how-it-stays-clean }

- **En cas de panne, tout se ferme.** Le pare-feu d’une gateway rejette tout sauf
  son unique amont. Si la gateway tombe, tout ce qui l’a rejointe perd sa route. Le
  kill switch, c’est l’absence de route, pas un logiciel qui doit s’en apercevoir.
- **Rien ne tourne sans être utilisé.** Une gateway démarrée par une box ou un
  navigateur disparaît quand le dernier la quitte. Seules les sorties que vous
  démarrez avec `kiwi-proxy up` restent actives.
- **Ce qui est séparé reste séparé.** Ce qui est sur la même sortie la partage (une
  IP, un espace de noms). Les clients qui ne doivent pas se rencontrer ont des
  sorties différentes, et chaque box a son propre répertoire personnel, si bien que
  les clés SSH et les profils de navigateur ne se croisent pas.
- **Pas de root, pas de routes sur l’hôte.** Tout tourne dans Podman rootless, et le
  réseau de l’hôte lui-même n’est pas touché.
- **Le DNS passe aussi par la sortie.** Par défaut, les noms sont résolus en DoH à
  travers la sortie, avec des listes de blocage de publicités. Pour les **noms
  d’hôtes internes** d’un client, confiez plutôt les noms au côté du client avec
  `--dns remote` (c’est aussi le mode pour Tor et les noms `.onion`).

## Limites { #limits }

Elles viennent des dépôts :

- **TCP uniquement, IPv4 uniquement.** L’UDP ne sort nulle part (pas de QUIC, pas
  de média WebRTC), et l’IPv6 n’a pas de route.
- **Une seule configuration VPN par machine.** Le module de fournisseur VPN contient
  une seule configuration gluetun (un `vpn.json`, une configuration WireGuard
  personnalisée), et ses sorties ne diffèrent que par le pays du serveur. Pour faire
  cohabiter les VPN de plusieurs clients, un point d’accès SOCKS5 par client est la
  voie à suivre aujourd’hui.
- **Une box, c’est une garde réseau, pas un bac à sable.** Elle partage votre
  affichage, votre bus de session et votre presse-papiers, comme distrobox. Ce
  qu’elle ne peut pas faire, c’est atteindre le réseau autrement que par sa sortie.
- **Mysterium :** une identité ne tient qu’une connexion à la fois.

## Pour commencer { #get-started }

```bash
kiwi install kiwi-custodia            # installe aussi kiwi-proxy
kiwi-custodia setup                   # images et données DNS

kiwi-proxy add client-a socks5://user:pass@jump.client-a.example:1080 --dns remote
kiwi-custodia new client-a --exit client-a --distro fedora
kiwi-custodia enter client-a          # a shell whose only way out is client A's SOCKS5
```
