# Dépôts et état

Cette page recense tous les dépôts du projet Kiwi Network : à quoi sert chacun,
sa dernière version et sa licence. Elle se termine par la liste de ce qui
manque encore ou n’a pas encore été testé, à notre connaissance.

Tous les dépôts se trouvent sur [github.com/derlocke-ng](https://github.com/derlocke-ng).
Un dépôt « publié » est un dépôt qui a un tag de version, car c’est un tag de
version que kiwi-updater installe. Les versions indiquées sont celles de
novembre 2026.

## Le réseau { #the-network }

| Dépôt | Ce que c’est | Version | Catalogue | Licence |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | construit et gère le réseau : il transforme le fichier fleet en ISO d’installation et applique par SSH le rôle de chaque machine | v2.42.0 | oui | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | les 20 modules et leur générateur, qui transforme le fichier d’une machine en un paquet pour sa stack | v0.23.0 | non | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | la partie qui tourne sur la machine : elle y installe un paquet et le maintient en marche | v0.5.0 | non | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | listes et enregistrements DNS des proxys SOCKS5 de Mullvad, régénérés toutes les 6 heures | la branche `list` | non | MIT (README) |

## Les hubs { #people }

| Dépôt | Ce que c’est | Version | Licence |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | le framework avec lequel sont construits les hubs communautaires fédérés sur nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | le premier hub construit avec kiwi-framework, avec dix outils web pair-à-pair ([en ligne](https://derlocke-ng.github.io/armory/)) | suit `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | un catalogue de hubs et de leurs applications | (une liste) | CC0 (README) |

## Le poste de travail { #the-desktop }

| Dépôt | Ce que c’est | Version | Catalogue | Licence |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installe et met à jour des applications à partir de catalogues git | v2.4.0 | oui | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | le catalogue des applications Kiwi | (une liste) | sans objet | non précisée |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configure Bluefin-DX une fois le système installé | v2.5.0 | oui | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | un kill switch VPN fail-closed pour GNOME : si la connexion VPN tombe, le trafic est bloqué | v0.2.3 | oui | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | des exits SOCKS5 et VPN dans Podman rootless, chacun enfermé dans un conteneur dont la seule route est cette connexion | v0.7.3 | oui | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | des box (distributions Linux dans des conteneurs) dont le trafic ne peut rejoindre Internet que par un exit de kiwi-proxy | v0.2.3 | oui | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | des identités de navigateur isolées, qui se connectent par des exits de kiwi-proxy | v0.7.1 | oui | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | module fournisseur pour kiwi-proxy : Tor | v0.3.0 | oui | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | module fournisseur pour kiwi-proxy : un VPN par gluetun | v0.2.2 | oui | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | module fournisseur pour kiwi-proxy : 9proxy | v0.2.0 | oui | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | module fournisseur pour kiwi-proxy : Mysterium | v0.5.2 | oui | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | dispositions des écrans pour GNOME | v0.3.2 | oui | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | synchronisation de dossiers dans les deux sens, sous forme de services utilisateur systemd | v0.4.1 | oui | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | oui | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | crée des clés et des certificats SSH et TLS hors ligne, dans le navigateur ([en ligne](https://derlocke-ng.github.io/kiwi-gen/)) | page web | non | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | les icônes des applications ([aperçu](https://derlocke-ng.github.io/kiwi-icons/)) | aucun tag | non | non précisée |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | ce site et cette documentation | sans objet | sans objet | GPL-3.0-or-later, CC BY-SA 4.0 |

## Lacunes connues { #known-gaps }

Les dépôts signalent eux-mêmes les lacunes suivantes :

- **kiwi-server** : il a été testé sur du matériel réel en octobre et
  novembre 2026. Lors de ces tests, les sauvegardes d’un node ont
  été restaurées sur un autre node, et la MTU du tunnel a été ajustée, y
  compris pour les connexions mobiles. Quatre ajouts se trouvent sur les
  branches `several-servers` de kiwi-server et de kiwi-modules et ne sont pas
  encore publiés : plusieurs serveurs de sauvegarde, la restauration
  automatique d’une machine reconstruite, un timer qui supprime les anciens
  snapshots, et un health check qui relance la connexion au fournisseur VPN
  commercial lorsqu’elle est bloquée. La fédération entre réseaux n’a pas
  encore été vérifiée en pratique. Tout fonctionne uniquement en IPv4, et
  l’ISO Debian n’existe que pour amd64. Le plan de contrôle est conçu, mais pas
  encore réalisé.
- **kiwi-modules** : les modules OpenCloud, Immich et Paperless-ngx sont
  signalés comme étant « à essayer ». Un serveur TURN pour les appels attend
  d’être fusionné.
- **kiwi-stack** : il n’y a pas de retour arrière. Vous pouvez seulement
  restaurer les données et appliquer de nouveau un paquet plus ancien.
- **kiwi-framework** : plusieurs éléments restent à venir, à savoir le blog, les
  validations de modération, la possibilité de suivre des espaces qu’un hub ne
  fournit pas, et les signataires NIP-07/NIP-46.
- **kiwi-updater** : un registre hébergé de catalogues de confiance est prévu.
  Les tags de version des autres applications ne sont pas encore signés. C’est
  pourquoi la partie de kiwi-killswitch qui tourne en root demande un mot de
  passe lors de sa mise à jour.
- **kiwi-proxy** : son module pour kiwi-server n’a encore jamais tourné sur une
  machine. Les exits ne transportent que du TCP et de l’IPv4. Le module VPN
  n’accepte qu’une configuration par machine.
- **Modules fournisseurs** : les modules VPN et 9proxy n’ont pas encore été
  validés de bout en bout avec un vrai compte. Le module Mysterium, lui, a été
  validé le 7 novembre 2026.
- **kiwi-custodia** : certains points doivent encore être mesurés sur une
  vraie machine, à savoir tun2socks dans un conteneur gateway rootless et les
  compositeurs autres que GNOME.
- **Licences** : kiwi-icons, kiwi-catalog et mullvad-socks5 n’ont pas de
  fichier LICENSE, et kiwi-killswitch n’indique sa licence que dans son README
  et son manifeste.
