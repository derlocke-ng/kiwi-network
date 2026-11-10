# Je eigen hub draaien

Een hub bestaat uit statische bestanden, dus er een hosten is een map serveren via
HTTPS. Er zijn drie manieren om er een te draaien:

- **Gebruik Armory zoals het is:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Maak je eigen distributie:** jouw naam, relays en apps, op elke statische host.
- **Draai de hub-container:** bijvoorbeeld binnen je eigen Kiwi Network, met je
  eigen relay, als privéhub die alleen de mesh kan bereiken.

## Soorten hubs { #kinds-of-hub }

| Soort | Hoe | Voorbeeld |
|---|---|---|
| **Publiek** | Publieke relays; iedereen kan hem openen | Armory |
| **Privé** | De relays van de hub zijn vergrendeld (`policy.relays: 'locked'`) en pagina's wachten tot een ervan antwoordt (`requireHub`), met relays binnen een VPN | een bedrijfshub op zijn kiwi-master |
| **Semipubliek** | Een privéhub met een publiek gedeelte voor gekozen apps (bijvoorbeeld de chat) op publieke relays | |

Elk event hoort bij één netwerk (dat van de hub zelf, het publieke gedeelte, of
dat van een space) en gaat nooit over naar een ander.

## Je eigen distributie { #your-own-distribution }

Armory is het sjabloon (op GitHub geeft *Use this template* je een kopie zonder
de geschiedenis):

1. Bewerk **`distribution.js`**: id, naam, merkteken, beschrijving, homepage,
   repository, relays, mediaservers, spaces, apps en mounts. Wil je ook de spaces
   van Armory bedienen, kopieer dan hun `owner` en `id` uit de `hub.json` van
   Armory.
2. Bewerk **`locales/*.json`**: de titel, intro en voettekst, en één kaarttekst
   per mount. Engels is de terugvaltaal.
3. Werk **`kiwi.manifest`** bij en voeg, optioneel, je hub toe aan
   [kiwi-web-catalog](#kiwi-web-catalog).
4. Op GitHub: *Settings → Pages → Source: GitHub Actions*, en push daarna.

```bash
npm install
npm run dev                  # de hub met hot reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # een lokale testrelay op ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # een nieuwe app opzetten
```

Pin kiwi-framework vast op een commit of tag, nooit op een branch. De build
controleert je `distribution.js` (een publieke mount heeft bijvoorbeeld publieke
relays nodig, en andersom).

De stack is TypeScript, React 19 en Vite voor alles wat zichtbaar is. De
gegevenslaag in `shared/` is gewoon JavaScript met JSDoc-types. Tests draaien in
de testrunner van node en, voor de browser, in Playwright.

## De hub-container { #the-hub-container }

Armory is ook een container-image, `ghcr.io/derlocke-ng/armory`, gebouwd uit
`container/Dockerfile` (nginx) van het framework. Bij de start schrijft het
entrypoint `hub.local.json` uit `HUB_*`-variabelen, en de pagina leest dat in
voordat ze verbinding maakt. Een deployment kan zo relays en beleid kiezen, maar
geen code toevoegen. Zonder ingestelde variabelen draait de hub zoals hij gebouwd
is.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variabele | Betekenis |
|---|---|
| `HUB_RELAYS` | de eigen relays van de hub |
| `HUB_PUBLIC_RELAYS` | de relays van het publieke gedeelte (ingesteld en leeg: geen publiek gedeelte) |
| `HUB_DIRECTORY_RELAYS` | waar relaylijsten worden gepubliceerd en opgezocht |
| `HUB_RELAYS_LOCKED` | `true`: mensen kunnen de relays van de hub niet vervangen |
| `HUB_REQUIRE_HUB` | `true`: pagina's wachten zolang geen van de relays van de hub antwoordt |
| `HUB_PUBLIC_MOUNTS` | mounts op het publieke gedeelte, op id |
| `HUB_ACCOUNT_MOUNTS` | mounts die om een account vragen |
| `HUB_REQUIRE_ACCOUNT` | `true`: elke mount vraagt om een account |
| `HUB_SPACE_RELAYS` | relays per space: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | sleutels die elke space modereren die de hub definieert |
| `HUB_REGISTER_POW` | proof-of-work-bits voor een nieuw account (relays alleen voor leden) |
| `HUB_CALDAV` | een Nextcloud; nginx stuurt `/remote.php/dav/` ernaar door, zodat de agenda geen CORS nodig heeft |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | STUN/TURN-servers voor gesprekken en directe overdrachten. De TURN-login is zichtbaar in de pagina, dus geef hem een login die alleen voor deze hub is |

`HUB_USER_MOUNTS` wordt gelezen maar doet nog niets: een space volgen die de hub
niet meelevert, moet nog komen.

De hub moet via HTTPS geserveerd worden (WebCrypto heeft een beveiligde context
nodig) en zijn relays via `wss://`. Via gewone `http://` (anders dan localhost)
meldt de pagina dat en stopt ze.

### Op een Kiwi Network { #on-a-kiwi-network }

Een kiwi-master kan een eigen relay en hub dragen: de module `nostr-relay`
(strfry op `relay.<host>`) en de module `hub` (deze image, standaard Armory, op
`hub.<host>`). Ze zijn standaard privé: alleen bereikbaar vanuit de mesh, met het
certificaat van de fleet. Een semipublieke hub voegt `public_relays` en
`public_mounts` toe. Een publieke voegt `reverse-proxy.public` toe, die
Let's Encrypt-certificaten krijgt. De relay accepteert dan berichten vanuit de
mesh, en vanaf het internet alleen van leden die hun sleutel bewijzen (NIP-42):
wie op de lijst staat die de beheerders (`write_pubkeys`) ondertekenen, of, met
`members: registered`, iedereen met een account op de hub. Zie de
[modulereferentie](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
somt hubs, hun apps en het framework op, in dezelfde vorm als de
desktopcatalogus: een `apps.list` met één git-URL per regel (`path=` voor een app
binnen de repository van een hub, `ref=` om vast te pinnen), en een
`kiwi.manifest` in elke vermelding met als `CATEGORY` `Framework`, `Hub` of `App`.

Vandaag bevat hij kiwi-framework, Armory en de tien apps van Armory. Hij is
**niet** bedoeld voor `kiwi catalog add`: deze vermeldingen hebben geen
installer, en nog niets leest de catalogus automatisch. De catalogusbestanden
zijn publiek domein (CC0, volgens de README).

Je hub toevoegen: fork, voeg een regel toe, zorg dat de repository een
`kiwi.manifest` bevat, en open een pull request.

## Nog niet gebouwd { #not-built-yet }

Deze komen uit de eigen roadmap van het framework:

- De blog.
- Goedkeuringen door moderators (NIP-72 kind 4550).
- Spaces volgen die een hub niet meelevert.
- Signers voor NIP-07 en NIP-46.
- Een TURN-server in de kiwi-stack. Hij wacht in kiwi-modules; zonder TURN vinden
  twee telefoons op mobiele data vaak geen direct pad.
