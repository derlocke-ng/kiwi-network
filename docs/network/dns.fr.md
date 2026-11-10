# DNS, noms et certificats

## Une seule chaîne de résolution { #one-resolver-chain }

Le DNS est une seule chaîne pour tout le réseau :

```
LAN device ──▶ gateway node's Pi-hole ──▶ master's Pi-hole ──▶ gluetun DNS-over-TLS (Quad9)
VPN client ───────────────────────────────▶ master's Pi-hole       └─ leaves through the VPN exit
```

- **Les clients VPN** (ordinateurs portables, téléphones) interrogent le Pi-hole du
  master à `10.8.0.1`.
- **Le Pi-hole d’un node** interroge d’abord le Pi-hole du master, si bien que le
  réseau partage une seule liste de blocage et que chaque requête sort par la
  sortie du master. Quad9 (`9.9.9.9`, `149.112.112.112`, `fallback_dns`) suit dans
  un ordre strict et ne répond que tant que le master est injoignable.
- **Le Pi-hole du master** transmet au résolveur DNS-over-TLS de son client VPN
  (Quad9 par défaut, `dot_providers`).
- **Les noms sous le domaine de la fleet** sont transmis au master et ne le
  quittent jamais. Le master marque le domaine comme local.

Chaque hôte de stack porte aussi les noms de la fleet dans `/etc/hosts` (ses
propres noms pointant vers lui-même), si bien que les sauvegardes et les
renouvellements de certificats se résolvent sans Pi-hole. Sous Fedora CoreOS et
uCore, l’hôte lui-même résout via le Pi-hole de sa propre stack.

**Voisins sur le même LAN.** Le Pi-hole et le fichier hosts d’un node répondent
avec l’**adresse LAN** des nodes de la fleet qui ont une adresse statique dans son
propre sous-réseau, si bien que le trafic entre deux machines de la même pièce
reste dans la pièce. Le master continue de répondre avec les adresses de maillage.

## Noms : `service.hostname.home` { #names-servicehostnamehome }

Chaque hôte est `<host>.<domain>` (`papaya.home`), et chaque service qu’il fait
tourner est un nom en dessous : `cloud.papaya.home`, `vault.papaya.home`,
`portainer.papaya.home`, `dl.lychee.home`, et sur le master `wg.sorbet.home`,
`pihole.sorbet.home`, `hub.sorbet.home`, `relay.sorbet.home`. Chaque nom qu’un
module annonce entre dans les enregistrements DNS de la fleet à l’**adresse de
maillage** de l’hôte. Chaque Pi-hole de la fleet résout chaque nom d’hôte et de
service (split-horizon, `fleet_records`). Ajoutez les vôtres avec
`extra_records`.

Le domaine par défaut est **`.home`**, car l’ICANN ne le déléguera pas comme
domaine de premier niveau public. Un nom de la fleet ne peut jamais fuiter vers un
registre public, et personne d’autre ne peut l’enregistrer ni obtenir pour lui un
certificat reconnu par les navigateurs. `.kiwi` est un vrai TLD, c’est pourquoi la
fleet l’a abandonné. kiwi-server vérifie votre choix : `home`, `corp`, `mail`,
`internal`, `arpa` et `test` passent sans rien dire, `.local` est refusé (il
appartient à mDNS), `.lan` reçoit un avertissement (les routeurs y répondent
eux-mêmes), et les TLD publics reçoivent un avertissement.

Les noms *hors* du domaine de la fleet, pour un hub ou un relais public, reçoivent
des certificats Let’s Encrypt quand le reverse proxy du master est public.

## Les proxys SOCKS5 de Mullvad par leur nom { #mullvad-socks5-proxies-by-name }

Depuis kiwi-server 2.2.0, le Pi-hole du master répond pour chaque **proxy SOCKS5
de Mullvad**, à la fois sous `de-fra-wg-socks5-001.relays.mullvad.net` et sous la
forme courte `de-fra-001.mullvad.home`. gluetun refuse ces réponses en plage
privée (protection contre le DNS rebinding), donc sans ces enregistrements les noms
ne se résoudraient que via les résolveurs de secours. Un timer de l’hôte
(`km-mullvad-socks.timer`, toutes les 6 heures) actualise la liste depuis
[derlocke-ng/mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5). Seuls
les noms `*.relays.mullvad.net` avec des adresses `10.x` en sont acceptés, si bien
que la liste ne peut jamais rediriger aucun autre nom.

C’est activé dans le preset du master, dont la sortie est Mullvad. Désactivez-le
avec `mullvad_socks: false` dans le bloc `dns:` du master.

## Une seule autorité de certification pour la fleet { #one-ca-for-the-fleet }

Avec `tls.auto: true` (par défaut), kiwi-server conserve **une seule autorité de
certification** pour la fleet dans `secrets/ca/` (`kiwiCA.key`, `kiwiCA.pem`,
RSA-4096, valable 3650 jours), créée la première fois qu’un hôte a besoin d’un
certificat. Chaque hôte qui fait tourner le reverse proxy reçoit un certificat pour
`<hostname>` et `*.<hostname>` (825 jours, la plus longue durée de vie que les
navigateurs acceptent encore, renouvelé quand il reste moins de 30 jours), et
chaque machine que kiwi-server construit installe l’autorité de certification dans
son magasin de confiance.

Réglez des **contraintes de noms** et l’autorité de certification ne peut signer
que des noms sous le domaine de la fleet : `tls: { name_constraints: [home] }`.
La fleet d’exemple le fait ; la valeur par défaut intégrée est sans contrainte. Une
`kiwiCA.key` volée ne vaut alors rien pour quoi que ce soit d’autre, ce qui compte
parce que chaque machine lui fait confiance.

```bash
kiwi-server ca fleet.yaml        # afficher l’autorité de certification de la fleet
```

Importez `kiwiCA.pem` sur vos propres appareils (navigateurs, téléphones) pour que
`https://cloud.papaya.home` soit reconnu. Pour utiliser plutôt vos propres
certificats, réglez `tls_fullchain` et `tls_privkey` dans le module reverse-proxy.

!!! warning "Gardez `secrets/` privé"
    `kiwiCA.key` signe des certificats auxquels chacune de vos machines fait
    confiance. Gardez `secrets/` et `output/` hors de git (`output/` est déjà dans
    le `.gitignore` de kiwi-server).
