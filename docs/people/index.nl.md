# Hubs, geen platforms

Het netwerk verbindt je machines. **Hubs** verbinden mensen. Een hub is een set
webapps (een open markt, een feed, chat, bestanden delen, gedeelde lijsten, een
wachtwoordbeheerder, een agenda) die volledig in de browser draaien en
synchroniseren via [nostr](https://nostr.com)-relays die de gemeenschap kiest. Er
is geen accountserver en geen backend in het midden, en alles wat privé is, wordt
op het apparaat versleuteld voordat het vertrekt. Iedereen kan een hub draaien
voor elke gemeenschap. Zie [de apps van het framework](apps.md).

Drie repository's vormen het geheel:

| Repository | Wat het is |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | De motor: identiteit en accounts, relays en synchronisatie, mensen en delen, moderatie, de designkit, de hubpagina's en tien apps. Het levert niets wat een gebruiker op zichzelf opent. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | De eerste **distributie**: een hub gebouwd met het framework, met een naam, standaardrelays en alle tien apps gemount onder eigen namen. Het sjabloon om te forken voor je eigen hub. GPL-3.0-or-later. **Live:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Een git-catalogus van hubs en hun apps, in dezelfde vorm als de [kiwi-catalog](../desktop/catalogs.md) voor de desktop |

## Hoe het in elkaar past { #how-it-fits-together }

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

## De begrippen { #the-words }

- **Hub**: wat een distributie oplevert. Statische bestanden, dus er een hosten
  is een map serveren. Elke hub heeft een startpagina, instellingen en een
  accountpagina.
- **Distributie**: een hub gebouwd op het framework, met een naam en uiterlijk,
  standaardrelays, en een gekozen set apps op gekozen spaces. Alles wat een fork
  verandert, staat in één bestand, `distribution.js`, plus de vertalingen ervan.
- **App**: een map met een manifest die in elke distributie past. Apps praten
  alleen met de publieke API van het framework en raken opslag of sleutels nooit
  rechtstreeks aan.
- **Space**: een benoemde gemeenschap met een eigenaar, eigen moderators en,
  optioneel, eigen relays (gemodelleerd naar de gemodereerde communities van
  NIP-72). Een andere hub kan dezelfde space bedienen door het adres ervan te
  noemen.
- **Mount**: app-code op een space, met een eigen naam, route en icoon. Eén app
  kan vele keren gemount worden. *Trading Post* van Armory is de `market`-app van
  het framework, gemount op de space `tradingpost` van Armory.

Twee mensen op verschillende distributies zijn vrienden, delen en chatten precies
zoals op één distributie, omdat identiteit en gegevens nostr-events zijn, niet
van de hub.

## Accounts en sleutels { #accounts-and-keys }

- Elk apparaat krijgt bij het eerste bezoek een sleutel, bewaard in de browser.
- Een **account** is een gebruikersnaam en wachtwoord, gebouwd op gewone
  nostr-events zonder enig register: het wachtwoord wordt met scrypt opgerekt en
  ontgrendelt je sleutel. Niemand kan een account overnemen of overschrijven
  zonder het wachtwoord. Er is **geen wachtwoordherstel**.
- Je kunt ook inloggen met een bestaande nostr-sleutel (`nsec`, hex of
  `ncryptsec`). Signers via een browserextensie en op afstand (NIP-07, NIP-46)
  zijn gepland, niet gebouwd.
- Eén account werkt in alle apps van de hub en op elk apparaat waarop je inlogt.

## Privacymodel { #privacy-model }

**Wat versleuteld is.** Inhoud wordt in de browser verzegeld voordat hij ergens
heen gaat: AES-256-GCM met sleutels afgeleid via HKDF. Privéberichten zijn
NIP-17-berichten in NIP-59-gift-wraps. Bestanden krijgen elk een willekeurige
AES-256-GCM-sleutel voordat ze naar een mediaserver gaan, en foto's worden
opnieuw gecodeerd, waardoor cameragegevens wegvallen. De Vault is verzegeld met
een eigen wachtzin (scrypt + AES-256-GCM). Gesprekken gaan van browser naar
browser, versleuteld door WebRTC.

**Lokaal eerst.** Elke schrijfactie gaat eerst naar de eigen database van de
browser, daarna naar de relays. Leesacties komen van het apparaat, dus de apps
werken offline. Als een apparaat opnieuw verbinding maakt, zet het terug wat een
relay vergeten is: gegevens gaan alleen verloren als elk apparaat dat ze had weg
is *en* er geen back-up is.

**Wat anderen kunnen zien.** De repository's zijn expliciet over de grenzen:

- Relays zien metadata: wie naar welke adressen schrijft, wanneer, hoeveel, en
  vanaf welk IP-adres. Gebruik een VPN of Tor als dat ertoe doet.
- De sleutel van een space is geen geheim. Hij houdt de berichten van een
  gemeenschap uit het zicht. Likes, meldingen en wie waarop reageerde, zijn
  zichtbaar voor relays.
- DevBoard-notities en moderatiemeldingen zijn bewust openbaar.
- Je sleutel staat in de opslag van de browser. Alle GitHub Pages-sites van één
  account delen een origin, dus een hub op een eigen (sub)domein is de sterkere
  opzet.
- Directe overdrachten en gesprekken onthullen de IP-adressen van de twee
  browsers aan elkaar en aan de STUN-servers (standaard die van Google en
  Cloudflare; een hub kan eigen servers instellen).
- "Geen server van ons" betekent: geen enkele in het kritieke pad. De apps
  gebruiken nog steeds de relays, mediaservers en, voor de agenda, de
  CalDAV-server die jij of je hub kiest.

## Moderatie { #moderation }

Drie lagen: je eigen blokkeerlijst (versleuteld, alleen jij kunt hem lezen),
meldingen (openbaar, ondertekend), en het eigen beleid van de relays. Een space
heeft moderators. Een melding van een moderator klapt een bericht meteen in.
Anders zijn er drie meldingen nodig van mensen die niet geblokkeerd zijn.
Berichten kunnen als 18+ of als advertentie worden gemarkeerd, en die zijn alleen
zichtbaar voor mensen met een account.

## Verder lezen { #read-on }

- [Armory en zijn apps](armory.md)
- [Je eigen hub draaien](hubs.md)
- De eigen [architectuur](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  en het [wire-protocol](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
  van het framework
