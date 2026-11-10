# Héberger votre propre hub

Cette page explique comment faire tourner un hub pour votre propre communauté.
Un hub est le site web qu’une communauté obtient avec kiwi-framework : un
marché ouvert, un fil, une messagerie et d’autres applications qui tournent
dans le navigateur. Un hub n’est fait que de fichiers statiques, si bien que
l’héberger revient à servir un dossier de fichiers en HTTPS. Il y a trois
façons de procéder :

- **Utiliser Armory tel quel.** Armory est le premier hub construit avec le
  framework, et il est ouvert à tous à l’adresse
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Créer votre propre distribution.** Une distribution, c’est le framework
  avec votre nom, vos relais et votre choix d’applications. Vous pouvez la
  publier sur n’importe quel hébergement de fichiers statiques.
- **Lancer le conteneur du hub.** Vous pouvez par exemple le faire tourner
  dans votre propre Kiwi Network, avec votre propre relais. Vous obtenez alors
  un hub privé, accessible uniquement depuis le mesh, c’est-à-dire le réseau
  WireGuard privé que partagent toutes vos machines.

## Types de hub { #kinds-of-hub }

| Type | Principe | Exemple |
|---|---|---|
| **Public** | Le hub utilise des relais publics, et tout le monde peut l’ouvrir. | Armory |
| **Privé** | Personne ne peut remplacer les relais du hub (`policy.relays: 'locked'`), et les pages attendent qu’un de ces relais réponde (`requireHub`). Les relais se trouvent derrière un VPN. | le hub d’une entreprise, sur son kiwi-master |
| **Semi-public** | Un hub privé qui a aussi une zone publique. Certaines applications, la messagerie par exemple, y utilisent des relais publics. | |

Les relais d’un hub forment des réseaux séparés : le réseau propre au hub,
celui de la zone publique, et ceux de ses espaces. Chaque événement, c’est-à-dire
chaque message nostr signé, appartient à un seul de ces réseaux et n’est jamais
transmis à un autre.

## Votre propre distribution { #your-own-distribution }

Partez d’Armory, qui sert de modèle. Sur GitHub, le bouton *Use this template*
crée une copie du dépôt sans son historique. Suivez ensuite ces étapes :

1. Modifiez **`distribution.js`**. Ce fichier définit l’identifiant, le nom,
   le logo, la description, la page d’accueil, le dépôt, les relais, les
   serveurs de médias, les espaces, les applications et les montages. Si votre
   hub doit servir aussi les espaces d’Armory, copiez leurs champs `owner` et
   `id` depuis le fichier `hub.json` d’Armory.
2. Modifiez **`locales/*.json`**. Ces fichiers contiennent le titre, le texte
   d’introduction et le pied de page, ainsi qu’un texte de carte pour chaque
   montage. L’anglais est la langue de repli.
3. Mettez à jour **`kiwi.manifest`**. Si vous le souhaitez, ajoutez aussi
   votre hub à [kiwi-web-catalog](#kiwi-web-catalog).
4. Sur GitHub, choisissez *Settings → Pages → Source: GitHub Actions*, puis
   faites un push.

Voici les commandes dont vous vous servez pendant que vous travaillez sur une
distribution :

```bash
npm install
npm run dev                  # le hub avec rechargement à chaud, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # un relais de test local sur ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # créer le squelette d’une nouvelle application
```

Épinglez kiwi-framework à un commit ou à un tag, jamais à une branche. Le
build vérifie votre `distribution.js`. Par exemple, un hub qui a un montage
public doit avoir des relais publics, et un hub qui a des relais publics doit
avoir un montage public.

Tout ce que vous voyez dans le navigateur est écrit en TypeScript avec
React 19 et construit avec Vite. La couche de données, dans `shared/`, est
écrite en JavaScript simple avec des types JSDoc. Les tests tournent dans le
lanceur de tests de node, et ceux qui ont besoin d’un navigateur tournent dans
Playwright.

## Le conteneur du hub { #the-hub-container }

Armory existe aussi sous forme d’image de conteneur,
`ghcr.io/derlocke-ng/armory`. L’image est construite à partir du
`container/Dockerfile` du framework et sert le hub avec nginx. Au démarrage du
conteneur, son script d’entrée écrit le fichier `hub.local.json` à partir des
variables `HUB_*`, et la page lit ce fichier avant de se connecter. Une
installation peut ainsi choisir ses relais et sa politique, mais elle ne peut
pas ajouter de code. Si aucune variable n’est définie, le hub fonctionne tel
qu’il a été construit.

L’exemple suivant lance un hub avec son propre relais verrouillé et un montage
sur un relais public :

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Signification |
|---|---|
| `HUB_RELAYS` | Les relais propres au hub. |
| `HUB_PUBLIC_RELAYS` | Les relais de la zone publique. Si la variable est définie mais vide, il n’y a pas de zone publique. |
| `HUB_DIRECTORY_RELAYS` | Les relais sur lesquels les listes de relais sont publiées et recherchées. |
| `HUB_RELAYS_LOCKED` | Avec `true`, personne ne peut remplacer les relais du hub. |
| `HUB_REQUIRE_HUB` | Avec `true`, les pages attendent tant qu’aucun relais du hub ne répond. |
| `HUB_PUBLIC_MOUNTS` | Les montages qui utilisent la zone publique, désignés par leur identifiant. |
| `HUB_ACCOUNT_MOUNTS` | Les montages qui demandent un compte. |
| `HUB_REQUIRE_ACCOUNT` | Avec `true`, tous les montages demandent un compte. |
| `HUB_SPACE_RELAYS` | Les relais de chaque espace, sous la forme `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | Les clés des personnes qui modèrent tous les espaces définis par le hub. |
| `HUB_REGISTER_POW` | Le nombre de bits de preuve de travail qu’exige la création d’un compte. C’est utile pour les relais réservés aux membres. |
| `HUB_CALDAV` | Un serveur Nextcloud. nginx lui transmet `/remote.php/dav/`, si bien que l’agenda n’a pas besoin de CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | Les serveurs STUN/TURN pour les appels et les transferts directs, qui aident deux navigateurs à se connecter l’un à l’autre. L’identifiant TURN est visible dans la page : créez-en un qui ne sert qu’à ce hub. |

`HUB_USER_MOUNTS` est lue, mais n’a encore aucun effet. Elle appartient à une
fonction qui reste à venir : suivre un espace que le hub n’inclut pas.

Le hub doit être servi en HTTPS, car WebCrypto exige un contexte sécurisé. Ses
relais doivent être servis en `wss://`. Si le hub est ouvert en simple
`http://` ailleurs que sur localhost, la page le signale et s’arrête.

### Faire tourner un hub sur votre Kiwi Network { #on-a-kiwi-network }

Un kiwi-master est le seul serveur d’un Kiwi Network qui soit accessible depuis
Internet. Il peut faire tourner son propre relais et son propre hub, grâce à
deux modules. Le module `nostr-relay` fait tourner le logiciel de relais strfry
à l’adresse `relay.<host>`. Le module `hub` fait tourner cette image de
conteneur, avec Armory par défaut, à l’adresse `hub.<host>`.

Les deux sont privés par défaut : ils ne sont accessibles que depuis le mesh et
utilisent le certificat de votre réseau. Pour un hub semi-public, ajoutez
`public_relays` et `public_mounts`. Pour un hub public, ajoutez
`reverse-proxy.public`, qui obtient des certificats Let’s Encrypt.

Le relais d’un hub public accepte les publications venant du mesh. Depuis
Internet, il n’accepte que celles des membres qui prouvent qu’ils détiennent
leur clé (NIP-42). Les membres sont les personnes inscrites sur la liste que
signent les administrateurs (`write_pubkeys`). Avec `members: registered`, est
membre toute personne qui a un compte sur le hub. Voir la
[référence des modules](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
est un catalogue, c’est-à-dire un dépôt git qui répertorie d’autres dépôts. Il
répertorie des hubs, leurs applications et le framework, et il a le même
format que le catalogue du poste de travail. Le fichier `apps.list` contient
une URL git par ligne. Une ligne peut porter `path=`, pour une application qui
se trouve dans le dépôt d’un hub, et `ref=`, pour épingler une version. Chaque
entrée contient un `kiwi.manifest` dont la `CATEGORY` vaut `Framework`, `Hub`
ou `App`.

Aujourd’hui, il répertorie kiwi-framework, Armory et les dix applications
d’Armory. Il n’est **pas** fait pour `kiwi catalog add` : ses entrées n’ont
pas de script d’installation, et aucun programme ne lit encore le catalogue
automatiquement. D’après son README, les fichiers du catalogue sont dans le
domaine public (CC0).

Pour y ajouter votre hub, faites un fork du catalogue, ajoutez une ligne,
vérifiez que votre dépôt contient un `kiwi.manifest`, et ouvrez une pull
request.

## Pas encore réalisé { #not-built-yet }

Ces éléments figurent sur la feuille de route du framework et n’existent pas
encore :

- Le blog.
- Les approbations de modération (NIP-72, kind 4550).
- Suivre un espace que votre hub n’inclut pas.
- La connexion par une extension de navigateur (NIP-07) ou par un signataire
  distant (NIP-46).
- Un serveur TURN dans la kiwi stack. Le travail sur ce point est en attente
  dans kiwi-modules. Sans TURN, deux téléphones sur réseau mobile n’arrivent
  souvent pas à établir de connexion directe.
