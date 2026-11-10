# kiwi-proxy

kiwi-proxy s’adresse aux personnes qui travaillent dans les réseaux de nombreux
clients et qui accèdent à chacun par sa propre connexion VPN ou SOCKS. Vous
enregistrez chaque connexion comme un **exit** nommé, et vous ne le démarrez
que quand vous en avez besoin. Chaque exit est isolé des autres, et un
programme qui passe par un exit ne peut accéder au réseau que par lui. Avec
dix clients, vous n’avez donc pas dix connexions VPN actives en même temps sur
l’hôte. Des navigateurs, des outils de test, des programmes de l’hôte et des
machines kiwi-server peuvent utiliser un exit. kiwi-proxy tourne dans Podman
rootless, c’est-à-dire dans des conteneurs qui tournent sous votre propre
utilisateur, sans droits root.

- Dépôt : [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Dernière version : **v0.7.3**. Il figure dans le [catalogue Kiwi](../desktop/catalogs.md), en portée utilisateur.
- Il se compose d’un outil en ligne de commande (`kiwi-proxy`), d’une
  application GTK4 (**Kiwi Proxy**) et d’unités utilisateur systemd. C’est le
  moteur de proxy qui faisait autrefois partie de kiwi-fox. Il en a été sorti
  pour devenir un projet à part entière, afin que plusieurs applications
  puissent s’en servir.

Un **exit** est une connexion vers un upstream, enregistrée sous un nom.
L’upstream est le proxy auquel le trafic est envoyé : soit un proxy SOCKS5
qu’on vous a fourni, soit un proxy qu’un [module fournisseur](providers.md)
crée pour vous par Tor, un tunnel VPN, 9proxy ou Mysterium. À lui seul, un
exit n’est qu’une entrée enregistrée, et rien ne tourne pour lui. Quand vous
démarrez un exit, kiwi-proxy lance pour lui un conteneur **gateway** :

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

C’est la gateway qui détient le namespace réseau, c’est-à-dire une pile réseau
séparée, avec ses propres routes et ses propres règles de pare-feu. Un
navigateur kiwi-fox, une box kiwi-custodia ou un conteneur d’outils rejoint ce
namespace et devient membre de la gateway. À partir de là, sa seule route mène
à l’upstream de l’exit. Si la gateway s’arrête, ses membres n’ont plus de
route du tout. C’est ce qu’on appelle un fonctionnement fail-closed : une panne
coupe la connexion et n’ouvre jamais un autre chemin.

## Installation { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox et kiwi-custodia l’installent aussi
kiwi-proxy setup             # l’image de la gateway, les données DNS, les images des modules fournisseurs
```

kiwi-proxy a besoin de Podman rootless et de Python 3.12+ avec pydantic.
L’application a aussi besoin de GTK4 et de libadwaita. Les mots de passe sont
enregistrés dans le trousseau du bureau par `secret-tool`. Sur une machine
sans trousseau, ils sont enregistrés dans des fichiers en mode 0600, que seul
votre utilisateur peut lire.

## Utilisation { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # un exit ; rien ne tourne encore
kiwi-proxy add tor-de --module tor --country de        # un exit fourni par un module
kiwi-proxy list
kiwi-proxy check client-a      # ce que le monde voit à travers lui
kiwi-proxy up client-a         # démarrer sa gateway et la garder active
kiwi-proxy down client-a       # l’arrêter, avec tout ce qui y était rattaché
kiwi-proxy ps                  # les gateways actives, quelle que soit l’application qui les a lancées
kiwi-proxy reap                # arrêter les gateways que plus personne n’utilise
kiwi-proxy-gui                 # « Kiwi Proxy » dans la grille d’applications
```

Un point d’accès (endpoint) est l’adresse d’un upstream. Vous pouvez l’écrire
sous la forme `socks5://user:pass@host:port`, `http://…` ou `https://…`, ou au
format des vendeurs de proxys, `host:port:user:pass`.
`kiwi-proxy test ENDPOINT` teste un point d’accès sans créer d’exit.

### Exits pour les applications de l’hôte { #exits-for-host-applications }

Un programme de l’hôte n’a pas besoin de tourner dans un conteneur pour
utiliser un exit. kiwi-proxy peut publier un exit sous forme de port SOCKS5
sur l’hôte, avec un port par exit :

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Par défaut, le port n’écoute que sur `127.0.0.1`. Si vous le faites écouter
sur une autre adresse, vous devez soit définir un nom d’utilisateur avec
`--expose-user`, soit autoriser explicitement l’accès libre avec
`--expose-open`. Pour qu’un exit soit actif dès l’ouverture de votre session,
lancez `systemctl --user enable --now kiwi-proxy@NAME`.

### DNS { #dns }

- **Le mode résolveur** est le mode par défaut. dnscrypt-proxy résout les noms
  en DNS over HTTPS (DoH) et envoie ces requêtes à travers l’exit. Le
  résolveur DoH peut être Google, Cloudflare, Quad9 ou Mullvad. Des listes de
  blocage (OISD) sont appliquées, et elles sont actualisées chaque jour.
- **Le mode distant** (`--dns remote`) transmet les noms à l’upstream, qui les
  résout lui-même. Ce mode est fait pour Tor et les noms `.onion`. Les listes
  de blocage s’appliquent aussi dans ce mode.

### Règles de la gateway { #rules-of-the-gateway }

- UDP n’est pas transmis. Il n’y a donc ni QUIC, ni flux média WebRTC, ni DNS
  en clair.
- Un exit ne joint l’extérieur qu’en IPv4. Un nom qui n’a pas d’adresse IPv4
  est refusé.
- Une gateway lancée par une autre application, comme kiwi-fox ou
  kiwi-custodia, est supprimée quand son dernier membre s’en va. Une gateway
  que vous avez lancée avec `kiwi-proxy up` reste active jusqu’à ce que vous
  lanciez `kiwi-proxy down`.
- Chaque exit a exactement une gateway, et autant de membres que vous voulez
  peuvent la rejoindre. Des membres qui doivent rester séparés les uns des
  autres utilisent des exits différents.

## L’application { #the-app }

Dans l’application **Kiwi Proxy**, vous pouvez ajouter et modifier des exits,
soit à partir d’un proxy SOCKS5 qu’on vous a fourni, soit à partir d’un module
fournisseur. Pour un exit fourni par un module, vous choisissez dans une liste
de pays où l’on peut chercher, ou dans une liste de nœuds. Vous pouvez démarrer
et arrêter des exits, proposer un exit sous forme de port SOCKS5 sur cet
ordinateur et copier son adresse, et vérifier ce que voit le monde extérieur
quand vous vous connectez à travers lui. L’application montre aussi quels
membres ont rejoint une gateway, avec leurs journaux, et elle installe et
configure les modules fournisseurs.

## Sur une machine kiwi-server { #on-a-kiwi-server-machine }

Le dépôt de kiwi-proxy contient aussi un module pour kiwi-server. Avec lui, une
machine kiwi-server héberge des exits pour tout le mesh, c’est-à-dire le réseau
WireGuard privé qui relie vos machines kiwi-server. Le module fait tourner une
gateway par exit et la publie sur l’adresse mesh de l’hôte. Sa documentation
indique que le module ne fait pas encore partie du code source de kiwi-server
et qu’il n’a encore tourné sur aucune machine. Les modules fournisseurs ne
fonctionnent que sur le poste de travail : ils ne tournent pas sur une machine
kiwi-server.

Pour aller plus loin : [architecture](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[applications qui l’utilisent](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[système de plugins](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
