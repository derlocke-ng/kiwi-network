# Armory

**Des outils web pair-à-pair, armés de nostr.** Chaque outil tourne entièrement
dans votre navigateur et se synchronise via les relais que vous choisissez. Pas
d’inscription, pas de serveur chez nous et pas de pistage, et tout est chiffré avant
de quitter votre appareil. Installez-le comme application web depuis la page
d’accueil.

- **L’ouvrir :** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Dépôt : [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- Une distribution de [kiwi-framework](index.md) 0.32.1 (épinglé par commit). Il n’y
  a pas encore de tags de version.
- En anglais, allemand, français, espagnol, italien, néerlandais, polonais et
  portugais.

Armory s’appelait auparavant weaponized.js.

## Les outils { #the-tools }

| Outil | Ce qu’il fait |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Listes de courses et de choses à faire partagées, inventaires de la maison et notes Markdown entre vos appareils et avec les personnes avec qui vous les partagez. Chiffré de bout en bout, avec des liens en modification ou en lecture seule. Fonctionne hors ligne, et vos appareils remettent en place ce que les relais oublient. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Messages et fichiers à vos amis (NIP-17, scellés sur votre appareil), groupes qui restent jusqu’à ce que leur hôte les ferme, et salons en direct ouverts à qui a le lien, qui disparaissent une fois vides. Réponses, réactions, modifications, épinglages, recherche sur l’appareil, messages éphémères, et appels audio et vidéo jusqu’à six personnes. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Un partage de fichiers : un lien qui attend, chiffré, sur vos serveurs de médias jusqu’à ce que vous le supprimiez ; des fichiers à vos amis et groupes dans Uplink ; ou directement de votre navigateur au leur, stockés nulle part. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Un gestionnaire de mots de passe : identifiants, notes, cartes et codes de double authentification sur chaque appareil où vous vous connectez. Un générateur, un bilan de santé (mots de passe faibles, réutilisés, anciens et, si vous l’activez, compromis), imports et exports, clés SSH, une autorité de certification SSH, une autorité de certification X.509 et des certificats TLS. Scellé par sa propre phrase secrète. Pas de remplissage automatique. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Des codes de double authentification (TOTP) pour vos comptes ailleurs : ajoutez-en un par un code QR, un lien ou un secret, ou un export de Google Authenticator. Conservés dans le même coffre scellé. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Vos agendas depuis votre propre Nextcloud ou tout serveur CalDAV : les prochains jours ou un mois, les événements qui se répètent, des rappels tant qu’une page est ouverte. Rien ne va aux relais ; l’identifiant est scellé dans votre compte. Votre serveur doit autoriser l’origine d’Armory (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Carnets et rapports de culture : des entrées avec photos, semaine après semaine, pour tout le monde dans Outpost, vos amis, un cercle ou vous seul. Hashtags, j’aime et commentaires. Scellés sur votre appareil, photos chiffrées. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Un marché du chanvre : graines, boutures et matériel avec photos, trouvés par catégorie et selon l’endroit où ils sont envoyés. « Message seller » ouvre Uplink. Pour les personnes ayant un compte (pas de vérification d’âge). Les vendeurs doivent d’abord se montrer dans Outpost (trois publications, chacune aimée par trois personnes) ou être approuvés par un modérateur. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Un tableau d’affichage pour freelances : dites que vous recrutez ou que vous êtes disponible, signé avec votre clé, appuyé par une preuve de travail, soumis au vote, disparu à l’expiration (de 24 heures à 30 jours). Public par conception. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Un Pong rétro à deux joueurs entre deux navigateurs. Partagez un lien ou un code QR, ou choisissez une partie ouverte, ou entraînez-vous hors ligne contre l’ordinateur. |

Un blog est prévu.

Chaque outil est l’une des apps du framework, montée sous le nom d’Armory : Loadout
est `boards`, Uplink `chat`, Outpost `feed`, Trading Post `market`, DevBoard
`notices`, pongjs `pong`.

## Un compte, tous les outils { #one-account-every-tool }

Connectez-vous ou créez un compte sur la page d’accueil (nom d’utilisateur et mot
de passe, ou une clé nostr) et chaque outil l’utilise. Les listes que vous avez
créées sur un appareil avant de vous connecter sont reprises. Sans compte, chaque
appareil utilise sa propre clé.

La page des réglages couvre tout le hub : votre compte et vos appareils, amis et
cercles, personnes bloquées, relais, espaces et serveurs de médias, notifications,
et sauvegardes chiffrées.

## Relais et serveurs de médias { #relays-and-media-servers }

Les relais par défaut d’Armory sont `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` et `wss://relay.primal.net`. Ses serveurs de médias (Blossom) par
défaut sont `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (photos
uniquement) et `blossom.primal.net`. Vous pouvez choisir les vôtres dans les
réglages.

Les relais transmettent les données, mais ils ne peuvent pas lire ce qui a été
chiffré avant. Le [modèle de confidentialité](index.md#privacy-model) liste ce
qu’ils peuvent voir.

## Modération { #moderation }

Les modérateurs d’Armory modèrent Outpost, Trading Post et DevBoard. Les entrées
d’Outpost peuvent être marquées 18+ ou comme publicité par leur auteur, par deux
signalements ou par un modérateur. Ces entrées ne s’affichent qu’aux personnes
ayant un compte.

## Votre propre Armory { #your-own-armory }

Armory est le modèle pour votre propre hub. Forkez-le (ou utilisez-le comme
modèle), modifiez `distribution.js` et les traductions, et publiez-le. Voir
[Héberger votre propre hub](hubs.md).
