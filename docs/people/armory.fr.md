# Armory

Armory est le premier hub construit avec kiwi-framework, le logiciel qui permet
à n’importe quelle communauté de faire tourner son propre hub. Dans le
vocabulaire du framework, Armory est une **distribution** : le framework,
plus un nom, des relais par défaut et une sélection d’applications. Armory
reprend les dix applications du framework et leur donne ses propres noms. Son
marché et son fil sont pensés pour les cultivateurs de chanvre. Ce thème est le
choix de ce hub-là, pas celui du framework : une autre communauté utiliserait
les mêmes applications pour son propre sujet. Vous pouvez utiliser Armory tel
quel, ou le copier pour en faire le modèle de votre propre hub.

Chaque outil tourne entièrement dans votre navigateur. Les outils se
synchronisent par des relais, c’est-à-dire des serveurs qui stockent vos
données et les retransmettent, et c’est vous qui choisissez les relais. Vous
n’avez pas besoin de vous inscrire, le projet n’exploite lui-même aucun
serveur pour Armory, et rien ne vous piste. Tout est chiffré avant de quitter votre
appareil. Depuis la page d’accueil, vous pouvez installer Armory comme une
application web.

- **L’ouvrir :** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Le dépôt est [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  sous licence GPL-3.0-or-later.
- Armory est une distribution de [kiwi-framework](index.md) 0.32.1, qu’il
  épingle par commit. Armory n’a pas encore de tags de version.
- Il est disponible en anglais, en allemand, en français, en espagnol, en
  italien, en néerlandais, en polonais et en portugais.

Armory s’appelait autrefois weaponized.js.

## Les outils { #the-tools }

| Outil | Ce qu’il fait |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Des listes de courses et de choses à faire, des inventaires de la maison et des notes en markdown, partagés. Ils restent identiques sur tous vos appareils et chez les personnes avec qui vous les partagez. Tout est chiffré de bout en bout, et vous partagez une liste par un lien qui permet soit de la modifier, soit seulement de la consulter. Loadout fonctionne hors ligne, et vos appareils renvoient aux relais ce que ceux-ci ont perdu. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Des messages et des fichiers pour vos amis (NIP-17, chiffrés sur votre appareil). Les groupes existent jusqu’à ce que leur hôte les ferme. N’importe qui ayant le lien peut rejoindre un salon en direct, et le salon disparaît quand la dernière personne est partie. Uplink permet de répondre, de réagir, de modifier et d’épingler des messages, de chercher sur votre appareil et d’envoyer des messages éphémères. Les appels audio et vidéo réunissent jusqu’à six personnes. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Le partage de fichiers, de trois façons. Vous pouvez créer un lien vers des fichiers qui restent chiffrés sur vos serveurs de médias jusqu’à ce que vous les supprimiez. Vous pouvez envoyer des fichiers à vos amis et à vos groupes dans Uplink. Vous pouvez enfin envoyer des fichiers directement de votre navigateur à celui d’une autre personne : ils ne sont alors stockés nulle part. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Un gestionnaire de mots de passe pour les identifiants, les notes, les cartes et les codes de double authentification, disponible sur chaque appareil où vous vous connectez. Il comprend un générateur de mots de passe et un bilan de santé. Ce bilan repère les mots de passe faibles, réutilisés ou anciens et, si vous activez cette vérification, ceux qui ont fuité. Vault importe et exporte des entrées. Il gère aussi des clés SSH, une autorité de certification SSH, une CA X.509 et des certificats TLS. Il est chiffré avec une phrase secrète qui lui est propre. Il ne remplit pas les mots de passe à votre place sur les sites web. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Des codes de double authentification (TOTP) pour vos comptes sur d’autres services. Vous ajoutez un compte à partir d’un code QR, d’un lien ou d’un secret, ou d’un export de Google Authenticator. Les codes sont conservés dans le même coffre chiffré que celui de Vault. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Vos agendas, depuis votre propre Nextcloud ou tout autre serveur CalDAV. Il affiche les prochains jours ou un mois, gère les événements récurrents et vous rappelle les événements tant qu’une page est ouverte. Rien n’est envoyé aux relais, et l’identifiant de votre serveur est stocké chiffré dans votre compte. Votre serveur doit accepter les requêtes venant de l’origine d’Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Le fil d’Armory, consacré aux comptes rendus et aux journaux de culture. Vous publiez des entrées avec des photos, semaine après semaine. Chaque entrée peut s’adresser à tout le monde dans Outpost, à vos amis, à un cercle d’amis ou à vous uniquement. Les entrées peuvent avoir des hashtags, des j’aime et des commentaires. Elles sont chiffrées sur votre appareil, tout comme les photos. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Le marché d’Armory, consacré au chanvre : graines, boutures et matériel. Les annonces ont des photos, et les acheteurs les trouvent par catégorie et selon les lieux de livraison. Le bouton « Écrire au vendeur » ouvre Uplink. Il faut un compte pour utiliser Trading Post, et il n’y a aucune vérification de l’âge. Avant de pouvoir vendre, il faut avoir publié dans Outpost (trois publications, chacune aimée par trois personnes) ou avoir été approuvé par un modérateur. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Un tableau d’affichage pour les freelances. Vous publiez une note pour dire que vous recrutez ou que vous êtes disponible. Chaque note est signée avec votre clé et exige une preuve de travail, un petit calcul qui rend coûteuse la publication en masse. Les autres peuvent voter pour une note. Une note disparaît quand elle expire, c’est-à-dire entre 24 heures et 30 jours après sa publication. Toutes les notes sont publiques, et c’est voulu. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Un Pong rétro à deux joueurs, dans deux navigateurs. Pour lancer une partie, partagez un lien ou un code QR, ou choisissez une des parties ouvertes. Vous pouvez aussi vous entraîner contre l’ordinateur, hors ligne. |

Un blog est prévu.

Chaque outil est une application du framework, sous un nom qu’Armory lui a
donné. Loadout est l’application `boards` du framework, Uplink est `chat`,
Outpost est `feed`, Trading Post est `market`, DevBoard est `notices` et
pongjs est `pong`.

## Un compte pour tous les outils { #one-account-every-tool }

Vous vous connectez ou créez un compte sur la page d’accueil, soit avec un nom
d’utilisateur et un mot de passe, soit avec une clé nostr. Tous les outils
utilisent ensuite ce compte. Les listes que vous avez créées sur un appareil
avant de vous connecter sont reprises dans le compte. Si vous n’utilisez pas de
compte, chaque appareil fonctionne avec sa propre clé.

La page de réglages vaut pour tout le hub. Elle couvre votre compte et vos
appareils, vos amis et vos cercles, les personnes bloquées, les relais, les
espaces et les serveurs de médias, les notifications et les sauvegardes
chiffrées.

## Relais et serveurs de médias { #relays-and-media-servers }

Les relais par défaut d’Armory sont `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` et `wss://relay.primal.net`. Les serveurs de médias stockent
les fichiers que vous envoyez et utilisent un protocole appelé Blossom. Les
serveurs de médias par défaut d’Armory sont `nostr.download`,
`blossom.yakihonne.com`, `blossom.band` (qui n’accepte que les photos) et
`blossom.primal.net`. Vous pouvez choisir vos propres relais et serveurs de
médias dans les réglages.

Les relais stockent les données et les retransmettent, mais ne peuvent rien
lire de ce qui a été chiffré avant l’envoi. Le
[modèle de confidentialité](index.md#privacy-model) indique ce que les relais
peuvent voir.

## Modération { #moderation }

Les modérateurs d’Armory s’occupent d’Outpost, de Trading Post et de DevBoard.
Une entrée d’Outpost peut être marquée 18+ ou comme publicité. Cette marque
peut être posée par l’auteur, par un modérateur, ou à la suite de deux
signalements. Les entrées marquées ne sont montrées qu’aux personnes qui ont un
compte.

## Votre propre Armory { #your-own-armory }

Armory sert aussi de modèle pour votre propre hub. Faites un fork du dépôt ou
utilisez-le comme modèle, modifiez `distribution.js` et les traductions, puis
publiez le résultat. La page [Héberger votre propre hub](hubs.md) décrit les
étapes.
