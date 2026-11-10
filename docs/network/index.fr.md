# Comment fonctionne le réseau

Un Kiwi Network est un **maillage WireGuard avec un seul hub**, le *kiwi-master*.
Toutes les autres machines (nodes à la maison ou au bureau, ordinateurs portables,
téléphones, routeurs) se connectent au master et retrouvent les autres dans le
maillage. Le tout est décrit dans un seul fichier fleet et construit par
[kiwi-server](../server/index.md).

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

Le rôle `master` fait tourner cinq modules. Pi-hole, Tor et nginx vivent dans
l’espace de noms réseau du serveur WireGuard et redémarrent avec lui.

- **vpn-server** (wg-easy) est le point d’entrée de chaque client et de chaque
  node, et émet leurs configurations WireGuard. kiwi-server peut les créer pour
  vous (`kiwi-server enroll`).
- **vpn-client** (gluetun) se connecte à un fournisseur VPN commercial : Mullvad
  dans le preset, n’importe quel fournisseur pris en charge par gluetun en général.
  La route par défaut du serveur WireGuard pointe vers lui, si bien que le trafic du
  maillage sort par le fournisseur, et non par l’adresse propre du master. C’est le
  **double saut**. Un master sans vpn-client sort directement.
- **dns** (Pi-hole 6) répond à l’adresse de maillage du master, `10.8.0.1`. Voir
  [DNS, noms et certificats](dns.md).
- **tor** offre un SOCKS5 sur `10.8.0.1:9050` aux clients du maillage, avec les
  nœuds d’entrée et de sortie épinglés à un ensemble de pays (par défaut
  `de,ch,at,nl,fr`, `StrictNodes`).
- **reverse-proxy** (nginx) sert les pages d’administration, `wg.<master>` et
  `pihole.<master>`, aux groupes d’administration du maillage.

Un master peut aussi porter un **relais nostr** et un **hub** pour
[les personnes de votre réseau](../people/hubs.md#on-a-kiwi-network), plus
Portainer et des sauvegardes.

### Ce qui est joignable depuis Internet { #what-is-reachable-from-the-internet }

Par défaut, le master publie **un seul port** : WireGuard, UDP 51820. Les pages
d’administration ne répondent qu’au maillage. Deux réglages en ajoutent :

- `reverse-proxy.public: true` publie 80 et 443, avec des certificats Let’s
  Encrypt pour les noms hors du domaine de la fleet. Tout le reste continue de ne
  répondre qu’au maillage, et les pages d’administration répondent 403 depuis
  l’extérieur. C’est pour un hub ou un relais public.
- `vpn-server.unlock_relay` ouvre les ports TCP des
  [anneaux Tang](../server/operations.md#encrypted-disks-and-unlocking) pour les
  machines derrière un NAT.

SSH reste tel que le système d’exploitation l’a configuré (clés uniquement par
défaut). kiwi-server l’utilise pour `apply` et `status`.

## Groupes de clients { #client-groups }

Les clients de wg-easy sont répartis en **groupes** selon leur adresse. Chaque
groupe décide de ce que ses membres peuvent atteindre :

| Groupe | Sous-réseau | Atteint | Voit les autres clients | Pages d’administration |
|---|---|---|---|---|
| `guests` | `10.8.1.0/24` | les nodes | non | non |
| `pentest` | `10.8.2.0/24` | rien dans le maillage | non | non |
| `devices` | `10.8.3.0/24` | tout | oui | oui |
| `routers` | `10.8.4.0/24` | tout | oui | non |

```bash
kiwi-server enroll fleet.yaml phone --group devices --qr   # un code QR pour l’application WireGuard
kiwi-server enroll fleet.yaml anna  --group guests --split # seul le maillage passe par le tunnel
```

Chaque groupe peut sortir vers Internet par la sortie, sauf si vous réglez
`internet: false`. Les clients hors de tout groupe (`10.8.0.x`) sont le maillage
simple : ils atteignent tout, et voient les pages d’administration tant que
`admin_from_mesh` est activé. Les groupes sont un réglage du module vpn-server
(`groups`), vous pouvez donc les modifier ou ajouter les vôtres (`reach` accepte
`all`, `nodes`, des noms d’hôtes, des adresses ou des sous-réseaux). L’ancien
réglage unique `isolated_subnet` existe toujours, mais il est désactivé par
défaut.

## Nodes { #nodes }

Le vpn-client d’un node ne parle pas à un VPN commercial. Il utilise la
configuration WireGuard que le master a émise pour lui (`kiwi-server enroll` écrit
`secrets/<hostname>.conf`, et le node la récupère tout seul). Un node n’a besoin
d’aucun port ouvert sur Internet : il se connecte au master, donc il fonctionne
derrière le NAT d’un routeur domestique.

Le rôle `node` a trois presets :

| Preset | Ce que devient la machine |
|---|---|
| `gateway` (par défaut) | Une passerelle LAN. Les clients du LAN qui l’utilisent comme passerelle par défaut sortent par le VPN et peuvent atteindre le maillage. Pi-hole sert le LAN (en option comme son serveur DHCP). Transmission et JDownloader tournent *à l’intérieur* de l’espace de noms réseau du client VPN, si bien qu’ils n’ont aucune route quand le tunnel est coupé. Avec nginx, Portainer et SFTP. |
| `cloud` | Nextcloud (à partir des conteneurs du projet AIO, sans le conteneur maître AIO) avec Collabora, plus Vaultwarden, derrière nginx, plus Portainer |
| `minimal` | Uniquement le client VPN et nginx, pour les modules de votre choix |

Les nodes peuvent aussi faire tourner des sauvegardes, un serveur de sauvegarde,
Tang et (à l’essai) OpenCloud, Immich et Paperless-ngx. Voir la
[liste des modules](../server/modules.md).

Les services d’un node sont joignables sur son LAN et à son **adresse de
maillage** (par ex. `10.8.0.25`). Le trafic du maillage vers cette adresse sur les
ports 80 et 443 est transmis au reverse proxy.

## Noms { #names }

Les machines tirent leur nom du verger : **les masters, de desserts aux fruits**
(`crumble`, `sorbet`, `compote`, `chutney`, `strudel`, `cobbler`, `trifle`,
`cider`) et **les nodes, de fruits** (`papaya`, `lychee`, `guava`, `quince`,
`damson`), si bien que le type d’une machine se lit dans chaque ligne de journal.
C’est une convention, et n’importe quel nom fonctionne. Les services se placent
sous leur hôte : `cloud.papaya.home`, `vault.papaya.home`, `wg.sorbet.home`. Voir
[DNS, noms et certificats](dns.md).

## Sorties { #ways-out }

Un master est un serveur WireGuard avec une sortie, et la sortie a trois modes :

| Mode | Comment le maillage atteint Internet | État |
|---|---|---|
| **provider** | via un VPN commercial (gluetun) : le double saut, et le preset du master | construit |
| **direct** | directement par la liaison montante du master. Listez les modules du master sans `vpn-client` | construit |
| **master** | via *le master d’un autre réseau*, en tant que client dans l’un de ses groupes qui peut atteindre Internet et rien d’autre : multi-saut | conçu ; il exige l’enrôlement entre réseaux, c’est-à-dire la fédération |

Chaque master offre aussi le SOCKS5 de Tor au maillage, quelle que soit sa sortie.

## Un maillage par réseau { #one-mesh-per-network }

Chaque réseau a son propre maillage. La plage par défaut est `10.8.0.0/16` :
masters et nodes dans `10.8.0.0/24`, puis guests `.1`, pentest `.2`, devices `.3`
et routers `.4`. Un deuxième réseau prend une autre plage, par exemple
`10.9.0.0/16`, pour qu’un appareil qui est dans les deux puisse les distinguer.
Aujourd’hui, la plage est répartie sur plusieurs réglages (`mesh_subnet`, le
`server_ip` du vpn-server, `wg_subnet`, `wg_default_address` et `groups`, et le
`socks_policy_accept` de Tor), et le fichier fleet les règle tous.

## Adressage { #addressing }

| Quoi | Par défaut |
|---|---|
| Tout le maillage (routé sur chaque hôte) | `10.8.0.0/16` par défaut (`mesh_subnet`) |
| Clients wg-easy | `10.8.0.0/24` ; le serveur est `10.8.0.1` |
| Groupes de clients | `10.8.1.0/24` … `10.8.4.0/24` |
| Réseau de la stack | `172.64.0.0/24` sur un master, `172.128.0.0/24` sur un node |
| MTU WireGuard | `1376` (`wg_mtu`), mesurée avec [`kiwi-server mtu`](../server/operations.md#tunnel-mtu) |
| MTU du pont de la stack | `1500` (`bridge_mtu`) |

Chaque hôte de stack route le maillage via son client VPN (sur le master, via le
serveur WireGuard), si bien que l’hôte et ses conteneurs atteignent chaque node.

## Rester à jour { #keeping-it-fresh }

Chaque machine reçoit deux timers à partir des réglages de sa stack : un
**redémarrage quotidien du VPN** (`07:00`, pour une adresse de sortie neuve) et une
**mise à jour hebdomadaire** (dimanche 00:00, qui lance `podman auto-update` tant
que `auto_update: registry` est réglé). Le système d’exploitation se met à jour
lui-même et ne redémarre que dans [votre créneau](../server/machines.md#updates).

## Tout un LAN dans le maillage { #a-whole-lan-in-the-mesh }

Un routeur peut rejoindre le maillage comme client WireGuard dans le groupe
`routers`, ou envoyer le sous-réseau du maillage à un node gateway par une route
statique. Chaque appareil de ce LAN atteint alors chaque node sans faire tourner
WireGuard. Voir [Routeurs](routers.md).
