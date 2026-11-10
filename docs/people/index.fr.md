# Des hubs, pas des plateformes

**kiwi-framework** est un logiciel qui permet à n'importe quelle communauté de
faire tourner son propre **hub**. Un hub est un site web qui réunit des
applications pour les membres de la communauté : un marché ouvert, un fil, une
messagerie, le partage de fichiers, des listes partagées, un gestionnaire de
mots de passe et un agenda. N'importe qui peut faire tourner un hub, pour
n'importe quelle communauté, et celle-ci ne dépend alors d'aucune plateforme
centrale qui détiendrait les comptes et les données de tout le monde.

Les applications tournent entièrement dans le navigateur. Elles se
synchronisent par des relais [nostr](https://nostr.com), c'est-à-dire des
serveurs qui stockent des messages signés et les retransmettent, et c'est la
communauté qui choisit les relais de son hub. Il n'y a ni serveur de comptes ni
backend entre le navigateur et les relais, et tout ce qui est privé est chiffré
sur l'appareil avant d'être envoyé. Les autres parties de Kiwi Network relient
vos machines. Les hubs, eux, relient des personnes. La page
[Les applications du framework](apps.md) décrit chaque application.

Armory est le premier hub construit avec le framework. C'est un exemple parmi
d'autres, et c'est aussi le modèle que les autres communautés copient pour
créer leur propre hub.

Le logiciel est réparti dans trois dépôts :

| Dépôt | Ce que c'est |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | Le logiciel général à partir duquel chaque hub est construit. Il contient l'identité et les comptes, les relais et la synchronisation, les amis et le partage, la modération, le kit graphique, les pages du hub et dix applications. Le framework ne s'ouvre pas tel quel comme un site web : c'est une distribution qui en fait un hub. La version actuelle est la v0.32.1, sous licence GPL-3.0-or-later. |
| [**Armory**](armory.md) | La première **distribution**, c'est-à-dire un hub construit avec le framework. Elle y ajoute un nom, des relais par défaut et les dix applications, chacune sous un nom propre à Armory. C'est le modèle à reprendre pour créer votre propre hub. Elle est sous licence GPL-3.0-or-later. **En ligne :** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Un catalogue, c'est-à-dire un dépôt git qui répertorie des hubs et leurs applications. Il a le même format que le [kiwi-catalog](../desktop/catalogs.md) du poste de travail. |

## Comment tout s'assemble { #how-it-fits-together }

Le schéma montre comment le framework devient un hub dans votre navigateur, et
avec quels serveurs le navigateur communique ensuite.

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

## Les termes employés ici { #the-words }

- **Hub** : le site web qu'utilise une communauté. C'est ce que vous obtenez
  quand vous construisez une distribution. Un hub n'est fait que de fichiers
  statiques, si bien que l'héberger revient à servir un dossier de fichiers.
  Chaque hub a une page d'accueil, une page de réglages et une page de compte.
- **Distribution** : le framework, plus les choix qui en font un hub
  particulier. Ces choix sont un nom et une apparence, des relais par défaut,
  et une sélection d'applications montées sur les espaces voulus. Quand vous
  faites un fork d'une distribution, tout ce que vous modifiez se trouve dans
  un seul fichier, `distribution.js`, et dans ses traductions.
- **Application** : un dossier accompagné d'un fichier manifeste. Elle peut
  être ajoutée à n'importe quelle distribution. Les applications n'utilisent
  que l'API publique du framework et n'accèdent jamais directement au stockage
  ni aux clés.
- **Espace** : une communauté qui a un nom, un propriétaire, ses propres
  modérateurs et, si elle le souhaite, ses propres relais. Les espaces
  reprennent le modèle des communautés modérées de nostr (NIP-72). Un autre hub
  peut servir le même espace : il lui suffit d'en indiquer l'adresse.
- **Montage** : une application utilisée pour un espace. Chaque montage a son
  propre nom, sa propre route (son adresse à l'intérieur du hub) et sa propre
  icône. Une même application peut être montée plusieurs fois. Par exemple, le
  *Trading Post* d'Armory est l'application `market` du framework, montée sur
  l'espace `tradingpost` d'Armory.

Deux personnes qui utilisent des hubs issus de distributions différentes
peuvent être amies, partager des contenus et discuter exactement comme si elles
utilisaient le même hub. C'est possible parce que l'identité et les données
d'une personne sont des événements nostr, c'est-à-dire des messages signés
stockés sur des relais, et qu'elles n'appartiennent à aucun hub.

## Comptes et clés { #accounts-and-keys }

- La première fois que vous ouvrez un hub sur un appareil, le navigateur crée
  une clé pour cet appareil et la conserve.
- Un **compte**, c'est un nom d'utilisateur et un mot de passe. Il repose sur
  des événements nostr ordinaires, et il n'existe aucun registre des comptes.
  Votre mot de passe est transformé par scrypt, une fonction volontairement
  lente à calculer, et c'est le résultat qui déverrouille votre clé. Sans le
  mot de passe, personne ne peut s'emparer d'un compte ni l'écraser. Il n'y a
  **aucun moyen de réinitialiser le mot de passe**.
- Vous pouvez aussi vous connecter avec une clé nostr que vous avez déjà, au
  format `nsec`, hexadécimal ou `ncryptsec`. La connexion par une extension de
  navigateur (NIP-07) ou par un signataire distant (NIP-46) est prévue, mais
  pas encore réalisée.
- Un seul compte sert pour toutes les applications du hub et sur chaque
  appareil où vous vous connectez.

## Modèle de confidentialité { #privacy-model }

**Ce qui est chiffré.** Le navigateur chiffre le contenu avant de l'envoyer où
que ce soit. Il utilise AES-256-GCM, avec des clés dérivées par HKDF. Les
messages privés sont des messages NIP-17 placés dans des « gift wraps » NIP-59.
Un gift wrap est une seconde couche de chiffrement, grâce à laquelle un relais
voit seulement qu'une clé a reçu un message emballé. Chaque fichier est chiffré
avec sa propre clé AES-256-GCM, tirée au hasard, avant d'être envoyé sur un
serveur de médias. Les photos sont d'abord réencodées, ce qui supprime les
métadonnées ajoutées par les appareils photo. Le Vault est chiffré avec une
phrase secrète qui lui est propre (scrypt + AES-256-GCM). Les appels passent
directement d'un navigateur à l'autre et sont chiffrés par WebRTC.

**Local d'abord.** Tout ce que vous écrivez est d'abord enregistré dans la base
de données du navigateur, puis envoyé aux relais. Les applications lisent cette
base, sur l'appareil, et fonctionnent donc aussi hors ligne. Quand un appareil
se reconnecte, il renvoie au relais les données que celui-ci n'a plus. Des
données ne sont donc perdues que si tous les appareils qui les détenaient ont
disparu *et* qu'il n'existe aucune sauvegarde.

**Ce que les autres peuvent voir.** Les dépôts indiquent eux-mêmes les
limites :

- Les relais voient les métadonnées : qui écrit à quelles adresses, quand, en
  quelle quantité et depuis quelle adresse IP. Si cela compte pour vous,
  utilisez un VPN ou Tor.
- La clé d'un espace n'est pas un secret. Elle évite seulement que les
  publications d'une communauté soient lisibles par tout le monde. Les relais
  voient les j'aime, les signalements et qui a commenté quoi.
- Les notes de DevBoard et les signalements de modération sont publics, et
  c'est voulu.
- Votre clé est conservée dans le stockage du navigateur. Or tous les sites
  GitHub Pages d'un même compte partagent une seule origine, et c'est par
  origine que les navigateurs séparent le stockage des sites web. Un hub sur
  son propre domaine ou sous-domaine est donc mieux protégé.
- Lors d'un transfert direct de fichiers ou d'un appel, chacun des deux
  navigateurs apprend l'adresse IP de l'autre, et les serveurs STUN qui les
  aident à se connecter voient eux aussi les deux adresses. Par défaut, ce sont
  les serveurs STUN de Google et de Cloudflare. Un hub peut définir les siens.
- « Pas de serveur chez nous » veut dire que les applications ne dépendent
  d'aucun serveur exploité par le projet. Elles utilisent tout de même des
  relais, des serveurs de médias et, pour l'agenda, un serveur CalDAV. C'est
  vous, ou votre hub, qui choisissez lesquels.

## Modération { #moderation }

La modération se fait à trois niveaux. Le premier est votre propre liste de
blocage, chiffrée de sorte que vous seul puissiez la lire. Le deuxième, ce sont
les signalements, qui sont publics et signés. Le troisième est la politique de
chaque relais.

Chaque espace a ses modérateurs. Quand un modérateur signale une publication,
elle est aussitôt repliée. Sinon, une publication est repliée au bout de trois
signalements venant de personnes qui ne sont pas bloquées. Une publication peut
être marquée 18+ ou comme publicité, et les publications marquées ne sont
montrées qu'aux personnes qui ont un compte.

## Pour aller plus loin { #read-on }

- [Armory et ses applications](armory.md)
- [Faire tourner son propre hub](hubs.md)
- L'[architecture](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  et le [protocole réseau](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  du framework, décrits dans son dépôt
