# Dépôts et état

Tous les dépôts se trouvent sous [github.com/derlocke-ng](https://github.com/derlocke-ng).
« Publié » signifie un tag de version, c’est-à-dire ce que kiwi-updater installe.
Les versions sont celles de novembre 2026.

## Le réseau { #the-network }

| Dépôt | Ce que c’est | Version | Catalogue | Licence |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | construire et faire tourner le réseau : fichier fleet → ISO d’installation → application via SSH | v2.42.0 | oui | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | les 20 modules et leur moteur de rendu : un fichier de machine → un bundle de stack | v0.23.0 | non | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | le côté machine : installe un bundle sur une machine et le maintient en marche | v0.5.0 | non | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | les proxys SOCKS5 de Mullvad sous forme de listes et d’enregistrements DNS, reconstruits toutes les 6 heures | la branche `list` | non | MIT (README) |

## Personnes { #people }

| Dépôt | Ce que c’est | Version | Licence |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | le moteur des hubs communautaires fédérés sur nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | le premier hub : dix outils web pair-à-pair ([en ligne](https://derlocke-ng.github.io/armory/)) | suit `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | un catalogue de hubs et de leurs applications | (une liste) | CC0 (README) |

## Le bureau { #the-desktop }

| Dépôt | Ce que c’est | Version | Catalogue | Licence |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | installe et met à jour des applications depuis des catalogues git | v2.4.0 | oui | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | le catalogue d’applications Kiwi | (une liste) | s.o. | aucune indiquée |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configuration post-installation pour Bluefin-DX | v2.5.0 | oui | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | kill switch VPN pour GNOME qui se ferme en cas de panne | v0.2.3 | oui | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | sorties SOCKS5/VPN scellées dans Podman rootless | v0.7.3 | oui | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | box de distributions dont le trafic ne sort que par une sortie | v0.2.3 | oui | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identités de navigateur isolées sur des sorties kiwi-proxy | v0.7.1 | oui | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | fournisseur kiwi-proxy : Tor | v0.3.0 | oui | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | fournisseur kiwi-proxy : un VPN via gluetun | v0.2.2 | oui | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | fournisseur kiwi-proxy : 9proxy | v0.2.0 | oui | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | fournisseur kiwi-proxy : Mysterium | v0.5.2 | oui | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | dispositions d’écrans pour GNOME | v0.3.2 | oui | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | synchronisation bidirectionnelle de dossiers en services utilisateur | v0.4.1 | oui | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | oui | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | clés et certificats SSH et TLS, hors ligne dans le navigateur ([en ligne](https://derlocke-ng.github.io/kiwi-gen/)) | page web | non | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | les icônes des applications ([aperçu](https://derlocke-ng.github.io/kiwi-icons/)) | pas de tags | non | aucune indiquée |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | ce site web et cette documentation | s.o. | s.o. | AGPL-3.0 |

## Lacunes connues { #known-gaps }

D’après les dépôts eux-mêmes :

- **kiwi-server** : éprouvé sur du matériel en octobre–novembre 2026, avec des
  sauvegardes de nodes restaurées d’un node à l’autre et la MTU du tunnel ajustée,
  chemins mobiles compris. Plusieurs serveurs de sauvegarde, la restauration
  automatique d’une machine reconstruite, un timer d’élagage et un contrôle de santé
  pour une sortie commerciale bloquée se trouvent sur les branches
  `several-servers` de kiwi-server et de kiwi-modules, pas encore publiés. La
  fédération entre réseaux n’est pas encore éprouvée. IPv4 uniquement, et l’ISO
  Debian est uniquement amd64. Le plan de contrôle est conçu, pas construit.
- **kiwi-modules** : OpenCloud, Immich et Paperless-ngx sont « à l’essai ». Un
  serveur TURN pour les appels attend d’être fusionné.
- **kiwi-stack** : pas de retour arrière au-delà de la restauration des données et
  de la réapplication d’un bundle plus ancien.
- **kiwi-framework** : le blog, les approbations de modération, le suivi d’espaces
  qu’un hub ne livre pas, et les signataires NIP-07/NIP-46 sont encore à venir.
- **kiwi-updater** : un registre hébergé de catalogues de confiance est prévu. Les
  tags de version des autres applications ne sont pas encore signés, donc la moitié
  root de kiwi-killswitch demande un mot de passe pour se mettre à jour.
- **kiwi-proxy** : son module kiwi-server n’a encore tourné sur aucune machine. Les
  sorties sont en TCP et IPv4 uniquement. Le module VPN contient une seule
  configuration par machine.
- **Modules de fournisseurs** : VPN et 9proxy ne sont pas validés de bout en bout
  avec un vrai compte ; Mysterium l’est (7 novembre 2026).
- **kiwi-custodia** : certaines parties restent à mesurer sur une vraie machine
  (tun2socks dans une gateway rootless, compositeurs autres que GNOME).
- **Licences** : kiwi-icons, kiwi-catalog et mullvad-socks5 n’ont pas de fichier
  LICENSE, et kiwi-killswitch n’indique sa licence que dans son README et son
  manifeste.
