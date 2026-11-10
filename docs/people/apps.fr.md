# Les applications du framework

kiwi-framework est le logiciel qui permet à une communauté de faire tourner son
propre hub. Cette page décrit les dix applications qui l’accompagnent, parmi
lesquelles un marché ouvert, un fil communautaire, une messagerie et le partage
de fichiers.

Le framework donne à ses applications des noms simples, comme `market`. Une
distribution, c’est-à-dire un hub particulier construit avec le framework,
**monte** les applications qu’elle veut. Monter une application, c’est
l’utiliser pour un espace, c’est-à-dire une communauté qui a ses propres
modérateurs et ses propres relais, et lui donner un nom propre au hub. Une même
application peut être montée plusieurs fois. Une banque de graines et une
boutique de pierres précieuses, par exemple, sont le même code `market` sur
deux espaces. Chacune a ses modérateurs et ses relais, et elles
apparaissent comme deux tuiles sur un même hub.

| Application | Ce que c’est | Nom du montage dans Armory |
|---|---|---|
| `market` | **Un marché ouvert** pour la communauté que sert le montage. Une annonce comporte des photos, un prix et, au choix, les lieux d’expédition et de livraison ou une remise en main propre. Les acheteurs trouvent les annonces par catégorie et selon leur propre lieu. La recherche s’appuie sur des étiquettes que les relais peuvent comparer sans pouvoir les lire. Un acheteur écrit au vendeur dans la messagerie, où un message au sujet de l’annonce est déjà rédigé. Une annonce peut être réservée, marquée comme vendue, renouvelée et signalée, et elle expire au bout de 30 à 90 jours. Un montage peut exiger que les vendeurs aient d’abord été actifs dans un fil ou qu’un modérateur les ait approuvés. | Trading Post |
| `feed` | **Un fil communautaire.** Chacun publie des entrées avec des photos et des hashtags, que les autres peuvent aimer et commenter. Une entrée peut s’adresser à tout l’espace, à vos amis, à un cercle (un groupe de vos amis) ou à vous uniquement. Un journal est une série d’entrées avec une couverture. Les entrées peuvent être marquées 18+ ou comme publicité. | Outpost |
| `chat` | **La messagerie.** Vous envoyez des messages privés et des fichiers à vos amis (NIP-17). Les groupes existent jusqu’à ce que leur hôte les ferme, et les salons en direct disparaissent quand la dernière personne est partie. La messagerie permet de répondre, de réagir, de modifier et d’épingler des messages, de chercher sur l’appareil et d’envoyer des messages éphémères. Les appels audio et vidéo réunissent jusqu’à six personnes. | Uplink |
| `notices` | **Un tableau d’affichage** pour des notes publiques. Chaque note est signée par son auteur et exige une preuve de travail, un petit calcul qui rend coûteuse la publication en masse. On peut voter pour les notes et les signaler, et elles expirent. | DevBoard |
| `boards` | **Des listes et des notes partagées** : des listes de tâches, des inventaires avec des quantités et des notes en markdown. Elles sont chiffrées de bout en bout, et vous les partagez par des liens qui permettent soit de modifier, soit seulement de consulter. | Loadout |
| `payload` | **Le partage de fichiers**, de trois façons : par un lien vers des fichiers stockés chiffrés sur vos serveurs de médias, par l’envoi de fichiers à vos amis et à vos groupes, ou directement d’un navigateur à l’autre. | Payload |
| `vault` | **Un gestionnaire de mots de passe** pour les identifiants, les notes, les cartes et les codes de double authentification. Il comprend un générateur de mots de passe et un bilan de santé. Il gère aussi des clés SSH, une CA SSH, une CA X.509 et des certificats TLS. Il est chiffré avec une phrase secrète qui lui est propre. | Vault |
| `authenticator` | **Des codes de double authentification** (TOTP). Ils sont conservés dans le même coffre chiffré que les entrées du gestionnaire de mots de passe. | Authenticator |
| `calendar` | **Vos agendas** venant de Nextcloud ou de tout autre serveur CalDAV. Rien n’est envoyé aux relais. | Calendar |
| `pong` | **Un Pong à deux joueurs**, entre deux navigateurs. | pongjs |

Chaque hub a aussi une page d’accueil, une page de compte et une page de
réglages. Les réglages couvrent votre compte et vos appareils, vos amis et vos
cercles, les personnes bloquées, les relais, les espaces, les serveurs de
médias et les sauvegardes. Les notifications ne sont pas une application à
part : elles font partie du hub lui-même.

## Espaces et montages { #spaces-and-mounts }

- Un **espace** est une communauté qui a un nom et un propriétaire. Il
  comporte un identifiant, la clé du propriétaire, un nom, des modérateurs,
  ses propres relais et une option qui le réserve aux adultes. Il reprend le
  modèle des communautés modérées de nostr (NIP-72), si bien que d’autres
  clients nostr peuvent le lire. Chaque publication et chaque annonce
  appartient à un seul espace.
- Un **montage** est une application utilisée pour un espace, avec son propre
  identifiant, son nom et son icône. Pour ajouter à votre hub la boutique
  d’une autre communauté, il suffit d’une ligne qui définit le montage.
- **Un lien désigne l’application, l’espace et l’élément, mais jamais
  l’hôte.** Un hub ouvre ce lien avec son propre montage de cette application
  et de cet espace. S’il n’a pas de montage correspondant, il vous indique à
  qui appartient l’espace et vous propose de revenir en arrière.
- **Les espaces sont fédérés** : un espace n’est lié à aucun hub en
  particulier. Deux hubs peuvent servir le même espace. Les relais d’un espace
  ne transportent que le contenu de cet espace.

Trois choses sont prévues, mais pas encore réalisées. Les hubs s’annonceront
par un manifeste signé, pour que d’autres puissent les trouver. Des
approbations viendront s’ajouter aux outils de modération. Enfin, chacun
pourra suivre un espace que son hub n’inclut pas.

## Écrire une application { #writing-an-app }

Cette commande crée le squelette d’une nouvelle application dans votre
distribution :

```bash
npm run new-app -- <id> "<Name>" <icon>
```

Vous obtenez une application React qui utilise le kit d’interface du
framework. Elle comprend un cadre (qui entoure les pages de l’application), une
page d’accueil et une page de réglages, ses textes dans toutes les langues, une
entrée dans le registre des applications et un montage. Les applications
n’utilisent que l’API publique du framework et n’accèdent jamais directement
au stockage ni aux clés. La page [Héberger votre propre hub](hubs.md)
explique comment construire et publier un hub.
