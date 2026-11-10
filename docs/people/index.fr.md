# Des hubs, pas des plateformes

Le réseau relie vos machines. Les **hubs** relient les personnes. Un hub est un
ensemble d’applications web (un marché ouvert, un fil, une messagerie, du partage
de fichiers, des listes partagées, un gestionnaire de mots de passe, un agenda) qui
tournent entièrement dans le navigateur et se synchronisent via des relais
[nostr](https://nostr.com) que la communauté choisit. Il n’y a ni serveur de
comptes ni backend au milieu, et tout ce qui est privé est chiffré sur l’appareil
avant de le quitter. N’importe qui peut faire tourner un hub pour n’importe quelle
communauté. Voir [les apps du framework](apps.md).

Trois dépôts composent l’ensemble :

| Dépôt | Ce que c’est |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Le moteur : identité et comptes, relais et synchronisation, personnes et partage, modération, le kit de design, les pages du hub et dix applications. Il ne livre rien qu’un utilisateur ouvre tel quel. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | La première **distribution** : un hub construit avec le framework, avec un nom, des relais par défaut et les dix applications montées sous ses propres noms. Le modèle à forker pour le vôtre. GPL-3.0-or-later. **En ligne :** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Un catalogue git de hubs et de leurs applications, de même forme que le [kiwi-catalog](../desktop/catalogs.md) du bureau |

## Comment tout s’assemble { #how-it-fits-together }

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Le vocabulaire { #the-words }

- **Hub** : ce que produit une distribution. Des fichiers statiques, si bien
  qu’héberger un hub revient à servir un dossier. Chaque hub a une page d’accueil,
  des réglages et une page de compte.
- **Distribution** : un hub construit sur le framework, avec un nom et une
  apparence, des relais par défaut, et un ensemble choisi d’applications sur des
  espaces choisis. Tout ce qu’un fork modifie se trouve dans un seul fichier,
  `distribution.js`, plus ses traductions.
- **App** : un dossier avec un manifeste, qui se branche sur n’importe quelle
  distribution. Les apps ne parlent qu’à l’API publique du framework et ne touchent
  jamais directement au stockage ni aux clés.
- **Espace** (space) : une communauté nommée, qui a un propriétaire, avec ses
  propres modérateurs et, en option, ses propres relais (sur le modèle des
  communautés modérées de NIP-72). Un autre hub peut servir le même espace en
  indiquant son adresse.
- **Montage** (mount) : du code d’app sur un espace, avec son propre nom, sa propre
  route et sa propre icône. Une app peut être montée de nombreuses fois. Le
  *Trading Post* d’Armory est l’app `market` du framework montée sur l’espace
  `tradingpost` d’Armory.

Deux personnes sur des distributions différentes sont amies, partagent et
discutent exactement comme sur une seule, car l’identité et les données sont des
événements nostr, pas ceux du hub.

## Comptes et clés { #accounts-and-keys }

- Chaque appareil reçoit une clé à sa première visite, conservée dans le
  navigateur.
- Un **compte** est un nom d’utilisateur et un mot de passe, construit sur de
  simples événements nostr sans aucun registre : le mot de passe est étiré avec
  scrypt et déverrouille votre clé. Personne ne peut prendre ni écraser un compte
  sans le mot de passe. Il n’y a **pas de réinitialisation du mot de passe**.
- Vous pouvez aussi vous connecter avec une clé nostr existante (`nsec`, hex ou
  `ncryptsec`). Les signataires par extension de navigateur et à distance (NIP-07,
  NIP-46) sont prévus, pas construits.
- Un seul compte fonctionne dans toutes les apps du hub et sur chaque appareil où
  vous vous connectez.

## Modèle de confidentialité { #privacy-model }

**Ce qui est chiffré.** Le contenu est scellé dans le navigateur avant d’aller où
que ce soit : AES-256-GCM avec des clés dérivées par HKDF. Les messages privés sont
des messages NIP-17 dans des emballages cadeaux (gift wraps) NIP-59. Chaque fichier
reçoit une clé AES-256-GCM aléatoire avant d’aller sur un serveur de médias, et les
photos sont réencodées, ce qui supprime les métadonnées de l’appareil photo. Le
Vault est scellé par sa propre phrase secrète (scrypt + AES-256-GCM). Les appels
vont de navigateur à navigateur, chiffrés par WebRTC.

**Le local d’abord.** Chaque écriture va d’abord dans la base de données propre du
navigateur, puis vers les relais. Les lectures viennent de l’appareil, si bien que
les apps fonctionnent hors ligne. Quand un appareil se reconnecte, il remet en
place ce qu’un relais a oublié : les données ne sont perdues que si chaque appareil
qui les détenait a disparu *et* qu’il n’existe aucune sauvegarde.

**Ce que les autres peuvent voir.** Les dépôts sont explicites sur les limites :

- Les relais voient les métadonnées : qui écrit à quelles adresses, quand, combien,
  et depuis quelle adresse IP. Utilisez un VPN ou Tor si cela compte pour vous.
- La clé d’un espace n’est pas un secret. Elle tient les publications d’une
  communauté à l’écart des regards directs. Les j’aime, les signalements et qui a
  commenté quoi sont visibles des relais.
- Les notes de DevBoard et les signalements de modération sont publics par
  conception.
- Votre clé se trouve dans le stockage du navigateur. Tous les sites GitHub Pages
  d’un même compte partagent une origine, si bien qu’un hub sur son propre
  (sous-)domaine est la configuration la plus solide.
- Les transferts directs et les appels révèlent les adresses IP des deux
  navigateurs l’un à l’autre et aux serveurs STUN (ceux de Google et de Cloudflare
  par défaut ; un hub peut régler les siens).
- « Pas de serveur chez nous » signifie aucun sur le chemin critique. Les apps
  utilisent tout de même les relais, les serveurs de médias et, pour l’agenda, le
  serveur CalDAV que vous ou votre hub choisissez.

## Modération { #moderation }

Trois couches : votre propre liste de blocage (chiffrée, vous seul pouvez la lire),
les signalements (publics, signés), et la politique propre aux relais. Un espace a
des modérateurs. Le signalement d’un modérateur replie aussitôt une publication.
Sinon, il faut trois signalements de personnes qui ne sont pas bloquées. Les
publications peuvent être marquées 18+ ou comme publicité, et elles ne s’affichent
alors qu’aux personnes ayant un compte.

## Pour aller plus loin { #read-on }

- [Armory et ses applications](armory.md)
- [Héberger votre propre hub](hubs.md)
- L’[architecture](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  et le [protocole d’échange](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  du framework lui-même
