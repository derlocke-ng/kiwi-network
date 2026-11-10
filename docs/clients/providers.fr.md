# Modules de fournisseurs

Un module de fournisseur donne à [kiwi-proxy](kiwi-proxy.md) une sortie qu’il
produit lui-même, au lieu d’un SOCKS5 qu’on vous a fourni. Chacun vit dans son
propre dépôt, s’installe via kiwi-updater dans le répertoire des modules de
kiwi-proxy, et est géré par kiwi-proxy : celui-ci construit l’image du module, la
démarre quand une sortie en a besoin, et l’arrête quand plus aucune gateway ne
l’utilise.

| Module | Dépôt | Version | Sortie | Prérequis |
|---|---|---|---|---|
| `tor` | [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | v0.3.0 | le réseau Tor, un circuit par sortie, n’importe quel pays de sortie | rien (gratuit) |
| `vpn` | [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | v0.2.2 | un tunnel WireGuard ou OpenVPN via [gluetun](https://github.com/qdm12/gluetun) | un abonnement VPN |
| `9proxy` | [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | v0.2.0 | une sortie résidentielle [9proxy](https://9proxy.com/) | un compte 9proxy et son client propriétaire (non redistribué) |
| `mysterium` | [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | v0.5.2 | le dVPN [Mysterium](https://mysterium.network/), avec un sélecteur de nœuds par pays et type d’IP | une identité de consommateur enregistrée avec un solde en MYST |

Les quatre sont sous GPL-3.0-or-later, figurent dans le [catalogue Kiwi](../desktop/catalogs.md)
et déclarent `DEPENDS=kiwi-proxy`, si bien que kiwi installe d’abord kiwi-proxy. Tor
et Mysterium sont le moyen rapide d’obtenir plus d’IP de sortie, par exemple pour
les tests.

## Installation et utilisation { #install-and-use }

```bash
kiwi install kiwi-plugin-tor
kiwi-proxy module setup tor                      # construire son image (kiwi-proxy setup fait tout)
kiwi-proxy module list
kiwi-proxy module countries tor                  # où Tor peut sortir
kiwi-proxy add tor-de --module tor --country de  # une sortie depuis ce module
kiwi-custodia new test --exit tor-de             # une box dessus, ou :
kiwi-fox new test --exit tor-de                  # un profil de navigateur dessus
```

Pour Tor, le pays est imposé avec `StrictNodes`, si bien que le circuit échoue
plutôt que de sortir ailleurs. Les sorties sur le module tor transmettent par
défaut les identifiants SOCKS par site de Tor Browser (`--socks-auth passthrough`).

## Comment c’est câblé { #how-it-is-wired }

**Chaque fournisseur expose du SOCKS5 et rien d’autre.** Un conteneur de
fournisseur a besoin de sa propre issue, il ne peut donc pas vivre dans l’espace de
noms d’une gateway, où tout est rejeté sauf une destination. Les deux se
rencontrent sur un pont Podman rootless, `kf-providers`, où chaque module reçoit
une adresse fixe :

```
provider container ──── kf-providers bridge ──── gateway ──── box / browser / tool
(its own way out)                                permits only <provider-ip>:port
SOCKS5 only
```

- **Tor** parle déjà SOCKS5. kiwi-proxy envoie un identifiant par sortie, et
  l’option `IsolateSOCKSAuth` de Tor donne à chaque sortie son propre circuit.
- **VPN et Mysterium** passent par un tunnel qui ne parle pas SOCKS5 ; un petit
  adaptateur microsocks rejoint donc l’espace de noms réseau du tunnel et offre un
  SOCKS5 qui passe par le tunnel.
- **9proxy** fait tourner le client 9proxy, qui ouvre un port SOCKS5 sur une sortie
  résidentielle.

Un seul conteneur de fournisseur sert toutes les sorties sur le même module et le
même bail. Un tunnel qui perd sa session se ferme et est redémarré.

## Configuration { #configuration }

L’état de chaque module se trouve dans `~/.local/share/kiwi-proxy/modules-state/<module>/`,
en dehors de tout dépôt :

- **vpn** : `vpn.json` avec les réglages de gluetun (`VPN_SERVICE_PROVIDER`,
  `VPN_TYPE`, `WIREGUARD_ADDRESSES`, … ; chaque clé en majuscules est transmise
  telle quelle à gluetun), une liste `leases` facultative, et un répertoire
  `gluetun/` facultatif (par exemple un `wireguard.conf` pour le fournisseur
  `custom` de gluetun). C’est une seule configuration par machine : les sorties
  dessus diffèrent par le pays du serveur.
- **9proxy** : `config/account.conf`. Placez le client propriétaire dans
  `module/containers/vendor/` du plugin et ajoutez `COPY vendor/ /opt/9proxy/` à son
  `Containerfile` avant `kiwi-proxy module setup 9proxy`. Sans lui, l’image se
  construit, mais le fournisseur refuse de démarrer plutôt que d’ouvrir un port.
- **mysterium** : `kiwi-proxy module config mysterium keystore=/path/to/0x….json
  --ask passphrase`, ou *Configure…* dans l’application Kiwi Proxy. La phrase
  secrète devient un secret Podman. Une identité ne tient qu’une connexion à la
  fois.

## État { #status }

Tor ne demande aucun compte. Mysterium a été vérifié de bout en bout le 2026-11-07.
Les modules VPN et 9proxy sont complets et couverts par des tests unitaires, mais
n’ont pas été exécutés de bout en bout avec un vrai abonnement ou un vrai compte,
comme le disent leurs README.
