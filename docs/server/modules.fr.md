# Modules

Un module est un service que fait tourner une machine de votre Kiwi Network,
par exemple le serveur VPN, le serveur DNS qui bloque les publicités, Nextcloud
ou la sauvegarde de chaque nuit. C’est par les modules que vous décidez de ce
que fait chaque machine. Un [rôle](roles.md) apporte un ensemble de modules, et
vous pouvez modifier cet ensemble dans le fichier fleet.

Un générateur transforme les modules d’un hôte en une **stack**, c’est-à-dire
tout ce dont la machine a besoin pour faire tourner ces services. Ce générateur
est [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules), dont
kiwi-server contient une copie. Une stack se compose d’un fichier compose, de
**quadlets podman** (une unité systemd par conteneur), des fichiers de
configuration, des unités systemd de l’hôte et de `stack.sh`, un manifeste qui
les répertorie tous. [kiwi-stack](single.md) installe la stack sur la machine.
Tous les templates sont remplis sur l’ordinateur qui génère la stack. La
machine qui fait tourner la stack n’a besoin que de podman 4.4 ou plus récent,
ou de docker avec le plugin compose si vous définissez `runtime: docker`.

La commande suivante liste tous les modules avec leurs réglages.

```bash
kiwi-server modules -v      # tous les modules et tous les réglages, avec leur valeur par défaut
```

## Le réseau { #the-network }

Ces modules construisent le mesh, c’est-à-dire le réseau WireGuard privé qui
relie toutes vos machines, et déterminent comment son trafic rejoint Internet.

| Module | Ce que c’est | Tourne sur | Dépend de | Sur l’hôte |
|---|---|---|---|---|
| `vpn-server` | **wg-easy**, le serveur WireGuard auquel se connectent tous les clients et tous les nodes. Sa route par défaut passe par le client VPN : le trafic vers Internet continue donc par le VPN commercial du master (le double saut) | master | aucun | `51820/udp`, et l’interface web sur `127.0.0.1:51821` |
| `vpn-client` | **gluetun**, le tunnel VPN par lequel passe le trafic d’une machine. Sur un node, le tunnel mène au master ; sur le master, il mène à un VPN commercial | les deux | aucun | rien |
| `dns` | **Pi-hole 6**, un serveur DNS qui bloque les publicités, pour le mesh ou pour le LAN. Il répond pour les noms de votre réseau et peut aussi fournir des noms pour les proxys SOCKS5 de Mullvad | les deux | aucun | `53` sur un node |
| `tor` | Un proxy **SOCKS5 Tor** pour les clients du mesh. Il n’utilise que des nœuds Tor situés dans les pays que vous avez choisis | les deux | aucun | `127.0.0.1:9050` sur un node, et l’adresse mesh `:9050` sur un master |
| `reverse-proxy` | **nginx** avec TLS. Il a un bloc server par service, si bien que chaque service est joignable sous son propre nom. Les pages d’administration ne sont accessibles que depuis le mesh. Des noms publics avec des certificats Let’s Encrypt sont possibles en option | les deux | aucun | `80`, `443` sur un node, ou sur un master avec `public` activé |
| `gateway` | Routage par règles (policy routing) sur l’hôte. Les appareils du LAN qui utilisent cette machine comme passerelle voient leur trafic Internet passer par le VPN | node | vpn-client | une unité systemd sur l’hôte |
| `dhcp-relay` | Transmet les requêtes DHCP du LAN à Pi-hole, pour que Pi-hole puisse servir de serveur DHCP au LAN | node | dns | `67/udp` |

## Services { #services }

| Module | Ce que c’est | Tourne sur | Dépend de |
|---|---|---|---|
| `cloud` | **Nextcloud**, construit à partir des conteneurs du projet AIO, mais *sans* le conteneur maître d’AIO. Il n’a donc pas besoin du socket docker et tourne sous podman. Collabora, OnlyOffice, Talk, Imaginary, ClamAV, la recherche plein texte et Whiteboard s’activent ou se désactivent chacun séparément | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, un gestionnaire de mots de passe compatible avec Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** et **JDownloader**. Tous deux tournent dans le namespace réseau du client VPN : ils utilisent sa connexion réseau et n’en ont aucune à eux. Tant que le tunnel est coupé, ils ne transfèrent rien | node | vpn-client |
| `sftp` | Un serveur SFTP sur son propre port (`2224`), d’où vous pouvez récupérer les téléchargements | node | aucun |
| `portainer` | **Portainer CE**, une interface web pour les conteneurs. Elle est accessible à `127.0.0.1:9443` et sous `portainer.<host>` | les deux | aucun |
| `opencloud` | **OpenCloud**, pour les fichiers et le partage de fichiers, en un seul binaire Go (à essayer) | node | vpn-client, reverse-proxy |
| `immich` | **Immich**, pour les photos et les vidéos (à essayer) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx**, pour les documents numérisés, avec OCR et recherche plein texte (à essayer) | node | vpn-client, reverse-proxy |

Ces trois derniers modules ne font partie d’aucun preset. Pour utiliser l’un
d’eux, ajoutez-le à `modules:`.

## Hubs { #people }

Un hub est le site d’une communauté, qui fonctionne dans le navigateur. Ces
deux modules font tourner un hub et le relais sur lequel le hub stocke ses
événements.

| Module | Ce que c’est | Tourne sur | Dépend de |
|---|---|---|---|
| `nostr-relay` | **strfry**, le relais sur lequel un hub conserve ses événements. Il est accessible sous `relay.<host>`. Les personnes qui se connectent depuis Internet ne peuvent publier que si elles sont membres et ont prouvé qu’elles possèdent leur clé (NIP-42). Avec `approved`, les membres sont les clés d’une liste signée par les admins. Avec `registered`, toute personne qui a un compte est membre. Les connexions venues du mesh peuvent toujours publier | master | reverse-proxy |
| `hub` | Un **hub kiwi-framework** qui tourne dans un conteneur. Par défaut, il s’agit d’Armory, accessible sous `hub.<host>`. Un hub peut être privé, semi-public ou public | master | reverse-proxy |

Voir [Héberger votre propre hub](../people/hubs.md).

## Sauvegardes et disques { #backups-and-disks }

| Module | Ce que c’est | Tourne sur | Dépend de |
|---|---|---|---|
| `backup` | Sauvegarde les données de cette machine avec **restic**, chiffrées, sur un node qui fait tourner le module backup-server. La sauvegarde a lieu chaque nuit à `03:00`, ou jusqu’à 15 minutes plus tard, et chaque fois que vous lancez `kiwi-stack backup`. Chaque module définit lesquelles de ses données sont sauvegardées. Sont prévues pour la prochaine version : les sauvegardes vers plusieurs serveurs, et la restauration de ses propres données par une machine reconstruite ([détails](operations.md#coming-in-the-next-release)) | les deux | aucun |
| `backup-server` | Un **serveur REST restic** qui stocke les sauvegardes. Chaque machine n’a accès qu’à son propre dépôt, et elle peut seulement y ajouter des données, sans rien supprimer (append-only) | node | vpn-client, reverse-proxy |
| `tang` | Des serveurs **Tang**, qui permettent aux machines dont les disques sont chiffrés de les déverrouiller au démarrage sans que personne soit présent. Un anneau est un serveur Tang avec ses propres clés. Par défaut, il y a un anneau nommé `infra` sur le port `7500` | node | aucun |

Voir [Exploitation](operations.md).

## Réglages importants { #important-settings }

| Module | Réglage | Par défaut | Remarques |
|---|---|---|---|
| vpn-server | `wg_host` | (obligatoire) | le nom ou l’adresse IP à laquelle se connectent les clients |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | voir [groupes de clients](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | des ports du master par lesquels les machines placées derrière un NAT joignent leur anneau Tang |
| vpn-client | `vpn_provider` | `custom` | `custom` utilise la configuration WireGuard délivrée par le master, ce dont un node a besoin. Sinon, indiquez un fournisseur pris en charge par gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | les pays et les villes des serveurs VPN commerciaux à utiliser |
| | `dot_providers` | `quad9` | le fournisseur DNS-over-TLS qu’utilise gluetun |
| | `extra_dnat_rules` | `[]` | des règles de redirection supplémentaires, par exemple pour SSH depuis le mesh vers l’hôte |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | utilisé seulement quand le master est injoignable |
| | `dhcp_enabled` | `false` | s’utilise avec `dhcp_start`, `dhcp_end` et `dhcp_router` |
| | `mullvad_socks` | `true` sur un master | [les proxys de Mullvad par leur nom](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | les pays des nœuds d’entrée et de sortie de Tor, imposés avec `StrictNodes` |
| reverse-proxy | `public` | `false` | master uniquement. Ouvre les ports 80/443 et utilise Let’s Encrypt pour les noms situés en dehors du domaine de votre réseau |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | indiquez un dossier situé sur un grand disque |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | activez-le pour créer le premier compte, puis désactivez-le |
| downloader | `download_dir` | (obligatoire) | |
| nostr-relay | `members` | `approved` | ou `registered` |
| | `write_pubkeys` | `[]` | les clés des admins. Les admins peuvent toujours publier, et seules leurs listes de membres et leurs listes de bannissement font foi |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | l’image de n’importe quel hub construit avec kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | à définir pour un hub semi-public |
| backup | `server` | (obligatoire) | l’adresse `https://…` d’un node backup-server qui répertorie cette machine |
| tang | `rings` | `{ infra: "7500" }` | le nom et le port de chaque anneau |

Si vous n’indiquez pas un mot de passe ou une clé, il est généré à partir du
seed de votre réseau.

## Noms { #names }

Chaque module déclare les noms de ses services auprès du reverse proxy et du
DNS de votre réseau. Chaque nom se compose du nom du service et du nom de
l’hôte.

| Service | Nom |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (tout hôte qui a `dns` et le reverse proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relais / hub | `relay.<host>` / `hub.<host>` |
| serveur de sauvegarde | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Conteneurs { #containers }

- Sous podman, chaque service est un quadlet dans `/etc/containers/systemd`.
  Les quadlets sont démarrés par `kiwi-stack.target`, et leurs journaux vont
  dans le journal systemd. Un conteneur qui partage le namespace réseau d’un
  autre conteneur est lié à celui-ci : il redémarre donc en même temps que lui.
- Les secrets sont écrits dans des fichiers `kiwi/env/<service>.env` que seul
  root peut lire. Ils ne sont jamais écrits dans les unités.
- Les conteneurs ont des adresses fixes qui suivent le plan d’adressage de la
  v1 : une machine migrée depuis la v1 garde donc ses adresses. Ce sont
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250` et
  sftp `.251`. Les autres modules reçoivent des adresses attribuées en montant
  à partir de `.100`. Les conteneurs sans adresse fixe en reçoivent une dans le
  troisième quart du réseau (`.128/26`).
- Fedora CoreOS et uCore tournent avec SELinux activé : les bind mounts
  reçoivent donc l’étiquette `:z`. Les montages du socket des conteneurs et de
  `/lib/modules` ne sont jamais étiquetés.

## Écrire un module { #writing-a-module }

Un module est un dossier qui contient les fichiers suivants.

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` décrit le module. Il déclare ses métadonnées et les types de
nodes sur lesquels il tourne, ses dépendances et les ports qu’il ouvre sur
l’hôte. Il nomme les templates du module et l’endroit où leur résultat est
écrit, son stockage, et celles de ses données qui sont sauvegardées. Il déclare
aussi l’intégration à l’hôte (sysctls et modules du noyau), les blocs server
nginx que le module enregistre, les URL affichées lorsque le rôle est terminé,
les règles de validation et les réglages du module (`settings`).

Le schéma des réglages sert à deux choses. Il valide le fichier fleet, et
l’application kiwi-server en tire son formulaire de réglages. Les templates
sont écrits en Jinja2 et peuvent utiliser le contexte de l’hôte. Ce contexte
contient le nom et le type de l’hôte, l’adresse de chaque module, le mesh, les
noms de votre réseau, les modules activés et les réglages de chaque module.

Sous podman, le fichier compose est traduit en quadlets. Cette traduction prend
en charge un ensemble défini de clés compose, et toute autre clé provoque une
erreur au moment où la stack est générée.

Les modules sont développés et publiés dans
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). La référence
complète du format se trouve dans
[docs/modules.md de kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
