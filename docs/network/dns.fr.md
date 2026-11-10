# DNS, noms et certificats

Chaque machine et chaque service d’un Kiwi Network a un nom, par exemple
`cloud.papaya.home`, et vous l’ouvrez en HTTPS avec un certificat auquel vos
appareils font confiance. Cette page explique comment les noms sont résolus
dans le réseau, comment ils sont formés et d’où viennent les certificats. Les
serveurs DNS sont des Pi-hole, qui bloquent aussi les domaines indésirables
grâce à une liste de blocage commune.

## Une seule chaîne de résolution { #one-resolver-chain }

Toutes les requêtes DNS du réseau suivent la même chaîne de serveurs DNS :

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Les clients VPN** (ordinateurs portables, téléphones) envoient leurs
  requêtes au Pi-hole du master, à l’adresse `10.8.0.1`.
- **Le Pi-hole d’un node** interroge d’abord le Pi-hole du master. Tout le
  réseau partage ainsi une seule liste de blocage, et chaque requête rejoint
  Internet par la sortie du master, c’est-à-dire par la connexion du master à
  Internet. Quad9 (`9.9.9.9`, `149.112.112.112`, défini avec `fallback_dns`)
  vient ensuite, dans un ordre strict : il ne répond donc que lorsque le master
  est injoignable.
- **Le Pi-hole du master** transmet les requêtes au résolveur DNS-over-TLS de
  son client VPN. Par défaut, ce résolveur est Quad9 (`dot_providers`).
- **Les noms du domaine de votre réseau** sont transmis au master, qui ne les
  envoie jamais plus loin. Le master déclare ce domaine comme local.

Chaque machine qui fait tourner une stack, c’est-à-dire un ensemble de
conteneurs avec leur configuration, a aussi les noms du réseau dans son fichier
`/etc/hosts`, et ses propres noms y pointent vers elle-même. Les sauvegardes et
les renouvellements de certificats peuvent donc résoudre les noms sans Pi-hole.
Sous Fedora CoreOS et uCore, la machine elle-même utilise comme résolveur le
Pi-hole de sa propre stack.

**Voisins sur le même LAN.** Si d’autres nodes de votre réseau ont une adresse
statique dans le sous-réseau d’un node, le Pi-hole et le fichier hosts de ce
node répondent avec leur **adresse LAN**. Le trafic entre deux machines du même
LAN reste alors sur ce LAN. Le master, lui, continue de répondre avec les
adresses mesh.

## Noms : `service.hostname.home` { #names-servicehostnamehome }

Chaque hôte porte le nom `<host>.<domain>`, par exemple `papaya.home`. Chaque
service qu’il héberge reçoit un nom placé sous celui de l’hôte :
`cloud.papaya.home`, `vault.papaya.home`, `portainer.papaya.home`,
`dl.lychee.home`, et sur le master `wg.sorbet.home`, `pihole.sorbet.home`,
`hub.sorbet.home`, `relay.sorbet.home`. Tous les noms qu’un module annonce sont
inscrits dans les enregistrements DNS du réseau avec l’**adresse mesh** de
l’hôte. Chaque Pi-hole du réseau peut ainsi résoudre tous les noms d’hôtes et
tous les noms de services. Le réglage correspondant est `fleet_records`, et la
technique s’appelle le DNS split-horizon, parce que ces noms ne reçoivent de
réponse qu’à l’intérieur de votre réseau. Vous pouvez ajouter vos propres
enregistrements avec `extra_records`.

Le domaine par défaut est **`.home`**. Il a été choisi parce que l’ICANN ne le
déléguera pas comme domaine de premier niveau (TLD) public. Un nom de votre
réseau ne peut donc jamais se retrouver dans un registre public, et personne
d’autre ne peut l’enregistrer ni obtenir pour lui un certificat reconnu par les
navigateurs. `.kiwi`, en revanche, est un vrai TLD, et c’est pourquoi Kiwi
Network ne l’utilise plus. kiwi-server vérifie le domaine que vous choisissez.
`home`, `corp`, `mail`, `internal`, `arpa` et `test` sont acceptés sans
remarque. `.local` est refusé, car il est réservé à mDNS. `.lan` déclenche un
avertissement, parce que les routeurs y répondent eux-mêmes, et les TLD publics
en déclenchent un aussi.

Les noms situés *en dehors* du domaine de votre réseau, dont vous avez besoin
pour un hub ou un relais public, obtiennent des certificats Let's Encrypt si le
reverse proxy du master est public.

## Les proxys SOCKS5 de Mullvad par leur nom { #mullvad-socks5-proxies-by-name }

Les proxys SOCKS5 de Mullvad ont des adresses dans une plage privée, et cette
fonction vous permet de les utiliser par leur nom. Depuis kiwi-server 2.2.0, le
Pi-hole du master répond pour chaque **proxy SOCKS5 de Mullvad**, aussi bien
sous son nom complet, par exemple `de-fra-wg-socks5-001.relays.mullvad.net`,
que sous un nom court, par exemple `de-fra-001.mullvad.home`. gluetun rejette
les réponses DNS qui pointent vers des adresses privées : c’est sa protection
contre le DNS rebinding. Sans ces enregistrements, ces noms ne seraient donc
résolus que par les résolveurs de secours. Un timer sur l’hôte
(`km-mullvad-socks.timer`, toutes les 6 heures) met la liste à jour à partir de
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5).
Dans cette liste, seuls les noms `*.relays.mullvad.net` associés à des adresses
en `10.x` sont acceptés. Elle ne peut donc jamais rediriger un autre nom.

Cette fonction est activée dans le preset du master, puisque la sortie de ce
preset passe par Mullvad. Pour la désactiver, définissez `mullvad_socks: false`
dans le bloc `dns:` du master.

## Une seule CA pour tout le réseau { #one-ca-for-the-fleet }

Une autorité de certification (CA) signe les certificats que vos services
utilisent pour HTTPS. Avec `tls.auto: true`, qui est la valeur par défaut,
kiwi-server conserve **une seule autorité de certification** pour tout le
réseau dans `secrets/ca/`. La CA se compose des fichiers `kiwiCA.key` et
`kiwiCA.pem`, utilise RSA-4096 et est valable 3 650 jours. kiwi-server la crée
la première fois qu’un hôte a besoin d’un certificat. Chaque hôte qui fait
tourner le reverse proxy reçoit un certificat pour `<hostname>` et
`*.<hostname>`. Ce certificat est valable 825 jours, la durée la plus longue
que les navigateurs acceptent encore, et il est renouvelé lorsqu’il lui reste
moins de 30 jours. Chaque machine construite par kiwi-server installe la CA
parmi ses autorités de confiance.

Si vous définissez des **contraintes de nom**, la CA ne peut signer que des
noms du domaine de votre réseau : `tls: { name_constraints: [home] }`.
L’exemple de fichier fleet le fait, mais la valeur par défaut intégrée ne
prévoit aucune contrainte. Avec cette contrainte, une `kiwiCA.key` volée ne
vaut rien pour tout autre nom. C’est important, car toutes les machines font
confiance à la CA.

```bash
kiwi-server ca fleet.yaml        # afficher la CA de la fleet
```

Importez `kiwiCA.pem` sur vos propres appareils (navigateurs, téléphones) pour
qu’ils fassent confiance à `https://cloud.papaya.home`. Si vous préférez
utiliser vos propres certificats, définissez `tls_fullchain` et `tls_privkey`
dans le module reverse-proxy.

!!! warning "Gardez `secrets/` pour vous"
    `kiwiCA.key` signe des certificats auxquels toutes vos machines font
    confiance. Gardez `secrets/` et `output/` hors de git (`output/` figure
    déjà dans le `.gitignore` de kiwi-server).
