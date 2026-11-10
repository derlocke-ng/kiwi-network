# Je eigen hub draaien

Op deze pagina lees je hoe je een hub voor je eigen community draait. Een hub is
de website die een community met kiwi-framework krijgt: een open markt, een
feed, chat en andere apps die in de browser draaien. Een hub bestaat alleen uit
statische bestanden, dus een hub hosten betekent een map met bestanden via
HTTPS aanbieden. Er zijn drie manieren:

- **Armory gebruiken zoals het is.** Armory is de eerste hub die met het
  framework is gebouwd, en staat voor iedereen open op
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Een eigen distributie maken.** Een distributie is het framework met je
  eigen naam, relays en keuze van apps. Je kunt haar op elke statische host
  publiceren.
- **De hub-container draaien.** Bijvoorbeeld binnen je eigen Kiwi Network, samen
  met een eigen relay. Dan heb je een besloten hub die alleen bereikbaar is
  vanuit de mesh, het besloten netwerk waarin al je machines zitten.

## Soorten hubs { #kinds-of-hub }

| Soort | Hoe | Voorbeeld |
|---|---|---|
| **Openbaar** | De hub gebruikt openbare relays, en iedereen kan hem openen. | Armory |
| **Besloten** | Gebruikers kunnen de relays van de hub niet vervangen (`policy.relays: 'locked'`), en de pagina’s wachten tot een van die relays antwoordt (`requireHub`). De relays staan binnen een VPN. | de hub van een bedrijf op zijn kiwi-master |
| **Half openbaar** | Een besloten hub met daarnaast een openbaar deel. Daar gebruiken gekozen apps, bijvoorbeeld de chat, openbare relays. | |

De relays van een hub vormen gescheiden netwerken: het eigen netwerk van de hub,
het openbare deel en de netwerken van de spaces. Elk event, een ondertekend
nostr-bericht, hoort bij precies één van die netwerken en wordt nooit aan een
ander netwerk doorgegeven.

## Je eigen distributie { #your-own-distribution }

Begin met Armory, het sjabloon. Op GitHub krijg je met *Use this template* een
kopie van de repository zonder de geschiedenis. Ga daarna zo te werk:

1. Pas **`distribution.js`** aan. In dit bestand staan het id, de naam, het
   logo, de beschrijving, de homepage, de repository, de relays, de
   mediaservers, de spaces, de apps en de mounts. Moet je hub ook de spaces van
   Armory aanbieden, neem dan hun `owner` en `id` over uit `hub.json` van
   Armory.
2. Pas **`locales/*.json`** aan. Daarin staan de titel, de inleiding, de
   voettekst en voor elke mount de tekst op de tegel. Engels is de taal die
   wordt gebruikt als een vertaling ontbreekt.
3. Werk **`kiwi.manifest`** bij. Als je wilt, zet je je hub ook in
   [kiwi-web-catalog](#kiwi-web-catalog).
4. Kies op GitHub *Settings → Pages → Source: GitHub Actions* en push daarna.

Met deze commando’s werk je aan een distributie:

```bash
npm install
npm run dev                  # de hub met hot reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # een lokale testrelay op ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # het skelet van een nieuwe app
```

Zet kiwi-framework vast op een commit of een tag, nooit op een branch. Bij het
bouwen wordt je `distribution.js` gecontroleerd. Een hub met een openbare mount
moet bijvoorbeeld openbare relays hebben, en een hub met openbare relays moet
een openbare mount hebben.

Alles wat je in de browser ziet, is geschreven in TypeScript met React 19 en
wordt gebouwd met Vite. De datalaag in `shared/` is gewoon JavaScript met
JSDoc-types. De tests draaien in de testrunner van node, en de tests die een
browser nodig hebben, draaien in Playwright.

## De hub-container { #the-hub-container }

Armory is ook beschikbaar als container-image, `ghcr.io/derlocke-ng/armory`. Het
image wordt gebouwd uit `container/Dockerfile` van het framework en biedt de
hub aan via nginx. Bij het starten van de container schrijft het entrypoint-script
het bestand `hub.local.json` op basis van de `HUB_*`-variabelen, en de pagina
leest dat bestand voordat ze verbinding maakt. Wie de hub draait, kan zo relays en
beleid kiezen, maar geen code toevoegen. Zijn er geen variabelen gezet, dan
draait de hub zoals hij gebouwd is.

Dit voorbeeld start een hub met een eigen, vergrendelde relay en één mount op
een openbare relay:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variabele | Betekenis |
|---|---|
| `HUB_RELAYS` | De eigen relays van de hub. |
| `HUB_PUBLIC_RELAYS` | De relays van het openbare deel. Is de variabele gezet maar leeg, dan is er geen openbaar deel. |
| `HUB_DIRECTORY_RELAYS` | De relays waar lijsten met relays worden gepubliceerd en opgezocht. |
| `HUB_RELAYS_LOCKED` | Met `true` kunnen gebruikers de relays van de hub niet vervangen. |
| `HUB_REQUIRE_HUB` | Met `true` wachten de pagina’s zolang geen van de relays van de hub antwoordt. |
| `HUB_PUBLIC_MOUNTS` | De mounts die het openbare deel gebruiken, aangeduid met hun id. |
| `HUB_ACCOUNT_MOUNTS` | De mounts die om een account vragen. |
| `HUB_REQUIRE_ACCOUNT` | Met `true` vraagt elke mount om een account. |
| `HUB_SPACE_RELAYS` | De relays per space, geschreven als `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | De sleutels van de moderatoren van alle spaces die de hub zelf definieert. |
| `HUB_REGISTER_POW` | Het aantal bits proof of work dat een nieuw account nodig heeft. Dit is voor relays die alleen leden toelaten. |
| `HUB_CALDAV` | Een Nextcloud-server. nginx stuurt `/remote.php/dav/` naar die server door, zodat de agenda geen CORS nodig heeft. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | De STUN/TURN-servers voor gesprekken en rechtstreekse overdrachten. Ze helpen twee browsers om met elkaar verbinding te maken. De TURN-login is zichtbaar in de pagina, dus maak een TURN-login aan die alleen deze hub gebruikt. |

`HUB_USER_MOUNTS` wordt wel gelezen, maar heeft nog geen effect. De variabele
hoort bij een functie die nog moet komen: een space volgen die niet bij de hub
hoort.

De hub moet via HTTPS worden aangeboden, omdat WebCrypto een beveiligde context
nodig heeft. De relays moeten via `wss://` bereikbaar zijn. Wordt de hub via
gewoon `http://` geopend, op iets anders dan localhost, dan meldt de pagina dat
en stopt ze.

### Een hub op je Kiwi Network { #on-a-kiwi-network }

Een kiwi-master is de enige server van een Kiwi Network die bereikbaar is vanaf
internet. Hij kan een eigen relay en een eigen hub draaien, met twee modules.
De module `nostr-relay` draait de relaysoftware strfry op `relay.<host>`. De
module `hub` draait dit container-image, standaard met Armory, op `hub.<host>`.

Beide zijn standaard besloten. Ze zijn alleen bereikbaar vanuit de mesh en
gebruiken het certificaat van je netwerk. Voor een half openbare hub voeg je
`public_relays` en `public_mounts` toe. Voor een openbare hub voeg je
`reverse-proxy.public` toe, dat certificaten van Let's Encrypt haalt.

De relay van een openbare hub accepteert berichten vanuit de mesh. Vanaf
internet accepteert hij alleen berichten van leden die aantonen dat ze hun
sleutel hebben (NIP-42). Leden zijn de mensen op een lijst die de beheerders
(`write_pubkeys`) hebben ondertekend. Met `members: registered` is iedereen met een
account op de hub lid. Zie het [overzicht van de modules](../server/modules.md#people).

## kiwi-web-catalog { #kiwi-web-catalog }

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
is een catalogus: een git-repository met een lijst van andere repository’s. Er
staan hubs, hun apps en het framework in, en het formaat is hetzelfde als dat
van de catalogus voor de desktop. Het bestand `apps.list` bevat één git-URL per
regel. Een regel kan `path=` hebben voor een app binnen de repository van een
hub, en `ref=` om een versie vast te zetten. Elk item bevat een `kiwi.manifest`
met als `CATEGORY` `Framework`, `Hub` of `App`.

Op dit moment staan er kiwi-framework, Armory en de tien apps van Armory in. De
catalogus is **niet** bedoeld voor `kiwi catalog add`. De items hebben geen
installer, en nog niets leest de catalogus automatisch. Volgens de README zijn
de bestanden van de catalogus publiek domein (CC0).

Wil je je hub toevoegen, fork dan de catalogus, voeg een regel toe, zorg dat je
repository een `kiwi.manifest` bevat en open een pull request.

## Nog niet gebouwd { #not-built-yet }

Deze punten staan op de eigen roadmap van het framework en bestaan nog niet:

- De blog.
- Goedkeuringen bij moderatie (NIP-72 kind 4550).
- Een space volgen die niet bij je hub hoort.
- Inloggen via een browserextensie (NIP-07) of een signer op afstand (NIP-46).
- Een TURN-server in de kiwi-stack. Het werk daarvoor staat in
  kiwi-modules te wachten. Zonder TURN vinden twee telefoons op mobiele data vaak geen
  rechtstreekse verbinding.
