# Les apps du framework

kiwi-framework livre ses apps sous des noms simples. Une distribution les
**monte**, sur un espace et sous un nom qui lui est propre. Une app peut être
montée de nombreuses fois : une banque de graines et une boutique de pierres
précieuses sont le même code `market` sur deux espaces, chacun avec ses propres
modérateurs et relais, comme deux tuiles sur un même hub.

| App | Ce que c’est | Armory la monte sous le nom |
|---|---|---|
| `market` | **Un marché ouvert** pour la communauté que sert un montage. Les annonces ont des photos, un prix, d’où elles sont envoyées et vers où, ou un retrait sur place. Les acheteurs les trouvent par catégorie et selon l’endroit où ils sont, grâce à des étiquettes de recherche que les relais peuvent faire correspondre mais pas lire. Les acheteurs écrivent au vendeur dans la messagerie, avec un message sur l’annonce déjà rédigé. Les annonces peuvent être réservées, vendues, renouvelées et signalées, et expirent après 30 à 90 jours. Un montage peut exiger que les vendeurs se soient d’abord montrés dans un fil, ou qu’ils aient été approuvés par un modérateur | Trading Post |
| `feed` | **Un fil communautaire** : des entrées avec photos, hashtags, j’aime et commentaires pour l’espace, pour les amis, pour un cercle ou pour vous seul, plus des carnets (une série d’entrées avec une couverture). Les entrées peuvent être marquées 18+ ou comme publicité | Outpost |
| `chat` | **Messages** : messages privés et fichiers aux amis (NIP-17), groupes qui restent jusqu’à ce que leur hôte les ferme, salons en direct qui disparaissent une fois vides, réponses, réactions, modifications, épinglages, recherche sur l’appareil, messages éphémères, et appels audio et vidéo jusqu’à six personnes | Uplink |
| `notices` | **Un tableau d’affichage** de notes publiques signées avec preuve de travail, votes, signalements et date d’expiration | DevBoard |
| `boards` | **Listes et notes partagées** : listes de cases à cocher, inventaires avec quantités et notes Markdown, chiffrés de bout en bout, avec des liens en modification ou en lecture seule | Loadout |
| `payload` | **Partage de fichiers** : un lien qui attend, chiffré, sur vos serveurs de médias ; des fichiers aux amis et aux groupes ; ou directement de navigateur à navigateur | Payload |
| `vault` | **Un gestionnaire de mots de passe** : identifiants, notes, cartes, codes de double authentification, un générateur et un bilan de santé, clés SSH, une autorité de certification SSH, une autorité de certification X.509 et des certificats TLS. Scellé par sa propre phrase secrète | Vault |
| `authenticator` | **Codes de double authentification** (TOTP), conservés dans le même coffre scellé | Authenticator |
| `calendar` | **Vos agendas** depuis Nextcloud ou n’importe quel serveur CalDAV. Rien ne va aux relais | Calendar |
| `pong` | **Pong à deux joueurs** entre navigateurs | pongjs |

Chaque hub a aussi une page d’accueil, des réglages (votre compte et vos appareils,
amis et cercles, personnes bloquées, relais, espaces, serveurs de médias,
sauvegardes) et une page de compte. Les notifications se trouvent dans le hub
lui-même.

## Espaces et montages { #spaces-and-mounts }

- Un **espace** est une communauté nommée, qui a un propriétaire : un id, une clé
  de propriétaire, un nom, des modérateurs, ses propres relais et un indicateur
  adulte. Il est calqué sur les communautés modérées de nostr (NIP-72), si bien que
  d’autres clients nostr peuvent le lire. Chaque publication et chaque annonce
  appartient à exactement un espace.
- Un **montage** est du code d’app sur un espace, avec son propre id, son propre
  nom et sa propre icône. Importer la boutique d’une autre communauté tient en une
  ligne de montage.
- **Les liens nomment l’app, l’espace et l’élément, jamais l’hôte.** Un hub ouvre
  un lien avec son propre montage de cette app et de cet espace. S’il n’en a pas,
  il indique à qui appartient l’espace et propose le chemin du retour.
- **Les espaces sont fédérés.** Deux hubs peuvent servir le même espace, et les
  relais d’un espace ne transportent que son contenu.

Prévu : des hubs qui s’annoncent avec un manifeste signé pour que d’autres puissent
les trouver, des approbations de modération, et des personnes qui suivent un espace
que leur hub ne livre pas.

## Écrire une app { #writing-an-app }

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Cela génère le squelette d’une app React sur le kit d’interface du framework, avec
une coquille, des pages d’accueil et de réglages, des chaînes dans chaque langue,
une entrée de registre et un montage. Les apps ne parlent au framework que par son
API publique et ne touchent jamais directement au stockage ni aux clés. Voir
[Héberger votre propre hub](hubs.md).
