# Modules

Un module est un service d’une machine du Kiwi Network. Un [rôle](roles.md) choisit
un ensemble de modules, et le moteur de rendu les transforme en une **stack** pour
un hôte. Le moteur de rendu est [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules),
que kiwi-server embarque. La stack est un fichier compose, des **quadlets podman**
(une unité systemd par conteneur), les configurations et les unités de l’hôte, et
`stack.sh`, le manifeste qui les nomme tous. [kiwi-stack](single.md) l’installe sur
la machine. Tout le templating se fait sur la machine qui fait le rendu. La cible
n’a besoin que de podman 4.4 ou plus récent (ou de docker avec le plugin compose,
avec `runtime: docker`).

```bash
kiwi-server modules -v      # chaque module et chaque réglage avec sa valeur par défaut
```

## Le réseau { #the-network }

| Module | Ce que c’est | Tourne sur | Exige | Sur l’hôte |
|---|---|---|---|---|
| `vpn-server` | **wg-easy** : le point d’entrée de chaque client et de chaque node ; sa route par défaut est le client VPN (le double saut) | master | rien | `51820/udp` ; l’interface sur `127.0.0.1:51821` |
| `vpn-client` | **gluetun** : le tunnel auquel chaque machine est accrochée : vers le master sur un node, vers un VPN commercial sur le master | les deux | rien | rien |
| `dns` | **Pi-hole 6** : bloque les publicités pour le maillage ou le LAN, sert les noms de la fleet et, en option, les proxys SOCKS5 de Mullvad par leur nom | les deux | rien | `53` sur un node |
| `tor` | un proxy **SOCKS5 Tor** pour les clients du maillage, épinglé à des pays | les deux | rien | `127.0.0.1:9050` sur un node ; l’adresse de maillage `:9050` sur un master |
| `reverse-proxy` | **nginx** avec TLS : un bloc server par service ; les pages d’administration ne répondent qu’au maillage ; noms publics facultatifs avec Let’s Encrypt | les deux | rien | `80`, `443` sur un node, ou sur un master public |
| `gateway` | routage par politique sur l’hôte : les clients du LAN qui utilisent cette machine comme passerelle sortent par le VPN | node | vpn-client | une unité de l’hôte |
| `dhcp-relay` | relaie le DHCP du LAN vers Pi-hole, pour que Pi-hole puisse être le serveur DHCP du LAN | node | dns | `67/udp` |

## Services { #services }

| Module | Ce que c’est | Tourne sur | Exige |
|---|---|---|---|
| `cloud` | **Nextcloud** à partir des conteneurs du projet AIO, *sans* le conteneur maître AIO (pas de socket docker, tourne sur podman). Collabora, OnlyOffice, Talk, Imaginary, ClamAV, la recherche plein texte et Whiteboard sont des interrupteurs | node | vpn-client, reverse-proxy |
| `vault` | **Vaultwarden**, le gestionnaire de mots de passe compatible Bitwarden | node | vpn-client, reverse-proxy |
| `downloader` | **Transmission** et **JDownloader** dans l’espace de noms réseau du client VPN : pas de tunnel, pas de trafic | node | vpn-client |
| `sftp` | un serveur SFTP sur son propre port (`2224`), pour récupérer les téléchargements | node | rien |
| `portainer` | **Portainer CE**, une interface web pour les conteneurs (`127.0.0.1:9443`, et `portainer.<host>`) | les deux | rien |
| `opencloud` | **OpenCloud** : fichiers et partage dans un seul binaire Go (à l’essai) | node | vpn-client, reverse-proxy |
| `immich` | **Immich** : photos et vidéos (à l’essai) | node | vpn-client, reverse-proxy |
| `paperless` | **Paperless-ngx** : documents numérisés avec OCR et recherche plein texte (à l’essai) | node | vpn-client, reverse-proxy |

Les trois derniers ne sont dans aucun preset ; ajoutez-les à `modules:`.

## Personnes { #people }

| Module | Ce que c’est | Tourne sur | Exige |
|---|---|---|---|
| `nostr-relay` | **strfry**, le relais sur lequel un hub garde ses événements (sur `relay.<host>`). Depuis Internet, les membres peuvent publier après avoir prouvé leur clé (NIP-42) : les clés `approved` de la liste signée des administrateurs, ou toute personne `registered` avec un compte. Le maillage peut toujours publier | master | reverse-proxy |
| `hub` | un **hub kiwi-framework** en conteneur (Armory par défaut, sur `hub.<host>`), privé, semi-public ou public | master | reverse-proxy |

Voir [Héberger votre propre hub](../people/hubs.md).

## Sauvegardes et disques { #backups-and-disks }

| Module | Ce que c’est | Tourne sur | Exige |
|---|---|---|---|
| `backup` | les données de cette machine avec **restic**, chiffrées, vers un node backup-server : chaque nuit à `03:00` (dans les 15 minutes qui suivent) et avec `kiwi-stack backup`. Chaque module indique ce qui est conservé de lui. Prochaine version : plusieurs serveurs et une machine reconstruite qui se restaure elle-même ([détails](operations.md#coming-in-the-next-release)) | les deux | rien |
| `backup-server` | un **serveur REST restic** ; chaque machine n’atteint que son propre dépôt, en ajout seul | node | vpn-client, reverse-proxy |
| `tang` | des serveurs **Tang** pour que les machines chiffrées se déverrouillent au démarrage ; un anneau est un serveur avec ses propres clés (par défaut `infra` sur `7500`) | node | rien |

Voir [Exploitation](operations.md).

## Réglages importants { #important-settings }

| Module | Réglage | Par défaut | Remarques |
|---|---|---|---|
| vpn-server | `wg_host` | (obligatoire) | le nom ou l’IP auquel les clients se connectent |
| | `server_ip` / `wg_subnet` | `10.8.0.1` / `10.8.0.0/24` | |
| | `groups` | guests, pentest, devices, routers | voir [groupes de clients](../network/index.md#client-groups) |
| | `unlock_relay` | `{}` | ports Tang pour les machines derrière un NAT |
| vpn-client | `vpn_provider` | `custom` | `custom` : la configuration WireGuard émise par le master (un node) ; ou un fournisseur gluetun (`mullvad`, `protonvpn`, `airvpn`, `ivpn`, `windscribe`, …) |
| | `wireguard_config` | `secrets/<hostname>.conf` | |
| | `server_countries`, `server_cities` | | où se trouve une sortie commerciale |
| | `dot_providers` | `quad9` | le DNS-over-TLS de gluetun |
| | `extra_dnat_rules` | `[]` | par ex. SSH depuis le maillage vers l’hôte |
| dns | `fallback_dns` | `9.9.9.9;149.112.112.112` | uniquement tant que le master est injoignable |
| | `dhcp_enabled` | `false` | avec `dhcp_start`, `dhcp_end`, `dhcp_router` |
| | `mullvad_socks` | `true` sur un master | [les proxys de Mullvad par leur nom](../network/dns.md#mullvad-socks5-proxies-by-name) |
| tor | `countries` | `de,ch,at,nl,fr` | nœuds d’entrée et de sortie, `StrictNodes` |
| reverse-proxy | `public` | `false` | master uniquement : 80/443 avec Let’s Encrypt pour les noms hors du domaine de la fleet |
| cloud | `nextcloud_datadir` | `<docker_dir>/knnc-data` | à pointer vers un grand disque |
| | `collabora` / `talk` | `true` / `false` | |
| | `startup_apps` | `deck twofactor_totp tasks calendar contacts notes end_to_end_encryption` | |
| vault | `signups_allowed` | `false` | à activer pour le premier compte, puis à désactiver |
| downloader | `download_dir` | (obligatoire) | |
| nostr-relay | `members` | `approved` | ou `registered` |
| | `write_pubkeys` | `[]` | les administrateurs : ils peuvent toujours publier, et seules leurs listes de membres et de bannissements comptent |
| hub | `image` | `ghcr.io/derlocke-ng/armory:latest` | n’importe quel hub kiwi-framework |
| | `public_relays`, `public_mounts` | `[]` | un hub semi-public |
| backup | `server` | (obligatoire) | `https://…` d’un node backup-server qui liste cette machine |
| tang | `rings` | `{ infra: "7500" }` | nom et port |

Les mots de passe et les clés que vous omettez sont générés à partir de la graine
de la fleet.

## Noms { #names }

Chaque module annonce ses noms au reverse proxy et au DNS de la fleet, sous le nom
de l’hôte :

| Service | Nom |
|---|---|
| wg-easy (master) | `wg.<host>` |
| Pi-hole (tout hôte avec `dns` et le reverse proxy) | `pihole.<host>` |
| Nextcloud | `cloud.<host>` |
| Vaultwarden | `vault.<host>` |
| Transmission / JDownloader | `dl.<host>` / `jd.<host>` |
| Portainer | `portainer.<host>` |
| relais / hub | `relay.<host>` / `hub.<host>` |
| serveur de sauvegarde | `backup.<host>` |
| OpenCloud / Immich / Paperless | `opencloud.<host>` / `immich.<host>` / `paperless.<host>` |

## Conteneurs { #containers }

- Sous podman, chaque service est un quadlet dans `/etc/containers/systemd`,
  démarré via `kiwi-stack.target`, avec son journal dans le journal systemd. Un
  conteneur qui vit dans l’espace de noms réseau d’un autre lui est lié et redémarre
  avec lui.
- Les secrets vont dans des fichiers `kiwi/env/<service>.env` réservés à root,
  jamais dans les unités.
- Les adresses fixes suivent le plan v1, si bien qu’une machine migrée les garde :
  vpn-client `.2`, vpn-server `.3`, dns `.4`, reverse-proxy `.5`, cloud `.6`,
  vault `.7`, tor `.8`, downloader `.9`, gateway `.10`, portainer `.250`, sftp
  `.251`. Les autres modules comptent à partir de `.100`. Les conteneurs sans
  adresse fixe utilisent le troisième quart du réseau (`.128/26`).
- Fedora CoreOS et uCore tournent avec SELinux activé, si bien que les montages
  bind portent l’étiquette `:z`. Les montages du socket de conteneurs et de
  `/lib/modules` ne sont jamais étiquetés.

## Écrire un module { #writing-a-module }

```
modules/<name>/
├── module.yaml              what it is, what it needs, its settings
├── docker-compose.yml.j2    its services (merged into the host's compose file)
└── *.j2                     any config file it ships
```

`module.yaml` déclare les métadonnées du module et ses types de node, ses
dépendances, les ports de l’hôte qu’il ouvre, ses modèles et l’endroit où va leur
résultat, le stockage, ce qui est sauvegardé de lui, l’intégration à l’hôte
(sysctls, modules du noyau), les blocs server nginx qu’il annonce, les URL
affichées quand le rôle a terminé, ses règles de validation, et ses `settings`. Le
schéma des réglages valide le fichier fleet et construit le formulaire de
l’application. Les modèles sont en Jinja2 et voient le contexte de l’hôte : le nom
et le type de l’hôte, l’adresse de chaque module, le maillage, les noms de la
fleet, chaque module activé, et les réglages de chaque module.

Sous podman, le fichier compose est traduit en quadlets. Seul un ensemble connu de
clés compose est traduit, et tout le reste est une erreur au moment du rendu.

Les modules sont développés et publiés dans
[kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). La référence complète
du format est
[docs/modules.md de kiwi-server](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/modules.md).
