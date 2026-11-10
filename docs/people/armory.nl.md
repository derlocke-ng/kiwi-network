# Armory

Armory is de eerste hub die met kiwi-framework is gebouwd, de software waarmee
elke community haar eigen hub kan draaien. In de termen van het framework is
Armory een **distributie**: het framework samen met een naam, standaardrelays en
een selectie apps. Armory bevat alle tien apps van het framework en geeft ze
eigen namen. De markt en de feed zijn ingericht voor hennepkwekers. Dat
onderwerp is de keuze van deze ene hub, niet van het framework: een andere
community gebruikt dezelfde apps voor haar eigen onderwerp. Je kunt Armory
gebruiken zoals het is, of het kopiëren als sjabloon voor je eigen hub.

Elke tool draait volledig in je browser. De tools synchroniseren via relays,
servers die je gegevens opslaan en doorgeven, en je kiest zelf welke relays je
gebruikt. Je hoeft je niet te registreren, het project draait geen eigen server
voor Armory, en er is geen tracking. Alles wordt versleuteld voordat het je apparaat
verlaat. Vanaf de startpagina kun je Armory als webapp installeren.

- **Openen:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- De repository is [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  de licentie is GPL-3.0-or-later.
- Armory is een distributie van [kiwi-framework](index.md) 0.32.1, vastgezet op
  een commit. Armory zelf heeft nog geen release-tags.
- Armory is er in het Engels, Duits, Frans, Spaans, Italiaans, Nederlands, Pools
  en Portugees.

Vroeger heette Armory weaponized.js.

## De tools { #the-tools }

| Tool | Wat het doet |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Gedeelde boodschappen- en takenlijsten, huishoudvoorraden en notities in Markdown. Ze blijven gelijk op al je apparaten en bij de mensen met wie je ze deelt. Alles is end-to-end versleuteld, en je deelt een lijst met een link waarmee de ander kan bewerken of alleen kan bekijken. Loadout werkt offline, en je apparaten zetten op de relays terug wat de relays kwijt zijn. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Berichten en bestanden aan vrienden (NIP-17, versleuteld op je apparaat). Een groep blijft bestaan tot de beheerder van de groep hem sluit. Iedereen met de link kan een live-kamer binnengaan, en een kamer verdwijnt zodra de laatste persoon weg is. In Uplink kun je antwoorden, reageren, berichten bewerken en vastzetten, op je apparaat zoeken en berichten laten verdwijnen. Spraak- en videogesprekken werken met maximaal zes mensen. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | Bestanden delen op drie manieren. Je kunt een link maken naar bestanden die versleuteld op je mediaservers blijven staan tot je ze verwijdert. Je kunt bestanden naar vrienden en groepen in Uplink sturen. Of je stuurt bestanden rechtstreeks van je browser naar die van een ander, en dan worden ze nergens opgeslagen. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | Een wachtwoordbeheerder voor logins, notities, kaarten en tweestapscodes, op elk apparaat waarop je inlogt. Hij heeft een wachtwoordgenerator en een gezondheidsrapport. Het rapport vindt zwakke, hergebruikte en oude wachtwoorden en, als je die controle aanzet, gelekte wachtwoorden. Vault kan items importeren en exporteren. Daarnaast beheert hij SSH-sleutels, een SSH-certificaatautoriteit, een X.509-CA en TLS-certificaten. Hij is versleuteld met een eigen wachtzin. Wachtwoorden op websites vult hij niet voor je in. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Tweestapscodes (TOTP) voor je accounts bij andere diensten. Je voegt een account toe met een QR-code, een link of het geheim, of uit een export van Google Authenticator. De codes staan in dezelfde versleutelde kluis die Vault gebruikt. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Je agenda’s uit je eigen Nextcloud of een andere CalDAV-server. De agenda toont de komende dagen of een maand, kan terugkerende afspraken aan en herinnert je aan afspraken zolang er een pagina open is. Er gaat niets naar relays, en de aanmeldgegevens voor je server worden versleuteld in je account bewaard. Je server moet verzoeken vanaf de origin van Armory toestaan (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | De feed van Armory, voor kweekverslagen en kweekdagboeken. Je plaatst berichten met foto’s, week na week. Elk bericht kan bedoeld zijn voor iedereen in Outpost, voor je vrienden, voor één kring van vrienden of alleen voor jou. Berichten kunnen hashtags, likes en reacties hebben. Ze worden op je apparaat versleuteld, de foto’s ook. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | De markt van Armory, voor hennep: zaden, stekken en spullen. Advertenties hebben foto’s, en kopers vinden ze via de categorie en via de plaatsen waarheen wordt verzonden. Met “Verkoper berichten” open je Uplink. Je hebt een account nodig om Trading Post te gebruiken, en er is geen leeftijdscontrole. Voordat iemand kan verkopen, moet die in Outpost hebben gepost (drie berichten, elk door drie mensen geliket) of door een moderator zijn goedgekeurd. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | Een prikbord voor freelancers. Je hangt een briefje op dat je mensen zoekt of dat je beschikbaar bent. Elk briefje is ondertekend met je sleutel en vraagt proof of work: een kleine berekening die het massaal plaatsen van briefjes duur maakt. Anderen kunnen op een briefje stemmen. Een briefje verdwijnt als het verloopt, 24 uur tot 30 dagen nadat het is geplaatst. Alle briefjes zijn bewust openbaar. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro-Pong voor twee spelers in twee browsers. Om een spel te starten, deel je een link of een QR-code, of je kiest een van de open spellen. Offline kun je ook tegen de computer oefenen. |

Een blog is gepland.

Elke tool is een van de apps van het framework, onder een naam die Armory
eraan heeft gegeven. Loadout is de app `boards` van het framework, Uplink is
`chat`, Outpost is `feed`, Trading Post is `market`, DevBoard is `notices` en
pongjs is `pong`.

## Eén account voor alle tools { #one-account-every-tool }

Op de startpagina log je in of maak je een account aan, met een gebruikersnaam
en wachtwoord of met een nostr-sleutel. Alle tools gebruiken daarna dat
account. Lijsten die je op een apparaat hebt gemaakt voordat je inlogde, gaan
mee naar het account. Gebruik je geen account, dan werkt elk apparaat met een
eigen sleutel.

De pagina met instellingen geldt voor de hele hub. Daar beheer je je account en
apparaten, vrienden en kringen, geblokkeerde mensen, relays, spaces en
mediaservers, meldingen, en versleutelde back-ups.

## Relays en mediaservers { #relays-and-media-servers }

De standaardrelays van Armory zijn `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` en `wss://relay.primal.net`. Mediaservers bewaren de bestanden
die je uploadt, en gebruiken daarvoor een protocol dat Blossom heet. De
standaardmediaservers van Armory zijn `nostr.download`, `blossom.yakihonne.com`,
`blossom.band` (alleen voor foto’s) en `blossom.primal.net`. In de instellingen
kun je je eigen relays en mediaservers kiezen.

Relays slaan gegevens op en geven ze door, maar ze kunnen niets lezen dat
versleuteld was voordat het werd verstuurd. Wat relays wel kunnen zien, staat in
het [privacymodel](index.md#privacy-model).

## Moderatie { #moderation }

De moderatoren van Armory zijn verantwoordelijk voor Outpost, Trading Post en
DevBoard. Een bericht in Outpost kan als 18+ of als advertentie worden
gemarkeerd. Die markering kan de schrijver zetten of een moderator, en twee meldingen
zetten haar ook. Gemarkeerde berichten zijn alleen zichtbaar voor mensen met een
account.

## Je eigen Armory { #your-own-armory }

Armory is ook het sjabloon voor je eigen hub. Fork de repository of gebruik haar
als sjabloon, pas `distribution.js` en de vertalingen aan, en publiceer het
resultaat. De stappen staan in [Je eigen hub draaien](hubs.md).
