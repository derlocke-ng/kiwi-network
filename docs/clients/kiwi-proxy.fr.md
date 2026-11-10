# kiwi-proxy

Des sorties SOCKS5 et VPN scellées dans Podman rootless, pour les navigateurs, les
outils de test, les applications de l’hôte et les machines kiwi-server.

- Dépôt : [derlocke-ng/kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy), GPL-3.0-or-later
- Dernière version : **v0.7.3**. Elle figure dans le [catalogue Kiwi](../desktop/catalogs.md), portée utilisateur.
- Une CLI (`kiwi-proxy`), une application GTK4 (**Kiwi Proxy**) et des unités
  utilisateur systemd. C’est le moteur de proxy qui se trouvait auparavant dans
  kiwi-fox, séparé pour servir plus d’une application.

Une **sortie** est un amont désigné par un nom : un SOCKS5 qu’on vous a fourni, ou
un que produit un [module de fournisseur](providers.md) (Tor, un tunnel VPN,
9proxy, Mysterium). Une sortie n’est que des données. La démarrer crée une
**gateway** :

```
gateway container   owns the network namespace
                    nftables: default drop, one permitted destination
                    forwarder 127.0.0.1:1080: adds the upstream's credentials
                    dnscrypt-proxy 127.0.0.2:53: DNS through the same exit, with blocklists
```

Tout ce qui rejoint l’espace de noms de la gateway (un navigateur kiwi-fox, une box
kiwi-custodia, un conteneur d’outils) n’a aucune route hormis cet amont. Si la
gateway tombe, ses membres perdent leur route.

## Installation { #install }

```bash
kiwi install kiwi-proxy      # kiwi-fox et kiwi-custodia l’installent aussi
kiwi-proxy setup             # l’image de gateway, les données DNS, les images des modules de fournisseurs
```

Il faut Podman rootless, Python 3.12+ avec pydantic, et GTK4 + libadwaita pour
l’application. Les mots de passe vont dans le trousseau du bureau (`secret-tool`),
ou dans des fichiers 0600 sur une machine qui n’en a pas.

## Utilisation { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # une sortie ; rien ne tourne encore
kiwi-proxy add tor-de --module tor --country de        # une sortie depuis un module de fournisseur
kiwi-proxy list
kiwi-proxy check client-a      # ce que le monde voit à travers elle
kiwi-proxy up client-a         # démarrer sa gateway et la garder active
kiwi-proxy down client-a       # l’arrêter, avec ceux qui l’ont rejointe
kiwi-proxy ps                  # gateways en cours, quelle que soit l’application qui les a démarrées
kiwi-proxy reap                # arrêter les gateways que personne n’utilise
kiwi-proxy-gui                 # "Kiwi Proxy" in the app grid
```

Les points d’accès sont `socks5://user:pass@host:port`, `http://…`, `https://…`, ou
le format fournisseur `host:port:user:pass`. `kiwi-proxy test ENDPOINT` en sonde un
sans rien créer.

### Sorties pour les applications de l’hôte { #exits-for-host-applications }

N’importe quel programme de l’hôte peut utiliser une sortie via un port SOCKS5
publié, un port par sortie :

```bash
kiwi-proxy add se socks5://10.64.0.1:1080 --expose 1081
kiwi-proxy add nl socks5://10.65.0.1:1080 --expose 1082
kiwi-proxy up se && kiwi-proxy up nl
curl --proxy socks5h://127.0.0.1:1082 https://ifconfig.co/json
```

Le port écoute sur `127.0.0.1` par défaut. Une autre adresse exige un nom
d’utilisateur (`--expose-user`) ou un `--expose-open` explicite.
`systemctl --user enable --now kiwi-proxy@NAME` garde une sortie active dès la
connexion.

### DNS { #dns }

- **Mode résolveur** (par défaut) : dnscrypt-proxy résout en DoH à travers la sortie
  (Google, Cloudflare, Quad9 ou Mullvad comme amont), avec des listes de blocage
  (OISD) actualisées chaque jour.
- **Mode distant** (`--dns remote`) : les noms vont à l’amont lui-même, pour Tor et
  les noms `.onion`. Les listes de blocage s’appliquent toujours.

### Règles de la gateway { #rules-of-the-gateway }

- L’UDP ne sort nulle part : pas de QUIC, pas de média WebRTC, pas de DNS en clair.
- Vue du monde, une sortie est en IPv4. Un nom sans adresse IPv4 est refusé.
- Une gateway démarrée par un consommateur s’arrête quand son dernier membre part.
  Une gateway démarrée avec `kiwi-proxy up` reste jusqu’à `kiwi-proxy down`.
- Une sortie, une gateway, un nombre quelconque de membres. Les membres qui doivent
  rester séparés utilisent des sorties différentes.

## L’application { #the-app }

**Kiwi Proxy** ajoute et modifie des sorties (un SOCKS5 qu’on vous a fourni, ou un
module de fournisseur, avec une liste de pays où chercher ou un sélecteur de
nœuds), les démarre et les arrête, en propose une comme port SOCKS5 sur cet
ordinateur et copie son adresse, vérifie ce que le monde voit, montre qui a rejoint
une gateway ainsi que leurs journaux, et installe et configure les modules de
fournisseurs.

## Sur une machine kiwi-server { #on-a-kiwi-server-machine }

kiwi-proxy contient aussi un module kiwi-server qui héberge des sorties pour tout le
maillage (une gateway par sortie, publiée sur l’adresse de maillage de l’hôte). Il
n’est pas encore dans l’arborescence de kiwi-server et n’a encore tourné sur aucune
machine, comme le dit sa documentation. Les modules de fournisseurs sont un
mécanisme du bureau et n’y tournent pas.

Pour aller plus loin : [architecture](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/architecture.md),
[consommateurs](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/consumers.md),
[système de plugins](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md).
