# Hubs, geen platforms

**kiwi-framework** is software waarmee elke community haar eigen **hub** kan
draaien. Een hub is een website met een reeks apps voor de leden van de
community: een open markt, een feed, chat, bestanden delen, gedeelde lijsten,
een wachtwoordbeheerder en een agenda. Iedereen kan een hub draaien voor welke
community dan ook. Die community is dan niet afhankelijk van een centraal
platform dat de accounts en gegevens van iedereen in handen heeft.

De apps draaien volledig in de browser. Ze synchroniseren via
[nostr](https://nostr.com)-relays: servers die ondertekende berichten opslaan en
doorgeven. De community kiest zelf welke relays haar hub gebruikt. Er is geen
accountserver en geen backend tussen de browser en de relays, en alles wat
privé is, wordt op het apparaat versleuteld voordat het wordt verstuurd. De
andere onderdelen van Kiwi Network verbinden je machines, hubs verbinden mensen.
Elke app wordt beschreven in [De apps van het framework](apps.md).

Armory is de eerste hub die met het framework is gebouwd. Het is één voorbeeld,
en tegelijk het sjabloon dat andere community’s kopiëren om hun eigen hub te
bouwen.

De software staat in drie repository’s:

| Repository | Wat het is |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | De algemene software waaruit elke hub wordt gebouwd. Ze bevat identiteit en accounts, relays en synchronisatie, vrienden en delen, moderatie, de designkit, de pagina’s van de hub en tien apps. Het framework zelf kun je niet als website openen: pas een distributie maakt er een hub van. De huidige versie is v0.32.1, de licentie is GPL-3.0-or-later. |
| [**Armory**](armory.md) | De eerste **distributie**, dat wil zeggen een hub die met het framework is gebouwd. Armory voegt een naam, standaardrelays en alle tien apps toe, elk onder een eigen naam. Het is het sjabloon om te forken voor je eigen hub. De licentie is GPL-3.0-or-later. **Online:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | Een catalogus, een git-repository met een lijst van hubs en hun apps. Het formaat is hetzelfde als dat van de [kiwi-catalog](../desktop/catalogs.md) voor de desktop. |

## Hoe het in elkaar zit { #how-it-fits-together }

Het schema laat zien hoe het framework een hub in je browser wordt, en met
welke servers de browser daarna praat.

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

## De begrippen op deze pagina { #the-words }

- **Hub**: de website die een community gebruikt. Een hub krijg je door een
  distributie te bouwen. Hij bestaat alleen uit statische bestanden, dus een hub
  hosten betekent een map met bestanden aanbieden. Elke hub heeft een
  startpagina, een pagina met instellingen en een accountpagina.
- **Distributie**: het framework samen met de keuzes die er één bepaalde hub van
  maken: een naam en uiterlijk, standaardrelays, en een selectie apps op
  gekozen spaces. Fork je een distributie, dan staat alles wat je verandert in
  één bestand, `distribution.js`, en in de vertalingen daarvan.
- **App**: een map met een manifestbestand. Een app kan aan elke distributie
  worden toegevoegd. Apps gebruiken alleen de openbare API van het framework en
  komen nooit rechtstreeks aan de opslag of de sleutels.
- **Space**: een community met een naam, een eigenaar, eigen moderatoren en, als
  ze dat wil, eigen relays. Spaces zijn gebaseerd op de gemodereerde
  community’s van nostr (NIP-72). Een andere hub kan dezelfde space aanbieden
  door het adres van de space op te geven.
- **Mount**: één app die voor één space wordt gebruikt. Elke mount heeft een
  eigen naam, een eigen route (het adres binnen de hub) en een eigen icoon. Eén
  app kan vele keren worden gekoppeld. *Trading Post* van Armory is bijvoorbeeld
  de app `market` van het framework, gekoppeld aan de space `tradingpost` van
  Armory.

Twee mensen die hubs van verschillende distributies gebruiken, kunnen vrienden
zijn, dingen delen en chatten, precies alsof ze dezelfde hub gebruiken. Dat kan
omdat de identiteit en de gegevens van iemand uit nostr-events bestaan:
ondertekende berichten die op relays staan. Ze horen niet bij een hub.

## Accounts en sleutels { #accounts-and-keys }

- De eerste keer dat je een hub op een apparaat opent, maakt de browser een
  sleutel voor dat apparaat aan en bewaart die.
- Een **account** is een gebruikersnaam met een wachtwoord. Het is opgebouwd uit
  gewone nostr-events, en er is geen register van accounts. Je wachtwoord gaat
  door scrypt, een functie die met opzet traag rekent, en het resultaat
  ontgrendelt je sleutel. Zonder het wachtwoord kan niemand een account
  overnemen of overschrijven. Een vergeten wachtwoord kan **niet** opnieuw worden ingesteld.
- Je kunt ook inloggen met een nostr-sleutel die je al hebt, als `nsec`, hex of
  `ncryptsec`. Inloggen via een browserextensie (NIP-07) of een signer op
  afstand (NIP-46) is gepland, maar nog niet gebouwd.
- Eén account werkt in alle apps van de hub en op elk apparaat waarop je
  inlogt.

## Privacymodel { #privacy-model }

**Wat versleuteld is.** De browser versleutelt inhoud voordat hij die ergens
naartoe stuurt. Dat gebeurt met AES-256-GCM, met sleutels die met HKDF worden
afgeleid. Privéberichten zijn NIP-17-berichten in NIP-59-gift-wraps. Een gift
wrap is een tweede laag versleuteling, zodat een relay alleen ziet dat een of
andere sleutel een ingepakt bericht heeft ontvangen. Elk bestand wordt met een
eigen willekeurige AES-256-GCM-sleutel versleuteld voordat het naar een
mediaserver gaat. Foto’s worden eerst opnieuw gecodeerd, waardoor de metadata
die camera’s toevoegen verdwijnt. De Vault is versleuteld met een eigen wachtzin
(scrypt + AES-256-GCM). Gesprekken gaan rechtstreeks van browser naar browser en
worden door WebRTC versleuteld.

**Eerst lokaal.** Alles wat je schrijft, wordt eerst in de eigen database van
de browser opgeslagen en daarna naar de relays gestuurd. De apps lezen uit die
database op het apparaat, dus ze werken ook offline. Komt een apparaat weer
online, dan stuurt het de relay alle gegevens die de relay niet meer heeft.
Gegevens gaan dus alleen verloren als elk apparaat dat ze had weg is *en* er
geen back-up is.

**Wat anderen kunnen zien.** De repository’s noemen de grenzen zelf:

- Relays zien metadata: wie naar welke adressen schrijft, wanneer, hoeveel en
  vanaf welk IP-adres. Gebruik een VPN of Tor als dat voor jou belangrijk is.
- De sleutel van een space is geen geheim. Hij zorgt er alleen voor dat de
  berichten van een community niet openlijk te lezen zijn. Relays zien wel likes
  en meldingen, en wie op wat heeft gereageerd.
- Briefjes op DevBoard en meldingen voor moderatie zijn bewust openbaar.
- Je sleutel staat in de opslag van de browser. Alle GitHub Pages-sites van één
  account hebben dezelfde origin, en browsers scheiden de opslag van websites
  per origin. Een hub op een eigen domein of subdomein is daarom veiliger.
- Bij een rechtstreekse bestandsoverdracht of een gesprek leren de twee
  browsers elkaars IP-adres kennen, en de STUN-servers die helpen de verbinding
  op te zetten, zien ook beide adressen. Standaard zijn dat de STUN-servers van
  Google en Cloudflare. Een hub kan eigen servers instellen.
- “Geen server van ons” betekent dat de apps van geen enkele server van het
  project afhankelijk zijn. Ze gebruiken wel relays, mediaservers en, voor de
  agenda, een CalDAV-server. Welke dat zijn, kies je zelf of kiest je hub.

## Moderatie { #moderation }

Moderatie werkt op drie niveaus. Het eerste is je eigen blokkeerlijst, die
versleuteld is zodat alleen jij hem kunt lezen. Het tweede zijn meldingen, die
openbaar en ondertekend zijn. Het derde is het beleid van elke relay.

Elke space heeft moderatoren. Meldt een moderator een bericht, dan wordt het
meteen ingeklapt. Anders wordt een bericht ingeklapt na drie meldingen van
mensen die niet geblokkeerd zijn. Een bericht kan als 18+ of als advertentie
worden gemarkeerd, en gemarkeerde berichten zijn alleen zichtbaar voor mensen
met een account.

## Verder lezen { #read-on }

- [Armory en zijn apps](armory.md)
- [Je eigen hub draaien](hubs.md)
- De eigen documentatie van het framework over de [architectuur](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  en het [berichtenprotocol](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
