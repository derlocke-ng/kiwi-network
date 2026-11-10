# Comment fonctionne le réseau

Un Kiwi Network réunit vos machines dans un seul réseau privé, où qu’elles se
trouvent : serveurs chez vous ou au bureau, ordinateurs portables, téléphones,
et même des réseaux domestiques entiers derrière leur routeur. Les machines se
joignent entre elles comme si elles étaient branchées sur le même réseau local,
et une seule d’entre elles doit être accessible depuis Internet. Cette page
explique comment ce réseau est construit et à quoi sert chacun de ses éléments.

Ce réseau privé est un **mesh WireGuard**. WireGuard est le logiciel VPN qui
chiffre les connexions, et *le mesh* est le nom que ces pages donnent au réseau
privé que partagent toutes vos machines. Au centre du mesh se trouve une
machine, le *kiwi-master*. Toutes les autres (nodes chez vous ou au bureau,
ordinateurs portables, téléphones, routeurs) établissent elles-mêmes la
connexion vers le master et peuvent ensuite se joindre à travers le mesh.
L’ensemble du réseau est décrit dans un seul fichier, le fichier fleet
(`fleet.yaml`), et c’est à partir de ce fichier que
[kiwi-server](../server/index.md) le construit.

```
                          Internet
                             ▲
                             │  the mesh's traffic leaves through a commercial VPN
                             │  (gluetun · Mullvad in the preset): the double hop
            ┌────────────────┴──────────────────────────────┐
            │ kiwi-master   (a VPS, or any box people can reach) │
            │   wg-easy    WireGuard server · 10.8.0.1       │ ◀── UDP 51820: the one port
            │   gluetun    the master's own exit             │     it publishes by default
            │   Pi-hole    DNS for the mesh                  │
            │   Tor        SOCKS5 for mesh clients           │
            │   nginx      admin pages, optional hub & relay │
            └────────────────▲──────────────────────────────┘
                             │  WireGuard mesh 10.8.0.0/16 · everyone dials out
     ┌───────────────────────┼─────────────────────┬────────────────────────┐
 kiwi-node (cloud)     kiwi-node (gateway)     devices & guests        routers
 Nextcloud, Vaultwarden routes its LAN through  in client groups:       OpenWrt, FritzBox …
 behind nginx           the VPN; Pi-hole, DHCP  devices, guests,        bring a whole LAN in
                        relay, downloads, SFTP  routers, pentest
```

## Le master { #the-master }

Le master est la machine à laquelle toutes les autres se connectent. Son rôle,
`master`, fait tourner les cinq modules décrits ci-dessous. Pi-hole, Tor et
nginx partagent le namespace réseau du serveur WireGuard. Un namespace réseau
est un jeu d’interfaces, d’adresses et de routes propre à un conteneur : ces
trois services utilisent donc le réseau du serveur WireGuard au lieu d’avoir le
leur. C’est pour cette raison qu’ils redémarrent en même temps que lui.

- **vpn-server** (wg-easy) est le serveur WireGuard. Tous les clients et tous
  les nodes s’y connectent, et c’est lui qui délivre leurs configurations
  WireGuard. kiwi-server peut créer ces configurations pour vous
  (`kiwi-server enroll`).
- **vpn-client** (gluetun) relie le master à un fournisseur VPN commercial. Le
  preset utilise Mullvad, mais tout fournisseur pris en charge par gluetun
  convient. La route par défaut du serveur WireGuard pointe vers ce client VPN.
  Le trafic du mesh à destination d’Internet passe donc par le fournisseur, et
  les sites web voient l’adresse du fournisseur, pas celle du master. Cette
  connexion est la *sortie* du master, c’est-à-dire le chemin par lequel le
  trafic du mesh rejoint Internet. Comme le trafic traverse deux VPN à la
  suite, le vôtre puis celui du fournisseur, on parle de **double saut**
  (double hop). Un master sans vpn-client envoie le trafic directement sur
  Internet, depuis sa propre adresse.
- **dns** (Pi-hole 6) est le serveur DNS du mesh. Il répond à l’adresse mesh du
  master, `10.8.0.1`. Voir [DNS, noms et certificats](dns.md).
- **tor** met un proxy SOCKS5 à la disposition des clients du mesh, à l’adresse
  `10.8.0.1:9050`. Les nœuds d’entrée et de sortie de Tor sont limités à une
  liste de pays (par défaut `de,ch,at,nl,fr`, imposée avec `StrictNodes`).
- **reverse-proxy** (nginx) sert les pages d’administration, c’est-à-dire les
  interfaces web de wg-easy et de Pi-hole, sous les noms `wg.<master>` et
  `pihole.<master>`. Il ne les sert qu’à l’intérieur du mesh, et seulement aux
  clients autorisés à voir les pages d’administration (voir « Groupes de
  clients » plus bas).

Un master peut aussi héberger un **relais nostr** et un **hub** pour les
[personnes de votre réseau](../people/hubs.md#on-a-kiwi-network). Un hub est le
site d’une communauté, qui fonctionne dans le navigateur, et un relais nostr
est le type de serveur par lequel les hubs se synchronisent. Vous pouvez
également ajouter Portainer et les sauvegardes à un master.

### Ce qui est accessible depuis Internet { #what-is-reachable-from-the-internet }

Par défaut, le master n’a qu’**un seul port** ouvert sur Internet : celui de
WireGuard, en UDP 51820. Les pages d’administration ne s’ouvrent que depuis
l’intérieur du mesh. Deux réglages ouvrent d’autres ports :

- `reverse-proxy.public: true` ouvre les ports 80 et 443 et obtient des
  certificats Let’s Encrypt pour les noms situés en dehors du domaine de votre
  réseau. Tout le reste demeure accessible uniquement depuis le mesh, et les
  pages d’administration répondent par une erreur 403 aux requêtes venues de
  l’extérieur. Ce réglage est destiné à un hub ou à un relais public.
- `vpn-server.unlock_relay` ouvre les ports TCP des
  [anneaux Tang](../server/operations.md#encrypted-disks-and-unlocking) pour
  les machines placées derrière un NAT. Tang est un serveur qui permet à une
  machine dont le disque est chiffré de déverrouiller ce disque au démarrage,
  et un anneau est un serveur Tang avec ses propres clés.

kiwi-server ne modifie pas SSH : il reste tel que le système d’exploitation le
configure, c’est-à-dire, par défaut, avec une connexion par clés uniquement.
kiwi-server lui-même passe par SSH pour `apply` et `status`.

## Groupes de clients { #client-groups }

Les clients du serveur WireGuard (wg-easy) sont répartis en **groupes** d’après
leur adresse. Un groupe détermine ce que ses membres ont le droit de joindre :

| Groupe | Sous-réseau | Peut joindre | Voit les autres clients | Pages d’administration |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | les nodes | non | non |
| `pentest` | `10.8.2.0/24` | rien dans le mesh | non | non |
| `devices` | `10.8.3.0/24` | tout | oui | oui |
| `routers` | `10.8.4.0/24` | tout | oui | non |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # un code QR pour l'application WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # seul le trafic du mesh passe par le tunnel
```

Les membres de tous les groupes peuvent aussi accéder à Internet par la sortie
du master, sauf si vous définissez `internet: false` pour le groupe. Un client
dont l’adresse n’appartient à aucun groupe (`10.8.0.x`) est un membre ordinaire
du mesh. Il peut tout joindre, et il peut ouvrir les pages d’administration
tant que `admin_from_mesh` est activé.

Les groupes sont un réglage du module vpn-server (`groups`). Vous pouvez donc
les modifier ou ajouter les vôtres. Le réglage `reach` d’un groupe accepte
`all`, `nodes`, des noms d’hôte, des adresses ou des sous-réseaux. L’ancien
réglage `isolated_subnet`, qui définissait un unique groupe isolé, existe
toujours, mais il est désactivé par défaut.

## Nodes { #nodes }

Un node est une machine installée chez vous ou au bureau, sur laquelle tournent
vos services. Il a lui aussi un module vpn-client, mais sur un node ce module
ne se connecte pas à un fournisseur VPN commercial. Il se connecte au master,
avec la configuration WireGuard que le master a délivrée pour ce node.
`kiwi-server enroll` écrit cette configuration dans `secrets/<hostname>.conf`,
et le node l’utilise sans autre réglage. Un node n’a besoin d’aucun port ouvert
sur Internet, puisque c’est lui qui établit la connexion vers le master. C’est
ce qui lui permet de fonctionner derrière le NAT d’un routeur domestique.

Le rôle `node` propose trois presets, c’est-à-dire trois listes de modules
prêtes à l’emploi :

| Preset | Ce que devient la machine |
|---|---|
| `gateway` (par défaut) | Une passerelle pour le réseau local (LAN). Les appareils du LAN qui prennent cette machine comme passerelle par défaut accèdent à Internet par le VPN et peuvent joindre le mesh. Pi-hole est le serveur DNS du LAN et peut aussi, si vous le souhaitez, en être le serveur DHCP. Les programmes de téléchargement Transmission et JDownloader tournent *à l’intérieur* du namespace réseau du client VPN : tant que le tunnel est coupé, ils n’ont aucune route. Le preset comprend aussi nginx, Portainer et SFTP. |
| `cloud` | Votre propre cloud : Nextcloud avec Collabora pour les fichiers, les agendas et les documents, et Vaultwarden pour les mots de passe. Ces services sont placés derrière nginx, et Portainer est fourni lui aussi. Nextcloud est construit à partir des conteneurs du projet AIO, sans le conteneur maître d’AIO. |
| `minimal` | Uniquement le client VPN et nginx. Vous ajoutez vous-même les modules dont vous avez besoin. |

Un node peut aussi se charger des sauvegardes, d’un serveur de sauvegarde et de
Tang. OpenCloud, Immich et Paperless-ngx sont fournis pour que vous puissiez
les essayer. Voir la [liste des modules](../server/modules.md).

Les services d’un node sont accessibles depuis son LAN et à l’**adresse mesh**
du node (par exemple `10.8.0.25`). Le trafic qui arrive du mesh à cette adresse
sur les ports 80 et 443 est transmis au reverse proxy du node.

## Noms { #names }

Les noms de machines suivent une convention. **Les masters portent des noms de
préparations à base de fruits** (`crumble`, `sorbet`, `compote`, `chutney`,
`strudel`, `cobbler`, `trifle`, `cider`) et **les nodes des noms de fruits**
(`papaya`, `lychee`, `guava`, `quince`, `damson`). Ainsi, n’importe quelle
ligne de journal vous indique à quel type de machine un nom appartient. Ce
n’est qu’une convention, et n’importe quel nom fonctionne. Un service reçoit un
nom placé sous celui de la machine qui l’héberge : `cloud.papaya.home`,
`vault.papaya.home`, `wg.sorbet.home`. Voir
[DNS, noms et certificats](dns.md).

## Comment le mesh accède à Internet { #ways-out }

Un master est un serveur WireGuard doté d’une sortie, c’est-à-dire du chemin
par lequel le trafic du mesh rejoint Internet. Cette sortie a trois modes :

| Mode | Comment le mesh accède à Internet | État |
|---|---|---|
| **provider** | Par un fournisseur VPN commercial (gluetun). C’est le double saut, et c’est ce que met en place le preset du master. | réalisé |
| **direct** | Directement par la connexion Internet du master. Pour obtenir ce mode, indiquez la liste des modules du master sans `vpn-client`. | réalisé |
| **master** | Par *le master d’un autre réseau*. Votre master y est client, dans un groupe qui peut accéder à Internet et à rien d’autre. C’est ce qu’on appelle le multi-saut (multi-hop). | conçu ; il faut pour cela pouvoir ajouter une machine au réseau de quelqu’un d’autre, c’est-à-dire la fédération |

Quel que soit son mode de sortie, chaque master met aussi le proxy SOCKS5 de
Tor à la disposition du mesh.

## Un mesh par réseau { #one-mesh-per-network }

Chaque réseau a son propre mesh, avec sa propre plage d’adresses. La plage par
défaut est `10.8.0.0/16`. Les masters et les nodes se trouvent dans
`10.8.0.0/24`, puis viennent les groupes : guests en `.1`, pentest en `.2`,
devices en `.3` et routers en `.4`. Un deuxième réseau utilise une autre plage,
par exemple `10.9.0.0/16`, pour qu’un appareil membre des deux réseaux puisse
les distinguer. Aujourd’hui, cette plage ne se règle pas en un seul endroit.
Elle est répartie entre plusieurs réglages (`mesh_subnet`, les réglages
`server_ip`, `wg_subnet`, `wg_default_address` et `groups` du vpn-server, et
`socks_policy_accept` pour Tor). Le fichier fleet les définit tous.

## Adressage { #addressing }

| Quoi | Valeur par défaut |
|---|---|
| L’ensemble du mesh (routé sur chaque hôte) | `10.8.0.0/16` par défaut (`mesh_subnet`) |
| Clients wg-easy | `10.8.0.0/24` ; le serveur est `10.8.0.1` |
| Groupes de clients | `10.8.1.0/24` … `10.8.4.0/24` |
| Réseau de la stack | `172.64.0.0/24` sur un master, `172.128.0.0/24` sur un node |
| MTU WireGuard | `1376` (`wg_mtu`), mesurée avec [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU du bridge de la stack | `1500` (`bridge_mtu`) |

La stack d’une machine est l’ensemble des conteneurs que font tourner ses
modules. Chaque machine dotée d’une stack route la plage d’adresses du mesh par
son client VPN ou, sur le master, par le serveur WireGuard. La machine et ses
conteneurs peuvent ainsi joindre tous les nodes.

## Redémarrages et mises à jour automatiques { #keeping-it-fresh }

Chaque machine reçoit deux timers, configurés dans les réglages de sa stack. Le
premier est un **redémarrage quotidien du VPN** à `07:00`, qui donne à la
machine une nouvelle adresse de sortie. Le second est une **mise à jour
hebdomadaire**, le dimanche à 00:00, qui lance `podman auto-update` à condition
que `auto_update: registry` soit défini. Le système d’exploitation se met lui
aussi à jour tout seul, et il ne redémarre que pendant
[la fenêtre de maintenance que vous avez fixée](../server/machines.md#updates).

## Tout un LAN dans le mesh { #a-whole-lan-in-the-mesh }

Un routeur peut rejoindre le mesh comme client WireGuard, dans le groupe
`routers`. Autre possibilité : le routeur envoie le trafic destiné au
sous-réseau du mesh vers un node passerelle, au moyen d’une route statique.
Dans les deux cas, tous les appareils du LAN de ce routeur peuvent joindre tous
les nodes sans faire tourner WireGuard eux-mêmes. Voir [Routeurs](routers.md).
