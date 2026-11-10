# kiwi-killswitch

Un **kill switch VPN qui se ferme en cas de panne** pour GNOME sous Fedora
Silverblue et Bluefin. Un seul démon root possède le pare-feu. Un bouton dans les
Réglages rapides de GNOME, une application GTK4 et une CLI le pilotent via le bus
système D-Bus, sans jamais demander de mot de passe.

Il protège **une seule** connexion VPN à la fois, WireGuard ou OpenVPN. Il ne
connecte pas votre VPN à votre place : vous établissez les connexions dans les
Paramètres de GNOME, et le kill switch construit un pare-feu sans fuite autour de
ce qui est réellement actif.

- Dépôt : [derlocke-ng/kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch), GPL-3.0-or-later
- Dernière version : **v0.2.3**. Elle figure dans le [catalogue Kiwi](catalogs.md), portées utilisateur + système.
- GNOME Shell 45 à 50.

```
┌─ your session (unprivileged) ─────────────┐   ┌─ root ──────────────────────┐
│  GNOME Quick Settings toggle              │   │  kiwi-killswitchd           │
│  kiwi-killswitch-settings (GTK4)          │──▶│   nftables  (inet + netdev) │
│  kiwi-killswitch (CLI)                    │   │   systemd-resolved steering │
└───────────────────────────────────────────┘   │   NM + kernel event watcher │
             D-Bus system bus, group `wheel`    └─────────────────────────────┘
```

Une extension GNOME est un processus non privilégié. Elle ne peut pas et ne doit
pas toucher au pare-feu ; l’application des règles se fait donc dans le démon, et
l’interface ne fait que demander.

## Ce qu’il fait { #what-it-does }

- **Fermé en cas de panne.** `policy drop` sur la sortie, l’entrée et le transfert,
  en IPv4 et en IPv6, basculé de façon atomique. Le trafic ne sort que par le
  tunnel protégé. Si le VPN tombe, si vous redémarrez, ou si vous passez du Wi-Fi
  au partage de connexion, tout reste bloqué jusqu’au retour d’un chemin autorisé.
- **Les nouvelles interfaces ne peuvent pas fuir.** Branchez un partage de
  connexion USB ou activez le Wi-Fi alors qu’il est armé, et la nouvelle interface
  est bloquée par défaut, pas autorisée par omission.
- **Trois niveaux d’application.** *Standard* filtre la sortie et l’entrée.
  *Strict* (par défaut) filtre aussi le trafic **transféré**, car les conteneurs,
  les VM et Waydroid passent par l’hôte, et les paquets transférés ne passent jamais
  par le hook de sortie. *Paranoid* ajoute une chaîne **netdev egress** sur chaque
  carte réseau, la seule couche qui voit le trafic des sockets bruts.
- **Le DNS ne peut pas s’égarer.** Choisissez via le VPN, celui du réseau (kiwi-nodes
  de confiance uniquement), ou un résolveur que vous choisissez. Il est appliqué via
  les réglages par lien de systemd-resolved, avec un filet de sécurité nftables qui
  rejette toute autre requête.
- **Les points d’accès désignés par nom d’hôte sont épinglés, pas confiés au DNS.**
  Le démon résout lui-même le nom d’hôte d’un serveur VPN, en DNS-over-HTTPS vers
  une IP épinglée avec un certificat vérifié, et met chaque réponse en cache.
- **Choisissez une connexion, puis Appliquer.** Les changements sont préparés, si
  bien que vous pouvez passer de « LAN de la maison + kiwi-node » à « partage de
  connexion + VPN » *alors que vous êtes déjà en partage de connexion*, puis
  l’appliquer en une seule transaction atomique, sans fenêtre désarmée entre les
  deux.
- **kiwi-nodes de confiance.** Une gateway qui tunnelise déjà pour vous (un
  [node gateway](../server/roles.md#node)), reconnue par son IP **et** son adresse
  MAC, peut remplacer le VPN sur son propre réseau. C’est sur activation explicite,
  jamais déduit.
- **Un seul VPN, imposé.** Seul le serveur de la connexion sélectionnée est
  joignable. Tout autre tunnel que vous démarrez ne peut pas se connecter, et
  l’interface le nomme.
- **Survit à tout.** Redémarrages, déconnexion et reconnexion, redémarrages de
  NetworkManager : les règles restent. Une unité séparée pose un blocage strict
  *avant que le réseau ne démarre*.

## Installation { #install }

Il exige `nftables`, `NetworkManager`, `python3-gobject` et, pour WireGuard,
`wireguard-tools`, tous présents sur Silverblue et Bluefin. Rien n’est écrit dans
le `/usr` immuable. Votre utilisateur doit être dans `wheel`.

```bash
kiwi install kiwi-killswitch   # both halves; sets up kiwi's system scope if needed
```

Ou depuis un clone : `sudo ./install.sh install` (le démon, la CLI, la politique du
bus et les unités systemd), puis `./install.sh install` (l’extension GNOME et
l’application de réglages). Déconnectez-vous puis reconnectez-vous pour que GNOME
charge l’extension. La désinstallation désarme d’abord, si bien qu’elle ne peut pas
vous laisser enfermé dehors.

## Utilisation { #use }

Ouvrez **Réglages rapides → Kill Switch** pour armer, désarmer et choisir quel VPN
est protégé, ou **Kiwi Kill Switch** dans la grille d’applications pour tout le
reste.

```bash
kiwi-killswitch status                   # ce qui est appliqué en ce moment
kiwi-killswitch list                     # les connexions VPN que NetworkManager connaît
kiwi-killswitch vpn <name>               # préparer laquelle est protégée
kiwi-killswitch set dns_mode tunnel
kiwi-killswitch apply                    # une seule transaction atomique
kiwi-killswitch arm                      # ou : arm <vpn>
kiwi-killswitch disarm
kiwi-killswitch pending                  # ce qui est préparé ; revert l’abandonne
```

!!! warning "Armer via SSH"
    Armer coupe une session venant d’un sous-réseau qui n’est pas dans
    `mgmt_subnets`. C’est le comportement correct d’un kill switch. Réglez-le
    d’abord :
    ```bash
    kiwi-killswitch set mgmt_subnets 192.168.0.0/16
    kiwi-killswitch set allow_in_ports 22
    kiwi-killswitch apply
    ```

**Récupération.** La CLI n’a pas besoin du réseau, donc un TTY suffit toujours :
`kiwi-killswitch disarm`. Si le démon lui-même a disparu :
`sudo nft delete table inet kiwi_ks` et `sudo nft delete table netdev kiwi_ks_egress`.

**Machines virtuelles.** Une VM en pont ne passe jamais par l’hôte, donc le kill
switch la laisse tranquille (évitez `paranoid`, qui filtre au niveau de la carte
physique). Une VM en NAT passe par l’hôte. `strict` la fait sortir par le tunnel et
la bloque quand le tunnel est coupé. Ajoutez son sous-réseau à `mgmt_subnets` pour
que son DHCP et son DNS atteignent l’hôte :

| Réglage | Sortant | Entrant | Épinglé hors du tunnel |
|---|---|---|---|
| `allow_lan` | oui (auto) | non | non |
| `bypass_subnets` | oui | non | non |
| `mgmt_subnets` | oui | oui | oui |

**Vérification.** Armez-le, puis coupez le VPN (`nmcli connection down …`).
`curl --max-time 5 ifconfig.me` doit **expirer**, et non afficher votre vraie IP. Ne
le jugez pas en comparant les IP de sortie : prouvez l’usage du tunnel avec
`wg show <iface> transfer` ou `ip route get 1.1.1.1`.

## Cohabitation et limites connues { #coexistence-and-known-limits }

- **firewalld peut rester actif.** Ses chaînes tournent à la priorité 10 et les
  nôtres à −10.
- Ne le faites **pas** tourner à côté d’un autre kill switch qui possède une table
  output-drop.
- Laissez `nftables.service` tranquille si vous ne l’utilisez pas. L’arrêter vide
  toutes les tables. Le démon rétablit ses règles en quelques secondes, mais il n’y
  a aucune raison d’ouvrir cette fenêtre.
- Un VPN dont le point d’accès est un **nom d’hôte** ne peut pas se reconnecter
  tant que le kill switch est armé, sauf si le DNS est réglé sur *a resolver I
  choose* (un résolveur que je choisis). NetworkManager et OpenVPN résolvent le nom via le résolveur du
  système, qui est bloqué tant qu’aucun tunnel n’est actif. Les connexions avec une
  IP littérale ne sont pas concernées.
- **Un résolveur que vous choisissez est joignable hors du tunnel** tant que le
  tunnel est coupé. Activez DNS-over-TLS pour lui.
- **Un node de confiance enregistré sans adresse MAC** est reconnu sur sa seule
  adresse de gateway.
- **Le contrôle sans mot de passe** repose sur la politique du bus D-Bus pour le
  groupe `wheel`. Cela signifie aussi que n’importe quel programme qui tourne sous
  votre utilisateur peut désactiver le kill switch sans demander.
- Il arrête les fuites au niveau du réseau. Ce n’est ni Tails ni Whonix, et il ne
  fait rien contre l’empreinte du navigateur, WebRTC, ou une application qui
  appelle chez elle à travers le tunnel.
- C’est un outil personnel et il n’a pas été audité de façon indépendante.
  `tests/run.sh` exerce le vrai démon avec le vrai nftables, chaque groupe de tests
  dans son propre espace de noms, sans root.
- Ses tags de version ne sont pas encore signés, donc avec kiwi-updater 2.4 sa
  moitié root demande votre mot de passe lors des mises à jour.

Il descend de `gnome-vpn-killswitch` (ordre de démarrage), `kiwi-vpn-monitor`
(détection de la gateway) et `nova-killswitch` (l’architecture du démon), du même
auteur.
