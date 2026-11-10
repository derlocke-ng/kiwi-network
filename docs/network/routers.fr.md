# Routeurs : tout un LAN dans le mesh

Cette page montre comment relier tout un réseau local (LAN), par exemple celui
de votre domicile ou de votre bureau, à votre Kiwi Network en passant par son
routeur. Un appareil du mesh, c’est-à-dire du réseau WireGuard privé de vos
machines, peut résoudre tous les noms du réseau et joindre tous les nodes. Les
appareils d’un LAN placé derrière un routeur peuvent en faire autant, sans que
chacun doive faire tourner WireGuard. Il y a deux façons de s’y prendre :

- **Le routeur est client du mesh.** Il fait tourner WireGuard avec une
  configuration délivrée par wg-easy, le serveur WireGuard du master
  (`kiwi-server enroll fleet.yaml router --group routers`). Il route le
  sous-réseau du mesh (`10.8.0.0/16`) dans le tunnel. On parle alors de tunnel
  *split*, parce que seul le trafic destiné au mesh y passe. Un tunnel *full*,
  lui, fait passer tout le trafic : tout le LAN accède alors à Internet par la
  sortie du master, c’est-à-dire par la connexion du master à Internet.
- **Le routeur a une route statique vers un node passerelle.** Le routeur n’a
  pas de tunnel. Il envoie le trafic destiné au sous-réseau du mesh à un node
  du LAN qui fait tourner le module `gateway`, et ce node le transmet par son
  client VPN.

Dans les deux cas, une seule règle DNS suffit, et vous n’avez aucune entrée à
créer pour des hôtes particuliers. Cette règle transmet les requêtes qui
portent sur le domaine de votre réseau (`*.home`) au Pi-hole du master, qui
connaît tous les noms d’hôtes et tous les noms de services. Rien d’autre ne
change dans le DNS du routeur.

Une chose ne fonctionne pas : un appareil du LAN ne peut pas joindre un
appareil situé *derrière un autre routeur* par l’adresse LAN de cet appareil.
Le mesh ne transporte que le trafic destiné aux adresses mesh, et c’est voulu.

## OpenWrt { #openwrt }

Pour OpenWrt, kiwi-server écrit toute la configuration sous la forme d’un
script `uci` :

```bash
# le routeur comme client du mesh, avec la configuration délivrée par le wg-easy du master
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf          # split : seulement le mesh
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf --full   # full : tout le trafic

# pas de tunnel sur le routeur : une route statique vers le node passerelle lychee
# (lychee doit avoir une adresse LAN statique dans le fichier fleet : network.dhcp false + address)
kiwi-server openwrt fleet.yaml --via lychee
kiwi-server openwrt fleet.yaml --via 192.168.1.5
```

Copiez le script obtenu sur le routeur, puis exécutez-le :

```bash
kiwi-server openwrt fleet.yaml --wireguard secrets/router.conf > kiwi.sh
scp kiwi.sh root@192.168.1.1:/tmp/ && ssh root@192.168.1.1 sh /tmp/kiwi.sh
```

Le script installe le paquet WireGuard s’il manque. Il crée une interface
nommée `kiwi`, nom que vous pouvez changer avec `--name`. Cette interface prend
comme MTU le `wg_mtu` du fichier fleet et n’a qu’un seul pair, le master. Ce
pair est créé avec `route_allowed_ips`, de sorte qu’OpenWrt ajoute lui-même les
routes. Le script crée aussi une zone de pare-feu vers laquelle le LAN est
autorisé à transmettre du trafic, avec masquerading et MSS clamping. Enfin, il
ajoute la règle dnsmasq qui transmet le domaine de votre réseau au master
(`server=/home/10.8.0.1`). Avec `--full`, dnsmasq envoie toutes les requêtes
DNS au Pi-hole du master. Chaque section écrite par le script porte un nom :
si vous relancez le script, il remplace donc ce qu’il avait écrit auparavant.

## FritzBox { #fritzbox }

Fritz!OS dispose d’un client WireGuard et de routes statiques, mais il ne sait
pas transmettre les requêtes DNS d’un seul domaine. C’est donc un node qui doit
se charger de la règle DNS. Les menus sont indiqués ci-dessous avec les
libellés de l’interface anglaise de Fritz!OS :

1. **Tunnel :** ouvrez Internet → Permit Access → VPN (WireGuard) → Add
   Connection, choisissez de vous connecter à un autre service WireGuard
   (« connect to another WireGuard service »), puis importez la configuration
   délivrée par le master. C’est la ligne
   `AllowedIPs` de cette configuration qui décide si le tunnel est split ou
   full.
2. **Ou une route statique :** ouvrez Home Network → Network → Network
   Settings → IPv4 Routes. Saisissez `10.8.0.0` comme destination, `255.255.0.0`
   comme masque de sous-réseau et l’adresse LAN du node passerelle comme
   passerelle.
3. **DNS :** faites en sorte que le LAN utilise un Pi-hole comme serveur DNS.
   Soit vous indiquez le node passerelle comme serveur DNS local, soit vous
   laissez le Pi-hole du node servir de serveur DHCP au LAN (les réglages
   `dns.dhcp_*`, avec le module dhcp-relay). Le Pi-hole du node connaît les
   noms de votre réseau et transmet toutes les autres requêtes au master.

Vous pouvez utiliser le tunnel et des routes statiques en même temps. Le trafic
destiné au mesh passe alors par le tunnel.

## Tout autre routeur { #any-other-router }

Pour n’importe quel autre routeur, trois choses suffisent. Soit vous donnez au
routeur une configuration de client WireGuard, soit vous ajoutez une route
statique pour `10.8.0.0/16` qui pointe vers l’adresse LAN du node passerelle.
Ensuite, faites en sorte que le LAN utilise comme serveur DNS un Pi-hole qui
connaît votre réseau. Tout node qui fait tourner le module `dns` en est un. Les
routeurs fondés sur dnsmasq (DD-WRT, Tomato, le redirecteur DNS de pfSense)
acceptent aussi la règle de transmission, qui tient en une ligne :
`server=/home/10.8.0.1`.
