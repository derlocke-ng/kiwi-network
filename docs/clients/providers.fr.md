# Modules fournisseurs

Dans [kiwi-proxy](kiwi-proxy.md), un exit est une connexion nommée vers un
upstream, par laquelle vos box et vos navigateurs font passer leur trafic. Le
plus souvent, c’est une connexion qu’on vous a fournie, comme le proxy SOCKS5
qui donne accès au réseau d’un client. Un module fournisseur sert dans l’autre
cas : il crée lui-même l’exit, par Tor, par un abonnement VPN, par 9proxy ou
par Mysterium. Tor et Mysterium, en particulier, sont là pour vous donner
davantage d’adresses IP pour vos tests.

Chaque module a son propre dépôt. kiwi-updater l’installe dans le répertoire
des modules de kiwi-proxy, et c’est ensuite kiwi-proxy qui le gère :
kiwi-proxy construit l’image de conteneur du module, démarre le module quand un
exit en a besoin, et l’arrête quand plus aucune gateway ne l’utilise. Une
gateway est le conteneur que kiwi-proxy fait tourner pour un exit tant que cet
exit est actif.

| Module | Dépôt | Version | Exit | Prérequis |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | le réseau Tor, avec un circuit par exit et n’importe quel pays de sortie | rien (c’est gratuit) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | un tunnel WireGuard ou OpenVPN via [gluetun](https://github.com/qdm12/gluetun) | un abonnement VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | une adresse résidentielle fournie par [9proxy](https://9proxy.com/) | un compte 9proxy et le client propriétaire de 9proxy, qui n’est pas redistribué |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | le dVPN [Mysterium](https://mysterium.network/) (un VPN décentralisé), avec une liste de nœuds parmi lesquels vous choisissez par pays et par type d’IP | une identité de consommateur enregistrée, avec un solde en MYST |

Les quatre modules sont sous licence GPL-3.0-or-later et figurent dans le
[catalogue Kiwi](../desktop/catalogs.md). Chacun déclare `DEPENDS=kiwi-proxy`,
si bien que kiwi-updater installe d’abord kiwi-proxy. Tor et Mysterium sont le
moyen rapide d’obtenir davantage d’adresses IP pour vos exits, par exemple
pour des tests.

## Installation et utilisation { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # construire son image (kiwi-proxy setup les fait toutes)
kiwi-proxy module list
kiwi-proxy module countries tor                  # les pays où Tor peut sortir
kiwi-proxy add tor-de --module tor --country de  # un exit fourni par ce module
kiwi-custodia new test --exit tor-de             # une box qui passe par lui, ou :
kiwi-fox new test --exit tor-de                  # un profil de navigateur qui passe par lui
```

Pour un exit Tor, le pays est imposé par l’option `StrictNodes` de Tor. Un
circuit qui ne peut pas sortir dans ce pays échoue, et ne sort jamais dans un
autre pays. Les exits du module tor transmettent les identifiants SOCKS que
Tor Browser envoie pour chaque site. C’est leur réglage par défaut
(`--socks-auth passthrough`).

## Comment un fournisseur est relié à une gateway { #how-it-is-wired }

**Chaque fournisseur propose du SOCKS5, et rien d’autre.** Un conteneur de
fournisseur a besoin de sa propre connexion à Internet. Il ne peut donc pas
tourner dans le namespace réseau d’une gateway, puisque tout y est rejeté sauf
le trafic vers une seule destination. Le fournisseur et la gateway sont donc
reliés par un réseau bridge de Podman rootless, `kf-providers`, sur lequel
chaque module a une adresse fixe :

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** propose lui-même du SOCKS5. kiwi-proxy envoie des identifiants
  différents pour chaque exit, et l’option `IsolateSOCKSAuth` de Tor donne
  alors à chaque exit son propre circuit, c’est-à-dire son propre chemin à
  travers le réseau Tor.
- **VPN et Mysterium** passent par un tunnel, et un tunnel ne propose pas de
  SOCKS5. Un petit adaptateur, microsocks, rejoint donc le namespace réseau du
  tunnel. Il propose du SOCKS5 et fait passer le trafic par le tunnel.
- **9proxy** fait tourner le client 9proxy, qui ouvre un port SOCKS5 menant à
  une adresse résidentielle.

Un même conteneur de fournisseur sert tous les exits qui utilisent le même
module et le même bail (lease). Un bail est l’un des exits qu’un module
propose au choix, par exemple le pays d’un serveur VPN ou un nœud Mysterium.
Si un tunnel perd sa session, il reste fermé (fail-closed), c’est-à-dire
qu’aucun trafic ne sort, puis il est redémarré.

## Configuration { #configuration }

L’état de chaque module est stocké dans
`~/.local/share/kiwi-proxy/modules-state/<module>/`, en dehors de tout dépôt :

- **vpn** : le fichier `vpn.json` contient les réglages de gluetun, comme
  `VPN_SERVICE_PROVIDER`, `VPN_TYPE` et `WIREGUARD_ADDRESSES`. Chaque clé en
  majuscules est transmise telle quelle à gluetun. Le fichier peut aussi
  contenir une liste `leases`. Un répertoire `gluetun/`, facultatif, contient
  d’autres fichiers, par exemple un `wireguard.conf` pour le fournisseur
  `custom` de gluetun. Il y a une seule configuration de ce type par machine,
  et les exits qui en dépendent ne diffèrent que par le pays du serveur.
- **9proxy** : le fichier de configuration est `config/account.conf`. Le
  client propriétaire n’est pas fourni. Avant de lancer
  `kiwi-proxy module setup 9proxy`, placez le client dans le répertoire
  `module/containers/vendor/` du plugin et ajoutez `COPY vendor/ /opt/9proxy/`
  au `Containerfile` du plugin. Sans le client, l’image est tout de même
  construite, mais le fournisseur refuse de démarrer et n’ouvre aucun port.
- **mysterium** : lancez `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, ou utilisez *Configure…* dans l’application Kiwi Proxy. La
  phrase de passe est enregistrée comme secret Podman. Une identité ne peut
  avoir qu’une connexion à la fois.

## État { #status }

Tor ne demande aucun compte. Le module Mysterium a été vérifié de bout en bout
le 7 novembre 2026. D’après leurs README, les modules VPN et 9proxy sont
complets et ont des tests unitaires, mais ils n’ont pas encore tourné de bout
en bout avec un vrai abonnement ou un vrai compte.
