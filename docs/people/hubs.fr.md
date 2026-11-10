# Héberger votre propre hub

Un hub, ce sont des fichiers statiques, si bien qu’en héberger un revient à servir
un dossier en HTTPS. Il y a trois façons d’en faire tourner un :

- **Utiliser Armory tel quel :** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Créer votre propre distribution :** votre nom, vos relais et vos apps, sur
  n’importe quel hébergeur statique.
- **Faire tourner le conteneur du hub :** par exemple dans votre propre Kiwi
  Network, avec votre propre relais, comme hub privé que seul le maillage peut
  atteindre.

## Types de hub { #kinds-of-hub }

| Type | Comment | Exemple |
|---|---|---|
| **Public** | Relais publics ; n’importe qui peut l’ouvrir | Armory |
| **Privé** | Les relais du hub sont verrouillés (`policy.relays: 'locked'`) et les pages attendent que l’un d’eux réponde (`requireHub`), avec des relais à l’intérieur d’un VPN | le hub d’une entreprise sur son kiwi-master |
| **Semi-public** | Un hub privé avec une zone publique pour des apps choisies (la messagerie, par exemple) sur des relais publics | |

Chaque événement appartient à un seul réseau (celui du hub, la zone publique, ou
celui d’un espace) et ne passe jamais dans un autre.

## Votre propre distribution { #your-own-distribution }

Armory est le modèle (sur GitHub, *Use this template* vous en donne une copie sans
son historique) :

1. Modifiez **`distribution.js`** : id, nom, marque, description, page d’accueil,
   dépôt, relais, serveurs de médias, espaces, apps et montages. Pour servir aussi
   les espaces d’Armory, copiez leurs `owner` et `id` depuis le `hub.json`
   d’Armory.
2. Modifiez **`locales/*.json`** : le titre, le chapeau et le pied de page, et un
   texte de carte par montage. L’anglais sert de langue de repli.
3. Mettez à jour **`kiwi.manifest`** et, en option, ajoutez votre hub à
   [kiwi-web-catalog](#kiwi-web-catalog).
4. Sur GitHub : *Settings → Pages → Source: GitHub Actions*, puis faites un push.

```bash
npm install
npm run dev                  # le hub avec rechargement à chaud, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # un relais de test local sur ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # générer le squelette d’une nouvelle app
```

Épinglez kiwi-framework par commit ou par tag, jamais par branche. La compilation
vérifie votre `distribution.js` (par exemple, un montage public a besoin de relais
publics, et inversement).

La pile technique est TypeScript, React 19 et Vite pour tout ce qui est visible. La
couche de données dans `shared/` est en JavaScript simple avec des types JSDoc. Les
tests tournent dans le test runner de node et, pour le navigateur, dans Playwright.

## Le conteneur du hub { #the-hub-container }

Armory est aussi une image de conteneur, `ghcr.io/derlocke-ng/armory`, construite à
partir du `container/Dockerfile` du framework (nginx). Au démarrage, son point
d’entrée écrit `hub.local.json` à partir des variables `HUB_*`, et la page le lit
avant de se connecter. Un déploiement peut ainsi choisir les relais et la
politique, mais il ne peut pas ajouter de code. Sans aucune variable réglée, le hub
tourne tel qu’il a été construit.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Signification |
|---|---|
| `HUB_RELAYS` | les relais propres au hub |
| `HUB_PUBLIC_RELAYS` | les relais de la zone publique (réglée et vide : pas de zone publique) |
| `HUB_DIRECTORY_RELAYS` | où les listes de relais sont publiées et consultées |
| `HUB_RELAYS_LOCKED` | `true` : les gens ne peuvent pas remplacer les relais du hub |
| `HUB_REQUIRE_HUB` | `true` : les pages attendent tant qu’aucun des relais du hub ne répond |
| `HUB_PUBLIC_MOUNTS` | montages sur la zone publique, par id |
| `HUB_ACCOUNT_MOUNTS` | montages qui demandent un compte |
| `HUB_REQUIRE_ACCOUNT` | `true` : chaque montage demande un compte |
| `HUB_SPACE_RELAYS` | relais par espace : `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | clés qui modèrent chaque espace que le hub définit |
| `HUB_REGISTER_POW` | bits de preuve de travail pour un nouveau compte (relais réservés aux membres) |
| `HUB_CALDAV` | un Nextcloud ; nginx transmet `/remote.php/dav/` vers lui, si bien que l’agenda n’a pas besoin de CORS |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | serveurs STUN/TURN pour les appels et les transferts directs. L’identifiant TURN est visible dans la page : donnez-lui donc un identifiant réservé à ce hub |

`HUB_USER_MOUNTS` est lu mais ne fait encore rien : suivre un espace que le hub ne
livre pas reste à venir.

Le hub doit être servi en HTTPS (WebCrypto a besoin d’un contexte sécurisé) et ses
relais en `wss://`. En simple `http://` (hors localhost), la page le signale et
s’arrête.

### Sur un Kiwi Network { #on-a-kiwi-network }

Un kiwi-master peut porter son propre relais et son propre hub : le module
`nostr-relay` (strfry sur `relay.<host>`) et le module `hub` (cette image, Armory
par défaut, sur `hub.<host>`). Ils sont privés par défaut : joignables uniquement
depuis le maillage, avec le certificat de la fleet. Un hub semi-public ajoute
`public_relays` et `public_mounts`. Un hub public ajoute `reverse-proxy.public`,
qui obtient des certificats Let’s Encrypt. Le relais accepte alors les
publications depuis le maillage et, depuis Internet, uniquement de la part de
membres qui prouvent leur clé (NIP-42) : ceux de la liste que signent les
administrateurs (`write_pubkeys`) ou, avec `members: registered`, toute personne
ayant un compte sur le hub. Voir la [référence des modules](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
liste les hubs, leurs apps et le framework, sous la même forme que le catalogue du
bureau : un `apps.list` avec une URL git par ligne (`path=` pour une app dans le
dépôt d’un hub, `ref=` pour épingler), et un `kiwi.manifest` dans chaque entrée
avec une `CATEGORY` valant `Framework`, `Hub` ou `App`.

Aujourd’hui, il liste kiwi-framework, Armory et les dix apps d’Armory. Il n’est
**pas** destiné à `kiwi catalog add` : ces entrées n’ont pas d’installateur, et rien
ne lit encore le catalogue automatiquement. Les fichiers du catalogue sont dans le
domaine public (CC0, selon son README).

Pour ajouter votre hub : forkez, ajoutez une ligne, vérifiez que le dépôt contient
un `kiwi.manifest`, et ouvrez une pull request.

## Pas encore construit { #not-built-yet }

Ces éléments viennent de la feuille de route du framework lui-même :

- Le blog.
- Les approbations de modération (NIP-72 kind 4550).
- Le suivi d’espaces qu’un hub ne livre pas.
- Les signataires NIP-07 et NIP-46.
- Un serveur TURN dans la stack kiwi. Il attend dans kiwi-modules ; sans TURN,
  deux téléphones sur données mobiles ne trouvent souvent aucun chemin direct.
