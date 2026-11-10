# Routeurs : tout un LAN dans le maillage

Un appareil du maillage résout chaque nom de la fleet et atteint chaque node. Un
LAN derrière un routeur peut faire de même sans que chaque appareil fasse tourner
WireGuard, de l’une de deux façons :

- **Le routeur est un client du maillage.** Il fait tourner WireGuard avec une
  configuration émise par le wg-easy du master
  (`kiwi-server enroll fleet.yaml router --group routers`) et route le sous-réseau
  du maillage (`10.8.0.0/16`) dans le tunnel.
  C’est le tunnel *partiel* (split) : seul le trafic du maillage y passe. Le tunnel
  *complet* (full) envoie tout, si bien que tout le LAN atteint Internet par la
  sortie du master.
- **Une route statique vers un node gateway.** Le routeur n’a pas de tunnel. Il
  envoie le sous-réseau du maillage à un node du LAN qui fait tourner le module
  `gateway`, lequel le transmet via son client VPN.

Dans les deux cas, une seule règle DNS remplace les surcharges hôte par hôte : le
domaine de la fleet (`*.home`) est transmis au Pi-hole du master, qui connaît chaque
nom d’hôte et de service. Rien d’autre ne change dans le DNS du routeur.

Ce que le LAN ne peut pas faire, c’est atteindre un appareil *derrière un autre
routeur* par son adresse LAN. Le maillage ne transporte que des adresses de
maillage, à dessein.

## OpenWrt { #openwrt }

kiwi-server écrit toute la configuration sous forme de script `uci` :

```bash
# le routeur comme client du maillage, avec la configuration émise par le wg-easy du master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split : uniquement le maillage
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full : tout

# pas de tunnel sur le routeur : une route statique vers le node gateway lychee
# (lychee a besoin d’une adresse LAN statique dans la fleet : network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copiez la sortie sur le routeur et exécutez-la :

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Le script installe le paquet WireGuard s’il manque. Il crée une interface `kiwi`
(changez le nom avec `--name`), avec le `wg_mtu` de la fleet comme MTU et un pair
pour le master
et `route_allowed_ips`, une zone de pare-feu vers laquelle le LAN peut transmettre
(avec masquerading et MSS clamping), et le renvoi dnsmasq pour le domaine de la
fleet (`server=/home/10.8.0.1`). Avec `--full`, dnsmasq envoie chaque requête au
Pi-hole du master. Chaque section porte un nom, si bien que relancer le script
remplace ce qu’il a écrit auparavant.

## FritzBox { #fritzbox }

Fritz!OS a un client WireGuard et des routes statiques, mais pas de renvoi DNS par
domaine ; la règle DNS passe donc sur un node :

1. **Tunnel :** Internet → Permit Access → VPN (WireGuard) → Add Connection →
   connect to another WireGuard service → importez la configuration émise par le
   master. Son `AllowedIPs` décide entre split et full.
2. **Ou une route statique :** Home Network → Network → Network Settings → IPv4
   Routes. Destination `10.8.0.0`, masque de sous-réseau `255.255.0.0`, passerelle :
   l’adresse LAN du node gateway.
3. **DNS :** faites pointer le LAN vers un Pi-hole. Soit vous réglez le node gateway
   comme serveur DNS local, soit vous laissez le Pi-hole du node être le serveur
   DHCP du LAN (réglages `dns.dhcp_*` plus le module dhcp-relay). Le Pi-hole du node
   porte les noms de la fleet et transmet le reste au master.

Le tunnel et les routes statiques peuvent coexister. Le tunnel l’emporte pour le
maillage.

## Tout autre routeur { #any-other-router }

Trois faits suffisent. Soit vous donnez au routeur une configuration client
WireGuard, soit vous ajoutez une route statique pour `10.8.0.0/16` vers l’adresse
LAN du node gateway. Puis faites pointer le DNS du LAN vers un Pi-hole qui connaît
la fleet, c’est-à-dire n’importe quel node qui fait tourner le module `dns`. Les
routeurs reposant sur dnsmasq (DD-WRT, Tomato, le forwarder de pfSense) acceptent
aussi le renvoi d’une ligne `server=/home/10.8.0.1`.
